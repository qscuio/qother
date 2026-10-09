"""Earthstory original vector-paper animation. Deterministic, audio-cued renderer.
Only intact guide is a raster asset. All science scenes are original drawn diagrams.
"""
from PIL import Image, ImageDraw, ImageFont
import math, random, json, subprocess, os, argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parent
W,H,FPS=1280,720,24
PAPER='#E9DFC7'; INK='#403A31'; OCHRE='#A8754F'; GREEN='#69765A'; LIGHT='#F5EDD8'; MUTED='#AD9B7A'; DARK='#292923'; GOLD='#C89F65'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD='/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'
fonts={}
def font(sz,b=False):
 k=(sz,b)
 if k not in fonts: fonts[k]=ImageFont.truetype(BOLD if b else FONT,sz)
 return fonts[k]
def txt(d,xy,s,size=24,color=INK,b=False,anchor=None): d.text(xy,s,font=font(size,b),fill=color,anchor=anchor)
def ease(x): x=max(0,min(1,x));return x*x*(3-2*x)
def lerp(a,b,x):return a+(b-a)*x
def ell(d,x,y,rx,ry,c,outline=None,width=1):d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=c,outline=outline,width=width)
def line(d,pts,c=INK,w=2):d.line(pts,fill=c,width=w,joint='curve')
def poly(d,pts,c,outline=None):d.polygon(pts,fill=c,outline=outline)
def arrow(d,a,b,c=INK,w=2):
 line(d,[a,b],c,w);an=math.atan2(b[1]-a[1],b[0]-a[0]);q=9
 poly(d,[b,(b[0]-q*math.cos(an-.45),b[1]-q*math.sin(an-.45)),(b[0]-q*math.cos(an+.45),b[1]-q*math.sin(an+.45))],c)
def rock(d,x,y,r,c=OCHRE,seed=0):
 rr=random.Random(seed);pts=[(x+math.cos(i*math.tau/9)*r*rr.uniform(.78,1.1),y+math.sin(i*math.tau/9)*r*rr.uniform(.78,1.1)) for i in range(9)]
 poly(d,pts,c);poly(d,[pts[0],pts[1],(x-r*.1,y-r*.1),pts[-1]],MUTED)
def star(d,x,y,r,c=LIGHT):
 pts=[(x+math.cos(i*math.pi/4)*r*(1 if i%2==0 else .24),y+math.sin(i*math.pi/4)*r*(1 if i%2==0 else .24)) for i in range(8)]
 poly(d,pts,c)
def cloud(d,x,y,rx,ry,c,phase=0):
 pts=[]
 for i in range(70):
  a=i*math.tau/70;k=1+.09*math.sin(a*5+phase)+.05*math.sin(a*9)
  pts.append((x+rx*math.cos(a)*k,y+ry*math.sin(a)*k))
 poly(d,pts,c)
def dashed(d,pts,c=MUTED,w=2):
 for i in range(0,len(pts)-1,3):line(d,pts[i:i+2],c,w)
rng=random.Random(841);STARS=[(rng.uniform(0,W),rng.uniform(100,600),rng.uniform(1,2.3)) for _ in range(115)]
PARTS=[(rng.random(),rng.random(),rng.random()) for _ in range(200)]
BASE={}
for dark in [False,True]:
 im=Image.new('RGB',(W,H),DARK if dark else PAPER);d=ImageDraw.Draw(im)
 # Fixed low-contrast paper fibres, never temporally noisy.
 for i in range(850):
  x=rng.randrange(W);y=rng.randrange(H);line(d,[(x,y),(x+rng.randrange(1,8),y)],'#2B2B25' if dark else '#E6DCC4',1)
 BASE[dark]=im
HOST=None
def configure_host(path):
 global HOST
 HOST=Image.open(path).convert('RGBA').resize((96,144),Image.Resampling.LANCZOS)
def sky(d,t=0):
 for x,y,r in STARS:ell(d,x,y,r,r,'#847B63')
