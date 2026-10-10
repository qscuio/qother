"""Original deterministic CPU volume/ray renderer; no external pixels or host/subtitles.
All positions are illustrative model units, never reconstructed stellar or galactic coordinates.
"""
from pathlib import Path
import math,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy.ndimage import gaussian_filter,map_coordinates
from functools import lru_cache
ROOT=Path(__file__).parent
import sys
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def _local_durations():
 data=json.loads((ROOT.parents[2]/'full_chapter_v1/audio/timeline.json').read_text())
 return {row['id']:row['duration'] for row in data['paragraphs']}
DUR=_local_durations()
def smooth(x):
 x=np.clip(x,0,1); return x*x*(3-2*x)
@lru_cache(1)
def noisegrid():
 rng=np.random.default_rng(81723); n=np.zeros((96,96,96),np.float32)
 for sig,amp in [(10,.42),(5,.38),(2,.32),(.65,.26),(.2,.12)]:
  a=gaussian_filter(rng.normal(size=n.shape).astype(np.float32),sig,mode='wrap'); a/=a.std(); n+=a*amp
 return n

def noise(x,y,z):
 return map_coordinates(noisegrid(),[np.broadcast_to((z*13+44)%96,x.shape),np.broadcast_to((y*13+40)%96,x.shape),(x*13+46)%96],order=1,mode='wrap',prefilter=False)

def canvas(w,h,seed=20):
 rng=np.random.default_rng(seed); a=np.zeros((h,w,3),np.float32)+np.array([.009,.014,.021],np.float32)
 return a

def tonemap(a):
 a=np.maximum(a,0); a=1-np.exp(-a*1.2); return Image.fromarray(np.uint8(np.clip(a**.82*255,0,255)))

def starfield(im,seed=10,number=170):
 rng=np.random.default_rng(seed); d=ImageDraw.Draw(im)
 for i in range(number):
  x,y=rng.uniform(0,im.width),rng.uniform(115,im.height-70); v=int(rng.uniform(24,90)); r=.35 if i%19 else .8
  d.ellipse((x-r,y-r,x+r,y+r),fill=(v,int(v*.91),int(v*.79)))
 return im

def volume(kind='cloud',phase=0,w=1280,h=720):
 # Pixel rays through a genuine 3-D density field. Emission/absorption is integrated near-to-far.
 sw=int(w*.5); sh=int(h*.5); Y,X=np.mgrid[:sh,:sw].astype(np.float32); X=(X/sw-.48)*9; Y=(Y/sh-.51)*5.1
 acc=np.zeros((sh,sw,3),np.float32); tr=np.ones((sh,sw),np.float32)
 steps=48; dz=5.5/steps
 for zz in np.linspace(-2.75,2.75,steps):
  # Perspective: ray cross-section increases with depth.
  x=X*(1+zz*.055); y=Y*(1+zz*.055); z=np.full_like(x,zz)
  if kind in ['cloud','enriched','early']:
   shrink=(1-.34*smooth(phase)) if kind=='cloud' else (1-.12*phase)
   qx=x/shrink; qy=y/shrink; qz=z/shrink
   n=noise(qx,qy,qz)
   e=np.exp(-((qx/2.1)**2+(qy/.9)**2+(qz/1.05)**2)*1.0)
   e+=.6*np.exp(-(((qx+1.5)/1.1)**2+((qy-.45)/.7)**2+((qz-.3)/.7)**2))
   den=e*np.clip(n+.6,0,4)**2.25*.55
   cool=np.array([.22,.34,.48]) if kind!='enriched' else np.array([.43,.34,.23])
   rad=np.sqrt(x*x+y*y+z*z)
   glow=np.exp(-rad**2/(.055+shrink*.015))*smooth((phase-.15)/.65)*3 if kind=='cloud' else np.zeros_like(x)
   col=cool[None,None,:]*(.9+.85*np.clip(n,0,2)[...,None])
   col+=glow[...,None]*np.array([3.3,1.6,.5])
   if kind=='early':
    for cx,cy,cz in [(-1.4,.1,-.25),(.4,-.35,.25),(1.4,.38,.1)]:
     rr=(x-cx)**2+(y-cy)**2+(z-cz)**2; col+=np.exp(-rr/.10)[...,None]*np.array([1.6,2.0,2.5])*(.3+phase)
  elif kind in ['wind','supernova']:
   rad=np.sqrt((x/1.13)**2+(y/.86)**2+z*z)
   n=noise(x*1.4,y*1.4,z*1.4)
   radius=.6+phase*1.9
   if kind=='wind':
    envelope=np.exp(-((rad-radius)/(.20+.10*phase))**2)+.30*np.exp(-((rad-radius*.7)/.28)**2)
    den=envelope*np.clip(n+.5,.0,3)*.65
    col=np.zeros((*x.shape,3))+np.array([.95,.32,.11]); col*=.55+np.clip(n,0,1.5)[...,None]*.45
   else:
    envelope=np.exp(-((rad-radius)/(.11+.06*phase))**2)
    den=envelope*np.clip(n+1,0,3)**1.4*.8
    col=np.zeros((*x.shape,3))+np.array([1.4,.45,.18]); col+=np.clip(n,0,2)[...,None]*np.array([.3,.35,.45])
  else: raise ValueError(kind)
  alpha=1-np.exp(-den*dz*1.8); acc+=tr[...,None]*alpha[...,None]*col; tr*=1-alpha
 im=tonemap(acc+np.array([.005,.009,.015])); return im.resize((w,h),Image.Resampling.LANCZOS)

