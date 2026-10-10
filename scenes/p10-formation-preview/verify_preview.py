import subprocess,json,hashlib,argparse
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import correlate,correlation_lags
parser=argparse.ArgumentParser(description='Decode verification only, not narration recognition or playback review.')
parser.add_argument('--video',type=Path,required=True)
parser.add_argument('--audio',type=Path,required=True,help='Original mono 24kHz int16 PCM WAV')
parser.add_argument('--output',type=Path,required=True,help='New diagnostic directory')
parser.add_argument('--render-metrics',type=Path)
args=parser.parse_args();v=args.video;O=args.output
if not v.is_file() or not args.audio.is_file():parser.error('Video and original audio must exist')
O.mkdir(parents=True,exist_ok=False)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(v)]))
if 'filename' in probe.get('format',{}):probe['format']['filename']=v.name
# Full decode checks both streams, without claiming real-time viewing.
r=subprocess.run(['ffmpeg','-v','error','-i',str(v),'-f','null','-'],capture_output=True,text=True)
assert r.returncode==0 and not r.stderr,r.stderr
subprocess.run(['ffmpeg','-v','error','-i',str(v),'-vf',"select='eq(n,0)+eq(n,84)+eq(n,228)+eq(n,360)+eq(n,480)+eq(n,550)'",'-vsync','0',str(O/'decoded-%02d.png')],check=True)
dec=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(v),'-map','0:a:0','-ar','24000','-ac','1','-f','f32le','-']),dtype=np.float32)
sr,orig=wavfile.read(args.audio)
assert sr==24000 and orig.ndim==1 and orig.dtype==np.int16, 'Expected mono 24kHz int16 PCM reference WAV'
orig=orig.astype(np.float64)/32768
# Short-lag correlation distinguishes codec priming from an actual sync shift.
a=dec[:min(len(dec),len(orig))];b=orig[:len(a)]*10**(-1/20)
corr=correlate(a[:sr*5],b[:sr*5],mode='full',method='fft');lags=correlation_lags(min(len(a),sr*5),min(len(b),sr*5),mode='full');near=np.abs(lags)<1024;lag=int(lags[near][np.argmax(corr[near])])
qa={'full_decode':'pass','ffprobe':probe,'decoded_samples':6,'decoded_audio_finite':bool(np.isfinite(dec).all()),'decoded_audio_peak':float(np.max(np.abs(dec))),'decoded_audio_samples_at_or_over_full_scale':int(np.sum(np.abs(dec)>=1)),'audio_correlation_estimated_lag_samples':lag,'audio_lag_ms':lag/24,'audio_speed':1,'subtitles':'estimated pause-based, not forced aligned','narration_transcript_verified':False,'fullspeed_playback':'not evaluated by this decode verification utility','render_metrics':json.loads(args.render_metrics.read_text()) if args.render_metrics else None}
assert qa['decoded_audio_finite'] and qa['decoded_audio_samples_at_or_over_full_scale']==0
streams=probe['streams'];vid=next(s for s in streams if s['codec_type']=='video');aud=next(s for s in streams if s['codec_type']=='audio')
assert (vid['width'],vid['height'],vid['r_frame_rate'],int(vid['nb_frames']))==(1280,720,'24/1',551)
assert abs(float(vid['start_time'])-float(aud['start_time']))<1/24
(O/'final-qa.json').write_text(json.dumps(qa,indent=2))
print(json.dumps({k:vv for k,vv in qa.items() if k!='ffprobe'},indent=2))