def orbit(d,cx,cy,rx,ry,col=MUTED):d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),outline=col,width=1)
def globe(d,x,y,r,hot=False,cut=False,p=1):
 ell(d,x+4,y+8,r,r,'#201F1B');ell(d,x,y,r,r,OCHRE if hot else GREEN)
 # Deliberately flat two-tone hemisphere, not photoreal plastic.
 d.pieslice((x-r,y-r,x+r,y+r),285,105,fill='#765C42' if hot else '#4B5644')
 for i in range(7):
  a=i*2.39;xx=x+math.cos(a)*r*.63;yy=y+math.sin(a)*r*.6
  if hot:
   pts=[(xx+math.cos(a)*j*r*.025+math.sin(j*.8)*r*.015,yy+math.sin(a)*j*r*.025) for j in range(-5,6)]
   line(d,pts,GOLD,max(2,int(r*.022)))
  else:cloud(d,xx,yy,r*.2,r*.09,'#A99D74',i)
 if cut:
  d.pieslice((x-r,y-r,x+r,y+r),-70,70,fill='#C39A65')
  rr=r*.73;d.pieslice((x-rr,y-rr,x+rr,y+rr),-70,70,fill='#A8754F')
  rr=r*.4*ease(p);d.pieslice((x-rr,y-rr,x+rr,y+rr),-70,70,fill=INK)
def disc(d,cx,cy,t,p=1,rx=430):
 for j,col in enumerate(['#554C3B','#756447','#9B8057','#BE9B67']):
  rr=rx*(1-j*.14);ell(d,cx,cy,rr,rr*.245,col)
 ell(d,cx,cy,rx*.17,rx*.065,GOLD)
 for i,(a,b,c) in enumerate(PARTS[:100]):
  ang=a*math.tau+t*(.05+.08*b);r=rx*(.24+.72*b)
  x=cx+r*math.cos(ang);y=cy+r*.245*math.sin(ang)
  ell(d,x,y,1+c*2,1+c*.8,PAPER)
 star(d,cx,cy,52,GOLD);ell(d,cx,cy,32,32,LIGHT)
def galaxy(d,cx,cy,t,scale=1,formation=1):
 for arm in range(3):
  pts=[]
  for i in range(130):
   a=i/129*5.8+arm*math.tau/3+t*.012;r=(15+i*2.8)*scale
   pts.append((cx+math.cos(a)*r,cy+math.sin(a)*r*.49))
  line(d,pts,'#5B5543',26);line(d,pts,'#8A7C5A',10)
  for i in range(8,130,4):
   a=i/129*5.8+arm*math.tau/3+t*.012;r=(15+i*2.8)*scale
   ell(d,cx+math.cos(a)*r,cy+math.sin(a)*r*.49,2.3,1.6,PAPER)
 ell(d,cx,cy,50*scale,26*scale,GOLD);ell(d,cx,cy,24*scale,13*scale,LIGHT)

