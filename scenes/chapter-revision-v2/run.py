"""Offline adapter. All private inputs must be supplied explicitly; no TTS/network."""
import argparse, hashlib, json, shutil, subprocess, sys
from pathlib import Path
BASE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def setup(args):
    runtime = args.runtime.resolve()
    if runtime.exists():
        raise ValueError('Use a new runtime directory; existing work/evidence is never overwritten.')
    reference = json.loads((BASE / 'gate-reference.json').read_text())
    validator = args.repository_root.resolve() / reference['canonical_validator']
    if not validator.is_file() or sha(validator) != reference['validator_sha256']:
        raise ValueError('Canonical repository validator missing or changed; review the workflow version explicitly.')
    mapping = json.loads(args.private_inputs.read_text())
    contract = json.loads((BASE / 'private-input-contract.json').read_text())['assets']
    if set(mapping) != set(contract):
        raise ValueError('Private input mapping must contain exactly the contract logical IDs.')
    paths = {}
    for key, value in mapping.items():
        p = Path(value['path'] if isinstance(value, dict) else value).expanduser().resolve()
        if not p.is_file():
            raise ValueError(f'Missing local input: {key}')
        if isinstance(value, dict) and sha(p) != value.get('sha256'):
            raise ValueError(f'Local input differs from your private manifest: {key}')
        paths[key] = p
    font = args.font.resolve()
    if not font.is_file():
        raise ValueError('An installed Chinese-capable font is required.')
    # No source imports: expensive scene initialization occurs only on explicit render.
    shutil.copytree(BASE / 'source', runtime)
    chapter = runtime / 'chapter_revision_v2'
    for key, item in contract.items():
        target = runtime / item['destination']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(paths[key], target)
    gate = runtime / 'workflow-gates-staging/scripts'
    gate.mkdir(parents=True)
    shutil.copyfile(validator, gate / 'validate_production_gate.py')
    for p in chapter.rglob('*.py'):
        p.write_text(p.read_text().replace('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', str(font)))
    # Authorizations from another renderer version must never be carried over.
    ledger = json.loads((BASE / 'production-gate.template.json').read_text())
    storyboard = json.loads((chapter / 'storyboard.json').read_text())
    def reset_reviews(value):
        if isinstance(value, dict):
            if 'status' in value: return {'status': 'not-run', 'reason': 'New local inputs require actual review', 'evidence': []}
            return {k: reset_reviews(v) for k,v in value.items()}
        if isinstance(value, list): return [reset_reviews(v) for v in value]
        return value
    ledger['paragraphs'] = reset_reviews(storyboard['paragraphs'])
    timeline = json.loads((chapter / 'timeline.json').read_text())
    ledger['narration_cues'] = {cue['id']: {'paragraph_id': row['id'], 'source_text': cue['text'], 'start': cue['start'], 'end': cue['end'], 'global_start': row['start'] + cue['start'], 'global_end': row['start'] + cue['end'], 'timing_source': 'Explicit local input; listening not verified'} for row in timeline['paragraphs'] for cue in row['cues']}
    (chapter / 'production-gate.json').write_text(json.dumps(ledger, ensure_ascii=False, indent=2))
    (chapter / 'qa').mkdir(exist_ok=True)
    (chapter / 'output/segments').mkdir(parents=True, exist_ok=True)
    (chapter / 'local-evidence.json').write_text('{}\n')
    (chapter / 'qa/runtime-capability.json').write_text(json.dumps({'python': sys.version.split()[0], 'scope': 'Offline setup only; runtime rendering/performance not yet measured', 'full_render': 'not-run'}, indent=2))
    (runtime / 'local-input-bindings.json').write_text(json.dumps({k: {'path': str(paths[k]), 'sha256': sha(paths[k])} for k in paths}, indent=2))
    (runtime / 'archive-runtime.json').write_text(json.dumps({'archive_provenance_sha256': sha(BASE / 'provenance.json'), 'font_path': str(font), 'font_sha256': sha(font), 'approval_state': 'not-run; new version-bound review required'}, indent=2))
    print('Created isolated runtime. Compile helper and review actual frames before granting render approvals.')

