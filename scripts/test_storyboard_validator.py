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
