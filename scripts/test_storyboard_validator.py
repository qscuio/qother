#!/usr/bin/env python3
"""Behavioral rejection tests; do not edit the repository fixture."""
from copy import deepcopy
import json
from pathlib import Path
from validate_storyboard import Invalid, validate
base=json.loads((Path(__file__).resolve().parent.parent/'examples/storyboard-demo.json').read_text())
assert validate(base)['shots']==2
cases={
 'overlap':lambda d:d['shots'][1].update(start_s=3),
 'gap':lambda d:d['shots'][1].update(start_s=5),
 'unknown source':lambda d:d['shots'][0].update(source_ids=['missing']),
 'unlocked version':lambda d:d['shots'][0]['assets'][0].update(version='changed'),
 'large guide':lambda d:d['guide'].update(height_fraction=0.4),
 'caption collision':lambda d:d['captions'].update(bbox=[0,0.6,1,0.3]),
 'broken body':lambda d:d['assets'][0].update(intact=False),
 'continuity':lambda d:d['shots'][1]['continuity'].update(**{'in':'different'}),
 'shot count':lambda d:d.update(expected_shot_count=3),
 'duration':lambda d:d.update(duration_s=9),
 'nonfinite time':lambda d:d['shots'][0].update(end_s=float('nan')),
 'frame alignment':lambda d:d['shots'][0].update(end_s=4.001),
 'duplicate shot':lambda d:d['shots'][1].update(shot_id='S001'),
 'absolute path':lambda d:d['assets'][0].update(path='/private/file.png'),
 'demo production leakage':lambda d:d.update(mode='production'),
}
for name,mutate in cases.items():
 d=deepcopy(base);mutate(d)
 try:validate(d)
 except Invalid:pass
 else:raise AssertionError(f'Invalid case accepted: {name}')
try:validate(base,production=True)
except Invalid:pass
else:raise AssertionError('production flag accepted demo')
print(f'PASS: valid fixture + {len(cases)+1} rejection cases')


# Synthetic structure-only current-layout fixture; never a production asset claim.
current=deepcopy(base)
current['guide'].update(height_fraction=250/1080,
                        bbox=[1622/1920,790/1080,250/1920,250/1080])
current['captions']['bbox']=[0.13,0.85,0.65,0.1]
assert validate(current)['mode']=='demo'
production_current=deepcopy(current)
production_current['mode']='production'
for asset in production_current['assets']:
 asset['sha256']='1'*64
for source in production_current['sources']:
 source.update(kind='factual',url='https://example.org/structure-test-only')
assert validate(production_current,production=True)['mode']=='production'

def change_box(d,index,value):
 d['guide']['bbox'][index]=value
 if index==3:d['guide']['height_fraction']=value

profile_cases={
 'wrong position':lambda d:change_box(d,0,1600/1920),
 'wrong y':lambda d:change_box(d,1,780/1080),
 'wrong diameter width':lambda d:change_box(d,2,240/1920),
 'wrong diameter height':lambda d:change_box(d,3,240/1080),
 'height mismatch':lambda d:d['guide'].update(height_fraction=0.2),
 'out of frame':lambda d:change_box(d,0,0.99),
 'nonfinite box':lambda d:change_box(d,0,float('nan')),
 'nonfinite height':lambda d:d['guide'].update(height_fraction=float('inf')),
 'caption collision':lambda d:d['captions'].update(bbox=[0.13,0.85,0.74,0.1]),
 'unreviewed resolution':lambda d:d.update(width=1280,height=720),
 'legacy production profile':lambda d:d['guide'].update(deepcopy(base['guide'])),
}
for name,mutate in profile_cases.items():
 d=deepcopy(production_current);mutate(d)
 try:validate(d,production=True)
 except Invalid:pass
 else:raise AssertionError(f'Invalid current profile accepted: {name}')
# A near-current demo with an unreviewed size cannot use the exact-profile exception.
d=deepcopy(current);change_box(d,2,240/1920)
try:validate(d)
except Invalid:pass
else:raise AssertionError('nonexact current demo accepted')
print(f'PASS: current demo + synthetic production profile + {len(profile_cases)+1} profile rejection cases')
