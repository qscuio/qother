"""Particle-sampled 3-D radiative illustration; original model, coherent material IDs."""
import importlib.util,math
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
P=Path(__file__).parent
spec=importlib.util.spec_from_file_location('stellar_p10_material',P.parent/'p10/scene_renderer.py');cloudbase=importlib.util.module_from_spec(spec);spec.loader.exec_module(cloudbase)
W,H=1280,720
Y,X=np.mgrid[:H,:W]

from functools import lru_cache
@lru_cache(maxsize=2)
def cloud(p=0,heat=0,kind='gas'):
 xx,yy,zz=cloudbase.x,cloudbase.y,cloudbase.z
 factor=1.04-.26*p;xx=xx*factor;yy=yy*factor;zz=zz*factor
 incl=.28;depth=yy*np.cos(incl)-zz*np.sin(incl);vertical=yy*np.sin(incl)+zz*np.cos(incl)
 persp=4.5/(4.5+depth);sx=630+xx*515*persp;sy=360-vertical*515*persp
 valid=(sx>1)&(sx<W-2)&(sy>1)&(sy<H-2)
 sx=sx[valid];sy=sy[valid];depth=depth[valid];weight=cloudbase.weights[valid]
 out=np.zeros((H,W,3),np.float32)+[3.,7.,12.]
 rr=np.hypot(X-630,Y-360);core=False
 for mid in np.linspace(1.6,-1.6,12):
  if mid<0 and not core:
   glow=(np.exp(-(rr/(30+heat*10))**1.5)*.65+np.exp(-(rr/12)**2)*.9)*heat
   out+=glow[...,None]*[255,200,110];core=True
  dep=np.clip(1-np.abs(depth-mid)/.30,0,1);sel=dep>0
  px=sx[sel];py=sy[sel];ww=weight[sel]*dep[sel];ix=px.astype(int);iy=py.astype(int);fx=px-ix;fy=py-iy;b=iy*W+ix
  counts=np.zeros(W*H)
  for dx,dy,q in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:counts+=np.bincount(b+dy*W+dx,weights=ww*q,minlength=W*H)
  a=counts.reshape(H,W);soft=gaussian_filter(a,1.0)*.85+gaussian_filter(a,3)*.15;opacity=1-np.exp(-soft*1.5)
  rgb=np.array([110.,130.,151.]) if kind=='gas' else np.array([142.,128.,107.])
  col=np.zeros((H,W,3),np.float32)+rgb*(1+.22*np.tanh(mid*2.3))
  lighting=np.exp(-(rr/170)**1.7)*heat
  col+=lighting[...,None]*[93,40,-28]
  if mid<-.1:col*=.90
  out=out*(1-opacity[...,None])+col*opacity[...,None]
 return Image.fromarray(np.clip(out,0,255).astype(np.uint8))

from functools import lru_cache
from scipy.ndimage import map_coordinates
@lru_cache(2)
def ejecta_anchors(kind):
 rng=np.random.default_rng(927 if kind=='wind' else 631);n=1100000
 z=rng.uniform(-1,1,n);theta=rng.uniform(-np.pi,np.pi,n);xy=np.sqrt(1-z*z)
 x=xy*np.cos(theta);y=xy*np.sin(theta)
 field=gaussian_filter(np.random.default_rng(728).normal(size=(72,72,72)),2);field/=field.std()
 f=map_coordinates(field,[z*25+36,y*25+36,x*25+36],order=1)
 if kind=='wind':
  radius=np.clip(rng.normal(1,.18,n),.2,1.5)*(1+.18*z*z)
  wt=np.clip(np.exp(f*.75)/3,0,1)*rng.uniform(.2,1.4,n)*.1
 else:
  radius=np.clip(rng.normal(1,.045,n),.7,1.3)*(1+.1*f)
  wt=np.clip(np.exp(f*1.2)/4,0,1)*rng.uniform(.3,2,n)*.13
 return x,y,z,radius,wt

def ejecta(p,kind='wind'):
 x,y,z,r,wt=ejecta_anchors(kind);rad=70+(245 if kind=='wind' else 260)*p
 sx=615+x*r*rad;sy=354-y*r*rad*.85;depth=z*r
 out=np.zeros((H,W,3),np.float32)+[3.,7.,12.]
 for mid in np.linspace(1.4,-1.4,10):
  dep=np.clip(1-np.abs(depth-mid)/.30,0,1);sel=(dep>0)&(sx>1)&(sx<W-2)&(sy>1)&(sy<H-2)
  px=sx[sel];py=sy[sel];ww=wt[sel]*dep[sel];ix=px.astype(int);iy=py.astype(int);fx=px-ix;fy=py-iy;b=iy*W+ix
  a=np.zeros(H*W)
  for dx,dy,q in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:a+=np.bincount(b+dy*W+dx,weights=ww*q,minlength=H*W)
  a=a.reshape(H,W);soft=gaussian_filter(a,.8)*.82+gaussian_filter(a,3)*.18
  opacity=1-np.exp(-soft*(6 if kind=='wind' else 3))
  rgb=np.array([168,101,63]) if kind=='wind' else np.array([151,180,189])
  rgb=rgb*(1+.2*mid)
  out=out*(1-opacity[...,None])+rgb*opacity[...,None]
  if kind=='supernova':out+=gaussian_filter(a,2)[...,None]*np.array([15,7,2])
 return Image.fromarray(np.clip(out,0,255).astype(np.uint8))
