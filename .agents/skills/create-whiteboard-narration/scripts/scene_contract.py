"""Semantic storyboard expansion and structural style checks, without external services."""
from __future__ import annotations
import copy
import math


def ordered_parts(parts):
    """Stable topological ordering; retain the author's order among ready parts."""
    if not isinstance(parts, list) or not parts:
        raise ValueError('parts must be a nonempty list')
    names = [p.get('id') for p in parts]
    if any(not isinstance(n, str) or not n.strip() for n in names) or len(set(names)) != len(names):
        raise ValueError('Each semantic part needs a unique nonempty id')
    for p in parts:
        deps = p.get('after', [])
        if not isinstance(deps, list) or any(d not in names or d == p['id'] for d in deps):
            raise ValueError(f"Invalid after dependencies for part {p['id']}")
    result, done, remaining = [], set(), list(parts)
    while remaining:
        ready = next((p for p in remaining if set(p.get('after', [])) <= done), None)
        if ready is None:
            raise ValueError('Semantic part dependencies contain a cycle')
        result.append(ready); done.add(ready['id']); remaining.remove(ready)
    return result


def block_items(block):
    """Legacy items are untouched; semantic parts share one contour/paint order."""
    if 'parts' not in block:
        if not block.get('items'):
            raise ValueError('Drawing block needs nonempty items or parts')
        return copy.deepcopy(block['items'])
    if 'items' in block:
        raise ValueError('Use items or parts in a block, not both')
    mode = block.get('ordering', 'outlines_then_fills')
    if mode not in ('outlines_then_fills', 'per_part'):
        raise ValueError('ordering must be outlines_then_fills or per_part')
    parts = ordered_parts(block['parts'])
    groups = []
    for part in parts:
        outlines, fills = part.get('outline', []), part.get('fills', [])
        if not outlines or any(i.get('type') not in ('path', 'text') for i in outlines):
            raise ValueError(f"Part {part['id']} needs path/text outline items")
        if not isinstance(fills, list) or any(i.get('type') != 'fill' for i in fills):
            raise ValueError(f"Part {part['id']} fills must contain only fill items")
        pair = []
        for phase, items in (('outline', outlines), ('fill', fills)):
            commands = []
            for item in items:
                command = copy.deepcopy(item)
                command['_part_id'] = part['id']; command['_phase'] = phase
                commands.append(command)
            pair.append(commands)
        groups.append(pair)
    if mode == 'per_part':
        return [i for pair in groups for phase in pair for i in phase]
    return [i for phase in (0, 1) for pair in groups for i in pair[phase]]


def inspect_style(spec):
    """Validate numeric style contract. Appearance and meaning still need visual review."""
    style = spec.get('style')
    if style is None:
        return {'status': 'not_declared', 'issues': [], 'visual_review': 'not_performed'}
    if not isinstance(style.get('id'), str) or not style['id'].strip():
        raise ValueError('style.id must identify the shared visual baseline')
    widths = style.get('outline_width_range', [2, 6])
    if len(widths) != 2 or not all(isinstance(x, (int, float)) and math.isfinite(x) and x > 0 for x in widths) or widths[0] > widths[1]:
        raise ValueError('style.outline_width_range must be two ordered positive numbers')
    palette = style.get('palette', [])
    if not palette or any(not isinstance(c, list) or len(c) not in (3, 4) or any(type(v) is not int or not 0 <= v <= 255 for v in c) for c in palette):
        raise ValueError('style.palette must contain RGB/RGBA integer arrays')
    palette = {tuple(c[:3]) for c in palette}
    lane = float(style.get('caption_lane_top', 590))
    if not math.isfinite(lane) or not 0 < lane <= 720:
        raise ValueError('style.caption_lane_top must lie in (0,720]')
    issues = []
    for bi, block in enumerate(spec.get('blocks', [])):
        for ii, item in enumerate(block_items(block)):
            label = f'block {bi}, item {ii}'
            c = item.get('color', [42, 48, 52, 255])
            if tuple(c[:3]) not in palette:
                issues.append(f'{label}: color is outside shared palette')
            if item['type'] != 'fill' and not widths[0] <= float(item.get('width', 3.5 if item['type'] == 'text' else 4)) <= widths[1]:
                issues.append(f'{label}: outline width is outside shared range')
            if item['type'] == 'text':
                x, y = item['at']; size = item.get('size', 40)
                if y < 0 or y + size > lane or x < 0:
                    issues.append(f'{label}: label may cross canvas/caption lane')
            else:
                p = item.get('points', item.get('polygon', []))
                if any(x < 0 or x > 1280 or y < 0 or y > lane for x, y in p):
                    issues.append(f'{label}: artwork crosses canvas/caption lane')
    return {'status': 'pass' if not issues else 'fail', 'baseline': style['id'], 'issues': issues,
            'visual_review': 'not_performed', 'scope': 'palette, declared stroke widths, basic layout bounds only'}
