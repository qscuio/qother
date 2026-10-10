from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,json,argparse
from scipy.ndimage import gaussian_filter
parser=argparse.ArgumentParser(description='Compare actual matching-camera 1280x720 reference and three candidate renders.')
parser.add_argument('--reference',type=Path,required=True)
parser.add_argument('--renders',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True,help='New directory for metrics and comparison panels')
args=parser.parse_args();D=args.output;D.mkdir(parents=True,exist_ok=False)
paths=[args.reference]+[args.renders/(x+'.png') for x in ['A-step1.6','B-step3.2','C-step1.6-s128']]
images=[Image.open(p).convert('RGB') for p in paths]
if any(im.size!=(1280,720) for im in images):raise ValueError('All images must be matching 1280x720 frames.')
labels=['Baseline 0.4 step / 256 samples','A: 1.6 step / 256 samples','B: 3.2 step / 256 samples','C: 1.6 step / 128 samples']
contact=Image.new('RGB',(1280,776),(24,24,24));draw=ImageDraw.Draw(contact)
for i,(im,label) in enumerate(zip(images,labels)):
 x=(i%2)*640;y=(i//2)*388;draw.text((x+10,y+7),label,fill='white');contact.paste(im.resize((640,360)),(x,y+28))
contact.save(D/'comparison-full.png')
regions=[('core and near dust',(450,285,850,535)),('far rim',(680,170,1080,420)),('near rim',(270,440,670,690))]
contact=Image.new('RGB',(1600,840),(24,24,24));draw=ImageDraw.Draw(contact)
for i,(im,label) in enumerate(zip(images,labels)):
 for j,(region,box) in enumerate(regions):
  x=i*400;y=j*280;draw.text((x+5,y+5),label+' / '+region,fill='white');contact.paste(im.crop(box),(x,y+28))
contact.save(D/'comparison-crops.png')
base=np.asarray(images[0],dtype=float)/255;mask=base.mean(2)>.08;stats=[]
for p,im in zip(paths[1:],images[1:]):
 a=np.asarray(im,dtype=float)/255
 lowa=gaussian_filter(a,sigma=(2,2,0));lowb=gaussian_filter(base,sigma=(2,2,0))
 stats.append(dict(name=p.stem,masked_MAE_rgb_0_1=float(abs(a-base)[mask].mean()),masked_lowpass_MAE=float(abs(lowa-lowb)[mask].mean()),masked_mean_luma_ratio=float(a.mean(2)[mask].mean()/base.mean(2)[mask].mean()),masked_high_frequency_rms=float(np.sqrt(((a-lowa)[mask]**2).mean())),baseline_masked_high_frequency_rms=float(np.sqrt(((base-lowb)[mask]**2).mean()))))
(D/'pixel-metrics.json').write_text(json.dumps(stats,indent=2))
