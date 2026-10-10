"""Authored illustrative Earth/Moon scenes. Deterministic, not a numerical simulation."""
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np, math
from functools import lru_cache
from scipy.ndimage import gaussian_filter
W,H=1280,720
CREAM=(228,220,202); MUTED=(156,158,155); GOLD=(217,155,94); TEAL=(121,173,174)
FONT=None  # Configured by the explicit local CLI before rendering.
@lru_cache(None)
def font(size): return ImageFont.truetype(FONT,size)
def label(d,xy,s,size=24,color=CREAM): d.text(xy,s,font=font(size),fill=color)
def lerp(a,b,t): return a+(b-a)*t
def ease(t): t=max(0,min(1,t));return t*t*(3-2*t)
def arrow(d,a,b,color=GOLD,width=2):
 d.line([a,b],fill=color,width=width); ang=math.atan2(b[1]-a[1],b[0]-a[0]);d.polygon([b,(b[0]-10*math.cos(ang-.45),b[1]-10*math.sin(ang-.45)),(b[0]-10*math.cos(ang+.45),b[1]-10*math.sin(ang+.45))],fill=color)
@lru_cache(None)
def backdrop():
 y,x=np.mgrid[0:H,0:W];r=np.exp(-((x-620)**2/680**2+(y-350)**2/390**2)); a=np.zeros((H,W,3),np.uint8)
 for c,b in enumerate([6,8,12]):a[:,:,c]=b+r*(10 if c!=0 else 14)
 im=Image.fromarray(a);d=ImageDraw.Draw(im);rng=np.random.default_rng(310)
 for x,y,lum in zip(rng.integers(0,W,180),rng.integers(0,H,180),rng.integers(25,105,180)):d.point((int(x),int(y)),fill=(int(lum),)*3)
 return im
@lru_cache(None)
def sphere(kind='earth',variant=0):
 n=512;y,x=np.mgrid[-1:1:complex(n),-1:1:complex(n)];r2=x*x+y*y;z=np.sqrt(np.maximum(0,1-r2));rng=np.random.default_rng(90+variant)
 noise=np.zeros((n,n))
 for sig,amp in [(2,.17),(7,.3),(22,.45),(55,.6)]:
  a=gaussian_filter(rng.random((n,n)),sig);noise+=amp*(a-a.mean())/(a.std()+1e-8)
 noise=(noise-noise.min())/(noise.max()-noise.min());light=np.clip(-.53*x-.45*y+.72*z,0,1);shade=.08+.92*light
 if kind=='sun':
  base=np.stack([230+noise*25,137+noise*80,65+noise*85],2);shade=.65+.35*z
 elif kind=='moon':base=np.stack([104+noise*76,99+noise*72,90+noise*66],2)
 elif kind=='iron':base=np.stack([166+noise*68,88+noise*46,45+noise*25],2)
 else:
  cracks=np.clip((noise-.51)*9,0,1); base=np.stack([48+noise*32+cracks*171,36+noise*20+cracks*66,30+noise*13+cracks*15],2)
  shade=np.maximum(shade,cracks*.67)
 rgb=np.clip(base*shade[:,:,None],0,255).astype('uint8');a=np.where(r2<=1,255,0).astype('uint8');return Image.fromarray(np.dstack([rgb,a]),'RGBA')
def ball(im,xy,r,kind='earth',variant=0):
 r=max(1,int(r));s=sphere(kind,variant).resize((2*r,2*r),Image.Resampling.BILINEAR);im.paste(s,(int(xy[0]-r),int(xy[1]-r)),s)
def dust(d,cx,cy,rx,ry,t,n=180,color=GOLD,seed=19,start=0,end=6.283):
 rng=np.random.default_rng(seed)
 for k in range(n):
  ang=start+(end-start)*rng.random()+t;rad=.65+.35*rng.random();x=cx+rx*rad*math.cos(ang);y=cy+ry*rad*math.sin(ang);rr=rng.choice([1,1,2,2,3]);d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=tuple(int(v*(.5+.5*rng.random())) for v in color))
def disk(im,t,cx=590,cy=342,scale=1):
 d=ImageDraw.Draw(im)
 for rr in range(440,90,-11):
  f=(rr-90)/350;c=tuple(int(v) for v in (lerp(115,35,f),lerp(63,68,f),lerp(34,79,f)))
  d.ellipse((cx-rr*scale,cy-rr*.32*scale,cx+rr*scale,cy+rr*.32*scale),outline=c,width=max(1,int(3*scale)))
 dust(d,cx,cy,420*scale,133*scale,t,370,(161,156,140));ball(im,(cx,cy),55*scale,'sun')
