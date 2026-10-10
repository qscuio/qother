"""Single title/caption/identity compositor; clean scene modules never bake these."""
import json,sys,importlib.util
from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;OLD=R.parent/'full_chapter_v1';W,H,FPS=1280,720,24
TITLE='地球往事｜序章：地球的来处';FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
TIMELINE=json.loads((R/'timeline.json').read_text());ROWS={p['id']:p for p in TIMELINE['paragraphs']};CLIPS=sorted(TIMELINE['paragraphs']+TIMELINE.get('inserts',[]),key=lambda x:x['start']);ALL_ROWS={p['id']:p for p in CLIPS}
HOST=Image.open(OLD/'assets/host-circle.png').convert('RGBA').resize((132,132),Image.Resampling.LANCZOS)
@lru_cache(None)
def font(n):return ImageFont.truetype(FONT,n)
@lru_cache(None)
def module(pid):
 n=9 if pid=='INSERT-MW' else int(pid[1:]);folder='early' if n<5 else 'stellar' if n<10 else 'p10' if n==10 else 'planet'
 path=R/'scenes'/folder/'renderer.py';spec=importlib.util.spec_from_file_location('scene_'+folder,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def overlay(im,pid,t):
 im=im.convert('RGB');d=ImageDraw.Draw(im);row=ALL_ROWS[pid]
 d.text((45,27),TITLE,font=font(19),fill='#b7b7b0',stroke_width=1,stroke_fill='#06090f')
 d.text((45,62),row['title'],font=font(27),fill='#e9e5d7',stroke_width=1,stroke_fill='#06090f')
 im.paste(HOST,(1114,548),HOST)
 text=next((c['text'] for c in row['cues'] if c['start']<=t<c['end']),'')
 if text:
  lines=[];line=''
  for c in text:
   if d.textlength(line+c,font=font(30))>1010:lines.append(line);line=''
   line+=c
  if line:lines.append(line)
  assert len(lines)<=2
  y=624 if len(lines)==2 else 646
  for line in lines:d.text((45,y),line,font=font(30),fill='#f4f2e9',stroke_width=3,stroke_fill='#080d12');y+=39
 d.text((45,694),'科学示意 · 时间压缩 · 非比例',font=font(14),fill='#8e9498',stroke_width=1,stroke_fill='#080d12')
 return im

def frame(pid,t):
 if pid=='INSERT-MW':return overlay(module(pid).render_insert(min(t/8,1),W,H),pid,t)
 return overlay(module(pid).render(pid,min(t/ROWS[pid]['narration_duration'],1),W,H),pid,t)
def keyframes(ids):
 out=R/'qa/composed';out.mkdir(exist_ok=True,parents=True)
 for pid in ids:
  for p in [.03,.25,.5,.75,.97]:
   frame(pid,p*(ALL_ROWS[pid]['narration_duration'] or ALL_ROWS[pid]['duration'])).save(out/f'{pid}-{int(p*100):02d}.png')
if __name__=='__main__':keyframes(sys.argv[1:])
