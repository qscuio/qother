"""Decode and scan the actual clip for gross flashes/freezes. Motion and noise are not separated."""
from pathlib import Path
import subprocess,json,hashlib
from PIL import Image
import numpy as np
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--movie',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True,help='New directory; never overwrites existing QA')
args=parser.parse_args();movie=args.movie.resolve();O=args.output.resolve()
if not movie.is_file():parser.error('--movie must exist')
O.mkdir(parents=True,exist_ok=False);P=O/'decoded-QA';P.mkdir()
probe=json.loads(subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,duration','-of','json',str(movie)],check=True,text=True,capture_output=True).stdout)['streams'][0]
assert probe['r_frame_rate']=='24/1' and abs(float(probe['duration'])-2)<.001, 'Expected 24fps / 2s clip'

subprocess.run(['ffmpeg','-n','-hide_banner','-loglevel','error','-i',str(movie),'-fps_mode','passthrough',str(P/'decoded-%03d.png')],check=True)
paths=sorted(P.glob('decoded-*.png'));assert len(paths)==48
means=[];adj=[];hashes=[];prev=None
for i,p in enumerate(paths,1):
 im=Image.open(p).convert('RGB');assert im.size==(1280,720);a=np.asarray(im,dtype=np.float32)/255;lum=a@np.array([.2126,.7152,.0722],dtype=np.float32);means.append(float(lum.mean()));hashes.append(hashlib.sha256(im.tobytes()).hexdigest())
 if prev is not None:
  diff=lum-prev;adj.append({'from_frame':i-1,'to_frame':i,'luma_rms_difference':float(np.sqrt(np.mean(diff**2))),'mean_luma_step':float(lum.mean()-prev.mean()),'identical_decoded_pixels':hashes[-1]==hashes[-2]})
 prev=lum
rms=np.array([x['luma_rms_difference'] for x in adj]);median=float(np.median(rms));mad=float(np.median(np.abs(rms-median)));cut_threshold=max(.03,median+6*mad)
flags=[]
for x in adj:
 if x['identical_decoded_pixels']:flags.append({'type':'exact_duplicate_adjacent_frame','frame':x['to_frame']})
 if x['luma_rms_difference']>cut_threshold:flags.append({'type':'large_adjacent_difference','frame':x['to_frame'],'value':x['luma_rms_difference']})
for i in range(1,47):
 delta=abs(means[i]-(means[i-1]+means[i+1])/2)
 if delta>.01:flags.append({'type':'transient_global_luma_flash','frame':i+1,'value':delta})
report={'source_movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'probe':probe,'decoded_frame_count':48,'dimensions':[1280,720],'fps':24,'duration_seconds':2,'unique_decoded_frames':len(set(hashes)),'mean_luminance_by_frame':means,'adjacent_frames':adj,'adjacent_rms_median':median,'adjacent_rms_max':float(rms.max()),'heuristics':{'large_adjacent_rms_threshold':cut_threshold,'global_transient_mean_luma_threshold':.01,'freeze_check':'exact consecutive decoded pixel equality'},'flags':flags,'interpretation':'A gross-anomaly scan of actual decoded frames. True camera motion, sampling grain and codec error all contribute to adjacent differences. No flags does not prove absence of subtle flicker or establish final cinematic quality.','sound':'none','physical_evolution':'none; only observer camera moves'}
(O/'temporal-frame-QA.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k] for k in ['decoded_frame_count','unique_decoded_frames','adjacent_rms_median','adjacent_rms_max','flags']},indent=2))
