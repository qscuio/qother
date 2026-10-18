#!/usr/bin/env python3
"""Validate a review record, not the truth or perceptual quality of a video.

No network, imports of renderers, media generation or changes to inputs.
Usage: python scripts/validate_video_review.py docs/video-production/review.example.json
"""
import argparse
import json
from pathlib import Path


def validate(record):
    errors = []
    if not isinstance(record, dict):
        return ['record must be an object']
    if type(record.get('version')) is not int or record['version'] != 1:
        errors.append('version must be integer 1')
    decision = record.get('decision')
    if decision not in ('ready', 'conditional', 'blocked'):
        errors.append('decision must be ready, conditional or blocked')
    for key in ('artifact', 'author', 'reviewer'):
        if not isinstance(record.get(key), str) or not record[key].strip():
            errors.append(f'{key} must be a nonempty string')
    if record.get('review_kind') not in ('cold', 'delta'):
        errors.append('review_kind must be cold or delta')
    if record.get('review_kind') == 'cold' and record.get('author') == record.get('reviewer'):
        errors.append('cold reviewer must differ from author')
    checks = record.get('checks')
    if not isinstance(checks, list) or not checks:
        errors.append('checks must be a nonempty list')
        checks = []
    seen = set()
    has_required = False
    unresolved_required = False
    failed_required = False
    for index, check in enumerate(checks):
        prefix = f'checks[{index}]'
        if not isinstance(check, dict):
            errors.append(f'{prefix} must be an object')
            continue
        ident = check.get('id')
        if not isinstance(ident, str) or not ident.strip() or ident in seen:
            errors.append(f'{prefix}.id must be nonempty and unique')
        else:
            seen.add(ident)
        if type(check.get('required')) is not bool:
            errors.append(f'{prefix}.required must be boolean')
        required = check.get('required') is True
        has_required |= required
        status = check.get('status')
        if status not in ('pass', 'fail', 'not_run'):
            errors.append(f'{prefix}.status invalid')
        evidence = check.get('evidence')
        if not isinstance(evidence, list) or any(not isinstance(e, str) or not e.strip() for e in evidence):
            errors.append(f'{prefix}.evidence must be a list of nonempty strings')
        if status in ('pass', 'fail') and not evidence:
            errors.append(f'{prefix} needs observed evidence for pass/fail')
        if status == 'not_run' and (not isinstance(check.get('limitation'), str) or not check['limitation'].strip()):
            errors.append(f'{prefix} needs a limitation for not_run')
        unresolved_required |= required and status != 'pass'
        failed_required |= required and status == 'fail'
    if not has_required:
        errors.append('at least one check must be required')
    issues = record.get('issues')
    if not isinstance(issues, list):
        errors.append('issues must be a list')
        issues = []
    seen = set()
    blockers = False
    for index, issue in enumerate(issues):
        prefix = f'issues[{index}]'
        if not isinstance(issue, dict):
            errors.append(f'{prefix} must be an object')
            continue
        ident = issue.get('id')
        if not isinstance(ident, str) or not ident.strip() or ident in seen:
            errors.append(f'{prefix}.id must be nonempty and unique')
        else:
            seen.add(ident)
        if issue.get('severity') not in ('S0', 'S1', 'S2', 'S3'):
            errors.append(f'{prefix}.severity invalid')
        status = issue.get('status')
        if status not in ('open', 'fixed', 'deferred'):
            errors.append(f'{prefix}.status invalid')
        for key in ('location', 'finding', 'evidence'):
            if not isinstance(issue.get(key), str) or not issue[key].strip():
                errors.append(f'{prefix}.{key} must be nonempty')
        if status == 'fixed' and (not isinstance(issue.get('recheck'), str) or not issue['recheck'].strip()):
            errors.append(f'{prefix} fixed issue needs recheck evidence')
        if status == 'deferred' and (not isinstance(issue.get('disposition'), str) or not issue['disposition'].strip()):
            errors.append(f'{prefix} deferred issue needs disposition')
        blockers |= issue.get('severity') in ('S0', 'S1') and status != 'fixed'
        if decision == 'ready' and status == 'open':
            errors.append(f'{prefix} open issue needs explicit disposition before ready')
    if decision == 'ready' and (blockers or unresolved_required):
        errors.append('ready requires all required checks pass and no unresolved S0/S1')
    if failed_required and decision != 'blocked':
        errors.append('failed required check requires blocked; conditional is for incomplete evidence')
    if blockers and decision != 'blocked':
        errors.append('unresolved S0/S1 requires blocked')
    if decision != 'ready' and (not isinstance(record.get('limitations'), str) or not record['limitations'].strip()):
        errors.append('conditional/blocked needs limitations and next step')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record', type=Path)
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding='utf-8'))
        errors = validate(record)
    except (OSError, ValueError) as exc:
        print(json.dumps({'record_valid': False, 'errors': [str(exc)]}, ensure_ascii=False))
        return 1
    print(json.dumps({'record_valid': not errors, 'decision': record.get('decision') if isinstance(record, dict) else None,
                      'errors': errors, 'scope': 'Record consistency only; no video viewing, listening, factual or permission verification.'}, ensure_ascii=False, indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
