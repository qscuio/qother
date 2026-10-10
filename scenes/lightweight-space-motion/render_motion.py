"""Deterministic 2.5D dust point layers; analytic projection, no mesh/volume tracing."""
import numpy as np, math,time,subprocess,json,argparse,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
from scipy.ndimage import gaussian_filter,zoom,map_coordinates
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True, help='Fresh or empty output directory; never overwrites an existing render.')
parser.add_argument('--host-image', type=Path, help='Optional owned/authorized portrait. Omitted by default; no character is bundled.')
parser.add_argument('--font', type=Path, help='Optional Chinese-capable TTF/TTC/OTF font.')
group=parser.add_mutually_exclusive_group()
group.add_argument('--preview', action='store_true', help='Render only frame 36.')
group.add_argument('--frame', type=int, choices=range(144), metavar='0..143', help='Render one specific frame.')
args=parser.parse_args()
O=args.output
if O.exists() and any(O.iterdir()):
 parser.error('--output must be a fresh or empty directory')
if args.host_image and not args.host_image.is_file():
 parser.error('--host-image does not exist')
O.mkdir(parents=True,exist_ok=True)
W,H=1280,720; FPS=24; N=144
rng=np.random.default_rng(7241)
# Fixed multiscale world-space density; no per-frame noise or generated images.
noise=np.zeros((512,512))
for n,w in [(8,.40),(24,.30),(64,.20),(160,.10)]:
 small=rng.normal(size=(n,n));noise+=zoom(small,512/n,order=1)[:512,:512]*w
