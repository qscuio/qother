"""Verify frozen paragraph coverage and internal timeline, not spoken-word accuracy."""
import math,re

def validate_manifest(manifest,paragraphs):
 rows=manifest['paragraphs'];expected=[f'P{i:02d}' for i in range(1,20)]
 if [r['id'] for r in rows]!=expected or [p['id'] for p in paragraphs]!=expected:raise ValueError('Must contain exactly ordered P01–P19')
 cursor=0;characters=0
 for row,p in zip(rows,paragraphs):
  if row['text'].strip()!=p['text'].strip() or ''.join(c['text'] for c in row['cues'])!=p['text'].strip():raise ValueError('Frozen text/cue coverage mismatch: '+p['id'])
  characters+=len(re.sub(r'[^\w\u4e00-\u9fff]','',p['text']))
  if not math.isclose(row['start'],cursor,abs_tol=1e-7):raise ValueError('Noncontiguous paragraph timeline')
  if not math.isclose(row['duration'],row['frames']/24,abs_tol=1e-7):raise ValueError('Non-frame-aligned duration')
  if not math.isclose(row['end']-row['start'],row['duration'],abs_tol=1e-7):raise ValueError('Duration mismatch')
  previous=-1
  for cue in row['cues']:
   if not 0<=cue['start']<cue['end']<=row['duration']+1e-6 or cue['start']<previous:raise ValueError('Invalid cue order/timing')
   previous=cue['end']-1e-7
  cursor=row['end']
 if characters!=1434 or manifest['frozen_character_count']!=1434:raise ValueError('Expected 1434 normalized frozen characters')
 if not math.isclose(manifest['total_duration'],cursor+8,abs_tol=1e-7):raise ValueError('Expected 8-second reference endcard')
 return {'paragraphs':19,'normalized_characters':1434,'main_frames':sum(r['frames'] for r in rows),'total_frames':sum(r['frames'] for r in rows)+192,'coverage':'exact frozen subtitle text; not independent ASR'}
