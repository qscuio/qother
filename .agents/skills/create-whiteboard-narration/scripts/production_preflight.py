#!/usr/bin/env python3
"""Local, read-only production gates. Never synthesizes speech or renders a video."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
from scene_contract import inspect_style


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def checked_file(record, root, key='path'):
    path = root / record[key]
    if not path.is_file():
        raise ValueError(f'Missing file: {path}')
    if record.get('sha256') != sha256_file(path):
        raise ValueError(f'Changed or unbound file: {path}; repeat the relevant review')
    return path


def positive(value, name):
    if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f'{name} must be finite and positive')
    return float(value)


def voice_configuration_hash(voice):
    configuration = {key: voice.get(key) for key in ('provider', 'model', 'id')}
    configuration['settings'] = voice.get('settings', {})
    encoded = json.dumps(configuration, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def voice_gate(project, root):
    narration = project['narration']
    source = narration.get('source')
    if source == 'provided':
        return {'status': 'provided_audio', 'acceptance': 'Reuse supplied audio; no synthesis audition required'}
    if source != 'synthesized':
        raise ValueError('narration.source must be provided or synthesized')
    voice = narration.get('voice', {})
    identity = {key: voice.get(key) for key in ('provider', 'model', 'id')}
    if not all(isinstance(v, str) and v.strip() for v in identity.values()):
        raise ValueError('Select an exact provider, model, and voice id before full synthesis')
    if any(isinstance(rejected, dict) and all(rejected.get(k) == v for k, v in identity.items())
           for rejected in project.get('rejected_voices', [])):
        raise ValueError('Selected voice is rejected; choose a different voice or record the user’s explicit changed decision')
    acceptance = voice.get('acceptance', {})
    if acceptance.get('status') != 'accepted' or not acceptance.get('user_evidence'):
        raise ValueError('Full synthesis is blocked until the user accepts an audition of this exact voice')
    if acceptance.get('configuration_sha256') != voice_configuration_hash(voice):
        raise ValueError('Voice configuration changed or is unbound; accept an audition of the exact provider/model/id/settings')
    checked_file(acceptance['sample'], root)
    return {'status': 'accepted_record', 'voice': identity,
            'scope': 'Recorded user decision and audition hash; no listening performed by this tool'}


def measured_duration(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(path)],
                            capture_output=True, text=True, check=True)
    return positive(float(json.loads(result.stdout)['format']['duration']), 'measured audio duration')


def narration_gate(project, root):
    narration = project['narration']
    path = checked_file(narration['master'], root)
    script = checked_file(narration['script'], root).read_text(encoding='utf-8')
    duration = measured_duration(path)
    recorded = positive(narration.get('duration_seconds'), 'narration.duration_seconds')
    if abs(recorded - duration) > .02:
        raise ValueError('Recorded narration duration differs from measured master duration')
    if narration.get('timing_method') not in ('manual_measured', 'provider_timestamps', 'forced_alignment'):
        raise ValueError('Narration requires measured timings; interpolation is preview-only')
    if narration.get('continuous_master') is not True:
        raise ValueError('Keep one authoritative continuous narration master')
    if narration.get('visual_edit_audio_policy') != 'preserve_master':
        raise ValueError('Visual scene edits must preserve the approved master; no hidden chunk resynthesis')
    beats = narration.get('beats', [])
    if not beats or ''.join(b.get('text', '') for b in beats) != script:
        raise ValueError('Ordered beat text must reproduce the exact approved script, including whitespace')
    seen, end = set(), 0.0
    for beat in beats:
        name = beat.get('id')
        start, stop = beat.get('start'), beat.get('end')
        if not isinstance(name, str) or not name or name in seen:
            raise ValueError('Narration beat ids must be unique and nonempty')
        if not all(isinstance(t, (int, float)) and math.isfinite(t) for t in (start, stop)) or not end <= start < stop <= duration + .001:
            raise ValueError('Narration beats must be finite, ordered, nonoverlapping, and inside the master')
        seen.add(name); end = stop
    return {'status': 'pass', 'master_sha256': sha256_file(path), 'duration_seconds': duration,
            'beat_count': len(beats), 'timing_evidence': 'declared method and bounds checked; alignment not performed'}


def scene_gate(project, root):
    scenes = project.get('scenes', [])
    if not scenes:
        raise ValueError('Record and review each production storyboard before full rendering')
    baseline = project.get('style_id')
    if not isinstance(baseline, str) or not baseline.strip():
        raise ValueError('Project needs a shared style_id')
    reports = []
    ids = set()
    shared_style = None
    for scene in scenes:
        if not scene.get('id') or scene['id'] in ids:
            raise ValueError('Scene ids must be unique and nonempty')
        ids.add(scene['id'])
        path = checked_file(scene['storyboard'], root)
        spec = json.loads(path.read_text(encoding='utf-8'))
        style = inspect_style(spec)
        if style['status'] != 'pass' or style.get('baseline') != baseline:
            raise ValueError(f"Scene {scene['id']} has a failing or inconsistent style contract")
        definition = spec['style']
        signature = json.dumps({
            'palette': sorted([list(c[:3]) for c in definition['palette']]),
            'outline_width_range': definition.get('outline_width_range', [2, 6]),
            'caption_lane_top': definition.get('caption_lane_top', 590)
        }, sort_keys=True)
        if shared_style is not None and signature != shared_style:
            raise ValueError(f"Scene {scene['id']} changes the shared palette, line weights, or caption lane")
        shared_style = signature
        review = scene.get('visual_review', {})
        if review.get('status') != 'accepted' or not review.get('reviewer') or not review.get('evidence'):
            raise ValueError(f"Scene {scene['id']} needs an explicit visual review with evidence")
        # Review the actual sampled artwork, not only a storyboard checksum.
        checked_file(review['sample'], root)
        if not scene.get('narration_quote') or not scene.get('explains'):
            raise ValueError(f"Scene {scene['id']} needs a narration quote and observable visual purpose")
        spoken = ''.join(b.get('text', '') for b in project.get('narration', {}).get('beats', []))
        if scene['narration_quote'] not in spoken:
            raise ValueError(f"Scene {scene['id']} quote is absent from the measured narration beats")
        reports.append({'id': scene['id'], 'status': 'accepted_record', 'style': style})
    return reports


def delivery_budget(duration, limit_mib, audio_kbps=160, reserve=.05):
    duration = positive(duration, 'duration')
    limit_mib = positive(limit_mib, 'delivery limit MiB')
    if not isinstance(audio_kbps, (int, float)) or not math.isfinite(audio_kbps) or audio_kbps < 0:
        raise ValueError('audio bitrate must be finite and nonnegative')
    if not 0 < reserve < 1:
        raise ValueError('container/variance reserve must lie between zero and one')
    limit = math.floor(limit_mib * 1024 * 1024)
    total_kbps = limit * 8 / duration / 1000
    video = math.floor(total_kbps * (1-reserve) - audio_kbps)
    if video < 64:
        raise ValueError('Delivery limit leaves under 64 kbps for video; change destination, duration, or audio/video settings')
    return {'limit_bytes': limit, 'duration_seconds': duration, 'video_target_kbps': video,
            'audio_kbps': audio_kbps, 'reserve_fraction': reserve,
            'guaranteed_size': False, 'next_check': 'Measure the final file; bitrate estimates do not prove delivery fit'}


def delivery_gate(project, root, narration_report):
    delivery = project.get('delivery', {})
    plan = delivery_budget(narration_report['duration_seconds'], delivery.get('limit_mib'), delivery.get('audio_kbps', 160))
    if not delivery.get('destination'):
        raise ValueError('Record the intended delivery destination and its verified size limit')
    if 'final_file' in delivery:
        path = root / delivery['final_file']
        if not path.is_file():
            raise ValueError('Delivery final_file must be a regular file, not a directory or missing path')
        size = path.stat().st_size
        if size <= 0:
            raise ValueError('Delivery final_file is empty')
        plan.update(actual_bytes=size, fits=size <= plan['limit_bytes'])
        if not plan['fits']:
            raise ValueError(f'Final file exceeds delivery limit: {size} > {plan["limit_bytes"]} bytes')
    return plan


def run(project, root, stage):
    if project.get('version') != 1:
        raise ValueError('Project manifest version must be 1')
    report = {'stage': stage, 'voice': voice_gate(project, root),
              'listening_review': 'not_performed', 'media_decode': 'not_performed'}
    if stage != 'voice':
        report['narration'] = narration_gate(project, root)
        report['scenes'] = scene_gate(project, root)
        report['delivery'] = delivery_gate(project, root, report['narration'])
    if stage == 'delivery' and 'final_file' not in project.get('delivery', {}):
        raise ValueError('Delivery gate requires delivery.final_file and actual size verification')
    report['status'] = 'pass'
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--stage', choices=['voice', 'render', 'delivery'], default='render')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--voice-fingerprint', action='store_true', help='Print the exact selected voice configuration hash; does not accept or approve it')
    args = parser.parse_args()
    try:
        project = json.loads(args.manifest.read_text(encoding='utf-8'))
        if args.voice_fingerprint:
            report = {'configuration_sha256': voice_configuration_hash(project['narration']['voice']), 'acceptance': 'not_granted'}
        else:
            report = run(project, args.manifest.parent, args.stage)
        payload = json.dumps(report, ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(payload, encoding='utf-8')
        print(payload)
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({'status': 'blocked', 'error': str(exc)}, ensure_ascii=False)); return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
