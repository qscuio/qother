"""Compile measured SRT plus explicitly authored vector beats; no inference or TTS."""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

TIME = re.compile(r'^(\d{2,}):([0-5]\d):([0-5]\d)[,.](\d{3})$')

def timestamp(value):
    match = TIME.fullmatch(value.strip())
    if not match:
        raise ValueError('Invalid SRT timestamp: ' + value)
    h, m, s, ms = map(int, match.groups())
    return ((h * 60 + m) * 60 + s) * 1000 + ms

def parse_srt(text):
    blocks = re.split(r'\n\s*\n', text.lstrip('\ufeff').replace('\r\n', '\n').strip())
    cues, ids = [], set()
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3 or not lines[0].strip().isdigit():
            raise ValueError('Each cue requires an integer ID, timing and text')
        cue_id = int(lines[0])
        times = lines[1].split('-->')
        if len(times) != 2 or cue_id in ids:
            raise ValueError('Invalid timing or duplicate cue ID')
        start, end = map(timestamp, times)
        if start >= end or (cues and start < cues[-1]['end_ms']):
            raise ValueError('Cues must be ordered, nonoverlapping, positive duration')
        body = '\n'.join(lines[2:]).strip()
        if not body:
            raise ValueError('Empty cue')
        cues.append(dict(id=cue_id, start_ms=start, end_ms=end, text=body))
        ids.add(cue_id)
    return cues

def compile_storyboard(srt, plan):
    cues = parse_srt(srt)
    duration = plan.get('duration_ms')
    if type(duration) is not int or duration <= 0 or cues[-1]['end_ms'] > duration:
        raise ValueError('duration_ms must cover measured audio and every cue')
    method = plan.get('caption_timing')
    if method not in ('manual_measured', 'provider_timestamps', 'forced_alignment', 'preview_only'):
        raise ValueError('Declare caption_timing provenance; SRT alone is not alignment evidence')
    if plan.get('theme', 'warm-paper-stream') != 'warm-paper-stream':
        raise ValueError('This adapter supports warm-paper-stream')
    by_id = {c['id']: c for c in cues}
    covered, blocks, ledger, last = set(), [], [], 0
    ids = set()
    for beat in plan.get('beats', []):
        bid = beat.get('id')
        if not isinstance(bid, str) or not bid or bid in ids or not beat.get('narrative_role'):
            raise ValueError('Each beat needs unique ID and narrative_role')
        ids.add(bid)
        refs = beat.get('cue_ids', [])
        if not refs or any(type(i) is not int or i not in by_id for i in refs) or len(set(refs)) != len(refs):
            raise ValueError('Each beat requires valid distinct cue_ids')
        start, end = beat.get('start_ms'), beat.get('end_ms')
        if type(start) is not int or type(end) is not int or not last <= start < end <= duration - 1000:
            raise ValueError('Drawing windows must be serial with 1 second for exit/hold')
        if not all(start < by_id[i]['end_ms'] and end > by_id[i]['start_ms'] for i in refs):
            raise ValueError('Every referenced cue must intersect its drawing beat')
        parts = beat.get('parts')
        if not isinstance(parts, list) or not parts:
            raise ValueError('Author semantic vector parts; rectangles cannot become strokes')
        blocks.append(dict(start=start/1000, end=end/1000, ordering='per_part', parts=copy.deepcopy(parts)))
        ledger.append(dict(id=bid, cue_ids=refs, narrative_role=beat['narrative_role']))
        last=end; covered.update(refs)
    if covered != set(by_id):
        raise ValueError('Every caption requires an authored visual beat')
    return dict(version=1, preview_duration=duration/1000,
                background=[245,235,215], caption_timing=method,
                captions=[dict(start=c['start_ms']/1000,end=c['end_ms']/1000,text=c['text']) for c in cues],
                blocks=blocks, exit=dict(start=last/1000,end=last/1000+0.5),
                style=dict(id='warm-paper-stream-v1',palette=[[42,48,52],[190,220,235],[224,194,150],[190,80,65]],
                           outline_width_range=[2,6],caption_lane_top=590),
                provenance=dict(srt_sha256=hashlib.sha256(srt.encode()).hexdigest(),beats=ledger,
                                timing_review='required',visual_review='not_performed'))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('srt',type=Path); parser.add_argument('plan',type=Path); parser.add_argument('output',type=Path)
    args=parser.parse_args()
    result=compile_storyboard(args.srt.read_text(encoding='utf-8-sig'),json.loads(args.plan.read_text()))
    # Reuse the production renderer's structural expansion, without rendering or network access.
    from scene_contract import block_items, inspect_style
    for block in result['blocks']: block_items(block)
    review=inspect_style(result)
    if review['issues']: raise ValueError('; '.join(review['issues']))
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__': main()
