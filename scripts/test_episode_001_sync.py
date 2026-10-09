#!/usr/bin/env python3
"""Check episode narration/source/timeline consistency and local Markdown links."""
import json,re,sys,copy
from pathlib import Path
from validate_storyboard import validate,Invalid
ROOT=Path(__file__).resolve().parent.parent
E=ROOT/'docs/episodes/001'
s=json.loads((E/'scene-spine.json').read_text()); source={x['id']:x for x in json.loads((E/'sources.json').read_text())}
assert s['duration_seconds']==420 and len(s['shots'])==24
assert len({x['id'] for x in s['shots']})==24
script=(E/'script.md').read_text(); assert script.count('\n## ')==7
for x in s['shots']: assert script.count(x['narration'])==1 and all(y in source for y in x['source_ids'])
assert [x['id'] for x in s['shots']]==[i for section in s['reading_sections'] for i in section['shot_ids']]
for p in E.glob('storyboard-*.json'):
 d=json.loads(p.read_text());print(p.name,validate(d))
 for a,b in zip(s['shots'],d['shots']):
  assert (a['id'],a['start'],a['end'],a['narration'],a['source_ids'])==(b['shot_id'],b['start_s'],b['end_s'],b['narration'],b['source_ids'])
  assert p.with_suffix('.md').read_text().count(a['narration'])==1
 for x in d['sources']:
  assert x['source_type']==source[x['id']]['kind'] and x['kind']=='factual'
  assert all(x[k]==source[x['id']][k] for k in ('id','url','supports'))
 for test in (d,dict(d,mode='production')):
  try:validate(test,production=True)
  except Invalid as e:print('EXPECTED REJECTION',e)
  else:raise AssertionError('Production gate unexpectedly passed')
links=0
for p in ROOT.rglob('*.md'):
 for url in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if '://' in url or url.startswith('#'):continue
  assert (p.parent/url.split('#')[0]).exists(),(p,url)
  links+=1
print('PASS narration, IDs, sources, timelines, production blocks and',links,'relative Markdown links')