def sphere(im,cx,cy,r,t=0,cut=False,massive=False,color=(1,.43,.095)):
 margin=r*1.8+4
 box=(max(0,int(cx-margin)),max(0,int(cy-margin)),min(im.width,int(cx+margin)+1),min(im.height,int(cy+margin)+1))
 patch=_sphere(im.crop(box),cx-box[0],cy-box[1],r,t,cut,massive,color)
 out=im.copy();out.paste(patch,box[:2]);return out

def _sphere(im,cx,cy,r,t=0,cut=False,massive=False,color=(1,.43,.095)):
 w,h=im.size; yy,xx=np.mgrid[:h,:w].astype(np.float32); x=(xx-cx)/r;y=(yy-cy)/r; rr=x*x+y*y; mask=rr<1; z=np.sqrt(np.clip(1-rr,0,1))
 # Surface turbulence on a sphere; stable material rotates slightly, not texture zoom.
 nx=x*np.cos(t*.06)+z*np.sin(t*.06); nz=z*np.cos(t*.06)-x*np.sin(t*.06)
 tex=noise(nx*1.7,y*1.7,nz*1.7); tex2=noise(nx*7,y*7,nz*7)*.16
 light=(.38+.62*z)*(1.05+tex*.23+tex2); col=np.stack([light*color[0],light*color[1],light*color[2]],-1)
 if cut:
  # Remove a quadrant of the front hemisphere. Exposed plane is a spherical interior,
  # with depth/shadows, not concentric flat shell rings. Element tags mark reaction products,
  # not an invented universal layered stellar structure.
  opening=((x-.22)/.66)**2+((y+.02)/.73)**2
  wedge=(opening<1)&mask
  radial=np.sqrt(x*x+y*y)
  hot=np.clip(1-radial,0,1)
  cutcol=np.stack([.5+hot*.75,.14+hot*.63,.035+hot*.32],-1)
  cutcol*=.78+.21*tex[...,None]+tex2[...,None]*.4
  # Curved recessed viewing aperture, with rim thickness and occlusion.
  edge=(opening>.85)&(opening<1);cutcol[edge]*=.36
  cutcol*= (.62+.38*np.sqrt(np.clip(1-opening,0,1)))[...,None]
  # A luminous spherical reaction region is visible behind the exposed plane.
  cr=np.sqrt(((x-.15)/.32)**2+((y-.05)/.32)**2);cz=np.sqrt(np.clip(1-cr*cr,0,1))
  corecol=np.stack([.85+cz*.55,.36+cz*.65,.09+cz*.35],-1)*(1+tex[...,None]*.08)
  cutcol=np.where((cr<1)[...,None],corecol,cutcol*.72)
  col=np.where(wedge[...,None],cutcol,col)
 arr=np.asarray(im).astype(np.float32)/255
 halo=np.exp(-np.maximum(np.sqrt(rr)-1,0)*10)*.20*(~mask)
 arr+=halo[...,None]*np.array(color)[None,None,:]
 arr=np.where(mask[...,None],1-np.exp(-col*1.65),arr)
 im=Image.fromarray(np.uint8(np.clip(arr,0,1)*255)); return im

