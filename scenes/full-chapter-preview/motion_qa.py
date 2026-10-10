import json,subprocess,argparse
from pathlib import Path
import numpy as np
parser=argparse.ArgumentParser(description='Decoded near-static interval heuristic; not playback approval')
parser.add_argument('--video',type=Path,required=True);parser.add_argument('--manifest',type=Path,required=True);parser.add_argument('--output',type=Path,required=True,help='New JSON report file')
args=parser.parse_args()
if args.output.exists():parser.error('Output report already exists')
m=json.loads(args.manifest.read_text());v=args.video
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(v),'-vf','scale=160:90','-pix_fmt','gray','-f','rawvideo','-']);a=np.frombuffer(raw,np.uint8).reshape(-1,90,160);diff=np.abs(a[24:].astype(np.int16)-a[:-24]).mean(axis=(1,2));near=diff<.1
runs=[];start=None
for i,flag in enumerate(list(near)+[False]):
 if flag and start is None:start=i
 elif not flag and start is not None:
  if i-start>=12:
   sec=start/24;p=next((r['id'] for r in m['paragraphs'] if r['start']<=sec<r['end']),'END');runs.append({'paragraph':p,'start':sec,'duration':(i-start+24)/24,'threshold_mean_luma_delta':.1})
  start=None
result={'method':'One-second-separated final decoded frames downscaled160x90 gray; mean absolute luma delta <0.1 marks near-static intervals, including encoding-noise tolerance','runs_half_second_or_longer':runs,'note':'P15 evidence timeline/P17 rock comparison contain deliberate reading holds; endcard static. No claim that every encoded frame is visually unique.'}
args.output.parent.mkdir(parents=True,exist_ok=True)
with args.output.open('x') as f:f.write(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
