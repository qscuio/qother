"""Encode precisely 48 actual rendered PNGs without interpolation or denoising."""
from pathlib import Path
import subprocess,json,hashlib,struct
import argparse
_parser=argparse.ArgumentParser(description=__doc__)
_parser.add_argument('--output',type=Path,required=True,help='Existing scene output directory')
_args=_parser.parse_args()
D=_args.output.resolve();O=D/'camera-motion-48';F=O/'frames'
paths=[F/('frame-%03d.png'%i) for i in range(1,49)]
for p in paths:
 data=p.read_bytes()
 if data[:8]!=b'\x89PNG\r\n\x1a\n' or struct.unpack('>II',data[16:24])!=(1280,720):raise RuntimeError('Invalid/missing rendered frame: '+str(p))
output=O/'H10-actual-3D-camera-test-2s.mp4'
subprocess.run(['ffmpeg','-n','-hide_banner','-loglevel','error','-framerate','24','-start_number','1','-i',str(F/'frame-%03d.png'),'-frames:v','48','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],check=True)
r=subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(output)],check=True,text=True,capture_output=True)
probe=json.loads(r.stdout);st=probe['streams'][0]
assert st['width']==1280 and st['height']==720 and st['r_frame_rate']=='24/1' and st['nb_read_frames']=='48' and abs(float(st['duration'])-2)<.001
manifest={'file':output.name,'encoding_verified':probe,'frame_origin':'Expected render_camera_batch.py output; PNG format alone does not verify origin','interpolation':False,'denoising':False,'world_state':'unchanged','purpose':'Technical camera-motion demonstration only, not physical evolution or finished science film','visual_playback_QA':'pending','source_frames':[{'frame':i,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for i,p in enumerate(paths,1)]}
(O/'encoding-QA.json').write_text(json.dumps(manifest,indent=2));print(output)
