"""Planet formation: authored CPU 2.5D scientific reconstruction, not simulation.
All texture/shape shading generated here; no sourced specimen or invented measurements.
Interface render returns clean PIL RGB, excluding host, subtitles and branding.
"""
from pathlib import Path
from functools import lru_cache
import math,json
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
W,H=1280,720
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
@lru_cache(None)
def font(s):return ImageFont.truetype(FONT,s)
def ease(t):t=np.clip(t,0,1);return t*t*(3-2*t)
def phase(t,a,b):return float(ease((t-a)/(b-a)))
def text(im,xy,s,size=24,color=(219,216,206)):
 ImageDraw.Draw(im).text(xy,s,font=font(size),fill=color)
def note(im,s):text(im,(48,576),s,18,(151,157,159))
@lru_cache(None)
def timing(p):
 tl=json.loads((ROOT/'full_chapter_v1/audio/timeline.json').read_text());row=next(x for x in tl['paragraphs'] if x['id']==p)
 return row
@lru_cache(None)
def cue(p,phrase):
 b=json.loads((ROOT/f'full_chapter_v1/audio/{p}.edge.json').read_text())['boundaries'];st='';pos=[]
 for v in b:
  st+=v['text'];pos.extend([v['offset']/1e7]*len(v['text']))
 i=st.find(phrase)
 return pos[i]/timing(p)['duration'] if i>=0 else 0
@lru_cache(None)
def background(lab=False):
 y,x=np.mgrid[0:H,0:W];g=np.exp(-((x-520)/750)**2-((y-360)/430)**2)
 a=np.stack([5+g*7,8+g*10,12+g*15],2)
 if lab:a+=np.exp(-((y-500)/130)**2)[:,:,None]*np.array([9,11,14])
 im=Image.fromarray(np.uint8(a));d=ImageDraw.Draw(im);rng=np.random.default_rng(722)
 if not lab:
  for _ in range(135):
   x,y=rng.integers([0,100],[1280,590]);v=int(rng.uniform(24,75));d.point((int(x),int(y)),fill=(v,v,v+5))
 return im

def noise(x,y,z,seed=0):
 ix=np.floor(x);iy=np.floor(y);iz=np.floor(z);fx=ease(x-ix);fy=ease(y-iy);fz=ease(z-iz)
 out=np.zeros_like(x)
 for a in (0,1):
  for b in (0,1):
   for c in (0,1):
    q=np.sin((ix+a)*127.1+(iy+b)*311.7+(iz+c)*74.7+seed*31.37)*43758.5453
    q=q-np.floor(q);out+=q*(fx if a else 1-fx)*(fy if b else 1-fy)*(fz if c else 1-fz)
 return out

def fbm(x,y,z,seed=0,octaves=5):
 out=np.zeros_like(x);amp=.5
 for k in range(octaves):
  out+=amp*noise(x,y,z,seed+k*3);x=x*2.03+4.1;y=y*2.01+2.7;z=z*2.02+3.9;amp*=.51
 return out

