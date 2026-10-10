"""P01–P09. Authored, schematic cosmic evolution illustrations; not simulations.
Native 1280x720; every frame seekable, deterministic. Public render API below.
"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from functools import lru_cache
import math
W,H=1280,720
FONT=None  # Configured by the explicit local CLI before rendering.
BOLD=None
WHITE=(238,229,207); GOLD=(235,177,91); TEAL=(117,201,199); MUTED=(147,146,143)
RNG=np.random.default_rng(735)
POINTS=RNG.random((800,5))
@lru_cache(None)
def font(s,b=False): return ImageFont.truetype(BOLD if b else FONT,s)
def ease(t): return max(0,min(1,t))**2*(3-2*max(0,min(1,t)))
def mix(a,b,t): return tuple(int(x*(1-t)+y*t) for x,y in zip(a,b))
def label(d,xy,s,size=22,color=WHITE,anchor=None,b=False): d.text(xy,s,font=font(size,b),fill=color,anchor=anchor)
def line(d,xy,col=GOLD,width=2):d.line(xy,fill=col,width=width)
def arrow(d,a,b,c=GOLD,w=2):
 d.line([a,b],fill=c,width=w); v=math.atan2(b[1]-a[1],b[0]-a[0]); q=10
 d.polygon([b,(b[0]-q*math.cos(v-.45),b[1]-q*math.sin(v-.45)),(b[0]-q*math.cos(v+.45),b[1]-q*math.sin(v+.45))],fill=c)
@lru_cache(None)
def glow(r,color):
 r=int(r);y,x=np.mgrid[-r:r+1,-r:r+1];rr=(x*x+y*y)/(r*r);a=np.exp(-rr*5.8)*(1-np.minimum(1,rr))
 z=np.zeros((2*r+1,2*r+1,4),np.uint8);z[:,:,:3]=color;z[:,:,3]=(a*230).astype('uint8');return Image.fromarray(z,'RGBA')
def light(im,x,y,r,color=GOLD):
 g=glow(max(2,int(r)),color);im.paste(g,(int(x-r),int(y-r)),g)
def star(im,x,y,r=2,c=WHITE):
 light(im,x,y,max(8,int(r*9)),c);d=ImageDraw.Draw(im);d.ellipse((x-r,y-r,x+r,y+r),fill=c)
 if r>3: d.line((x-r*3,y,x+r*3,y),fill=mix(c,(15,15,18),.45),width=1); d.line((x,y-r*3,x,y+r*3),fill=mix(c,(15,15,18),.45),width=1)
@lru_cache(None)
def background(kind):
 y,x=np.mgrid[0:H:2,0:W:2];xx=x/W;yy=y/H
 # Multiple nonperiodic warped filaments, baked once. No blank fog stage.
 n=np.zeros_like(xx,dtype=float)
 for k in range(1,8): n+=np.sin(xx*(k*7.1)+np.cos(yy*k*4.3)+k)*np.cos(yy*k*5.8-xx*k*2.4)/k
 n=(n-n.min())/(n.max()-n.min()); n=n**2
 if kind=='hot':
  a=np.stack([36+125*n,17+63*n,14+25*n],axis=-1)
 elif kind=='cloud':
  belt=np.exp(-((yy-.47-.10*np.sin(xx*7))/.26)**2);a=np.stack([7+72*n*belt,9+47*n*belt,12+30*n*belt],axis=-1)
 elif kind=='dark': a=np.stack([5+10*n,7+11*n,10+14*n],axis=-1)
 else:a=np.stack([7+22*n,8+19*n,11+19*n],axis=-1)
 im=Image.fromarray(np.uint8(a)).resize((W,H),Image.Resampling.BILINEAR)
 return im

def field(im,t=0,count=300,brightness=1):
 d=ImageDraw.Draw(im)
 for x,y,r,q,z in POINTS[:count]:
  px=(x*W+t*(z-.5)*12)%W;py=y*H;v=int((50+145*q)*brightness);rad=.5+1.3*r
  d.ellipse((px-rad,py-rad,px+rad,py+rad),fill=(v,v,int(v*.94)))

def nucleus(d,x,y,kind='H',scale=1):
 r=6*scale
 if kind=='He':
  for dx,dy,c in [(-3,-3,GOLD),(3,3,GOLD),(-3,3,TEAL),(3,-3,TEAL)]:d.ellipse((x+dx*scale-r,y+dy*scale-r,x+dx*scale+r,y+dy*scale+r),fill=c)
 else:d.ellipse((x-r,y-r,x+r,y+r),fill=GOLD)

def atom(d,x,y,t=0,kind='H',r=35,neutral=True):
 if neutral:
  d.ellipse((x-r,y-r*.48,x+r,y+r*.48),outline=(75,103,108),width=1)
  ex=x+math.cos(t)*r;ey=y+math.sin(t)*r*.48;d.ellipse((ex-3,ey-3,ex+3,ey+3),fill=TEAL)
 nucleus(d,x,y,kind)

def cloud_particles(im,t,cx=640,cy=340,scale=1,count=280,ignite=0):
 d=ImageDraw.Draw(im)
 for u,v,r,q,z in POINTS[:count]:
  a=u*math.tau*3;rad=(v**.6)*430*scale;px=cx+math.cos(a)*rad*(.5+.5*z);py=cy+math.sin(a)*rad*.52
  rr=1+3*r;c=mix((55,48,40),(193,147,90),q*.75);d.ellipse((px-rr,py-rr,px+rr,py+rr),fill=c)
 if ignite>0:star(im,cx,cy,3+10*ignite,(255,228,163))


def p01(t):
 im=background('hot').copy();d=ImageDraw.Draw(im)
 # Tiny charged matter symbols; expressly no astronomical stars.
 for x,y,r,q,z in POINTS[:95]:
  px=(x*W+20*t*(z-.5))%W;py=(y*H+15*t*(q-.5))%H;rr=2+3*r
  d.ellipse((px-rr,py-rr,px+rr,py+rr),outline=mix((181,74,35),(255,205,129),q),width=1)
  d.line((px-rr*.55,py,px+rr*.55,py),fill=(225,142,80),width=1)
 label(d,(135,168),'约 138 亿年前',40,b=True)
 label(d,(138,230),'炽热、稠密的早期宇宙',25)
 line(d,[(139,285),(440,285)],(176,104,63),2)
 label(d,(138,311),'尚无恒星',25);label(d,(138,354),'尚无岩石',25)
 label(d,(840,478),'早期物质示意',18,MUTED)
 return im

def p02(t):
 im=background('hot').copy(); cooling=ease(t);im=Image.blend(im,background('dark'),cooling*.65);d=ImageDraw.Draw(im)
 s=110*(1+.8*t);ox=640;oy=330
 for i in range(-8,9):
  x=ox+i*s;y=oy+i*s
  d.line((x,100,x,560),fill=(88,66,54));d.line((30,y,1250,y),fill=(88,66,54))
 for i in range(-5,6):
  for j in range(-2,3):
   x=ox+i*s;y=oy+j*s
   if 20<x<1260 and 110<y<550:d.ellipse((x-3,y-3,x+3,y+3),fill=TEAL)
 # Representative light scattering track, changing collision endpoints.
 path=[(120,400),(235,245),(330,407),(450,295),(535,430),(640,330),(745,410),(830,290),(960,390),(1090,220)]
 d.line(path,fill=(235,179,95),width=3)
 k=(t*2.7)%1*(len(path)-1);i=int(k);f=k-i;a,b=path[i],path[min(i+1,len(path)-1)];star(im,a[0]*(1-f)+b[0]*f,a[1]*(1-f)+b[1]*f,4,GOLD)
 d=ImageDraw.Draw(im)
 for x,y in path[1:-1]: d.ellipse((x-7,y-7,x+7,y+7),fill=TEAL)
 label(d,(96,128),'空间膨胀',30,b=True);label(d,(810,130),'光与自由电子不断散射',23)
 # Physical proper separation of comoving marks, no camera motion.
 arrow(d,(640,500),(640+s,500),TEAL);line(d,[(640,490),(640,510)],TEAL);label(d,(640+s/2,515),'同一对标记点的距离增大',18,TEAL,'mt')
 return im

def p03(t):
 im=background('dark').copy();d=ImageDraw.Draw(im);bind=ease((t-.15)/.45)
 label(d,(93,122),'约 38 万年后',31,b=True)
 label(d,(93,169),'电子与原子核结合',23)
 for k,(x,y) in enumerate([(220,310),(470,280),(720,345),(1020,270),(380,458),(880,456)]):
  atom(d,x,y,t*4+k,neutral=bind>.6)
  if bind<.97:
   ex=x+90*(1-bind)*math.cos(k+2*t)+30*bind;ey=y-65*(1-bind)+15*bind
   d.ellipse((ex-5,ey-5,ex+5,ey+5),fill=TEAL);line(d,[(ex-8,ey),(ex+8,ey)],WHITE)
 if t<.48:
  pts=[(45,355),(220,310),(380,458),(470,280),(720,345),(880,456),(1020,270),(1230,355)];d.line(pts,fill=(180,145,92),width=2)
 else:
  for k,y in enumerate([250,390,495]):
   arrow(d,(35,y),(1220,y+15),mix((70,61,46),GOLD,bind),2)
   x=(t*1300+k*375)%1280;light(im,x,y+x/1280*15,18,GOLD)
 d=ImageDraw.Draw(im);label(d,(765,143),'中性原子形成后，光可自由传播',22,WHITE)
 label(d,(110,516),'粒子与光路示意 · 非真实尺度',17,MUTED)
 return im

def p04(t):
 im=background('dark').copy();d=ImageDraw.Draw(im)
 for k,(x,y,r,q,z) in enumerate(POINTS[:38]):
  px=70+x*605;py=225+y*225;kind='He' if k%5==0 else 'H';atom(d,px,py,t*2+k,kind,24)
 label(d,(100,121),'恒星出现以前',31,b=True)
 label(d,(190,480),'H   氢',30,GOLD);label(d,(450,480),'He   氦',30,TEAL)
 if t>.30:
  alpha=ease((t-.3)/.3);c=mix((10,12,17),WHITE,alpha)
  label(d,(765,182),'岩石还需要……',23,c)
  for i,s in enumerate(['O   氧','Si   硅','Fe   铁']):label(d,(855,242+i*57),s,28,mix((10,12,17),MUTED,alpha))
  label(d,(765,443),'等待后来的恒星制造',22,c)
 return im

def p05(t):
 im=background('cloud').copy();con=ease(t/.68);cx,cy=515,335;light(im,cx,cy,250,(99,66,39));cloud_particles(im,t,cx,cy,1-.65*con,280,ease((t-.46)/.35))
 d=ImageDraw.Draw(im);label(d,(85,127),'引力使较密的气体继续聚拢',28,b=True)
 for a in [0,.8,2.1,3.2,4.3,5.3]:
  r=245-40*con;arrow(d,(cx+math.cos(a)*r,cy+math.sin(a)*r*.62),(cx+math.cos(a)*(r-52),cy+math.sin(a)*(r-52)*.62),(157,120,77),2)
 if t<.55:label(d,(825,259),'收缩',32,GOLD);label(d,(825,309),'中心升温',25)
 else:
  label(d,(827,240),'核聚变点燃',29,GOLD,b=True)
  nucleus(d,850,321,'H',1.1);nucleus(d,878,321,'H',1.1);nucleus(d,850,349,'H',1.1);nucleus(d,878,349,'H',1.1);arrow(d,(913,335),(993,335));nucleus(d,1042,335,'He',1.4)
  label(d,(837,378),'氢核',23);label(d,(1020,378),'氦核',23);label(d,(827,438),'释放能量，维持恒星发光',21);label(d,(827,477),'融合过程简化示意',17,MUTED)
 return im

def cluster(im,cx,cy,s,t,seedoff=0,n=100):
 light(im,cx,cy,int(s*1.5),(119,92,70))
 for u,v,r,q,z in POINTS[seedoff:seedoff+n]:
  a=u*math.tau;rad=v**1.2*s;x=cx+math.cos(a)*rad*(.7+z*.3);y=cy+math.sin(a)*rad*.58
  if q>.7:star(im,x,y,1.2+1.5*r,(243,225,191))
  else:
   d=ImageDraw.Draw(im);rr=.7+r;d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(119+int(q*75),116+int(q*60),109+int(q*50)))

def p06(t):
 im=background('space').copy();field(im,t,210,.7)
 for i,(x,y,s) in enumerate([(345,318,185),(777,287,125),(920,454,105),(556,488,80)]):cluster(im,x+(640-x)*t*.08,y,s*(.7+.3*t),t,i*100,100)
 # Distinct irregular clusters, birth in gas knots.
 for i,(x,y) in enumerate([(299,277),(397,350),(792,277),(900,461)]):star(im,x,y,2+3*ease((t-i*.15)/.35),(244,215,167))
 d=ImageDraw.Draw(im);label(d,(90,127),'最初几亿年',31,b=True);label(d,(744,146),'第一批恒星 · 早期星系',24)
 label(d,(117,500),'恒星在不规则的气体聚集区中诞生',22)
 return im

@lru_cache(None)
def layered_star(stage=2):
 r=192;y,x=np.mgrid[-r:r+1,-r:r+1];rr=np.sqrt(x*x+y*y);z=np.sqrt(np.clip(1-(rr/r)**2,0,1));lightness=.43+.47*z+.22*(-x/r)-.10*y/r
 col=np.zeros((2*r+1,2*r+1,4),np.uint8)
 layers=[(188,(160,61,23)),(143,(212,105,38))]
 if stage==2:layers += [(92,(230,161,84)),(47,(254,228,170))]
 for rad,c in layers:
  mask=rr<=rad
  for j,v in enumerate(c):col[:,:,j][mask]=np.clip(v*lightness[mask],0,255).astype('uint8')
 col[:,:,3]=(rr<=188)*255
 return Image.fromarray(col,'RGBA')

def p07(t):
 im=background('space').copy();field(im,t,160,.45);cx,cy=550,339
 # Schematic concentric composition zones; intentionally not claimed to be a scale model.
 stages=[(188,(124,49,25),'H / He'),(143,(192,89,35),'C / O'),(92,(213,138,65),'Si'),(47,(238,209,148),'Fe')]
 light(im,cx,cy,260,(182,90,40));d=ImageDraw.Draw(im)
 late=ease((t-.4)/.28);sp=Image.blend(layered_star(1),layered_star(2),late);im.paste(sp,(cx-192,cy-192),sp);d=ImageDraw.Draw(im)
 for r,col,s in stages[:2]:d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=mix(col,WHITE,.15),width=1)
 # Thin interior convection-like arcs to show living structure.
 for r in [115,164]:d.arc((cx-r,cy-r,cx+r,cy+r),int(t*70),int(t*70)+210,fill=(211,151,87),width=2)
 label(d,(83,122),'恒星内部，元素继续生成',29,b=True)
 for y,r,s in [(211,164,'氢、氦'),(279,120,'碳、氧'),(365,69,'硅'),(419,20,'铁')]:
  if s in ['硅','铁'] and t<.45:continue
  sy=cy+min(max(y-cy,-r*.65),r*.65);end=(cx+math.sqrt(max(0,r*r-(sy-cy)**2)),sy);line(d,[end,(785,sy),(810,y),(823,y)],(167,157,135));label(d,(843,y-17),s,26)
 label(d,(821,478),'硅、铁：需质量足够大的恒星' if t>=.45 else '一部分恒星进一步生成碳、氧',19,GOLD)
 label(d,(103,517),'演化晚期大质量恒星分层示意 · 非比例',17,MUTED)
 return im

def p08(t):
 im=background('space').copy();field(im,t,160,.6);d=ImageDraw.Draw(im)
 label(d,(89,120),'恒星把物质送回星际空间',29,b=True)
 # Two distinct mechanisms, not one flash. Particles continuously move into gas.
 for which,cx in enumerate([330,883]):
  cy=345;exp=(t*.8+.18);r0=55+exp*(112 if which==0 else 164)
  light(im,cx,cy,185,(87,49,29));d=ImageDraw.Draw(im)
  for k in range(4):
   r=r0-k*17;col=mix((14,15,19),(161,95,54),max(0,(1-k*.17)*(1-.30*t)))
   # Expanding irregular broken gas shells, not planetary orbital tracks.
   for seg in range(3):
    pts=[]
    for j in range(24):
     a=seg*math.tau/3+j/24*1.81;rad=r*(1+.07*math.sin(a*7+k)+.035*math.cos(a*13+k));pts.append((cx+math.cos(a)*rad,cy+math.sin(a)*rad*.60))
    d.line(pts,fill=col,width=3)
  for u,v,r,q,z in POINTS[which*110:which*110+110]:
   a=u*math.tau;rad=(40+v*125)*( .4+exp);px=cx+math.cos(a)*rad;py=cy+math.sin(a)*rad*.63;rr=1+2*r;d.ellipse((px-rr,py-rr,px+rr,py+rr),fill=mix((89,69,54),GOLD,q))
  star(im,cx,cy,5 if which==0 else 2,(255,222,167))
  if which==1:
   d=ImageDraw.Draw(im)
   for a in [0,.6,1.8,2.7,3.4,4.7,5.7]:arrow(d,(cx+math.cos(a)*70,cy+math.sin(a)*50),(cx+math.cos(a)*r0,cy+math.sin(a)*r0*.65),(181,126,68))
 d=ImageDraw.Draw(im);label(d,(225,177),'逐渐抛出外层',25);label(d,(773,177),'大质量恒星：超新星',25)
 label(d,(367,489),'新元素进入星际气体与尘埃',25,GOLD)
 if t>.58:
  for i,(s,x,y) in enumerate([('C',140,380),('O',515,345),('Si',680,391),('Fe',1105,351)]):
   label(d,(x,y),s,23,mix((13,13,18),GOLD,ease((t-.58)/.2)))
 return im

def p09(t):
 if t<.53:
  q=ease(t/.53);im=background('space').copy();field(im,t,240,.6)
  cluster(im,565,345,230,t,0,210)
  cluster(im,1040-260*q,205+80*q,110,t,290,100)
  cluster(im,230+170*q,458-70*q,90,t,440,90)
  d=ImageDraw.Draw(im);label(d,(82,127),'银河系在汇聚与合并中成长',28,b=True)
  arrow(d,(962-220*q,242+65*q),(806-100*q,284+30*q),(131,123,107))
  label(d,(120,506),'恒星诞生、演化，反复改变星际物质',22)
 else:
  q=ease((t-.53)/.47);im=background('cloud').copy();field(im,t,125,.4);cloud_particles(im,t,590,345,1.12,450,0)
  # Newly-made elements mix through the cloud; no Sun or planet exists yet.
  d=ImageDraw.Draw(im);label(d,(84,127),'太阳诞生以前',30,b=True);label(d,(85,176),'前代恒星留下的物质，混入新的云团',23)
  for i,(s,x,y) in enumerate([('C',320,318),('O',505,445),('Si',775,285),('Fe',865,447)]):
   x=x+(590-x)*q*.18;y=y+(345-y)*q*.18;d.ellipse((x-23,y-23,x+23,y+23),outline=(133,105,68),width=1);label(d,(x,y),s,20,GOLD,'mm')
  label(d,(107,507),'地球的材料：气体与细小尘粒',23,GOLD)
 return im

FUNCS={f'P{i:02}':globals()[f'p{i:02}'] for i in range(1,10)}
def render(paragraph_id,local_progress,width=1280,height=720):
 t=float(np.clip(local_progress,0,1));im=FUNCS[paragraph_id](t).convert('RGB')
 return im if (width,height)==(W,H) else im.resize((width,height),Image.Resampling.LANCZOS)

