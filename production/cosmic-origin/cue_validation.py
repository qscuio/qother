"""Text and timing integrity checks shared by builder and final assembler."""
import math,re
END_TOLERANCE_S=.05  # ASR rounding tolerance, explicitly bounded to 50 ms.
OVERLAP_TOLERANCE_S=.001  # Only one millisecond rounding noise, not real overlap.
def normalized_text(text):return ''.join(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',text))
def validate_cues(cues,duration,expected_text=None):
 assert type(duration) in (int,float) and math.isfinite(duration) and duration>0,'Invalid audio duration'
 assert isinstance(cues,list) and cues,'Missing subtitle/sentence cues'
 last_end=0
 for c in cues:
  assert isinstance(c,dict) and isinstance(c.get('text'),str) and normalized_text(c['text']),'Empty cue text'
  a,b=c.get('start'),c.get('end')
  assert type(a) in (int,float) and type(b) in (int,float) and math.isfinite(a) and math.isfinite(b),'Non-finite cue time'
  assert 0<=a<b<=duration+END_TOLERANCE_S,'Cue outside audio range or nonpositive duration'
  assert a>=last_end-OVERLAP_TOLERANCE_S,'Overlapping or out-of-order cues'
  last_end=b
 if expected_text is not None:
  assert normalized_text(''.join(c['text'] for c in cues))==normalized_text(expected_text),'Cue text does not cover the frozen selected text exactly'
 return True