@lru_cache(maxsize=320)
def body(kind='rock',seed=1,rot=0,n=400,heat=0,cut=0):
 y,x=np.mgrid[-1.12:1.12:complex(n),-1.12:1.12:complex(n)];ang=np.arctan2(y,x)
 irregular=kind in ('rock','dust','meteorite','lunar','terrestrial','meltfragment')
 radius=1+(0.065*np.sin(ang*3+seed)+.042*np.cos(ang*5+seed*2)+.022*np.sin(ang*9)) if irregular else np.ones_like(x)
 xx=x/(radius*(1 if not irregular else 1.02));yy=y/(radius*(1 if not irregular else .82));rr=xx*xx+yy*yy;z=np.sqrt(np.maximum(0,1-rr))
 r=rot/80*math.tau;u=xx*np.cos(r)+z*np.sin(r);v=yy;w=z*np.cos(r)-xx*np.sin(r)
 field=fbm(u*3,v*3,w*3,seed,5);fine=noise(u*105,v*105,w*105,seed+9)
 relief=field*.19+fine*.008;dy,dx=np.gradient(relief);norm=np.sqrt((xx+dx*n/2)**2+(yy+dy*n/2)**2+z*z)+1e-5
 light=np.clip((-.5*(xx+dx*n/2)-.48*(yy+dy*n/2)+.72*z)/norm,0,1)
 shade=.09+.91*light;fleck=np.clip((field-.46)*6,0,1)
 if kind in ('rock','dust','meteorite','meltfragment'):
  base=np.stack([52+field*100,51+field*91,48+field*80],2);metal=np.clip((fine-.82)*7,0,1)*np.clip((field-.48)*6,0,1);base+=metal[:,:,None]*np.array([110,104,91])
 elif kind in ('lunar','terrestrial'):
  grains=noise(u*22,v*22,w*22,seed+5);crystal=np.clip((grains-.51)*7,0,1);dark=np.clip((.42-grains)*7,0,1)
  base=np.stack([75+field*105,76+field*104,73+field*100],2)+crystal[:,:,None]*np.array([79,76,68])-dark[:,:,None]*35
  if kind=='meltfragment':base=base*.55+np.stack([110+field*80,25+field*60,8+field*12],2)
 elif kind=='metal':
  spec=np.clip((-.25*xx-.37*yy+.9*z),0,1)**34
  base=np.stack([136+field*30,92+field*29,53+field*25],2)+spec[:,:,None]*np.array([150,130,100])
 elif kind=='moon':
  base=np.stack([80+field*100,77+field*94,68+field*88],2)
  # Crater depression/rim height lighting, generated in object coordinates.
  rng=np.random.default_rng(711)
  crater=np.zeros_like(x)
  for _ in range(9):
   cx,cy=rng.uniform(-.8,.8,2);cr=rng.uniform(.025,.16);dist=np.sqrt((u-cx)**2+(v-cy)**2)/cr
   crater+=np.exp(-((dist-1)/.13)**2)*.032-np.exp(-(dist/.75)**4)*.017
  gy,gx=np.gradient(crater);shade=np.clip(shade+(-gx-gy)*n*.28,.05,1)
 else:
  # Incandescent silicate ocean with fine convection/rafts, not broad black/orange islands.
  convection=fbm(u*8,v*8,w*8,seed+30,4)
  fissure=np.exp(-((convection-.47)/.021)**2)
  raft=np.clip((field-.43-heat*.095)*8,0,.65)
  temp=np.clip(.38+convection*.60+fissure*.16+heat*.12,0,1)
  hot=np.stack([136+temp*114,30+temp*109,8+temp**3*42],2)
  stone=np.stack([67+field*62,52+field*53,43+field*46],2)
  rgb=hot*(1-raft[:,:,None])+stone*raft[:,:,None]
  rgb*= (.27+.58*z+.15*light)[:,:,None]
  rgb+=fissure[:,:,None]*np.array([18,11,2])
 if kind not in ('earth','embryo'):rgb=base*shade[:,:,None]
 if cut>0:
  # Recessed, oblique sectional face with a bevel and protruding liquid-metal core.
  plane=-.24+.21*x-.10*y
  radial3=np.sqrt(x*x+y*y+plane*plane)
  opening=(x>0)&(radial3<.985)&(x<cut*1.08)
  core=.18+.25*cut
  folds=fbm(x*7,y*7,plane*7,seed+31,3)
  mantle=np.stack([153+folds*71,51+folds*64,13+folds*31],2)
  cavity=np.clip(x/.12,0,1)*np.clip((.985-radial3)/.065,0,1)
  faceShade=(.43+.37*cavity)*(.9-.12*x-.18*y)
  mantle*=faceShade[:,:,None]
  hotCore=(x*x+y*y)<core*core
  cz=np.sqrt(np.maximum(0,1-(x*x+y*y)/(core*core)))
  cLight=np.clip(-.44*x/core-.35*y/core+.82*cz,0,1)
  spec=np.clip(-.20*x/core-.3*y/core+.93*cz,0,1)**24
  coreRGB=np.stack([125+cz*63,69+cz*64,30+cz*47],2)*(.35+.65*cLight)[:,:,None]+spec[:,:,None]*np.array([89,78,56])
  mantle=np.where(hotCore[:,:,None],coreRGB,mantle)
  rgb=np.where(opening[:,:,None],mantle,rgb)
 alpha=np.uint8(np.clip((1-rr)*n/3,0,1)*255)
 return Image.fromarray(np.dstack([np.uint8(np.clip(rgb,0,255)),alpha]),'RGBA')

