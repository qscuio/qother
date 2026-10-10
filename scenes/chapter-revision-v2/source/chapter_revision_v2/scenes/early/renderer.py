"""Authored perspective-volume scientific illustration. Not a numerical simulation.
Public interface: render(paragraph_id, local_progress, width=1280, height=720).
No presenter, branding or narration subtitles are baked in.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from functools import lru_cache
import math
from scipy.ndimage import map_coordinates, gaussian_filter
NOISE=gaussian_filter(np.random.default_rng(39).random((64,64,64)).astype(np.float32),1.0,mode='wrap')
NOISE=(NOISE-NOISE.mean())/NOISE.std()
W,H=1280,720
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
RNG=np.random.default_rng(418)
POINTS=RNG.uniform([-8,-4,3],[8,4,22],(90,3))
HERO=np.array([[-2.6,-.4,6.5],[.15,.6,8],[2.7,-.9,10],[-.3,-1.4,12],[4,.8,16]],float)
def ease(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
def font(s):return ImageFont.truetype(FONT,s)
def label(im,xy,text,size=22,color=(205,219,223)):
 d=ImageDraw.Draw(im);d.text(xy,text,font=font(size),fill=color,stroke_width=2,stroke_fill=(12,18,27))
def project(p,cam=0):
 x,y,z=p;z=max(.2,z-cam);return 640+780*x/z,345+780*y/z,780/z
@lru_cache(maxsize=256)
def _volume(stage,zoom=0):
 # Perspective integration of a continuous periodic 3-D field, no rendered edge.
 w,h=640,360;y,x=np.mgrid[0:h,0:w].astype(np.float32)
 dx=(x/w-.5)*1.64;dy=(y/h-.48)*.92
 acc=np.zeros((h,w,3),np.float32);trans=np.ones((h,w),np.float32)
 hot=np.array([.85,.65,.57]);cool=np.array([.16,.28,.36]);c=hot*(1-stage)+cool*stage
 for z in np.linspace(2,19,24)[::-1]:
  X=dx*z;Y=dy*z;Z=z+zoom
  # Fine, low-contrast plasma structure is illustrative, not primordial density data.
  f=np.zeros_like(X)
  for freq,amp in [(.65,.22),(1.8,.14),(4.8,.10),(12.2,.055)]:
   coords=np.array([X*freq+25,Y*freq+24,np.full_like(X,Z*freq+20)])
   f+=amp*map_coordinates(NOISE,coords,order=1,mode='grid-wrap')
  f=np.clip(.48+f,0,1)
  density=(.33*(1-stage)+.018)*np.clip((f-.40)*3.2,0,1)
  source=c[None,None,:]*(.08+f[...,None]**3*2.0)
  acc=acc*(1-density[...,None])+source*density[...,None]
 v=np.clip(acc*255,0,255)
 im=Image.fromarray(v.astype(np.uint8)).resize((W,H),Image.Resampling.BICUBIC)
 # Frame-wide falloff preserves an unbounded medium, without a sphere or origin.
 ar=np.asarray(im).astype(float);yy,xx=np.mgrid[:H,:W];v=1-.26*((xx-640)**2/640**2+(yy-345)**2/500**2)
 ar*=np.clip(v,.55,1)[...,None]
 return Image.fromarray(ar.astype('uint8'))
def volume(stage,zoom=0):
 # Continuously interpolate cached ray-integrated volume states for frame seeking.
 a=math.floor(stage*10)/10;b=min(1,a+.1);f=(stage-a)*10
 za=math.floor(zoom*10)/10;zb=za+.1;zf=(zoom-za)*10
 ia=Image.blend(_volume(a,za),_volume(a,zb),zf)
 if b==a:return ia
 ib=Image.blend(_volume(b,za),_volume(b,zb),zf)
 return Image.blend(ia,ib,f)
@lru_cache(maxsize=512)
def cloud_sprite(r,kind='cloud',seed=0):
 r=max(2,r);yy,xx=np.mgrid[-r:r+1,-r:r+1];u=xx/r;v=yy/r;rr=u*u+v*v
 ar=np.zeros((2*r+1,2*r+1,4),np.uint8)
 if kind=='nucleus':
  nz=np.sqrt(np.clip(1-rr,0,1));light=np.clip(-.42*u-.55*v+.69*nz,.07,1)
  col=np.array([231,162,91]);val=.20+.80*light
  ar[:,:,:3]=np.clip(col[None,None,:]*val[...,None]+(np.maximum(0,light-.82)**8*1e7)[...,None],0,255)
  ar[:,:,3]=np.where(rr<1,255,0)
 elif kind=='electron':
  val=np.exp(-rr*9);ar[:,:,:3]=(148,224,248);ar[:,:,3]=np.uint8(val*240)
 else:
  # Integrated translucent probability density. No orbit tracks or solid shell.
  n=.75+.25*np.random.default_rng(seed+77).random(u.shape)
  val=np.exp(-rr*3.1)*np.clip(1-rr,0,1)*n
  ar[:,:,:3]=(91,161,181);ar[:,:,3]=np.uint8(val*125)
 return Image.fromarray(ar,'RGBA')
def paste(im,s,x,y):im.paste(s,(round(x-s.width/2),round(y-s.height/2)),s)
def ball(im,x,y,r,kind='nucleus',seed=0):paste(im,cloud_sprite(int(max(2,r)),kind,seed),x,y)
def atom(im,x,y,s,neutral=1,he=False,seed=0):
 # nucleus is an illustrative enlarged marker; size is expressly non-proportional.
 if neutral>0:
  sp=cloud_sprite(int(max(3,58*s)),seed=seed).copy();sp.putalpha(sp.getchannel('A').point(lambda a:int(a*neutral)));paste(im,sp,x,y)
 if he:
  ball(im,x,y,6*s)
 else:ball(im,x,y,4*s)
 # foreground density provides occlusion over the bright nucleus.
 if neutral>.1:
  sp=cloud_sprite(int(max(3,46*s)),seed=seed+2).copy();sp.putalpha(sp.getchannel('A').point(lambda a:int(a*.22*neutral)));paste(im,sp,x,y)
def photon(im,points,progress,trail=.8,color=(244,238,193)):
 pts=np.asarray(points,float);lens=np.linalg.norm(np.diff(pts,axis=0),axis=1);total=sum(lens);distance=np.clip(progress,0,1)*total
 d=ImageDraw.Draw(im)
 for j,L in enumerate(lens):
  start=sum(lens[:j]);f=np.clip((distance-start)/L,0,1)
  if f<=0:break
  a=pts[j];b=a+(pts[j+1]-a)*f
  # Only the portion the packet has actually travelled is displayed.
  if distance-start<L+total*.20:d.line([tuple(a),tuple(b)],fill=(135,139,128),width=2)
  if distance<=start+L:
   ball(im,*b,19,'electron');d.ellipse((b[0]-3,b[1]-3,b[0]+3,b[1]+3),fill=color);break

def field(im,neutral=0,cam=0,expansion=1,hot=1):
 for i,p in sorted(enumerate(POINTS[:14]),key=lambda q:q[1][2],reverse=True):
  p=p.copy();p[:2]*=expansion;p[2]=9+(p[2]-9)*expansion
  x,y,s=project(p,cam)
  if 20<x<1250 and 120<y<610:
   atom(im,x,y,s*.005,neutral,i%11==0,i)

PLASMA=np.vstack([np.random.default_rng(722).uniform([-8,-4,2.8],[8,4,22],(340,3)),np.array([[-1.42,.55,2.6],[.50,-.42,6.8],[2.25,.25,11],[1.75,-.55,3.4],[-.6,.75,3]])])
def charged_medium(im,cam=0,expansion=1):
 d=ImageDraw.Draw(im)
 for i,p in sorted(enumerate(PLASMA),key=lambda pair:pair[1][2],reverse=True):
  q=p.copy();q[:2]*=expansion;q[2]=9+(q[2]-9)*expansion
  if q[2]-cam<.4:continue
  x,y,scale=project(q,cam);r=scale*(.10 if i>=340 else .032)
  if not (-40<x<1320 and -40<y<760):continue
  col=(216,167,137) if i%3 else (117,182,205)
  if r>5:
   # Solid-shaded charge markers are deliberately unlike astronomical points.
   ball(im,x,y,r,'nucleus' if i%3 else 'electron')
   dd=ImageDraw.Draw(im);dd.line((x-r*.42,y,x+r*.42,y),fill=(245,239,227),width=1)
   if i%3:dd.line((x,y-r*.42,x,y+r*.42),fill=(245,239,227),width=1)
  else:d.ellipse((x-r,y-r,x+r,y+r),fill=tuple(int(c*.68) for c in col))

def p01(t):
 cam=1.6*ease(t);im=volume(0,cam).copy()
 charged_medium(im,cam)
 # Broad-to-near view of the SAME selection. Tiny particle markers do not glow as stars.
 # Do not seed a starfield into the pre-stellar establishing view.
 # The 3-D emissive medium itself is the subject.
 label(im,(52,154),'热密介质中的同一局部',23)
 label(im,(52,557),'带电粒子示意 · 非比例',19,(196,190,182))
 if t>.28:label(im,(52,190),'尚无恒星与岩石',20,(174,187,195))
 return im

def p02(t):
 # Phase A: fixed camera; homologous separation about an arbitrary local origin.
 expansion=1+.30*ease(t/.23)+.18*ease((t-.45)/.50)
 stage=.18+.40*ease((t-.445)/.155)
 im=volume(stage,1.6).copy();charged_medium(im,cam=1.6,expansion=expansion)
 pp=[]
 for i,p in enumerate(HERO):
  q=p.copy();q[:2]*=expansion;q[2]=9+(p[2]-9)*expansion
  x,y,s=project(q,1.2);pp.append((x,y));ball(im,x,y,16,'electron')
 if t<.240:
  label(im,(52,148),'固定视点 · 相邻物质间距增大',23)
  # Track two individual markers, no grid, no outward explosion front.
  for i in [0,1]:
   x,y=pp[i];ImageDraw.Draw(im).line((x,y+20,x,y+41),fill=(180,203,212),width=1)
  label(im,(pp[0][0]-12,pp[0][1]+44),'A',19);label(im,(pp[1][0]-12,pp[1][1]+44),'B',19)
 elif t<.446:
  label(im,(52,148),'光与自由电子相遇，改变方向',23)
  route=[(100,390),pp[0],pp[1],pp[3],pp[2],(1040,270)]
  photon(im,route,(t-.240)/.206)
 else:
  label(im,(52,148),'空间持续膨胀 · 温度逐渐降低',23)
  # Continued small separation; colour change alone is not the expansion cue.
  label(im,(52,186),'局部示意，无宇宙中心或边缘',19,(144,165,178))
 return im

def p03(t):
 neutral=ease((t-.15)/.22);im=volume((.58+.42*neutral),1.2).copy()
 field(im,neutral,cam=1.2,expansion=1.48)
 label(im,(52,557),'微观过程示意 · 原子结构非比例',19,(144,168,185))
 # Stable close-up subject. Electrons approach then become a bound diffuse cloud.
 x,y=527,355;s=3.5
 atom(im,x,y,s,neutral,False,1)
 if neutral<.99:
  ex=x-185*(1-neutral);ey=y-80*(1-neutral);ball(im,ex,ey,18,'electron')
  label(im,(x-223,y-131),'自由电子',20);label(im,(x+34,y+48),'原子核',20,(225,190,146))
 else:label(im,(x+105,y+61),'中性氢原子',22)
 if t<.414:label(im,(52,148),'冷却后，电子被束缚在原子中',23)
 elif t<.765:
  label(im,(52,148),'自由电子减少，光能够传播得更远',23)
  photon(im,[(30,273),(1085,273)],(t-.414)/.35)
 else:
  label(im,(52,148),'这份辐射延续至今天',23)
  # A spreading wave packet: wavelength increases, not invented observation data.
  d=ImageDraw.Draw(im);start=240;end=990;period=34+90*ease((t-.765)/.235)
  pts=[(xx,270+12*math.sin((xx-start)/period*math.tau)) for xx in range(start,end,3)]
  d.line(pts,fill=(178,205,220),width=2)
  label(im,(726,225),'波长被拉长',20)
  label(im,(52,186),'宇宙微波背景 · 示意，非观测图',19,(151,170,185))
 return im

def p04(t):
 im=volume(1,1.2).copy()
 fade=1-ease((t-.70)/.28)
 layer=im.copy()
 if fade>.001:
  atom(layer,420,338,3.6,1,False,1);atom(layer,738,400,2.8,1,True,4)
  label(layer,(309,460),'氢 H',24);label(layer,(776,482),'氦 He',24)
  label(layer,(52,557),'微观结构示意 · 非比例',19,(144,168,185))
  im=Image.blend(im,layer,fade)
 if t<.22:label(im,(52,148),'光能远行，恒星尚未出现',23)
 elif t<.54:label(im,(52,148),'普通物质主要是氢与氦',23)
 elif t<.80:
  label(im,(52,148),'岩石所需的氧、硅、铁，要等后来的恒星制造',23)
 else:
  # A material-scale transition: enlarged atomic structure gives way to a diffuse
  # neutral-gas patch, not atoms literally swelling into astronomical clouds.
  gas=gas_bridge(ease((t-.76)/.24))
  im=Image.blend(im,gas,ease((t-.76)/.24))
  label(im,(52,148),'回到气体尺度 · 氢与氦',23)
 return im

@lru_cache(maxsize=1)
def _entry_gas():
 from pathlib import Path
 return Image.open(Path(__file__).parent.parent/'stellar/keyframes/P05-entry-gas.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
def gas_bridge(q):
 return _entry_gas().copy()

def render(paragraph_id,local_progress,w=1280,h=720,**kwargs):
 width=kwargs.get("width",w);height=kwargs.get("height",h)
 t=float(np.clip(local_progress,0,1));im={'P01':p01,'P02':p02,'P03':p03,'P04':p04}[paragraph_id](t)
 if im.size!=(width,height):im=im.resize((width,height),Image.Resampling.LANCZOS)
 return im.convert('RGB')
if __name__=='__main__':
 from pathlib import Path
 out=Path(__file__).parent/'keyframes';out.mkdir(exist_ok=True)
 frames=[]
 for p in ['P01','P02','P03','P04']:
  for name,t in [('start',.04),('middle',.5),('end',.95)]:
   im=render(p,t);im.save(out/f'{p}-{name}.png');thumb=im.resize((480,270));ImageDraw.Draw(thumb).text((12,244),f'{p} {name} | renderer-output',fill='white');frames.append(thumb)
 sheet=Image.new('RGB',(1440,1080))
 for i,im in enumerate(frames):sheet.paste(im,((i%3)*480,(i//3)*270))
 sheet.save(out/'contact-sheet.jpg',quality=92)