noise=(noise-noise.mean())/noise.std()
m=1600000
x=rng.uniform(-1.15,1.15,m);y=rng.uniform(-1.15,1.15,m);r=np.hypot(x,y)
tex=map_coordinates(noise,[(y+1.15)/2.3*511,(x+1.15)/2.3*511],order=1)
density=np.clip((1-r/1.15),0,1)**.7*np.clip(np.exp(tex*.9)/3,0,1)
sel=rng.random(m)<density
x=x[sel];y=y[sel];r=r[sel]
z=rng.normal(size=len(x))*(.019+.033*r)
weights=rng.uniform(.5,1.6,len(x))*(.5+.5*(1-r/1.2))
# Sparse stars stay screen-fixed; camera-motion test uses the disk as the reference.
stars=[(float(rng.uniform(0,W)),float(rng.uniform(0,H)),float(rng.uniform(.12,.6))) for _ in range(88)]
font=args.font
if font is None:
 for candidate in [Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'),Path('/System/Library/Fonts/PingFang.ttc'),Path('C:/Windows/Fonts/msyh.ttc')]:
  if candidate.is_file():font=candidate;break
if font is None or not font.is_file():
 parser.error('Chinese font unavailable; supply --font with an installed Chinese-capable font')
font=str(font)
f16=ImageFont.truetype(font,16); f22=ImageFont.truetype(font,22);f14=ImageFont.truetype(font,14)
host=ImageOps.fit(Image.open(args.host_image).convert('RGB'),(166,166),method=Image.Resampling.LANCZOS) if args.host_image else None
mask=Image.new('L',(166,166));ImageDraw.Draw(mask).ellipse((0,0,165,165),fill=255)
YY,XX=np.mgrid[:H,:W]; rad=((XX-603)/770)**2+((YY-374)/530)**2
bg=np.zeros((H,W,3),np.float32);bg[:]=[3,6,8];bg+=np.exp(-rad*2)[...,None]*[4,5,5]
for sx,sy,sv in stars:bg[int(sy),int(sx)]=np.array([115,136,145])*sv

def render(f):
 t=f/FPS;phase=min(t/3,1); ease=.5-.5*math.cos(math.pi*phase)
 incl=math.radians(37-6*math.sin(ease*math.pi))
 camaz=math.radians(-12+24*ease)
 theta=-.10*t-camaz
 expansion=1 if t<3 else 1+.15*(.5-.5*math.cos(math.pi*(t-3)/3))
 # Rotation and scale are independent transforms of persistent world points.
 xx=(x*math.cos(theta)-y*math.sin(theta))*expansion
 yy=(x*math.sin(theta)+y*math.cos(theta))*expansion
 vertical=yy*math.sin(incl)+z*math.cos(incl)
 depth=yy*math.cos(incl)-z*math.sin(incl)
 persp=3.8/(3.8+depth)
 sx=603+xx*440*persp; sy=383-vertical*440*persp
 valid=(sx>1)&(sx<W-2)&(sy>1)&(sy<H-2)
 sx=sx[valid];sy=sy[valid];dd=depth[valid];ww=weights[valid]
 out=bg.copy()
 # Far-to-near compositor. Dust surface opacity; not light transport.
 cuts=np.linspace(1.45,-1.45,13)
 core_done=False
 for k in range(12):
  mid=(cuts[k]+cuts[k+1])/2
  if not core_done and mid<0:
   rr=np.hypot(XX-603,YY-383)
   glow=(np.exp(-(rr/36)**1.1)*.55+np.exp(-(rr/10)**2)*.6)
   out=np.minimum(255,out+glow[...,None]*[255,203,134])
   core=(rr<4.7).astype(float);out=out*(1-core[...,None])+core[...,None]*[255,249,222]
   core_done=True
  choose=(dd<=cuts[k])&(dd>cuts[k+1]); px=sx[choose];py=sy[choose];wt=ww[choose]
  layer=np.zeros((H,W),np.float32)
  # Bilinear point splatting prevents pixel hopping.
  ix=px.astype(int);iy=py.astype(int);fx=px-ix;fy=py-iy
  for dx,dy,q in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:np.add.at(layer,(iy+dy,ix+dx),wt*q)
  soft=gaussian_filter(layer,1.85);fine=gaussian_filter(layer,1.0)
  opacity=1-np.exp(-(soft*.58+fine*.012))
  # Prebaked lighting: hot inside, muted dust outside; no view-dependent recalculation.
  dist=np.hypot((XX-603)/440,(YY-383)/(495*max(.25,math.sin(incl))))
  light=np.exp(-dist*2.2)
  rgb=np.empty_like(out);rgb[:,:,0]=88+light*142;rgb[:,:,1]=68+light*114;rgb[:,:,2]=47+light*84
  rgb *= (1.24 if mid>0 else .86)
  out=out*(1-opacity[...,None])+rgb*opacity[...,None]
 im=Image.fromarray(np.clip(out,0,255).astype(np.uint8))
 d=ImageDraw.Draw(im)
 d.text((45,34),'地球往事  /  轻量空间运动测试',font=f16,fill=(174,174,162))
 title='旋转与视差' if t<3 else '径向展开 · 技术演示'
 desc='同一批尘埃点，镜头小角度绕行' if t<3 else '用于测试扩张表现，不代表太阳形成时向外膨胀'
 d.text((45,65),title,font=f22,fill=(226,221,204));d.text((45,101),desc,font=f16,fill=(153,156,148))
 d.text((45,682),'2.5D 分层投影 · 预设明暗 · 非物理模拟',font=f14,fill=(149,151,142))
 if host is not None:im.paste(host,(1081,527),mask)
 return im

if __name__=='__main__':
 if args.preview or args.frame is not None:
  frame=36 if args.preview else args.frame
  started=time.perf_counter()
  render(frame).save(O/f'frame-{frame:03d}.png')
  (O/'single-frame-metrics.json').write_text(json.dumps({'frame':frame,'width':W,'height':H,'particles':len(x),'render_and_save_seconds':round(time.perf_counter()-started,3),'host_enabled':host is not None,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))
  print(f'Saved frame {frame}; host enabled: {host is not None}')
  raise SystemExit(0)
 start=time.time()
 proc=subprocess.Popen(['ffmpeg','-n','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(O/'P10-lightweight-space-test.mp4')],stdin=subprocess.PIPE)
 for f in range(N):
  im=render(f);proc.stdin.write(im.tobytes())
  if f in [0,71,143]:im.save(O/f'keyframe-{f:03d}.png')
  if f%24==0:print(f,round(time.time()-start,1),flush=True)
 proc.stdin.close();assert proc.wait()==0
 (O/'metrics.json').write_text(json.dumps(dict(host_enabled=host is not None,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),width=W,height=H,fps=FPS,frames=N,seconds=N/FPS,particles=len(x),render_seconds=round(time.time()-start,2),method='fixed seeded point sprites, analytic perspective and 12 alpha-composited depth bins; no volumetric integration'),indent=2))