def draw_scene(kind,p,t,act=0):
 dark=kind in ['dark','collapse','stars','eject','galaxy','nebula','inner','growth','impact','moon','ending','fusion','assembly','cloudrich']
 im=BASE[dark].copy();d=ImageDraw.Draw(im);fg=LIGHT if dark else INK
 if dark and kind not in ['dark','collapse','fusion','assembly','cloudrich']:sky(d,t)
 if kind=='expansion':
  # Uniformly extending coordinate grid fills the field: no explosion centre/edge.
  sp=100+110*p
  for i in range(-10,11):
   x=640+i*sp;line(d,[(x,145),(x,568)],'#C8BA9C',1)
  for j in range(-6,7):
   y=355+j*sp*.6;line(d,[(0,y),(1280,y)],'#C8BA9C',1)
  for i,(a,b,c) in enumerate(PARTS[:95]):
   x=(640+(a-.5)*1050*(1+p*.7))%1280;y=160+((b*380-190)*(1+p*.7)+190)%400
   ell(d,x,y,3,3,OCHRE if i%3 else GREEN)
  txt(d,(640,581),'空间处处伸展，温度逐渐降低',24,INK,anchor='mm')
  arrow(d,(440,350),(440-80*p,350),OCHRE,3);arrow(d,(830,350),(830+80*p,350),OCHRE,3)
 elif kind=='recombine':
  centers=[(255,260),(530,410),(810,250),(1040,415)]
  for i,(x,y) in enumerate(centers):
   ell(d,x,y,10,10,OCHRE)
   q=ease((p-.25)*2);an=t*1.3+i
   ex=x+math.cos(an)*(80-56*q);ey=y+math.sin(an)*(65-41*q)
   ell(d,ex,ey,5,5,GREEN)
   if q>.1:orbit(d,x,y,26,26,'#B6A98C')
  for j in range(3):
   if p<.5:
    pts=[(60,190+j*120),(225,245+j*20),(400,190+j*120),(525,405),(690,300+j*30)]
   else:pts=[(70,190+j*110),(1180,190+j*110)]
   line(d,pts,GOLD,3);k=(t*.17+j*.2)%1;x=lerp(pts[0][0],pts[-1][0],k);y=lerp(pts[0][1],pts[-1][1],k);star(d,x,y,9,OCHRE)
  txt(d,(640,580),'光在自由电子间反复散射' if p<.35 else '自由电子减少，光开始远行',24,anchor='mm')
 elif kind=='dark':
  for i in range(7):cloud(d,120+i*175,320+math.sin(i)*90,155,60,'#3A3C31',i)
  for i,(a,b,c) in enumerate(PARTS[:85]):ell(d,150+a*1000,190+b*340,2+c*2,2+c*2,MUTED)
  txt(d,(310,280),'氢',52,PAPER,True);txt(d,(810,390),'氦',42,MUTED,True)
  txt(d,(640,576),'星光尚未出现',23,LIGHT,anchor='mm')
 elif kind=='inventory':
  txt(d,(240,220),'早期普通物质',23,INK,anchor='mm')
  for j,sym in enumerate(['H','He']):
   ell(d,190+j*105,335,42,42,GREEN);txt(d,(190+j*105,335),sym,28,LIGHT,anchor='mm')
  arrow(d,(390,335),(520,335),MUTED,2)
  txt(d,(820,220),'组成岩石还缺少的成分',23,INK,anchor='mm')
  for j,(sym,name) in enumerate([('O','氧'),('Si','硅'),('Fe','铁')]):
   x=650+j*170
   if p>j*.14:
    d.rounded_rectangle((x-50,282,x+50,388),radius=10,outline=OCHRE,width=2)
    txt(d,(x,318),sym,29,INK,anchor='mm');txt(d,(x,361),name,19,INK,anchor='mm')
  txt(d,(640,551),'这些成分要等待后来的恒星制造',24,INK,anchor='mm')
 elif kind=='cloudrich':
  for j in range(6):
   x=180+j*175;y=340+math.sin(j*1.8)*70
   cloud(d,x,y,210,95,['#3C4133','#50573F','#697052'][j%3],j+t*.01)
  for i,(a,b,c) in enumerate(PARTS[:150]):
   x=80+(a*1120+t*(2+c*2))%1120;y=230+b*255+math.sin(t*.2+a*6)*8
   if i%8:ell(d,x,y,1+c*2,1+c*2,PAPER)
   else:rock(d,x,y,3+c*2,OCHRE,i)
  txt(d,(640,575),'星际气体与细小尘粒 · 已混入前代恒星的产物',21,LIGHT,anchor='mm')
 elif kind=='collapse':
  q=ease(p);cx,cy=680,365
  for k in range(4):cloud(d,cx,cy,340-k*46-q*130,160-k*22-q*50,['#3C4033','#50543E','#6C7050','#959068'][k],k)
  for i,(a,b,c) in enumerate(PARTS[:120]):
   an=a*math.tau;r=(.1+b*.9)*(290-210*q)
   ell(d,cx+math.cos(an)*r,cy+math.sin(an)*r*.6,2,2,PAPER)
  for an in [0,math.pi/2,math.pi,math.pi*1.5]:
   arrow(d,(cx+math.cos(an)*330,cy+math.sin(an)*190),(cx+math.cos(an)*240,cy+math.sin(an)*130),MUTED,2)
  if p>.5:star(d,cx,cy,65*ease((p-.5)*2),GOLD);ell(d,cx,cy,20*ease((p-.5)*2),20*ease((p-.5)*2),LIGHT)
  txt(d,(1025,330),'收缩',23,PAPER);txt(d,(1025,369),'中心升温',23,PAPER)
 elif kind=='fusion':
  # A symbolic net reaction, not a literal collision movie or scale drawing.
  q=ease(p);cx,cy=655,350
  for i in range(4):
   a=i*math.pi/2+math.pi/4;r=lerp(175,24,q)
   ell(d,cx+math.cos(a)*r,cy+math.sin(a)*r,19,19,GOLD)
  if p>.65:
   for i in range(4):
    a=i*math.pi/2;star(d,cx+math.cos(a)*(90+100*q),cy+math.sin(a)*(90+100*q),8,LIGHT)
  txt(d,(310,350),'氢',33,LIGHT,True,anchor='mm');txt(d,(990,350),'氦 + 能量',29,LIGHT,True,anchor='mm')
  arrow(d,(375,350),(435,350),MUTED,3);arrow(d,(840,350),(900,350),MUTED,3)
  txt(d,(640,580),'核聚变净过程 · 粒子与反应步骤作简化',20,LIGHT,anchor='mm')
 elif kind=='assembly':
  q=ease(p)
  for j,(sx,sy) in enumerate([(220,240),(1050,285),(420,530)]):
   cx=lerp(sx,650,q*.85);cy=lerp(sy,365,q*.85)
   cloud(d,cx,cy,100-q*30,45-q*10,['#575B43','#797657','#99916B'][j],j)
   for k in range(24):
    a=k*2.4;r=15+(k%9)*8;ell(d,cx+math.cos(a)*r,cy+math.sin(a)*r*.4,2,2,LIGHT)
   pts=[(lerp(sx,650,z/30),lerp(sy,365,z/30)+math.sin(z/30*math.pi)*30) for z in range(31)]
   dashed(d,pts,MUTED,1)
  if q>.5 and act==1:galaxy(d,650,365,t,scale=(q-.5)*1.4)
  txt(d,(640,583),'气体与恒星汇聚、并合 · 漫长过程的简化示意',20,LIGHT,anchor='mm')
 elif kind=='stars':
  for j,(cx,cy) in enumerate([(300,300),(670,410),(985,270)]):
   cloud(d,cx,cy,210,85,'#424534',j)
   for i in range(12):
    a=i*2.4;r=30+i*12;x=cx+math.cos(a)*r;y=cy+math.sin(a)*r*.45
    star(d,x,y,(3+5*ease(p+i*.05)),LIGHT)
  txt(d,(640,576),'最初几亿年 · 恒星与早期星系逐渐形成',22,LIGHT,anchor='mm')
 elif kind=='layers':
  cx,cy=530,355
  for j,(r,c) in enumerate([(192,'#C6A46C'),(148,'#A8754F'),(108,'#816A4D'),(66,'#69765A'),(30,INK)]):
   rr=r*ease(p*3-j*.25) if act==0 else r
   ell(d,cx,cy,max(.1,rr),max(.1,rr),c)
  d.pieslice((cx-192,cy-192,cx+192,cy+192),-70,70,fill=PAPER)
  labels=[('氢 / 氦',177,-.9),('碳 / 氧',126,-.45),('硅等元素',87,.25),('铁核',24,.7)]
  for j,(s,r,a) in enumerate(labels):
   x=cx+r*math.cos(a);y=cy+r*math.sin(a);yy=230+j*82
   line(d,[(x,y),(810,yy),(845,yy)],INK,2);txt(d,(860,yy),s,24,INK,anchor='lm')
  txt(d,(530,580),'大质量恒星晚期内部 · 层次简化示意',20,INK,anchor='mm')
 elif kind=='eject':
  cx,cy=480,350;q=ease(p)
  for k in range(5):
   pts=[]
   for i in range(70):
    a=i*math.tau/69;r=70+q*(110+k*38);r*=1+(.025 if act==0 else .16)*math.sin(a*5+k)
    pts.append((cx+math.cos(a)*r,cy+math.sin(a)*r*.62))
   line(d,pts,['#5D5542','#75674A','#A78556','#C69F65',PAPER][k],4)
  star(d,cx,cy,35*(1-q)+7,GOLD)
  for i,(a,b,c) in enumerate(PARTS[:100]):
   an=a*math.tau;r=70+q*(100+b*300)
   ell(d,cx+math.cos(an)*r,cy+math.sin(an)*r*.62,2,2,MUTED)
  arrow(d,(880,350),(1100,350),MUTED,2);cloud(d,1100,350,105,100,'#5A6047',1)
  txt(d,(1060,500),'新的材料',23,LIGHT,anchor='mm')
 elif kind=='galaxy':
  galaxy(d,620,355,t)
  if act>0:
   x,y=815,396;ell(d,x,y,10,10,None,GOLD,2);line(d,[(x+12,y),(1000,500)],GOLD,2);txt(d,(1000,530),'后来孕育太阳的区域',20,LIGHT,anchor='mm')
  txt(d,(640,580),'恒星诞生、演化，物质回到星际空间',22,LIGHT,anchor='mm')
 elif kind=='nebula':
  q=ease(p)
  for j in range(4):cloud(d,640,350,430-j*57,lerp(190-j*24,70-j*8,q),['#3F4436','#5E6548','#818260','#A89B70'][j],t*.02+j)
  if q>.3:disc(d,640,350,t,rx=300+130*q)
  if p<.6:
   for i,(a,b,c) in enumerate(PARTS[:60]):
    an=a*math.tau+t*.08;r=lerp(460,120,q)*(.4+b*.6)
    ell(d,640+math.cos(an)*r,350+math.sin(an)*r*(.5-q*.25),2,2,PAPER)
  txt(d,(640,572),'转动的云团逐渐形成扁平的盘',22,LIGHT,anchor='mm')
 elif kind=='inner':
  disc(d,630,350,t,rx=510)
  orbit(d,630,350,260,64,GOLD);line(d,[(867,375),(1000,480)],GOLD,2)
  txt(d,(1000,510),'岩石与金属',26,LIGHT,anchor='mm')
  for i in range(8):
   a=i*.8+t*.12;x=630+math.cos(a)*205;y=350+math.sin(a)*50;rock(d,x,y,4,GOLD,i)
  txt(d,(640,580),'近太阳区域 · 高温使冰难以保持固态',21,LIGHT,anchor='mm')
 elif kind=='grains':
  for j,(label,mode) in enumerate([('黏合',0),('弹开',1),('破碎',2)]):
   cy=225+j*140;txt(d,(160,cy),label,25,INK,anchor='mm');q=(p*1.1)%1
   if q<.48:
    for s in [-1,1]:rock(d,650+s*(180-170*q/.48),cy,17,OCHRE,j+s)
   elif mode==0:rock(d,650,cy,27,OCHRE,15)
   elif mode==1:
    for s in [-1,1]:rock(d,650+s*(15+170*(q-.48)/.52),cy,17,OCHRE,j+s)
   else:
    for k in range(12):
     a=k*2.4;r=15+(q-.48)*230;rock(d,650+math.cos(a)*r,cy+math.sin(a)*r*.3,4,OCHRE,k)
   arrow(d,(950,cy),(1030,cy),MUTED,2)
  txt(d,(640,594),'碰撞并不总能使颗粒长大',22,INK,anchor='mm')
 elif kind=='concentration':
  q=ease(p)
  for row in range(6):
   pts=[(x,210+row*55+math.sin(x*.01+t*.4)*12) for x in range(70,1220,10)];line(d,pts,'#C6BA9C',2)
  for i,(a,b,c) in enumerate(PARTS[:160]):
   x=lerp(140+a*1000,690+(a-.5)*130,q);y=lerp(195+b*350,365+(b-.5)*100,q)
   ell(d,x,y,2+c*3,2+c*3,OCHRE)
  if p>.75:rock(d,690,365,40*ease((p-.75)*4),OCHRE,71)
  txt(d,(640,582),'一种模型：局部聚集后，在自身引力下坍缩',21,INK,anchor='mm')
 elif kind=='growth':
  cx,cy=700,360;r=82+45*ease(p);globe(d,cx,cy,r,True)
  for i,(a,b,c) in enumerate(PARTS[:30]):
   an=a*math.tau;q=max(0,1-p*1.3+b*.4);rr=r+(q**1.5)*(110+b*210)
   if q>.05:rock(d,cx+math.cos(an)*rr,cy+math.sin(an)*rr*.75,3+c*13,OCHRE,i)
   if .02<q<.15:
    for j in range(4):ell(d,cx+math.cos(an+j*.06)*(r+15),cy+math.sin(an+j*.06)*(r+15)*.75,2,2,GOLD)
  if act>=1:
   for j in range(14):
    an=-.7+j*.07;rr=r+20+160*p
    rock(d,cx+math.cos(an)*rr,cy+math.sin(an)*rr*.75,2+(j%3),OCHRE,j)
  if act==1:txt(d,(640,577),'碰撞、合并与物质损失 · 数千万年的生长',22,LIGHT,anchor='mm')
 elif kind=='differentiate':
  globe(d,580,350,190,True,True,p)
  for i in range(18):
   a=-1+i*2/17;r=lerp(155,48,ease(p));x=580+math.cos(a)*r;y=350+math.sin(a)*r
   ell(d,x,y,4,4,INK)
  line(d,[(615,350),(880,320)],INK,2);txt(d,(900,320),'富铁金属向深处迁移',24,INK,anchor='lm')
  line(d,[(697,255),(880,235)],INK,2);txt(d,(900,235),'岩石外层',24,INK,anchor='lm')
  txt(d,(580,580),'熔融使物质重新分布 · 内部剖面示意',21,INK,anchor='mm')
 elif kind=='dating':
  rock(d,330,350,122,OCHRE,71)
  for i in range(25):
   a=i*2.4;r=20+i*3;ell(d,330+math.cos(a)*r,350+math.sin(a)*r,3,3,INK if i%2 else PAPER)
  for j in range(7):
   x=735+(j%4)*95;y=300+(j//4)*110
   col=GREEN if j<round(7*(1-ease(p)*.65)) else OCHRE
   ell(d,x,y,15,15,col)
  txt(d,(905,490),'同位素变化留下时间记录',23,INK,anchor='mm')
  txt(d,(905,532),'方法示意 · 无实测数据',18,INK,anchor='mm')
  txt(d,(330,548),'地球样品与陨石',22,INK,anchor='mm')
  txt(d,(905,175),'约 45.4 亿年',35,INK,True,anchor='mm')
 elif kind=='impact':
  q=ease(p);cx,cy=565,385
  if act==0:
   globe(d,cx,cy,130,True);x=lerp(1070,680,q);y=lerp(180,350,q);globe(d,x,y,66,True)
   dashed(d,[(1070-i*8,180+i*3.5) for i in range(43)],MUTED,2)
  else:
   globe(d,cx,cy,130,True)
   for i,(a,b,c) in enumerate(PARTS[:80]):
    an=-1.2+a*2.5;r=140+q*(100+b*400);x=cx+math.cos(an)*r;y=cy+math.sin(an)*r*.6
    rock(d,x,y,2+c*7,OCHRE,i)
   for k in range(3):
    pts=[(cx+math.cos(-1.2+i*.025)*(150+q*300+k*25),cy+math.sin(-1.2+i*.025)*(150+q*300+k*25)*.6) for i in range(95)]
    line(d,pts,['#746044','#A8754F',GOLD][k],3)
  txt(d,(640,584),'大碰撞假说 · 轨迹、比例与速度均为示意',20,LIGHT,anchor='mm')
 elif kind=='moon':
  orbit(d,480,370,410,145,'#615D4A')
  q=ease(p)
  for i,(a,b,c) in enumerate(PARTS[:80]):
   an=a*math.tau;r=300+b*100;x=480+math.cos(an)*r;y=370+math.sin(an)*r*.36
   x=lerp(x,860+(a-.5)*75,q);y=lerp(y,290+(b-.5)*75,q)
   ell(d,x,y,2+c*3,2+c*3,MUTED)
  # Earth occludes debris behind it; particles never appear to cross its interior.
  globe(d,480,370,142,True)
  if p>.4:
   ell(d,860,290,48*ease((p-.4)/.6),48*ease((p-.4)/.6),MUTED)
   for i in range(5):ell(d,850+math.cos(i*2.4)*20*q,285+math.sin(i*2.4)*20*q,4*q,4*q,'#827659')
  txt(d,(640,584),'抛出物质聚集成月球 · 形成细节仍在研究',21,LIGHT,anchor='mm')
 elif kind=='samples':
  rock(d,340,355,125,'#9A9076',82)
  for i in range(20):
   a=i*2.4;r=20+i*4;ell(d,340+math.cos(a)*r,355+math.sin(a)*r,3,3,INK)
  txt(d,(340,548),'月岩',26,INK,anchor='mm')
  if p>.18 or act==1:
   rock(d,900,345,105,OCHRE,83)
   for j in range(8):
    a=j*2.4;x=900+math.cos(a)*(25+j*5);y=345+math.sin(a)*(25+j*5)
    ell(d,x,y,4,4,INK if j%2 else PAPER)
   txt(d,(900,548),'地球岩石',26,INK,anchor='mm')
  q=ease((p-.3)*2) if act==0 else 1
  if q>0:
   line(d,[(490,320),(490+245*q,320)],MUTED,2);line(d,[(490,392),(490+245*q,392)],MUTED,2)
  if p>.5 or act==1:txt(d,(615,355),'部分成分相似',24,INK,anchor='mm')
  if act==1:
   txt(d,(640,175),'岩石记录，检验碰撞解释',27,INK,True,anchor='mm')
   for x in [340,900]:arrow(d,(x,218),(x,255),OCHRE,2)
  txt(d,(640,590),'样品对照 · 无比例的概念示意',20,INK,anchor='mm')
 elif kind=='ending':
  orbit(d,690,368,350,145,'#4B4B3B')
  globe(d,690,368,180,True);ell(d,1020,245,43,43,MUTED)
  txt(d,(320,307),'地球的历史',31,LIGHT,True,anchor='mm');txt(d,(320,357),'尚在开头',31,LIGHT,True,anchor='mm')
 return im

CHAPTERS={'inventory':('02','岩石的成分尚未齐备','元素成分 · 概念示意'),'cloudrich':('03','新一代星球的材料','星际云 · 艺术化示意'),'fusion':('02','恒星为何持续发光','核聚变 · 净反应示意'),'assembly':('03','银河逐渐形成','星系汇聚与并合 · 示意'),'expansion':('01','空间伸展','约 138 亿年前 · 膨胀示意'),'recombine':('01','光开始远行','约 38 万年后 · 微观示意'),'dark':('02','等待第一缕星光','早期宇宙 · 艺术化示意'),'collapse':('02','引力聚拢气体','恒星形成 · 过程示意'),'stars':('02','最初的恒星与星系','宇宙最初几亿年 · 示意'),'layers':('03','恒星改变物质','大质量恒星 · 结构简图'),'eject':('03','物质回到星际空间','恒星演化 · 示意'),'galaxy':('03','银河中的循环','银河结构 · 艺术化示意'),'nebula':('04','太阳与盘','约 46 亿年前 · 示意'),'inner':('04','地球材料所在的区域','原行星盘 · 非比例示意'),'grains':('04','颗粒的生长难关','碰撞行为 · 放大示意'),'concentration':('04','从颗粒到小天体','一种形成模型 · 示意'),'growth':('05','地球逐渐长大','吸积过程 · 示意'),'differentiate':('05','地球的内部分层','内部结构 · 非比例示意'),'dating':('05','岩石留下的时钟','年代测定 · 方法示意'),'impact':('06','一次大碰撞','月球形成主流解释 · 示意'),'moon':('06','月球逐渐聚成','大碰撞假说 · 示意'),'samples':('06','月岩带来的证据','样品与成分 · 示意'),'ending':('尾声','地球的来处','早期熔融表面 · 艺术化示意')}
def compose(kind,p,t,act=0,caption='',guide=True,progress=0):
 im=draw_scene(kind,p,t,act);d=ImageDraw.Draw(im);dark=kind in ['dark','collapse','stars','eject','galaxy','nebula','inner','growth','impact','moon','ending','fusion','assembly','cloudrich'];fg=LIGHT if dark else INK
 ch,title,tag=CHAPTERS[kind]
 if kind=='recombine' and p<.35:title='光尚不能远行';tag='早期热密宇宙 · 散射示意'
 if kind=='eject':title='恒星逐渐抛出外层' if act==0 else '大质量恒星的爆发'
 if kind=='assembly' and act==0:title='早期星系汇聚';tag='早期结构 · 简化示意'
 txt(d,(42,31),'地球往事  /  序章',18,MUTED)
 txt(d,(42,66),title,33,fg,True)
 txt(d,(1234,41),tag,17,MUTED,anchor='ra')
 # Every caption has its own reserved region. The guide's 144px never overlaps it.
 if guide:
  if HOST is None:raise RuntimeError('Supply the separately held intact guide asset using --host.')
  im.paste(HOST,(28,452),HOST)
 d=ImageDraw.Draw(im);d.rectangle((0,618,W,H),fill=DARK if dark else PAPER)
 if caption:
  rows=[];s=caption
  while len(s)>37:rows.append(s[:37]);s=s[37:]
  if s:rows.append(s)
  for i,row in enumerate(rows[:2]):txt(d,(640,637+i*33),row,26,fg,anchor='mt')
 line(d,[(42,709),(1238,709)],'#534E3E' if dark else '#CEBFA1',2)
 line(d,[(42,709),(42+1196*progress,709)],GOLD if dark else OCHRE,2)
 return im

def preview():
 out=ROOT.parent/'qa';out.mkdir(exist_ok=True)
 kinds=['expansion','recombine','inventory','collapse','fusion','layers','assembly','galaxy','cloudrich','nebula','grains','concentration','growth','differentiate','impact','moon','samples','ending']
 sheet=Image.new('RGB',(1280,math.ceil(len(kinds)/3)*260),PAPER)
 for i,k in enumerate(kinds):
  im=compose(k,.68,3,1 if k in ['impact','galaxy'] else 0,'画面测试：旁白与字幕将依实际录音逐句同步。',progress=.5)
  im.save(out/f'keyframe-{k}.png');sheet.paste(im.resize((426,240)),((i%3)*426,(i//3)*260))
 sheet.save(out/'contact-sheet.png')
 seq=[('expansion',0),('collapse',0),('nebula',0),('differentiate',0),('impact',1),('moon',0)]
 proc=subprocess.Popen(['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','24','-i','-','-c:v','libx264','-preset','fast','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(out/'technical-preview-24s.mp4')],stdin=subprocess.PIPE,stderr=open(out/'preview-encode.log','w'))
 for n in range(24*24):
  idx=n//96;k,a=seq[idx];p=(n%96)/95
  im=compose(k,p,n/24,a,'技术预览 · 示意画面，非正式旁白版本',progress=n/(24*24))
  proc.stdin.write(im.tobytes())
 proc.stdin.close();assert proc.wait()==0


# Full export is intentionally a separate function: it requires measured storyboard.
def render_full(audio_path,output_path):
 import bisect
 board=json.loads((ROOT/'storyboard.json').read_text());cues=json.loads((ROOT/'subtitle_cues.json').read_text());shots=board['shots'];starts=[s['render']['start_frame'] for s in shots];cstarts=[c['start'] for c in cues]
 total=round(board['duration_s']*FPS);out=Path(output_path);out.parent.mkdir(exist_ok=True,parents=True)
 qa=out.parent/'scene-qa';qa.mkdir(exist_ok=True)
 command=['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r',str(FPS),'-i','-','-i',str(audio_path),'-c:v','libx264','-preset','medium','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','96k','-af','apad','-t',str(total/FPS),'-movflags','+faststart',str(out)]
 proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=open(out.with_suffix('.encode.log'),'w'))
 samples={}
 for s in shots:
  r=s['render'];a,b=r['start_frame'],r['end_frame'];
  for frame,name in [(a,'start'),((a+b)//2,'middle'),(b-1,'end')]:samples[frame]=s['shot_id']+'-'+name
 for n in range(total):
  idx=max(0,bisect.bisect_right(starts,n)-1);s=shots[idx];r=s['render'];u=(n-r['start_frame'])/max(1,r['end_frame']-r['start_frame']-1);p=lerp(*r['p_range'],u);t=n/FPS
  ci=bisect.bisect_right(cstarts,t)-1;caption=cues[ci]['text'] if ci>=0 and t<cues[ci]['end']+.05 else ''
  im=compose(r['kind'],p,t,r['act'],caption,True,n/max(1,total-1))
  transition=n-r['start_frame']
  if idx and transition<12:
   prev=shots[idx-1]['render']
   if prev['kind']!=r['kind']:
    old=compose(prev['kind'],prev['p_range'][1],t,prev['act'],caption,True,n/max(1,total-1))
    if CHAPTERS[prev['kind']][0]!=CHAPTERS[r['kind']][0]:
     x=round(W*ease(transition/11));old.paste(im.crop((0,0,x,H)),(0,0));im=old
    else:im=Image.blend(old,im,ease(min(1,transition/9)))
  if n in samples:im.save(qa/(samples[n]+'.png'))
  proc.stdin.write(im.tobytes())
  if n%(FPS*20)==0:print(f'Rendered {n/FPS:.1f}/{total/FPS:.1f}s',flush=True)
 proc.stdin.close();assert proc.wait()==0,'FFmpeg export failed'
 print(str(out),flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--host',type=Path,required=True);ap.add_argument('--audio',type=Path);ap.add_argument('--output',type=Path);a=ap.parse_args();configure_host(a.host)
 if a.audio:
  assert a.output,'--output required';render_full(a.audio,a.output)
 else:preview()
