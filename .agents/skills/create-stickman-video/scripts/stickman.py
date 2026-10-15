#!/usr/bin/env python3
"""Offline storyboard validation and provider-neutral prompt compilation (stdlib only)."""
import argparse
import hashlib
import json
import math
import sys
from decimal import Decimal
from pathlib import Path

STYLES = {
    'classic-light': 'Hollow-head black line stick figures on a flat pure white field; monochrome figures, limited accent colors on props, stable line weight, no realistic depth.',
    'classic-dark': 'Hollow-head white line stick figures on a flat pure black field; monochrome figures, inverse light/dark polarity, stable line weight, no realistic depth.',
    'studio-tech': 'Simple clothed 2D stick characters in a sparse bright studio; restrained floor grid and icon-only floating panels. No circuit-board walls or busy UI; clothing follows the character anchors.',
    'cinematic-story': 'Clean 2D stick characters in colored narrative settings with deliberate lighting and depth. No realistic human anatomy or 3D avatars.',
    'prehistoric-comedy': 'Rough outlines, expressive light-filled heads, stick limbs, story-specific clothing and earthy settings. Distinct cast identities and held comedic reactions; modern workplace analogies are fiction, not archaeological reconstructions.',
    'cozy-story': 'Simple expressive characters in full-color 2D locations, varied shots and motivated location cuts. Preserve character, narrator, important props and screen direction. No forced paper texture, single-room restriction, or visible drawing hand.',
}
NEGATIVES = [
    'Do not change character anatomy, clothing, colors, identity, or declared voice between clips.',
    'Do not add narration, translate narration, or paraphrase the exact narration text.',
    'No visible text: no subtitles, captions, speech bubbles, dialogue boxes, letters, logos, or watermarks. Any exact labels or subtitles belong only on a separate post-production overlay track.',
    'Do not invent characters or props, teleport props, or change ownership outside the declared action.',
    'Do not introduce unrequested camera moves, timing changes, extra limbs, or photorealistic human anatomy.',
]

class Invalid(ValueError):
    """An actionable, user-facing input error."""


def need(condition, message):
    if not condition:
        raise Invalid(message)


def obj(value, path):
    need(isinstance(value, dict), f'{path}: expected an object')
    return value


def string(value, path, allow_empty=False):
    need(isinstance(value, str) and (allow_empty or bool(value.strip())),
         f'{path}: expected {"a string" if allow_empty else "a nonempty string"}')
    return value


def number(value, path, positive=False):
    need(type(value) in (int, float), f'{path}: expected a finite number')
    try:
        finite = math.isfinite(value)
    except (OverflowError, ValueError):
        finite = False
    need(finite and (value > 0 if positive else value >= 0),
         f'{path}: expected a finite {"positive" if positive else "nonnegative"} number')
    return Decimal(str(value))


def digest(project):
    body = {k: v for k, v in project.items() if k != 'approval'}
    try:
        canonical = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    except (ValueError, TypeError, UnicodeError) as exc:
        raise Invalid(f'Project cannot be canonicalized as UTF-8 JSON: {exc}') from None


def state(value, path):
    obj(value, path)
    # State is deliberately extensible: use identical JSON structures to declare continuity.
    # Keys should describe character positions and prop ownership; values may be structured.
    need(bool(value), f'{path}: provide character positions and/or prop ownership, not an empty state')
    return value


def validate(project, require_approved=False):
    obj(project, 'project')
    need(type(project.get('version')) is int and project['version'] == 1, 'version: expected integer 1')
    for field in ('title', 'source_summary', 'language', 'voice_lock'):
        string(project.get(field), field)
    need(project.get('ratio') in ('16:9', '9:16'), 'ratio: expected 16:9 or 9:16')
    need(isinstance(project.get('style'), str) and project['style'] in STYLES, 'style: unsupported preset')
    duration = number(project.get('duration_s'), 'duration_s', positive=True)
    chars = obj(project.get('characters'), 'characters')
    need(bool(chars), 'characters: at least one character anchor is required')
    for key, anchor in chars.items():
        string(key, 'character ID')
        string(anchor, f'characters.{key}')
    palette = project.get('palette')
    need(isinstance(palette, list) and len(palette) > 0, 'palette: expected a nonempty list')
    for i, color in enumerate(palette):
        string(color, f'palette[{i}]')
    clips = project.get('clips')
    need(isinstance(clips, list) and len(clips) > 0, 'clips: expected a nonempty list')
    total, ids, prior = Decimal(0), set(), None
    for i, clip in enumerate(clips):
        p = f'clips[{i}]'
        obj(clip, p)
        cid = string(clip.get('id'), p + '.id')
        need(cid not in ids, p + '.id: duplicate clip ID')
        ids.add(cid)
        length = number(clip.get('duration_s'), p + '.duration_s', positive=True)
        total += length
        for field in ('environment', 'composition'):
            string(clip.get(field), p + '.' + field)
        string(clip.get('narration'), p + '.narration', allow_empty=True)
        refs = clip.get('characters')
        need(isinstance(refs, list), p + '.characters: expected a list')
        seen = set()
        for ref in refs:
            string(ref, p + '.characters entry')
            need(ref in chars, p + '.characters: unknown character ' + ref)
            need(ref not in seen, p + '.characters: duplicate character ' + ref)
            seen.add(ref)
        opening = state(clip.get('opening_state'), p + '.opening_state')
        closing = state(clip.get('closing_state'), p + '.closing_state')
        transition = obj(clip.get('transition'), p + '.transition')
        kind = transition.get('kind')
        need(kind in ('continuous', 'cut'), p + '.transition.kind: expected continuous or cut')
        string(transition.get('reason'), p + '.transition.reason', allow_empty=(kind == 'continuous'))
        if prior is not None and kind == 'continuous':
            need(opening == prior, p + '.opening_state: continuous transition must equal preceding closing_state')
        prior = closing
        beats = clip.get('beats')
        need(isinstance(beats, list) and len(beats) > 0, p + '.beats: expected a nonempty list')
        last = Decimal(0)
        for j, beat in enumerate(beats):
            b = f'{p}.beats[{j}]'
            obj(beat, b)
            start = number(beat.get('start_s'), b + '.start_s')
            end = number(beat.get('end_s'), b + '.end_s', positive=True)
            need(start == last, b + '.start_s: beats must be contiguous and begin at 0')
            need(end > start and end <= length, b + ': require start_s < end_s <= clip duration')
            for field in ('action', 'camera', 'sfx'):
                string(beat.get(field), b + '.' + field)
            last = end
        need(last == length, p + '.beats: beats must cover the full clip duration')
    need(total == duration, f'duration_s: clip sum {total} does not equal declared total {duration}')
    approval = obj(project.get('approval'), 'approval')
    need(approval.get('status') in ('draft', 'user-approved', 'delegated-proceed'), 'approval.status: expected draft, user-approved, or delegated-proceed')
    string(approval.get('digest'), 'approval.digest', allow_empty=True)
    actual = digest(project)
    if approval['status'] in ('user-approved', 'delegated-proceed'):
        string(approval.get('evidence'), 'approval.evidence')
        need(approval['digest'] == actual, 'approval.digest: stale or invalid proceed authority; review the current storyboard again')
    if require_approved:
        need(approval['status'] in ('user-approved', 'delegated-proceed'), 'Compilation requires recorded user approval or delegated proceed authority for this exact storyboard and digest')
    return actual


