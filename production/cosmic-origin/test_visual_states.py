"""Exercise every planned scene at start/mid/end without inventing audio times."""
from pathlib import Path
from PIL import Image
import json,hashlib
from render import compose,PAPER,configure_host
import argparse
ap=argparse.ArgumentParser();ap.add_argument("--host",type=Path,required=True);args=ap.parse_args();configure_host(args.host)
from shot_design import DESIGN
root=Path(__file__).resolve().parent.parent/'qa';root.mkdir(exist_ok=True)
cases=list(dict.fromkeys((r[3],r[4]) for r in DESIGN));report=[]
for page in range((len(cases)+3)//4):
 sheet=Image.new('RGB',(1280,960),PAPER)
 for row,(kind,act) in enumerate(cases[page*4:page*4+4]):
  hashes=[]
  for col,p in enumerate([0,.5,1]):
   im=compose(kind,p,7*p,act,'视觉状态测试：首、中、末帧。',True,p)
   hashes.append(hashlib.sha256(im.tobytes()).hexdigest());sheet.paste(im.resize((426,240)),(col*426,row*240))
  report.append({'scene':kind,'act':act,'renders_ok':True,'distinct_frame_hashes':len(set(hashes))})
 sheet.save(root/f'all-states-{page+1}.png')
(root/'visual-state-tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(f'{len(cases)} scene states, {len(cases)*3} frames rendered')