def make_manifest(args):
    """Compute hashes locally; output is private and must not be committed."""
    contract = json.loads((BASE / 'private-input-contract.json').read_text())['assets']
    inputs = json.loads(args.private_inputs.read_text())
    if set(inputs) != set(contract): raise ValueError('Expected exactly the input contract IDs.')
    result = {}
    for key, value in inputs.items():
        path = Path(value['path'] if isinstance(value, dict) else value).expanduser().resolve()
        if not path.is_file(): raise ValueError(f'Missing local input: {key}')
        result[key] = {'path': str(path), 'sha256': sha(path)}
    if args.output.exists(): raise ValueError('Refusing to overwrite an existing private manifest.')
    args.output.write_text(json.dumps(result, indent=2))
    print('Private local manifest created; keep it outside version control.')

def activate_version(chapter, paragraph):
    """Select exact recorded scene dependencies only in this private working tree."""
    manifest = json.loads((BASE / 'paragraph-source-map.json').read_text())
    if paragraph not in manifest['sections']:
        raise ValueError('No actual source-bound record for this section yet.')
    version = manifest['sections'][paragraph]
    font = json.loads((chapter.parent / 'archive-runtime.json').read_text())['font_path']
    selected = dict(version['scene_sources'])
    # Preserve current fail-closed integration renderer; record legacy integration
    # source separately. Scene/compositor/timing bytes determine sampled pixels.
    selected.update({k:v for k,v in version['integration_sources'].items() if k != 'render.py'})
    for target, item in selected.items():
        source = BASE / item['archive']
        if sha(source) != item['sha256']: raise ValueError('Archived variant bytes changed.')
        dest = chapter / target; dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(source.read_text().replace('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', font))
    if 'scenes/stellar/galaxy_native.cpp' in selected:
        src = chapter / 'scenes/stellar/galaxy_native.cpp'
        subprocess.run(['g++', '-std=c++17', '-O3', '-shared', '-fPIC', '-fopenmp', str(src), '-o', str(src.with_suffix('.so'))], check=True)
    (chapter / 'qa/active-version.json').write_text(json.dumps({'paragraph': paragraph, 'source_map': version, 'scope': 'Private portable adaptation; reviews must bind actual adapted bytes'}, indent=2))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    sp = p.add_subparsers(dest='action', required=True)
    s = sp.add_parser('setup'); s.add_argument('--runtime', type=Path, required=True); s.add_argument('--private-inputs', type=Path, required=True); s.add_argument('--font', type=Path, required=True); s.add_argument('--repository-root', type=Path, required=True)
    s = sp.add_parser('manifest'); s.add_argument('--private-inputs', type=Path, required=True); s.add_argument('--output', type=Path, required=True)
    for name in ['compile-native', 'frame', 'section', 'inspect', 'snapshot', 'assemble', 'qa']:
        s = sp.add_parser(name); s.add_argument('--runtime', type=Path, required=True)
        if name in ['frame', 'section', 'inspect']: s.add_argument('--paragraph', required=True)
        if name == 'qa': s.add_argument('--video', type=Path, required=True)
    a = p.parse_args()
    if a.action == 'setup': return setup(a)
    if a.action == 'manifest': return make_manifest(a)
    r = a.runtime.resolve(); c = r / 'chapter_revision_v2'
    if not (r / 'archive-runtime.json').is_file(): raise ValueError('Run explicit setup first.')
    if a.action == 'compile-native':
        src = c / 'scenes/stellar/galaxy_native.cpp'
        subprocess.run(['g++', '-std=c++17', '-O3', '-shared', '-fPIC', '-fopenmp', str(src), '-o', str(src.with_suffix('.so'))], check=True)
        return
    if a.action in ['frame', 'section']: activate_version(c, a.paragraph)
    script = {'frame': 'compositor.py', 'section': 'render.py', 'inspect': 'inspect_section.py', 'snapshot': 'snapshot_inputs.py', 'assemble': 'assemble.py', 'qa': 'qa.py'}[a.action]
    args = [sys.executable, str(c / script)]
    if hasattr(a, 'paragraph'): args.append(a.paragraph)
    if hasattr(a, 'video'): args.append(str(a.video.resolve()))
    subprocess.run(args, cwd=c, check=True)

if __name__ == '__main__': main()
