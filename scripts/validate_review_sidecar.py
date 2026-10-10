#!/usr/bin/env python3
"""Original, dependency-free structural review-sidecar v1 validator.

API: validate(document) -> None, or raises ValidationError (first JSON-path error).
CLI: python validate_review_sidecar.py FILE.json. Exit 0 valid, 1 invalid.
All ranges are half-open integer frames. Sources have their own rational fps;
timeline has rational fps. rate is source seconds / timeline seconds. No rounding
is implied: mapped endpoints must agree exactly. Optional start_seconds and
end_seconds are redundant checks (absolute tolerance 1e-9 seconds).

Shots cover [0, duration_frames), unless policy.allow_gaps is true. Overlaps
require policy.allow_overlaps true. Cues need not cover the whole timeline and
may overlap independently. Each cue references one shot and follows its mapping.
Caption coverage_source_ranges must cover its declared source_range completely.
Optional audio_groups reference cues of matching narration/music/sfx role.
This checks declared structure, NOT media existence, spoken words, perceptual
caption quality, synchronization in rendered media, loudness or audio ducking.
Unknown object fields are rejected to expose misspellings and unit ambiguity.
"""
import argparse
from fractions import Fraction
import json
import math
import sys


class ValidationError(ValueError):
    """Invalid sidecar with a JSON path and explanation."""


def fail(path, message):
    raise ValidationError(f"{path}: {message}")


def obj(value, path, required, optional=()):
    if not isinstance(value, dict):
        fail(path, "expected object")
    for key in required:
        if key not in value:
            fail(f"{path}.{key}", "required field missing")
    for key in value:
        if key not in set(required) | set(optional):
            fail(f"{path}.{key}", "unknown field")
    return value


def integer(value, path, minimum=0):
    if type(value) is not int or value < minimum:
        fail(path, f"expected integer >= {minimum} (booleans are not integers)")
    return value


def rational(value, path):
    obj(value, path, ('num', 'den'))
    return Fraction(integer(value['num'], path+'.num', 1),
                    integer(value['den'], path+'.den', 1))