def stars(im,centres,seed=5,count=230):
 rng=np.random.default_rng(seed); layer=Image.new('RGB',im.size);d=ImageDraw.Draw(layer)
 for j,(cx,cy,scale,power) in enumerate(centres):
  for k in range(count):
   x,y=rng.normal(cx,scale),rng.normal(cy,scale*.46)
   r=rng.choice([.45,.75,1.15],[1],p=[.7,.25,.05])[0]; a=int(rng.uniform(40,180)*power)
   d.ellipse((x-r,y-r,x+r,y+r),fill=(min(a,255),min(int(a*1.08),255),min(int(a*1.2),255)))
 a=np.asarray(im).astype(np.float32)+np.asarray(layer)+np.asarray(layer.filter(ImageFilter.GaussianBlur(2)))*1.3
 return Image.fromarray(np.uint8(np.clip(a,0,255)))

def galaxy(phase=0,w=1280,h=720,history=False,zoom=1):
 # Original barred-spiral structural model; artistic arms, not an asserted Gaia pixel map.
 sw=w;sh=h; yy,xx=np.mgrid[:sh,:sw].astype(np.float32); X=(xx/sw-.47)*10;Y=(yy/sh-.52)*5.625
 ang=1.04; acc=np.zeros((sh,sw,3),np.float32);tr=np.ones((sh,sw),np.float32)
 for zz in np.linspace(-4,4,52):
  x=X/zoom*(1+.035*zoom*zz); y=Y/zoom*(1+.035*zoom*zz); z=np.full_like(x,zz)
  dy=y*np.cos(ang)+z*np.sin(ang); dz=-y*np.sin(ang)+z*np.cos(ang)
  rr=np.sqrt(x*x+dy*dy); n=noise(x,dy,dz)
  theta=np.arctan2(dy,x); wave=2*theta-6*np.log(rr+.35)+n*.38
  arm=np.exp(-np.sin(wave)**2/.10)*(1-np.exp(-(rr/.75)**3))
  dustarm=np.exp(-np.sin(wave+.23)**2/.055)*(1-np.exp(-(rr/.7)**3))
  disk=np.exp(-rr/1.7)*np.exp(-(dz/.22)**2)*np.clip(1+n*.35,.1,2)*np.exp(-(rr/3.4)**8)
  bx=x*np.cos(.35)+dy*np.sin(.35);by=dy*np.cos(.35)-x*np.sin(.35)
  bulge=np.exp(-((bx/.43)**2+(by/1.3)**2+(dz/.32)**2)*1.4)
  if history:
   # Irregular historical proto-galactic assembly, no precise reconstructed orbit.
   disk*=.6; dx=2.5*(1-phase); ddy=.7*(1-phase)
   satellite=np.exp(-(((x-dx)/.8)**2+((dy-ddy)/.7)**2+((dz-.2)/.36)**2)*1.6)
   bulge+=satellite*.7
  dust=disk*(np.clip(n-.05,0,2)*2.5+dustarm*8)
  emiss=disk[...,None]*(.48+1.6*arm[...,None])*np.array([.64,.76,1.09])+bulge[...,None]*np.array([2.65,1.77,.94])
  alpha=1-np.exp(-(disk*.23+bulge*.17+dust)*.23)
  acc+=tr[...,None]*emiss*.17;tr*=1-alpha
 return _galaxy_finish(acc,w,h,zoom)