def put(im,kind,xy,r,seed=1,rot=0,heat=0,cut=0):
 resolution=96 if r<30 else (192 if r<85 else 480)
 if kind in ('earth','embryo','moon'):rot=0
 # Interpolate the cached cut states so the reveal cannot jump between sampled sections.
 c0=math.floor(cut*20)/20;c1=min(1,c0+.05);f=(cut-c0)*20
 s=body(kind,seed,int(rot)%80,resolution,round(heat*10)/10,round(c0,2))
 if cut>0 and f>.001:
  s=Image.blend(s,body(kind,seed,int(rot)%80,resolution,round(heat*10)/10,round(c1,2)),f)
 size=max(2,int(r*2.24));s=s.resize((size,size),Image.Resampling.LANCZOS)
 im.paste(s,(int(xy[0]-size/2),int(xy[1]-size/2)),s)

def glow(im,xy,r,strength=1):
 y,x=np.mgrid[0:H,0:W];g=np.exp(-((x-xy[0])**2+(y-xy[1])**2)/(r*r));a=np.asarray(im,dtype=float)+g[:,:,None]*np.array([150,65,14])*strength
 return Image.fromarray(np.uint8(np.clip(a,0,255)))

@lru_cache(None)
def disk_base():
 # P10 bridge is replaced by the exact clean end plate when supplied.
 path=HERE/'p10_clean_end.png'
 if path.exists():return Image.open(path).convert('RGB').resize((W,H))
 return Image.open(ROOT/'disk-delivery/H10-original-disk-clean.png').convert('RGB').resize((W,H))
def disk(im,t):
 plate=disk_base();zoom=1+t*.45;cropw=W/zoom;croph=H/zoom;cx=640+t*130;cy=360+t*35
 plate=plate.crop((cx-cropw/2,cy-croph/2,cx+cropw/2,cy+croph/2)).resize((W,H),Image.Resampling.BICUBIC)
 return plate

def rockfield(im,t,cluster=0,count=70):
 rng=np.random.default_rng(320)
 pts=[]
 for i in range(count):
  x,y=rng.uniform([110,180],[1090,540]);z=rng.uniform(.3,1);x=600+(x-600)*(1-cluster*.83)+t*14*z;y=360+(y-360)*(1-cluster*.8)
  pts.append((z,x,y,i))
 for z,x,y,i in sorted(pts):put(im,'dust',(x,y),3+z*12,seed=i%11+1,rot=t*7+i*3)
 return im

def system(t=0,scale=1):
 im=background().copy();im=glow(im,(477,355),235*scale,.15)
 put(im,'earth',(495,355),177*scale,4,t*2,heat=.46)
 put(im,'moon',(913,238),55*scale,13,t*1.3)
 return im

