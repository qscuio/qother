"""Reusable 1280×720 editorial cover. Requires explicit local art and rights statement.
Example: python render_cover.py --hero prologue-disk-hero.png --rights 'Original procedural artwork' --title '地球的|来处' --chapter-label 序章 --output prologue-cover-candidate-v2.png
No presenter asset is read or embedded. Hero must already be composed at 16:9.
"""
from pathlib import Path
import argparse,json
from PIL import Image,ImageDraw,ImageFont
import numpy as np
W,H=1280,720
SERIF='/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'
SANS='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'

def font(path,size):return ImageFont.truetype(path,size,index=2)
def render(hero,title,chapter_label,output,rights):
    if not rights.strip():raise ValueError('A source / rights statement is required.')
    if not hero.is_file():raise ValueError('Hero must be an existing local file.')
    im=Image.open(hero).convert('RGB')
    if abs(im.width/im.height-16/9)>.01:raise ValueError('Compose the hero at 16:9; automatic crops are intentionally disabled.')
    im=im.resize((W,H),Image.Resampling.LANCZOS)
    # Consistent near-black left text field, while preserving right-side artwork.
    x=np.arange(W);opacity=np.clip((800-x)/340,0,1)*.91
    a=np.asarray(im).astype(float);base=np.array([10,10,12])
    a=a*(1-opacity[None,:,None])+base*opacity[None,:,None]
    im=Image.fromarray(a.astype('uint8'));d=ImageDraw.Draw(im)
    cream='#EEE8DB';muted='#B6AA99';accent='#C38F58'
    d.rectangle((72,61,76,92),fill=accent)
    d.text((94,54),'地球往事',font=font(SANS,30),fill=cream)
    lines=title.split('|')
    if not 1<=len(lines)<=2 or any(len(s)>5 for s in lines):raise ValueError('Use one or two lines, at most five Chinese characters per line.')
    size=104 if max(map(len,lines))<=4 else 88
    for i,line in enumerate(lines):
        if d.textbbox((0,0),line,font=font(SERIF,size))[2]>530:raise ValueError('Title exceeds the text safe area.')
        d.text((68,215+i*132),line,font=font(SERIF,size),fill=cream,stroke_width=0)
    d.line((74,574,122,574),fill=accent,width=3)
    d.text((74,602),chapter_label,font=font(SANS,28),fill=muted)
    output.parent.mkdir(parents=True,exist_ok=True);im.save(output)
    im.resize((320,180),Image.Resampling.LANCZOS).save(output.with_name(output.stem+'-320.png'))
    output.with_suffix('.json').write_text(json.dumps({'series':'地球往事','title':title.replace('|',''),'title_lines':lines,'chapter_label':chapter_label,'hero':hero.name,'hero_rights':rights,'size':[W,H],'private_presenter_embedded':False},ensure_ascii=False,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--hero',type=Path,required=True);p.add_argument('--rights',required=True);p.add_argument('--title',required=True);p.add_argument('--chapter-label',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();render(a.hero,a.title,a.chapter_label,a.output,a.rights)