def _galaxy_finish(acc,w,h,zoom):
 ang=1.04
 im=tonemap(acc+np.array([.006,.01,.017]));im=im.resize((w,h),Image.Resampling.LANCZOS)
 # Original discrete stellar sampling follows the same disk projection.
 rng=np.random.default_rng(812); lay=Image.new('RGB',(w,h));d=ImageDraw.Draw(lay)
 for i in range(16000):
  r=rng.gamma(2,.80)
  if r>4.1:continue
  theta=rng.uniform(0,2*np.pi);x=r*np.cos(theta); y=r*np.sin(theta);z=rng.normal(0,.035)
  sy=y*np.cos(ang)-z*np.sin(ang);depth=y*np.sin(ang)+z*np.cos(ang)
  px=(x*zoom/(1+.035*zoom*depth)/10+.47)*w;py=(sy*zoom/(1+.035*zoom*depth)/5.625+.52)*h
  v=int(rng.uniform(13,95)*(1-r/6)*np.exp(-(r/3.4)**8));d.point((px,py),fill=(v,int(v*.94),min(255,int(v*1.13))))
 arr=np.asarray(im).astype(np.float32)+np.asarray(lay)*.70
 return Image.fromarray(np.uint8(np.clip(arr,0,255)))


def label(im,title,small='艺术示意 · 时间压缩 · 非比例',tags=()):
 d=ImageDraw.Draw(im);s=im.width/1280
 def text(x,y,v,size=24,fill=(226,218,199)):
  d.text((int(x*s),int(y*s)),v,font=ImageFont.truetype(FONT,int(size*s)),fill=fill,stroke_width=1,stroke_fill=(3,8,13))
 text(46,120,title,25);text(46,575,small,16,(154,163,170))
 for x,y,v in tags:text(x,y,v,23)
 return im

def fusion(w,h,phase):
 im=Image.new('RGB',(w,h),(9,13,21));im=starfield(im,99,25)
 # Integrated process, 4 protons -> helium nucleus. Reaction chain intentionally omitted.
 p=smooth((phase-.12)/.58);s=w/1280
 for j,(x,y) in enumerate([(310,265),(360,425),(650,230),(780,420)]):
  xx=x*(1-p)+560*p;yy=y*(1-p)+345*p
  if p<.70: im=sphere(im,xx*s,yy*s,24*s,cut=False,color=(.28,.62,1))
 if p>=.70:
  for j,(dx,dy,col) in enumerate([(-16,-12,(.35,.7,1)),(14,-10,(1,.48,.18)),(-12,15,(1,.48,.18)),(16,16,(.35,.7,1))]):
   im=sphere(im,(560+dx)*s,(345+dy)*s,22*s,cut=False,color=col)
  # emitted energy: outward light packets, one event, never repeated impact.
  d=ImageDraw.Draw(im)
  for an in [-.5,.6,2.5]:
   rr=70+smooth((phase-.62)/.38)*220;xx=(560+np.cos(an)*rr)*s;yy=(345+np.sin(an)*rr)*s
   d.ellipse((xx-5*s,yy-5*s,xx+5*s,yy+5*s),fill=(255,229,137))
 return label(im,'氢核聚变为氦，释放能量','核反应净结果示意 · 中间步骤与粒子未全部绘出',[(280,490,'氢原子核') ] if p<.70 else [(650,335,'氦核'),(820,450,'释放能量')])