@lru_cache(None)
def mineral_detail(p):
 n=320;y,x=np.mgrid[-1:1:complex(n),-1:1:complex(n)];rng=np.random.default_rng(771+p)
 img=np.zeros((n,n,3))+np.array([49,48,45]);best=np.ones((n,n))*1e6;owner=np.zeros((n,n),int)
 seeds=rng.uniform(-1.3,1.3,(75,2))
 for i,(cx,cy) in enumerate(seeds):
  # Crystallized mineral grain section; authored illustration, never a micrograph.
  dd=((x-cx)*1.4)**2+((y-cy)*.75)**2;sel=dd<best;owner[sel]=i;best=np.minimum(best,dd)
 colors=rng.uniform(.4,1,(75,1))*np.array([[184,178,161]])
 img=colors[owner];gy,gx=np.gradient(owner.astype(float));edge=(gx!=0)|(gy!=0)
 img[edge]*=.37
 img+=noise(x*75,y*75,x*0,19)[:,:,None]*15
 alpha=np.uint8(np.clip((1-x*x-y*y)*n/3,0,1)*255)
 return Image.fromarray(np.dstack([np.uint8(np.clip(img,0,255)),alpha]),'RGBA')

def add_detail(im,p,t):
 q=(phase(t,.015,.08)*(1-phase(t,.24,.32))) if p==17 else phase(t,.30,.43)
 if q<=0:return im
 layer=background(True).copy();detail=mineral_detail(p);layer.paste(detail,(684,224),detail)
 # Keep first specimen as evidence origin; an anchored optical detail replaces the second.
 put(layer,'lunar' if p==17 else 'terrestrial',(414,369),175,17 if p==17 else 28,t)
 d=ImageDraw.Draw(layer);d.line([(493,346),(648,300),(688,300)],fill=(168,164,149),width=2)
 d.ellipse((481,334,505,358),outline=(207,190,151),width=2)
 if p==17:text(layer,(704,549),'矿物细节 · 示意',23)
 if p==15:
  text(layer,(70,146),'同位素记录用于推断年代',29)
  text(layer,(727,181),'母体核素 → 子体核素',23,(231,185,128))
  change=phase(t,.34,.57);ncol=tuple(int(a+(b-a)*change) for a,b in zip((239,162,72),(106,197,219)))
  d.ellipse((827,330,865,368),fill=(18,26,32),outline=ncol,width=2)
  d.ellipse((835,338,857,360),fill=ncol)
  d.line([(846,369),(846,414),(929,435)],fill=ncol,width=2)
  d.rounded_rectangle((891,427,995,465),radius=6,fill=(14,23,30))
  text(layer,(902,430),'母体' if change<.5 else '子体',23,ncol)
  text(layer,(692,549),'单个核素变化示意',23)
  if t>.76:text(layer,(67,201),'约 45.4 亿年前的一段历程',26,(231,185,128))
 else:
  text(layer,(70,146),'熔融后结晶的矿物记录',29)
  text(layer,(700,182),'矿物结构保留早期历史',23)
  if t>.72:text(layer,(67,202),'用样品检验大碰撞解释',25,(231,185,128))
 text(layer,(315,530),'返回的月岩' if p==17 else '地球样品',25)
 note(layer,'程序化标本与矿物结构示意 · 非实测图像、数量或比例')
 return Image.blend(im,layer,q)