def compile_project(project):
    # This checks the record, not the identity or truth of its author. The caller
    # must obtain actual user authority; setting JSON fields cannot grant it.
    approved_digest = validate(project, require_approved=True)
    compiled = []
    offset = Decimal(0)
    for clip in project['clips']:
        # Repeat complete anchors for the visible cast only. Each clip is standalone.
        sections = [
            f"STORYBOARD: {project['title']}\nSOURCE SUMMARY: {project['source_summary']}",
            f"STYLE LOCK [{project['style']}]: {STYLES[project['style']]}",
            f"ASPECT RATIO: {project['ratio']}\nLANGUAGE: {project['language']}\nPALETTE LOCK: " + json.dumps(project['palette'], ensure_ascii=False),
            'COMPLETE VISIBLE CHARACTER LOCKS:\n' + ('\n'.join(f'{key}: {project["characters"][key]}' for key in clip['characters']) or '(No characters visible.)'),
            'VOICE LOCK: ' + project['voice_lock'],
            'ONLY CHARACTERS PRESENT: ' + json.dumps(clip['characters'], ensure_ascii=False) + '\nAny character not listed here MUST NOT appear, including in reflections, crowds, or background imagery.',
            f"CLIP {clip['id']}: exactly {clip['duration_s']} seconds; timeline offset {offset} seconds.",
            f"ENVIRONMENT: {clip['environment']}\nCOMPOSITION: {clip['composition']}",
            'OPENING STATE: ' + json.dumps(clip['opening_state'], ensure_ascii=False, sort_keys=True),
            'CLOSING STATE: ' + json.dumps(clip['closing_state'], ensure_ascii=False, sort_keys=True),
            'INCOMING TRANSITION: ' + json.dumps(clip['transition'], ensure_ascii=False),
            'TIMED BEATS (seconds relative to clip):\n' + '\n'.join(
                f"{b['start_s']}–{b['end_s']}: ACTION: {b['action']} | CAMERA: {b['camera']} | SFX: {b['sfx']}" for b in clip['beats']),
            'EXACT AUDIO-ONLY NARRATION (verbatim spoken words; never visible text or speech bubbles; empty means silence):\n' + clip['narration'],
            'NEGATIVE CONSTRAINTS:\n' + '\n'.join(NEGATIVES),
        ]
        compiled.append({'id': clip['id'], 'duration_s': clip['duration_s'], 'timeline_start_s': float(offset),
                         'narration': clip['narration'], 'prompt': '\n\n'.join(sections)})
        offset += Decimal(str(clip['duration_s']))
    return {'artifact_type': 'prompt-package', 'version': 1, 'storyboard_digest': approved_digest, 'proceed_authority': project['approval']['status'],
            'title': project['title'], 'duration_s': project['duration_s'], 'ratio': project['ratio'],
            'status': 'compiled-prompts-only', 'clips': compiled}


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'JSON contains a duplicate object key: ' + key)
        result[key] = value
    return result


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=no_duplicates,
                          parse_constant=lambda value: (_ for _ in ()).throw(Invalid('Non-finite JSON number: ' + value)))
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise Invalid(f'Cannot read storyboard: {exc}') from None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('validate', help='Validate draft or approved JSON and print its digest').add_argument('project')
    compiler = commands.add_parser('compile', help='Compile a storyboard with recorded proceed authority into standalone prompts')
    compiler.add_argument('project')
    compiler.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    try:
        project = load(args.project)
        if args.command == 'validate':
            print(json.dumps({'valid': True, 'digest': validate(project)}, ensure_ascii=False))
        else:
            source, output = Path(args.project), Path(args.out)
            need(source.resolve() != output.resolve() and
                 not (output.exists() and source.samefile(output)),
                 'Output must not overwrite the source storyboard')
            package = compile_project(project)
            Path(args.out).write_text(json.dumps(package, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
            print(json.dumps({'artifact_type': 'prompt-package', 'output': args.out, 'clips': len(package['clips'])}))
        return 0
    except (Invalid, OSError, UnicodeError, RecursionError) as exc:
        print('Error: ' + str(exc), file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