def render(paragraph_id,local_progress,w=1280,h=720):
 width,height=w,h
 p=float(np.clip(local_progress,0,1));t=p*DUR[paragraph_id];w=width;h=height;s=w/1280
 if paragraph_id=='P05':
  if t<10.45:
   import materials
   im=materials.cloud(smooth((t-2.4)/8.0),smooth((t-5.5)/4.5)).resize((w,h))
   return label(im,'气体汇聚，中心升温',tags=[(830,240,'较密的云结')] if t<4.3 else [])
  if t<15.95:return fusion(w,h,(t-10.45)/5.5)
  im=starfield(Image.new('RGB',(w,h),(4,8,14)));im=sphere(im,590*s,345*s,148*s,t)
  return label(im,'核聚变，让恒星持续发光','恒星结构与颜色为示意 · 非太阳实拍')
 if paragraph_id=='P06':
  import materials
  im=materials.cloud(.12*p,0,'gas').resize((w,h));im=stars(im,[(450*s,325*s,100*s,.4+p*.4),(680*s,300*s,90*s,max(.1,p)),(840*s,390*s,75*s,max(.1,(p-.3)))],count=240)
  return label(im,'第一批恒星与早期星系','宇宙最初几亿年 · 不规则系统形成示意',[(750,495,'气体汇入，新的恒星诞生')] if t>9.9 else [])
 if paragraph_id=='P07':
  im=starfield(Image.new('RGB',(w,h),(5,8,13)),15,100)
  cut=t>4.8;massive=t>=8.89;im=sphere(im,545*s,346*s,195*s,t,cut,massive)
  tags=[]
  if 7.5<t<8.89:tags=[(800,295,'碳 · 氧')]
  if t>=8.89:tags=[(800,280,'硅 · 铁') ] if t>=11.2 else []
  if t>7.5:
   d=ImageDraw.Draw(im)
   symbols=['Si','Fe'] if massive else ['C','O']
   for k,(nx,ny) in enumerate([(592,286),(624,365)]):
    pass
    d=ImageDraw.Draw(im);d.text(((nx+27)*s,(ny-8)*s),symbols[k],font=ImageFont.truetype(FONT,int(22*s)),fill=(255,239,193))
  title='恒星内部，物质的成分改变' if t<4.8 else ('部分恒星：进一步生成碳与氧' if not massive else '质量足够大的恒星：进一步制造重元素')
  return label(im,title,'演化阶段切换 · 内部透视示意 · 元素标签非精确分层' if cut else '恒星外观示意 · 非比例',tags)
 if paragraph_id=='P08':
  if t<5.7:
   q=smooth(t/5.7);import materials;im=materials.ejecta(q,'wind').resize((w,h));im=sphere(im,614*s,360*s,(50-38*q)*s,t,color=(.66,.75,1))
   return label(im,'一种结局：逐渐抛出外层','较低质量恒星晚期 · 时间压缩示意')
  if t<11.8:
   q=smooth((t-8.1)/3.7)
   if t<8.1:
    im=starfield(Image.new('RGB',(w,h),(5,8,13)));im=sphere(im,614*s,360*s,110*s,t)
   else:
    import materials
    im=materials.ejecta(q,'supernova').resize((w,h))
   return label(im,'另一颗大质量恒星：超新星爆发','不同恒星、不同结局 · 时间压缩示意')
  import materials
  im=materials.cloud(.06*smooth((t-11.8)/8),0,'enriched').resize((w,h))
  return label(im,'抛出的物质，混入星际气体与尘埃','材料循环示意 · 未来恒星与行星的原料')
 if paragraph_id=='P09':
  if t<10.0:
   q=smooth(t/10);im=galaxy(q,w,h,True)
   dx=2.5*(1-q);dy=.7*(1-q);dz=.2;dep=dy*np.sin(1.04)+dz*np.cos(1.04)
   gx=(.47+dx/(1+.035*dep)/10)*w;gy=(.52+(dy*np.cos(1.04)-dz*np.sin(1.04))/(1+.035*dep)/5.625)*h
   im=stars(im,[(gx,gy,38*s,.9)],seed=623,count=130)
   return label(im,'回到形成历史：汇聚与并合','太阳诞生以前 · 历史机制示意，非精确轨道复原')
  if t<19.3:
   q=(t-10)/9.3;import materials;im=materials.cloud(0,0,'enriched').resize((w,h));im=stars(im,[(470*s,330*s,100*s,max(0,.9-q)),(770*s,350*s,130*s,.15+.5*q)],count=350)
   if q>.3:
    shell=materials.ejecta(smooth((q-.3)/.7),'wind').resize((420,236));a=np.asarray(im).astype(np.float32);b=np.asarray(shell).astype(np.float32);a[215:451,260:680]+=b*.55;im=Image.fromarray(np.uint8(np.clip(a,0,255)))
   return label(im,'一代代恒星，诞生、演化、送回物质','太阳诞生以前 · 多代恒星演化示意')
  import materials
  im=cold_cloud_start().resize((w,h))
  # Material settles without introducing a fully formed star before P10.
  return label(im,'孕育太阳的云团：气体与细小尘粒','太阳诞生以前 · 云团位置不等于今日太阳位置')
 raise ValueError(paragraph_id)