def items(value, path, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        fail(path, 'expected '+('nonempty ' if nonempty else '')+'array')
    return value


def identifier(value, path):
    if not isinstance(value, str) or not value.strip():
        fail(path, "expected nonempty string")
    return value


def frame_range(value, path, fps):
    obj(value, path, ('start', 'end'), ('start_seconds', 'end_seconds'))
    a = integer(value['start'], path+'.start')
    b = integer(value['end'], path+'.end')
    if b <= a:
        fail(path, "end must exceed start (half-open frame range)")
    for field, frame in (('start_seconds', a), ('end_seconds', b)):
        if field in value:
            seconds = value[field]
            if type(seconds) not in (int, float) or (type(seconds) is float and not math.isfinite(seconds)):
                fail(path+'.'+field, 'expected finite number, not boolean')
            if abs(Fraction(str(seconds)) - Fraction(frame, 1)/fps) > Fraction(1, 10**9):
                fail(path+'.'+field, 'inconsistent with frames and fps')
    return a, b


def validate(document):
    """Validate one decoded JSON document; return None or raise ValidationError."""
    d = obj(document, '$', ('schema', 'timeline', 'sources', 'shots'),
            ('cues', 'audio_groups', 'policy'))
    if d['schema'] != 'review-sidecar/v1':
        fail('$.schema', 'expected review-sidecar/v1')
    t = obj(d['timeline'], '$.timeline', ('fps', 'duration_frames'))
    tfps = rational(t['fps'], '$.timeline.fps')
    duration = integer(t['duration_frames'], '$.timeline.duration_frames', 1)
    policy = obj(d.get('policy', {}), '$.policy', (), ('allow_gaps', 'allow_overlaps'))
    for k, v in policy.items():
        if type(v) is not bool:
            fail('$.policy.'+k, 'expected boolean')
    ids = set()

    def register(entry, path):
        key = identifier(entry['id'], path+'.id')
        if key in ids:
            fail(path+'.id', f'duplicate id {key!r}; IDs are globally unique')
        ids.add(key)
        return key

    sources = {}
    for i, source in enumerate(items(d['sources'], '$.sources', True)):
        p = f'$.sources[{i}]'
        obj(source, p, ('id', 'fps', 'duration_frames'))
        key = register(source, p)
        sources[key] = (rational(source['fps'], p+'.fps'),
                        integer(source['duration_frames'], p+'.duration_frames', 1))
    shots, spans = {}, []
    for i, shot in enumerate(items(d['shots'], '$.shots', True)):
        p = f'$.shots[{i}]'
        obj(shot, p, ('id', 'source_id', 'source_range', 'timeline_range', 'rate'))
        key = register(shot, p)
        source_id = identifier(shot['source_id'], p+'.source_id')
        if source_id not in sources:
            fail(p+'.source_id', 'unknown source reference')
        sfps, limit = sources[source_id]
        sa, sb = frame_range(shot['source_range'], p+'.source_range', sfps)
        ta, tb = frame_range(shot['timeline_range'], p+'.timeline_range', tfps)
        rate = rational(shot['rate'], p+'.rate')
        if sb > limit:
            fail(p+'.source_range.end', 'exceeds source duration')
        if tb > duration:
            fail(p+'.timeline_range.end', 'exceeds timeline duration')
        if Fraction(sb-sa, 1)/sfps != Fraction(tb-ta, 1)/tfps*rate:
            fail(p+'.rate', 'source/timeline duration mismatch under retime')
        shots[key] = (sa, sb, ta, tb, sfps, rate)
        spans.append((ta, tb, p))
    cursor = 0
    for a, b, p in sorted(spans):
        if a > cursor and not policy.get('allow_gaps', False):
            fail(p+'.timeline_range.start', 'timeline gap requires policy.allow_gaps=true')
        if a < cursor and not policy.get('allow_overlaps', False):
            fail(p+'.timeline_range.start', 'timeline overlap requires policy.allow_overlaps=true')
        cursor = max(cursor, b)
    if cursor < duration and not policy.get('allow_gaps', False):
        fail('$.timeline.duration_frames', 'trailing gap requires policy.allow_gaps=true')

    cues = {}
    for i, cue in enumerate(items(d.get('cues', []), '$.cues')):
        p = f'$.cues[{i}]'
        obj(cue, p, ('id', 'role', 'shot_id', 'source_range', 'timeline_range'),
            ('coverage_source_ranges', 'text'))
        key = register(cue, p)
        role = identifier(cue['role'], p+'.role')
        if role not in ('caption', 'narration', 'music', 'sfx'):
            fail(p+'.role', 'expected caption, narration, music or sfx')
        shot_id = identifier(cue['shot_id'], p+'.shot_id')
        if shot_id not in shots:
            fail(p+'.shot_id', 'unknown shot reference')
        sa, sb, ta, tb, sfps, rate = shots[shot_id]
        ca, cb = frame_range(cue['source_range'], p+'.source_range', sfps)
        da, db = frame_range(cue['timeline_range'], p+'.timeline_range', tfps)
        if ca < sa or cb > sb:
            fail(p+'.source_range', 'outside referenced shot source range')
        if da < ta or db > tb:
            fail(p+'.timeline_range', 'outside referenced shot timeline range')
        if any(Fraction(c-sa, 1)/sfps/rate != Fraction(f-ta, 1)/tfps
               for c, f in ((ca, da), (cb, db))):
            fail(p+'.timeline_range', 'does not agree with referenced shot source mapping')
        if 'text' in cue:
            identifier(cue['text'], p+'.text')
        if role == 'caption' and 'coverage_source_ranges' not in cue:
            fail(p+'.coverage_source_ranges', 'required for caption source coverage')
        if 'coverage_source_ranges' in cue:
            coverage = []
            for j, r in enumerate(items(cue['coverage_source_ranges'], p+'.coverage_source_ranges', True)):
                rp = f'{p}.coverage_source_ranges[{j}]'
                a, b = frame_range(r, rp, sfps)
                if a < ca or b > cb:
                    fail(rp, 'outside cue source range')
                coverage.append((a, b))
            end = ca
            for a, b in sorted(coverage):
                if a > end:
                    fail(p+'.coverage_source_ranges', 'source coverage gap')
                end = max(end, b)
            if end != cb:
                fail(p+'.coverage_source_ranges', 'incomplete source coverage')
        cues[key] = role
    grouped = set()
    for i, group in enumerate(items(d.get('audio_groups', []), '$.audio_groups')):
        p = f'$.audio_groups[{i}]'
        obj(group, p, ('id', 'role', 'cue_ids'))
        register(group, p)
        role = identifier(group['role'], p+'.role')
        if role not in ('narration', 'music', 'sfx'):
            fail(p+'.role', 'expected narration, music or sfx')
        for j, ref in enumerate(items(group['cue_ids'], p+'.cue_ids', True)):
            rp = f'{p}.cue_ids[{j}]'
            identifier(ref, rp)
            if ref not in cues:
                fail(rp, 'unknown cue reference')
            if cues[ref] != role:
                fail(rp, 'cue role does not match audio group role')
            if ref in grouped:
                fail(rp, 'cue already assigned to an audio group')
            grouped.add(ref)


def load(path):
    """Load JSON; reject duplicate keys as well as nonstandard NaN/Infinity."""
    def pairs(entries):
        result = {}
        for key, value in entries:
            if key in result:
                fail('$', f'duplicate JSON key {key!r}')
            result[key] = value
        return result

    def constant(value):
        fail('$', f'nonfinite JSON number {value}')

    with open(path, encoding='utf-8') as stream:
        return json.load(stream, object_pairs_hook=pairs, parse_constant=constant)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sidecar')
    args = parser.parse_args(argv)
    try:
        validate(load(args.sidecar))
    except (ValidationError, ValueError, OSError) as error:
        print(f'INVALID: {error}', file=sys.stderr)
        return 1
    print('VALID: structural source mapping only; media/audio quality not measured')
    return 0


if __name__ == '__main__':
    sys.exit(main())
