#!/usr/bin/env python3
"""Validate the project shot contract; no rendering, network, or asset reads."""
import argparse
import json
import math
from pathlib import Path, PurePosixPath
import re

class Invalid(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise Invalid(message)

def number(value):
    return type(value) in (int, float) and math.isfinite(value)

def nonempty(value):
    return isinstance(value, str) and bool(value.strip())

def keyed(rows, label):
    require(isinstance(rows, list) and bool(rows), f'{label}: nonempty list required')
    out = {}
    for row in rows:
        require(isinstance(row, dict) and nonempty(row.get('id')), f'{label}: id required')
        require(row['id'] not in out, f'{label}: duplicate id {row["id"]}')
        out[row['id']] = row
    return out

def box(value, label):
    require(isinstance(value, list) and len(value) == 4 and all(number(v) for v in value), f'{label}: invalid bbox')
    x, y, w, h = value
    require(x >= 0 and y >= 0 and w > 0 and h > 0 and x+w <= 1+1e-8 and y+h <= 1+1e-8, f'{label}: bbox outside frame')
    return x, y, w, h

def validate(d, production=False):
    require(isinstance(d, dict), 'root must be an object')
    require(d.get('schema_version') == 1, 'unsupported schema_version')
    require(d.get('mode') in ('demo', 'production'), 'invalid mode')
    require(not production or d['mode'] == 'production', 'production required; demo rejected')
    strict = d['mode'] == 'production'
    manifest = json.loads((Path(__file__).resolve().parent.parent/'docs/style-manifest.json').read_text())
    require(d.get('style_id') in {s['id'] for s in manifest['styles']}, 'unknown style_id')
    for name in ('width', 'height', 'fps', 'expected_shot_count'):
        require(type(d.get(name)) is int and d[name] > 0, f'{name}: positive integer required')
    require(d['width']*9 == d['height']*16, 'frame must be 16:9')
    require(number(d.get('duration_s')) and d['duration_s'] > 0, 'duration_s invalid')
    sources = keyed(d.get('sources'), 'sources')
    for src in sources.values():
        require(src.get('kind') in ('illustrative','factual') and nonempty(src.get('supports')), 'source kind/supports required')
        require(nonempty(src.get('url')), 'source url required')
        if strict:
            require(src['kind'] == 'factual' and src['url'].startswith('https://'), 'production requires factual HTTPS sources')
    assets = keyed(d.get('assets'), 'assets')
    for a in assets.values():
        require(nonempty(a.get('version')) and nonempty(a.get('rights')), 'asset version/rights required')
        require(isinstance(a.get('sha256'), str) and re.fullmatch('[0-9a-f]{64}', a['sha256']), 'asset sha256 invalid')
        path = a.get('path')
        require(nonempty(path) and not PurePosixPath(path).is_absolute() and '..' not in PurePosixPath(path).parts and '\\' not in path and ':' not in path, 'asset path must be portable relative path')
        if strict:
            require(a['sha256'] != '0'*64, 'demo asset hash rejected')
    guide = d.get('guide', {})
    require(guide.get('asset_id') in assets, 'guide asset missing')
    ga = assets[guide['asset_id']]
    require(guide.get('version') == ga['version'] and ga.get('intact') is True, 'guide must use locked intact asset')
    gh = guide.get('height_fraction')
    require(number(gh) and 0.18 <= gh <= 0.22, 'guide height must be approximately 20%, not width')
    gx,gy,gw,gbh = box(guide.get('bbox'), 'guide')
    require(abs(gbh-gh) < 1e-8, 'guide bbox height mismatch')
    cx,cy,cw,ch = box(d.get('captions',{}).get('bbox'), 'captions')
    require(gx+gw <= cx or cx+cw <= gx or gy+gbh <= cy or cy+ch <= gy, 'guide overlaps captions')
    voice = d.get('voice', {})
    require(voice.get('status') in ('deferred','temporary','approved') and nonempty(voice.get('note')), 'voice state required')
    shots=d.get('shots')
    require(isinstance(shots,list) and len(shots)==d['expected_shot_count'], 'shot count mismatch')
    end = 0.0
    ids=set()
    prior=None
    for s in shots:
        require(isinstance(s,dict), 'shot must be an object')
        for field in ('shot_id','narration','visual','action','camera','audio'):
            require(nonempty(s.get(field)), f'shot {field} required')
        require(s['shot_id'] not in ids, 'duplicate shot_id')
        ids.add(s['shot_id'])
        start, stop=s.get('start_s'),s.get('end_s')
        require(number(start) and number(stop) and start >= 0 and stop > start, 'shot time invalid')
        require(abs(start-end)<1e-8, 'shot overlap or gap')
        require(all(abs(t*d['fps']-round(t*d['fps'])) < 1e-6 for t in (start,stop)), 'time not aligned to frame')
        end=stop
        refs=s.get('source_ids')
        require(isinstance(refs,list) and bool(refs) and all(isinstance(r,str) and r in sources for r in refs), 'unknown or missing source_ids')
        uses=s.get('assets')
        require(isinstance(uses,list) and bool(uses), 'shot assets required')
        for ref in uses:
            require(isinstance(ref,dict) and ref.get('asset_id') in assets, 'unknown asset')
            require(ref.get('version') == assets[ref['asset_id']]['version'], 'asset version mismatch')
        require(any(ref['asset_id']==guide['asset_id'] for ref in uses), 'shot guide asset missing')
        continuity=s.get('continuity',{})
        require(nonempty(continuity.get('in')) and nonempty(continuity.get('out')), 'continuity states required')
        require(prior is None or continuity['in']==prior, 'continuity mismatch')
        prior=continuity['out']
        require(isinstance(s.get('qa'),list) and bool(s['qa']) and all(nonempty(q) for q in s['qa']), 'shot QA required')
    require(abs(end-d['duration_s'])<1e-8, 'shots do not cover duration_s')
    return {'shots':len(shots),'assets':len(assets),'sources':len(sources),'duration_s':end,'mode':d['mode']}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('storyboard',type=Path)
    parser.add_argument('--production',action='store_true')
    args=parser.parse_args()
    try:
        result=validate(json.loads(args.storyboard.read_text()),args.production)
    except (Invalid,ValueError,TypeError,KeyError,OSError) as exc:
        parser.exit(1,f'INVALID: {exc}\n')
    print('VALID '+json.dumps(result,ensure_ascii=False))

if __name__=='__main__':
    main()