def render_insert(local_progress,w=1280,h=720):
 width,height=w,h
 """Extra 8 s reading insert between P08/P09; never consumes narration time."""
 p=float(np.clip(local_progress,0,1));zoom=1+.20*smooth((p-.3)/.5);im=galaxy(0,width,height,zoom=zoom)
 # In this model a stellar disk radius 15 kpc spans 4.25 model units; R_sun≈8 kpc.
 # Sun is in near-side disk, well outside bulge, not an invented exact spiral-arm point.
 s=width/1280;sunx=601*s;suny=586*s
 # Remain above reserved subtitle band by original scene composition shift of marker.
 depth=1.6*np.sin(1.04);sunx=(.47+1.6*zoom/(1+.035*zoom*depth)/10)*width;suny=(.52+1.6*np.cos(1.04)*zoom/(1+.035*zoom*depth)/5.625)*height
 if p<.34:
  im=label(im,'今日空间定位：银河系属于本星系群','棒旋结构艺术示意 · 非精确旋臂地图')
  return im
 d=ImageDraw.Draw(im);d.ellipse((sunx-5*s,suny-5*s,sunx+5*s,suny+5*s),fill=(255,219,132))
 d.line([(sunx,suny),(sunx+35*s,suny+28*s),(sunx+45*s,suny+28*s)],fill=(229,205,154),width=max(1,int(s)))
 im=label(im,'今日空间定位：太阳在银河系的星盘中','棒旋结构艺术示意 · 非精确旋臂地图 · 太阳位置为近似盘区',[(849,485,'太阳'),(849,518,'距银心约2.6万光年')])
 d=ImageDraw.Draw(im);d.text((46*s,162*s),'银河系属于本星系群',font=ImageFont.truetype(FONT,int(22*s)),fill=(174,184,194))
 return im

if __name__=='__main__':
 cases={'P05':[1,8.9,13.5,18.0],'P06':[1,6.3,11.7],'P07':[2,8.2,12.0,16.8],'P08':[4.8,6.8,10.3,17.8],'P09':[2,8.5,15,25]}
 import time
 start=time.time()
 for pid,times in cases.items():
  for tt in times:
   out=ROOT/'keyframes'/f'{pid}-{tt:05.2f}.png';render(pid,tt/DUR[pid]).save(out);print(out.name,flush=True)
 for p in [0,.5,1]:render_insert(p).save(ROOT/'keyframes'/f'G25-{p:.1f}.png')
 print('seconds',time.time()-start)

import ctypes
_native=ctypes.CDLL(str(ROOT/'galaxy_native.so'))
_native.galaxy_render.argtypes=[np.ctypeslib.ndpointer(dtype=np.float32,flags='C_CONTIGUOUS'),np.ctypeslib.ndpointer(dtype=np.float32,flags='C_CONTIGUOUS'),ctypes.c_int,ctypes.c_int,ctypes.c_double,ctypes.c_int,ctypes.c_double,ctypes.c_int]
_native.galaxy_render.restype=None
def galaxy_fast(phase=0,w=1280,h=720,history=False,zoom=1,threads=3):
 acc=np.zeros((h,w,3),np.float32)
 _native.galaxy_render(noisegrid(),acc,w,h,float(phase),int(history),float(zoom),threads)
 return _galaxy_finish(acc,w,h,zoom)

# Exact-state cache. Moving frames retain all 24 fps state samples; no time quantization.
import threading
_native_lock=threading.Lock()
galaxy_reference=galaxy
@lru_cache(maxsize=8)
def _galaxy_exact_cache(phase,w,h,history,zoom):
 with _native_lock:return galaxy_fast(phase,w,h,history,zoom,threads=3)
def galaxy(phase=0,w=1280,h=720,history=False,zoom=1):
 return _galaxy_exact_cache(float(phase),w,h,bool(history),float(zoom)).copy()
@lru_cache(maxsize=1)
def cold_cloud_start():
 import materials
 return materials.cloudbase.render(0)
