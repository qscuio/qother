"""Extract actual encoded adjacent cut endpoints, never generates a verdict."""
from pathlib import Path
import subprocess,json,hashlib
from PIL import Image,ImageDraw
from compositor import R,OLD,CLIPS
out=R/'qa/boundaries';out.mkdir(parents=True,exist_ok=True)
rows=[{'id':'COVER','frames':48,'duration':2}]+CLIPS
pairs=[]
for left,right in zip(rows,rows[1:]):
 a=R/'output/segments'/f'{left["id"]}.mp4';b=R/'output/segments'/f'{right["id"]}.mp4'
 if not b.exists() or (left['id']!='COVER' and not a.exists()):continue
 prefix=f'{left["id"]}-to-{right["id"]}' if left['id']!='COVER' or not a.exists() else f'COVER-encoded-to-{right["id"]}'
 targets=[]
 for side,row,video,fr in [('left',left,a,left['frames']-1),('right',right,b,0)]:
  path=out/f'{prefix}-{side}.png'
  if row['id']=='COVER' and not video.exists():Image.open(OLD/'cover-system/prologue-cover-candidate-v2.png').convert('RGB').save(path)
  else:subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',f'select=eq(n\\,{fr})','-frames:v','1',str(path)],check=True)
  targets.append(path)
 sheet=Image.new('RGB',(1280,390),'#080d12');d=ImageDraw.Draw(sheet)
 for x,path in enumerate(targets):sheet.paste(Image.open(path).resize((640,360)),(x*640,25))
 d.text((10,5),left['id']+' last frame',fill='white');d.text((650,5),right['id']+' first frame',fill='white');pair=out/f'{prefix}.jpg';sheet.save(pair,quality=94)
 pairs.append({'from':left['id'],'to':right['id'],'pair_file':str(pair.relative_to(R)),'sha256':hashlib.sha256(pair.read_bytes()).hexdigest(),'endpoints':[{'file':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in targets],'scope':'Actual encoded endpoints; only any unavailable cover clip would use exact source PNG','review':'not-run'})
(out/'manifest.json').write_text(json.dumps(pairs,indent=2));print('Extracted',len(pairs),'actual available boundaries; no verdict.')