@lru_cache(None)
def stellar_renderer():
 import importlib.util
 spec=importlib.util.spec_from_file_location('planet_recap_stellar',HERE.parent/'stellar'/'renderer.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def recap(t):
 a=cue('P18','其中许多元素');b=cue('P18','它们穿过');c=cue('P18','进入新的云团');d=cue('P18','又在太阳周围')
 end=.94
 if t<a:return system(t)
 if t<b:return stellar_renderer().render('P07',.66+.20*(t-a)/(b-a),W,H)
 if t<c:return stellar_renderer().render('P08',.46+.12*(t-b)/(c-b),W,H)
 if t<d:return stellar_renderer().render('P09',.82+.18*(t-c)/(d-c),W,H)
 if t<end:
  q=(t-d)/(end-d);diskim=disk(background().copy(),q*.5)
  return Image.blend(diskim,system(0),phase(q,.55,1))
 return system(0)

def render(paragraph_id,local_progress,width=1280,height=720):
 p=int(str(paragraph_id).replace('P',''));t=float(np.clip(local_progress,0,1));im=background().copy()
 if p==11:
  im=disk(im,min(t,.5)*.7)
  a=phase(t,.35,.68)
  if a:
   local=disk_base().crop((700,350,860,440)).resize((W,H),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(4))
   local=Image.blend(local,background(),.40)
   rockfield(local,t,0,35)
   put(local,'rock',(785,378),93,2,t*3);put(local,'rock',(952,475),49,5,t*3);put(local,'rock',(698,478),30,8,t*3)
   im=Image.blend(im,local,a)
  if t>.16:text(im,(68,154),'较热的内侧',28,(236,179,114))
  if t>.28:text(im,(70,195),'冰难以保持固态',24)
  if .10<t<.42:text(im,(829,208),'较远处更冷',23,(157,192,207))
  if t>.60:text(im,(756,531),'岩石与金属颗粒',24)
  note(im,'盘内局部放大 · 温度与尺度示意')
 elif p==12:
  a=cue('P12','碰撞并不');b=cue('P12','一种解释');c=cue('P12','当密度')
  if t<b:
   # The three outcomes are sequential, with hold time after each contact.
   bounce=cue('P12','有些弹开');frag=.205
   if t<bounce:idx=0;q=t/bounce
   elif t<frag:idx=1;q=(t-bounce)/(frag-bounce)
   else:idx=2;q=min(1,(t-frag)/(.32-frag))
   pair=[(300,790),(360,730),(345,745)][idx];travel=phase(q,0,.48)
   if idx==0:
    put(im,'dust',(pair[0]+215*travel,357),79,2);put(im,'dust',(pair[1]-140*travel,355),66,7)
    label='黏合' if q>.5 else '细小颗粒相遇'
   elif idx==1:
    off=113*phase(q,0,.40)-95*phase(q,.45,.65);put(im,'dust',(pair[0]+off,351),79,2);put(im,'dust',(pair[1]-off,366),64,7);label='弹开'
   else:
    put(im,'dust',(pair[0]+128*travel,351),79*(1-.55*phase(q,.48,.6)),2)
    if q<.52:put(im,'dust',(pair[1]-128*travel,366),64,7)
    else:
     for k in range(15):
      ang=k*2.39;d=(q-.48)*380*(.4+k/22);put(im,'dust',(552+math.cos(ang)*d,360+math.sin(ang)*d*.6),9+k%4*3,k%10+1)
    label='破碎'
   text(im,(65,154),label,28);text(im,(65,542),'碰撞并不总能带来生长',24)
   if t>a:text(im,(690,165),'最初的生长难关，仍在研究',23)
  else:
   q=phase(t,b,c if c>b else .78);collapse=phase(t,c,1)
   # Drifting gas density wakes (soft material, no line-loop floor).
   y,x=np.mgrid[0:H,0:W];gas=np.exp(-((y-355-33*np.sin(x/160+t*2))/64)**2)*np.exp(-((x-640)/580)**2)
   ar=np.asarray(im,dtype=float)+gas[:,:,None]*np.array([13,22,28]);im=Image.fromarray(np.uint8(ar))
   rockfield(im,t,.55*q+.4*collapse,100)
   if collapse>.25:put(im,'rock',(610,360),80*phase(collapse,.25,.85),6,t*3)
   text(im,(65,153),'局部富集 → 自引力坍缩',28);text(im,(66,198),'解释之一 · 仍在研究',23,(182,200,210))
  note(im,'过程示意 · 尺度与时间压缩')
 elif p==13:
  # Traceable target, incoming body, contact, growth and ejecta in two epochs.
  a=cue('P13','胚胎又');b=cue('P13','猛烈');q=t/max(a,.35) if t<a else (t-a)/(1-a)
  r=93 if t<a else 187;kind='rock' if t<a else 'embryo';contact=phase(q,.05,.43)
  if t>=a:im=glow(im,(574,355),270,.23)
  put(im,kind,(600,353) if t<a else (574,350),r+20*phase(q,.42,.65),6 if t<a else 4,t*4,heat=.18)
  if q<.5:put(im,'rock',(955-(355-r*.55)*contact,242+87*contact),r*.36*(1-phase(q,.43,.5)),3,t*6)
  if t>b:
   e=phase(t,b,1)
   for k in range(25):
    ang=-.8+k*.024;dist=185+e*(110+k*5);put(im,'rock',(600+dist*math.cos(ang),353+dist*math.sin(ang)),3+k%5,3+k%9,t*2)
   text(im,(65,202),'猛烈撞击，也会抛失物质',25)
  text(im,(65,154),'从小天体到行星胚胎' if t<a else '地球的漫长吸积',28)
  if t>.75:text(im,(65,539),'延续数千万年',27,(225,177,119))
  note(im,'演化阶段示意 · 非同一事件的实时尺度')
 elif p==14:
  melt=phase(t,0,cue('P14','熔融让'));cut=phase(t,cue('P14','熔融让'),.69)
  im=glow(im,(574,355),270,.23);put(im,'earth',(574,350),207,4,t*3,heat=.20+.55*melt,cut=cut)
  text(im,(67,150),'撞击能量 → 岩石熔融' if cut<.2 else '熔融后的内部重新分布',28)
  if cut>.2:
   rng=np.random.default_rng(150);d=ImageDraw.Draw(im)
   for k in range(16):
    xx,yy=rng.uniform(.2,.84),rng.uniform(-.67,.67);r0=np.hypot(xx,yy)
    if r0>.92:continue
    f=1-.76*phase(t,.32+k*.012,.68+k*.017);x=574+xx*207*f;y=350+yy*207*f
    if r0*f>(.18+.25*cut)+.025:put(im,'metal',(x,y),6+2*(k%2),4)
   text(im,(825,270),'富铁金属下沉',23,(240,194,130));text(im,(825,366),'较轻的岩石在外围',23)
  if t>.78:text(im,(825,451),'金属核逐渐形成',24,(240,194,130))
  note(im,'内部演化剖示 · 非比例 · 不表示瞬间分层')
 elif p in (15,17):
  im=background(True).copy();d=ImageDraw.Draw(im)
  # Objects have coherent area light, contact shadows, relief and distinct mineralogy.
  shadow=Image.new('RGBA',(W,H));sd=ImageDraw.Draw(shadow)
  sd.ellipse((210,482,607,535),fill=(0,0,0,210));sd.ellipse((698,482,1041,528),fill=(0,0,0,210));shadow=shadow.filter(ImageFilter.GaussianBlur(20));im=Image.alpha_composite(im.convert('RGBA'),shadow).convert('RGB')
  put(im,'terrestrial' if p==15 else 'lunar',(414,369),175,28 if p==15 else 17,t*1)
  put(im,'meteorite' if p==15 else 'terrestrial',(861,390),142,37 if p==15 else 28,t*1)
  base_image=im.copy();qdetail=(phase(t,.015,.08)*(1-phase(t,.24,.32))) if p==17 else phase(t,.30,.43)
  if qdetail<=0:
   text(im,(313,530),'地球样品' if p==15 else '返回的月岩',25);text(im,(798,530),'陨石' if p==15 else '地球岩石',25)
   if p==15:
    text(im,(68,143),'约 45.4 亿年',36,(232,187,126))
    if t>.3:text(im,(69,200),'样品中的同位素记录 → 形成年代',24)
    if t>.67:text(im,(716,159),'形成是一段漫长过程',25)
   else:
    text(im,(68,145),'早期高温熔融的记录' if t<.30 else '月岩与地球岩石对照',29)
    if t>.32:text(im,(731,169),'化学成分有许多相似之处',24)
    if t>.62:text(im,(70,207),'用样品检验大碰撞解释',24,(230,184,124))
   note(im,'程序化矿物标本示意 · 不是具体任务返回样品的照片或测量')
   label_visibility=(1-phase(t,.27,.30)) if p==15 else (phase(t,.32,.36) if t>.30 else 1-phase(t,0,.015))
   im=Image.blend(base_image,im,label_visibility)
  im=add_detail(im,p,t)
 elif p==16:
  a=cue('P16','一次大碰撞');b=cue('P16','抛出的物质');c=cue('P16','撞击怎样')
  q=phase(t,max(0,a-.10),b);put(im,'earth',(511,365),165,4,t*2,heat=.5)
  if q<.5:
   k=phase(q,0,.5);put(im,'embryo',(937-334*k,195+62*k),79*(1-.5*phase(q,.42,.5)),8,t*5,heat=.2)
  grow=phase(t,b,c)
  if grow>0:put(im,'moon',(916,250),53*phase(grow,.18,.90),13,t)
  if q>.40:
   burst=phase(q,.40,.85);rng=np.random.default_rng(566)
   plume=Image.new('RGBA',(W,H));pd=ImageDraw.Draw(plume)
   for k in range(100):
    escaping=k%4==0;ang=rng.uniform(-1.14,.42);dist=rng.uniform(205,395)
    ox=511+dist*math.cos(ang);oy=365+dist*math.sin(ang)*.69
    if escaping:
     ox+=burst*(190+k*3);oy-=burst*(25+k*.7)
    x=603+(ox-603)*burst;y=257+(oy-257)*burst
    if not escaping:
     x+=(916-x)*grow;y+=(250-y)*grow
    rad=rng.uniform(2,8)*(1-.7*grow if not escaping else 1)
    if grow>.88 and not escaping:continue
    alpha=int((1-grow*.7)*26);pd.ellipse((x-rad*4,y-rad*3,x+rad*4,y+rad*3),fill=(226,129,52,alpha))
   plume=plume.filter(ImageFilter.GaussianBlur(9));im=Image.alpha_composite(im.convert('RGBA'),plume).convert('RGB')
   rng=np.random.default_rng(566)
   for k in range(100):
    escaping=k%4==0;ang=rng.uniform(-1.14,.42);dist=rng.uniform(205,395)
    ox=511+dist*math.cos(ang);oy=365+dist*math.sin(ang)*.69
    if escaping:ox+=burst*(190+k*3);oy-=burst*(25+k*.7)
    x=603+(ox-603)*burst;y=257+(oy-257)*burst
    if not escaping:x+=(916-x)*grow;y+=(250-y)*grow
    rad=rng.uniform(2,8)*(1-.7*grow if not escaping else 1)
    if grow>.88 and not escaping:continue
    put(im,'meltfragment',(x,y),rad,k%11,t*3)
   if grow<.8:
    text(im,(844,484),'留在附近的物质',22)
    text(im,(846,137),'部分物质逃逸',22,(193,179,156))
  text(im,(65,148),'大碰撞解释',29);text(im,(65,194),'主流解释 · 具体细节仍在研究',23,(180,195,208))
  if t>b:text(im,(758,523),'部分抛出物聚集成月球',24)
  note(im,'碰撞及聚集示意 · 大幅压缩时间 · 非唯一轨迹')
 elif p==18:
  im=recap(t)
  if cue('P18','其中许多元素')<=t<.94:text(im,(65,570),'材料来历回顾 · 时间与尺度压缩',19,(169,176,178))
 elif p==19:im=system(t,1-.08*t)
 else:raise ValueError(paragraph_id)
 if (width,height)!=(W,H):im=im.resize((width,height),Image.Resampling.LANCZOS)
 return im.convert('RGB')

if __name__=='__main__':
 for p in range(11,20):
  for j,t in enumerate((.06,.50,.94)):
   fn=HERE/'keyframes'/f'P{p:02d}-K{j+1}.png';render(f'P{p:02d}',t).save(fn);print(fn,flush=True)
