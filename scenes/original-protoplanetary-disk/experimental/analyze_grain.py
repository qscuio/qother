"""Display-space Monte Carlo noise estimate, with no claim of linear radiance accuracy."""
from PIL import Image
import numpy as np,json
from pathlib import Path
import argparse
_parser=argparse.ArgumentParser(description=__doc__)
_parser.add_argument('--output',type=Path,required=True,help='Existing scene output directory')
_args=_parser.parse_args()
p=_args.output.resolve()/'motion-benchmark'
a=np.asarray(Image.open(p/'camera-test-001.png').convert('RGB'),float)/255;b=np.asarray(Image.open(p/'independent-seed-grain-crop.png').convert('RGB'),float)/255
l=np.array([.2126,.7152,.0722]);bb=b@l;h,w=bb.shape;res=[]
# Account for Blender's border rounding; register among the adjacent expected pixels.
for y in [251,252,253,254]:
 aa=a[y:y+h,320:320+w]@l;yy,xx=np.indices(aa.shape);mask=(aa>.045)&(aa<.55)&((xx-287)**2+(yy-(373-y))**2>80**2)&(xx>20)&(xx<w-20)&(yy>20)&(yy<h-20)
 sig=np.std((aa-bb)[mask])/2**.5;res.append((y,float(sig),float(aa[mask].mean())))
y,sig,mean=min(res,key=lambda x:x[1]);r={'method':'Independent-seed display-luminance difference divided by sqrt(2); exclude core, dark background and border. PNG tone mapping means this is not linear-radiance error.','seeds':[46109,46110],'crop_size':[w,h],'crop_alignment_top_pixel_y':y,'noise_sigma_8bit_levels':sig*255,'mean_display_luminance':mean,'relative_sigma_to_mean':sig/mean}
(p/'grain-measurement-reproducible.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