@lru_cache(None)
def rock(seed=1):
 n=330;rng=np.random.default_rng(seed);y,x=np.mgrid[0:n,0:n];no=rng.random((n,n));a=gaussian_filter(no,3);a=(a-a.min())/(a.max()-a.min());shade=np.clip(1.2-.55*x/n-.3*y/n,.3,1)
 rgb=np.stack([(68+115*a)*shade,(67+106*a)*shade,(64+92*a)*shade],2).astype('uint8');im=Image.fromarray(rgb).convert('RGBA');mask=Image.new('L',(n,n));d=ImageDraw.Draw(mask);pts=[(int(165+(115+rng.random()*35)*math.cos(i*math.tau/14)),int(165+(115+rng.random()*35)*math.sin(i*math.tau/14))) for i in range(14)];d.polygon(pts,fill=255);im.putalpha(mask)
 # angular mineral faces, chips and pores
 d=ImageDraw.Draw(im)
 for i in range(85):
  xx=int(rng.integers(50,280));yy=int(rng.integers(50,280));rr=int(rng.integers(1,5));
  if mask.getpixel((xx,yy)):d.ellipse((xx,yy,xx+rr,yy+rr),fill=(48,47,43,255))
 return im

def render(paragraph_id,local_progress,width=1280,height=720):
 p=int(str(paragraph_id).replace('P',''));t=max(0,min(1,float(local_progress)));im=backdrop().copy();d=ImageDraw.Draw(im)
 if p==11:
  disk(im,t*.45);d=ImageDraw.Draw(im)
  label(d,(740,137),'更远处：冰也能保持固态',24,TEAL);label(d,(665,450),'较热的内侧：岩石 · 金属',25,GOLD)
  for i in range(9):
   a=i*.66+t*.25;x=590+365*math.cos(a);y=342+116*math.sin(a);d.polygon([(x,y-5),(x+5,y),(x,y+5),(x-5,y)],fill=(157,189,186))
  arrow(d,(664,224),(1030,224),MUTED);label(d,(706,180),'温度向外降低',22);label(d,(648,188),'热',18,GOLD);label(d,(1020,188),'冷',18,TEAL)
  d.line([(749,436),(738,383)],fill=GOLD,width=2);label(d,(151,483),'示意：不按距离与大小比例',18,MUTED)
 elif p==12:
  if t<.46:
   q=t/.46;u=(q*2)%1;centers=[(290,328),(620,328),(948,328)]
   for i,(cx,cy) in enumerate(centers):
    label(d,(cx-46,170),['黏合','弹开','破碎'][i],27)
    if u<.5:
     gap=lerp(100,17,u*2);ball(im,(cx-gap,cy-7),20,'moon',i);ball(im,(cx+gap,cy+7),18,'moon',i+3)
    elif i==0:ball(im,(cx,cy),25,'moon',2)
    elif i==1:
     gap=lerp(18,100,(u-.5)*2);ball(im,(cx-gap,cy-12-(u-.5)*40),20,'moon',1);ball(im,(cx+gap,cy+12+(u-.5)*40),18,'moon',4)
    else:
     for j in range(12):
      a=j*2.4;r=20+(u-.5)*200;ball(im,(cx+math.cos(a)*r,cy+math.sin(a)*r*.7),4+j%4,'moon',j%4)
   d=ImageDraw.Draw(im);label(d,(403,460),'碰撞 ≠ 每次都能长大',28,GOLD)
  else:
   q=(t-.46)/.54;label(d,(180,137),'局部聚集 → 自引力坍缩',28);label(d,(180,184),'气体与颗粒相互作用：解释之一',22,TEAL)
   for k in range(8):
    yy=250+k*30;d.arc((70-k*10,yy-70,1140+k*10,yy+80),0,180,fill=(35,65,69),width=2)
   rng=np.random.default_rng(811)
   for k in range(270):
    xx=rng.uniform(120,1110);yy=rng.uniform(270,470);f=ease(q);xx=lerp(xx,680+rng.normal(0,30),f);yy=lerp(yy,363+rng.normal(0,30),f);d.ellipse((xx-2,yy-2,xx+2,yy+2),fill=GOLD)
   if q>.7:ball(im,(680,363),lerp(1,57,ease((q-.7)/.3)),'moon',3)
   label(d,(180,496),'最初的生长难关，仍在研究',24,MUTED)
 elif p==13:
  phase=min(2,int(t*3));q=t*3-phase;cx,cy=645,346;base=[68,98,125][phase];end=[98,125,147][phase];r=(base**3+(end**3-base**3)*ease(q))**(1/3);ball(im,(cx,cy),r,'earth',1)
  rng=np.random.default_rng(51+phase)
  for k in range(16):
   ang=rng.uniform(0,math.tau);rr=rng.uniform(r+80,510);rr=lerp(rr,r-5,ease(q));sz=rng.uniform(16,28)
   if rr>r:ball(im,(cx+rr*math.cos(ang),cy+rr*.55*math.sin(ang)),sz,'moon',k%5)
  d=ImageDraw.Draw(im);label(d,(165,150),['小天体彼此碰撞','较大的行星胚胎','年轻地球继续吸积'][phase],29)
  label(d,(165,487),'数千万年：合并增重，也可能抛失物质',25,GOLD)
  if q>.6:
   for k in range(20):
    a=-.9+k*.045;rr=r+(q-.6)*500*(.5+(k%5)/5);x=cx+math.cos(a)*rr;y=cy+math.sin(a)*rr;d.ellipse((x-2,y-2,x+2,y+2),fill=GOLD)
 elif p==14:
  cx,cy,r=620,343,192;ball(im,(cx,cy),r,'earth',1);d=ImageDraw.Draw(im)
  if t<.3:
   q=t/.3;ball(im,(lerp(1040,760,q),lerp(175,267,q)),35,'moon',3);label(d,(177,150),'撞击的动能 → 热',28)
   if q>.75:d.arc((cx-r-7,cy-r-7,cx+r+7,cy+r+7),285,355,fill=(255,183,91),width=7)
  else:
   q=ease((t-.3)/.7);d.pieslice((cx-r,cy-r,cx+r,cy+r),-90,90,fill=(139,69,37));d.pieslice((cx-r+13,cy-r+13,cx+r-13,cy+r-13),-90,90,fill=(181,91,44));core=lerp(46,90,q);d.pieslice((cx-core,cy-core,cx+core,cy+core),-90,90,fill=(244,176,85));d.line((cx,cy-r,cx,cy+r),fill=(241,187,112),width=2)
   for k in range(13):
    a=-1.35+k*.21;rr=lerp(160,core*.7,q);x=cx+math.cos(a)*rr;y=cy+math.sin(a)*rr;d.ellipse((x-4,y-4,x+4,y+4),fill=(249,200,113))
   label(d,(155,153),'熔融后，物质按密度重新分布',27);label(d,(863,290),'岩石外层',25);d.line([(840,311),(776,311)],fill=GOLD,width=2);label(d,(863,388),'富铁金属核',25,GOLD);d.line([(840,410),(691,371)],fill=GOLD,width=2)
   label(d,(164,487),'富铁金属向内迁移',23,GOLD)
 elif p==15:
  sample=rock(1).resize((185,185));im.paste(sample,(200,210),sample);sample=rock(7).resize((155,155));im.paste(sample,(430,225),sample);d=ImageDraw.Draw(im)
  label(d,(213,167),'地球样品',23);label(d,(427,167),'陨石',23);label(d,(678,164),'同位素留下时间信息',26)
  label(d,(680,222),'母体',20,GOLD);label(d,(845,222),'衰变产物',20,TEAL);arrow(d,(741,239),(822,239),MUTED)
  for k in range(24):
   x=690+(k%8)*28;y=282+(k//8)*27;c=GOLD if k>=int(lerp(3,15,t)) else TEAL;d.ellipse((x,y,x+12,y+12),fill=c)
  label(d,(680,381),'原理示意 · 非样品实测数值',18,MUTED)
  x1,x2,yy=162,1117,477;d.line((x1,yy,x2,yy),fill=MUTED,width=2)
  for age in [4.6,4,3,2,1,0]:
   xx=x1+(4.6-age)/4.6*(x2-x1);d.line((xx,yy-6,xx,yy+7),fill=MUTED,width=2);label(d,(xx-13,yy+14),str(age) if age else '今天',18,MUTED)
  xx=x1+.06/4.6*(x2-x1);d.line((xx,yy-31,xx,yy+8),fill=GOLD,width=4);label(d,(193,413),'约 45.4 亿年前：形成的年代',26,GOLD)
  label(d,(729,519),'十亿年前',17,MUTED)
 elif p==16:
  cx,cy=554,346;r=145
  label(d,(154,132),'大碰撞：目前的主流解释',26);label(d,(154,176),'约 45 亿年前 · 机制示意，细节仍在研究',19,MUTED)
  ball(im,(cx,cy),r,'earth',2)
  if t<.35:
   q=t/.35;ball(im,(lerp(1050,666,q),lerp(177,288,q)),72,'earth',4)
   d=ImageDraw.Draw(im)
   if q>.8:
    for k in range(35):
     a=-1.2+k*.035;rr=(q-.8)*700;xx=663+math.cos(a)*rr;yy=275+math.sin(a)*rr*.6;d.ellipse((xx-3,yy-3,xx+3,yy+3),fill=(244,157,73))
  else:
   q=(t-.35)/.65;d=ImageDraw.Draw(im);n=int(lerp(210,35,ease(q)))
   dust(d,cx,cy,360,104,q*1.1,n,(208,151,95),62)
   ball(im,(cx,cy),r,'earth',2);d=ImageDraw.Draw(im)
   dust(d,cx,cy,360,104,0,max(12,n//2),(208,151,95),62,start=0,end=math.pi)
   if q>.36:
    moonr=lerp(3,49,ease((q-.36)/.64));a=-.5+q*.15;mx=cx+350*math.cos(a);my=cy+105*math.sin(a);ball(im,(mx,my),moonr,'earth',5)
   d=ImageDraw.Draw(im);label(d,(173,498),'部分抛出物留在周围，并逐渐聚集',24,GOLD)
 elif p==17:
  if t<.31:
   q=t/.31;s=rock(3).resize((390,390));im.paste(s,(225,156),s);d=ImageDraw.Draw(im)
   label(d,(697,194),'月岩：保留下来的证据',28);label(d,(697,267),'早期高温熔融的记录',25,GOLD);label(d,(697,316),'矿物 · 岩石结构',23,MUTED)
   yy=int(260+130*q);d.line([(396,yy),(655,yy),(675,277)],fill=TEAL,width=2);d.ellipse((388,yy-8,404,yy+8),outline=TEAL,width=2)
  else:
   for seed,xy in [(3,(176,195)),(9,(705,195))]:
    s=rock(seed);im.paste(s,xy,s)
   d=ImageDraw.Draw(im);label(d,(235,140),'月球岩石',28);label(d,(759,140),'地球岩石',28)
   reveal=min(3,1+int((t-.31)/.14))
   for i,s in enumerate(['氧 O','硅 Si','铁 Fe'][:reveal]):
    yy=255+i*64;label(d,(554,yy),s,22,CREAM);d.line([(475,yy+17),(534,yy+17)],fill=TEAL,width=2);d.line([(650,yy+17),(715,yy+17)],fill=TEAL,width=2)
   label(d,(172,502),'部分成分相似，是检验解释的线索' if t<.78 else '怎样的碰撞，能同时解释这些记录？',25,GOLD)
 elif p==18:
  if t<.25:
   q=t/.25;ball(im,(535,357),176,'earth',1);ball(im,(866,270),47,'earth',3);label(d,(163,149),'仍然炽热的地球，与初生的月球',27)
  elif t<.48:
   q=(t-.25)/.23;ball(im,(500,340),95,'sun');d=ImageDraw.Draw(im);dust(d,500,340,100+q*350,75+q*130,q,260,(176,123,85),57);label(d,(165,149),'更早的恒星，制造并释放许多元素',27)
  elif t<.69:
   q=(t-.48)/.21;d=ImageDraw.Draw(im)
   for k in range(18):
    dust(d,610+80*math.sin(k),341+45*math.cos(k),400-q*150,130-q*40,q*.2+k,70,(104,111,115),k)
   label(d,(165,149),'进入星际空间，汇入新的云团',27)
  elif t<.85:
   disk(im,(t-.69)*2);d=ImageDraw.Draw(im);label(d,(165,149),'在年轻太阳周围，再次聚集',27)
  else:
   q=(t-.85)/.15;ball(im,(584,350),165+q*10,'earth',2);ball(im,(869,259),42,'earth',3);d=ImageDraw.Draw(im);label(d,(165,149),'许多材料的历史，比太阳更古老',27)
 elif p==19:
  q=ease(t);cx=lerp(554,613,q);cy=lerp(350,322,q);r=lerp(203,114,q);ball(im,(cx,cy),r,'earth',2);ball(im,(cx+lerp(323,207,q),cy-lerp(87,60,q)),lerp(53,30,q),'earth',3)
 else:raise ValueError(paragraph_id)
 if (width,height)!=(W,H):im=im.resize((width,height),Image.Resampling.LANCZOS)
 return im.convert('RGB')

