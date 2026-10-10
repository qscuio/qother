"""P10 2.5D formation schematic; deterministic material trajectories."""
import math,time,json,subprocess,argparse
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import gaussian_filter,zoom,map_coordinates
# Import has no filesystem writes, network calls, or private asset loading.
W,H,FPS,DURATION=1280,720,24,28
rng=np.random.default_rng(7241)
noise=np.zeros((512,512))
for n,w in [(8,.42),(24,.48),(64,.10),(160,.00)]:noise+=zoom(rng.normal(size=(n,n)),512/n,order=1)[:512,:512]*w
noise=(noise-noise.mean())/noise.std()
m=6400000
x=rng.uniform(-1.15,1.15,m);y=rng.uniform(-1.15,1.15,m);r=np.hypot(x,y)
tex=map_coordinates(noise,[(y+1.15)/2.3*511,(x+1.15)/2.3*511],order=1)
density=np.clip(1-r/1.15,0,1)**.7*np.clip(np.exp(tex*.9)/3,0,1)
sel=rng.random(m)<density;x=x[sel];y=y[sel];r=r[sel]
# Thick and irregular at birth; the very same z coordinates settle to a thin disk.
z=rng.normal(size=len(x))*(.12+.10*r)+.21*np.sin(x*5)*np.cos(y*4)
z=.40*np.tanh(z/.40) # Bound the initial cloud envelope; retain its uneven lobes.
weights=.25*rng.uniform(.5,1.6,len(x))*(.5+.5*(1-r/1.2))
accretes=rng.random(len(x))<.73
arrival=11+13*np.clip(r/1.15,0,1)+rng.uniform(-1,2,len(x))
# Only nearby pre-existing disk material gathers into small irregular clumps.
clump_centers=np.array([[.43,.18],[-.29,.39],[-.58,-.18],[.12,-.59],[.65,-.13]])
dsq=(x[:,None]-clump_centers[:,0])**2+(y[:,None]-clump_centers[:,1])**2
cid=dsq.argmin(axis=1);cw=np.exp(-dsq.min(axis=1)/(.095**2))*(~accretes)
stars=[(int(rng.uniform(0,W)),int(rng.uniform(0,H)),float(rng.uniform(.12,.6))) for _ in range(88)]
font=None;host=None;f16=f24=f14=None
mask=Image.new('L',(166,166));ImageDraw.Draw(mask).ellipse((0,0,165,165),fill=255)
def configure(host_image=None,font_path=None):
 global font,host,f16,f24,f14
 candidates=[Path(font_path)] if font_path else [Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'),Path('/System/Library/Fonts/PingFang.ttc'),Path('C:/Windows/Fonts/msyh.ttc')]
 font=next((str(p) for p in candidates if p.is_file()),None)
 if not font:raise ValueError('Supply --font with an installed Chinese-capable font')
 f16=ImageFont.truetype(font,16);f24=ImageFont.truetype(font,24);f14=ImageFont.truetype(font,14)
 host=Image.open(host_image).convert('RGB').resize((166,166),Image.Resampling.LANCZOS) if host_image else None

YY,XX=np.mgrid[:H,:W]; CX,CY=603,379
rad=((XX-CX)/770)**2+((YY-CY)/530)**2
bg=np.zeros((H,W,3),np.float32);bg[:]=[3,6,8];bg+=np.exp(-rad*2)[...,None]*[4,5,5]
for sx,sy,sv in stars:bg[sy,sx]=np.array([115,136,145])*sv
rr=np.hypot(XX-CX,YY-CY)
# Cache only time-independent screen geometry; same float64 expressions/order.
INCL=math.radians(18)
CUTS=np.linspace(1.8,-1.8,13)
DISKDIST=np.hypot((XX-CX)/452,(YY-CY)/(452*math.sin(INCL)))
LIGHT=np.exp(-DISKDIST*3.6)
RIDGE_BASE=np.exp(-((YY-CY-12)/12)**2)*np.exp(-((XX-CX)/210)**4)
def smooth(a):
 a=np.clip(a,0,1);return a*a*(3-2*a)
def state(t):
 flatten=smooth((t-3)/10);contract=smooth(t/20)
 radial=1.08-.24*contract
 # Every infalling point reaches central reservoir continuously; nothing is spawned.
 infall=smooth((t-5)/(arrival-5))*accretes
 remain=1-infall
 gather=smooth((t-19)/9)*cw*.79
 bx=x+(clump_centers[cid,0]-x)*gather
 by=y+(clump_centers[cid,1]-y)*gather
 theta=-.022*t-.00095*t*t-.35*infall
 xx=(bx*np.cos(theta)-by*np.sin(theta))*radial*remain
 yy=(bx*np.sin(theta)+by*np.cos(theta))*radial*remain
 zz=z*(1-.975*flatten)*radial*remain
 # Weight transfers only inside unresolved center, not by arbitrary global fade.
 transfer=smooth((infall-.92)/.08)
 live=weights*(1-transfer);central=float(np.sum(weights*transfer)/np.sum(weights))
 return xx,yy,zz,live,central

def render(t):
 xx,yy,zz,ww,central=state(t)
 # Artistic opacity is separate from the conserved material ledger.
 # Shrinking point support must not turn infall lanes into opaque paint.
 infall=smooth((t-5)/(arrival-5))*accretes
 ww=ww*(1-infall)**1.7
 az=math.radians(4*smooth((t-18)/10));xx,yy=xx*np.cos(az)-yy*np.sin(az),xx*np.sin(az)+yy*np.cos(az)
 incl=INCL;vertical=yy*np.sin(incl)+zz*np.cos(incl);depth=yy*np.cos(incl)-zz*np.sin(incl)
 persp=4.5/(4.5+depth);sx=CX+xx*452*persp;sy=CY-vertical*452*persp
 valid=(sx>1)&(sx<W-2)&(sy>1)&(sy<H-2)&(ww>0)
 sx=sx[valid];sy=sy[valid];dd=depth[valid];ww=ww[valid]
 out=bg.copy(); cuts=CUTS;core_done=False
 light=LIGHT
 heat=smooth((t-7)/17)
 rgb_base=np.empty_like(out);rgb_base[:,:,0]=142+light*(20+63*heat);rgb_base[:,:,1]=128+light*(16+53*heat);rgb_base[:,:,2]=107+light*(10+35*heat)
 rgb_base64=np.empty((H,W,3),np.float64);rgb_base64[:,:,0]=142+light*(20+63*heat);rgb_base64[:,:,1]=128+light*(16+53*heat);rgb_base64[:,:,2]=107+light*(10+35*heat)
 ridge=RIDGE_BASE*smooth((t-9)/8)
 ridge_factor=1-.40*ridge[...,None]
 opacity_scale=1.25+.40*smooth(t/23)
 for k in range(12):
  mid=(cuts[k]+cuts[k+1])/2
  if not core_done and mid<0:
   lum=smooth(central/.55)
   glow=(np.exp(-(rr/(20+lum*15))**1.25)*.65+np.exp(-(rr/8)**2)*.7)*lum
   out=np.minimum(255,out+glow[...,None]*[255,208,148]);core_done=True
  depth_weight=np.clip(1-np.abs(dd-mid)/.30,0,1);choose=depth_weight>0;px=sx[choose];py=sy[choose];wt=ww[choose]*depth_weight[choose]
  layer=np.zeros((H,W),np.float32);ix=px.astype(int);iy=py.astype(int);fx=px-ix;fy=py-iy
  bins=iy*W+ix
  counts=np.zeros(H*W,dtype=np.float64)
  for dx,dy,q in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:
   counts+=np.bincount(bins+dy*W+dx,weights=wt*q,minlength=H*W)
  layer=counts.reshape(H,W).astype(np.float32)
  soft=gaussian_filter(layer,1.8)*.86+gaussian_filter(layer,4.5)*.14;opacity=1-np.exp(-soft*opacity_scale)
  rgb=(rgb_base64 if out.dtype == np.float64 else rgb_base).copy()
  rgb*=(1.0+.22*math.tanh(mid*2.3))
  # Camera-facing dust gives a dark narrow near-side ridge, only where material exists.
  if mid<0:rgb*=ridge_factor
  out=out*(1-opacity[...,None])+rgb*opacity[...,None]
 im=Image.fromarray(np.clip(out,0,255).astype(np.uint8));d=ImageDraw.Draw(im)
 d.text((45,34),'地球往事  /  太阳系的形成',font=f16,fill=(174,174,162))
 title='云团开始收缩' if t<5 else ('转动，聚拢，形成扁平的盘' if t<13 else '中央孕育太阳，盘中物质继续聚集')
 d.text((45,65),title,font=f24,fill=(226,221,204))
 d.text((45,682),'形成过程示意 · 时间压缩 · 非比例',font=f14,fill=(149,151,142))
 if host is not None:im.paste(host,(1081,527),mask)
 return im

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--output',type=Path,required=True)
 ap.add_argument('--time',type=float,default=12,help='Model time in seconds, 0..28')
 ap.add_argument('--font',type=Path)
 ap.add_argument('--host-image',type=Path,help='Optional authorized pre-cropped square portrait; not bundled')
 args=ap.parse_args()
 if not 0<=args.time<=28:ap.error('--time must be 0..28')
 args.output.mkdir(parents=True,exist_ok=False)
 configure(args.host_image,args.font)
 start=time.perf_counter();render(args.time).save(args.output/'scene-frame.png')
 (args.output/'scene-frame-metrics.json').write_text(json.dumps({'model_time':args.time,'width':W,'height':H,'anchors':len(x),'render_and_save_seconds':time.perf_counter()-start,'host_enabled':host is not None},indent=2))
