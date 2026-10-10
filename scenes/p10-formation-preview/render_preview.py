"""P10 preview: original-speed narration, estimated sentence timing."""
import json,time,math,subprocess,hashlib,argparse,wave
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.interpolate import PchipInterpolator
import scene_renderer as scene
P=Path(__file__).parent
FPS=24; AUDIO_SECONDS=22.456875; N=math.ceil((AUDIO_SECONDS+.5)*FPS); DURATION=N/FPS
AUDIO_CUES=[0,3.49,9.62,17.89,AUDIO_SECONDS]
MODEL_CUES=[0,5,13,23,28]
warp=PchipInterpolator(AUDIO_CUES,MODEL_CUES)
SENTENCES=['约四十六亿年前，云团开始收缩。','它一边转动，一边向内聚拢，逐渐形成扁平的盘。','大部分物质汇向中央，孕育太阳；周围的物质则在盘中继续聚集。','太阳还在形成，行星的生长也已经开始。']
LINES=[[SENTENCES[0]],[SENTENCES[1]],['大部分物质汇向中央，孕育太阳；','周围的物质则在盘中继续聚集。'],[SENTENCES[3]]]
font=None;f14=None
def make_frame(f):
 seconds=f/FPS;modelt=float(warp(min(seconds,AUDIO_SECONDS)));im=scene.render(modelt)
 which=min(int(np.searchsorted(AUDIO_CUES,seconds,side='right')-1),3)
 d=ImageDraw.Draw(im);d.text((997,35),'样例 · 字幕时序待精校',font=f14,fill=(168,169,161))
 lines=LINES[which];ys=[620] if len(lines)==1 else [594,635]
 # Occupy the existing frame, staying left of the host circle; no blank footer.
 for line,y in zip(lines,ys):
  width=d.textlength(line,font=font);left=540-width/2
  d.text((left,y),line,font=font,fill=(244,241,227),stroke_width=2,stroke_fill=(5,8,10))
 return im,modelt

def stamp(t):
 ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
 return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',type=Path,required=True,help='New output directory')
 parser.add_argument('--audio',type=Path,help='Explicit local PCM WAV, original speed; required for video')
 parser.add_argument('--host-image',type=Path,help='Optional authorized square portrait')
 parser.add_argument('--font',type=Path)
 parser.add_argument('--frame',type=int,choices=range(N),metavar='0..550',help='Single subtitle-bearing frame; does not need audio')
 args=parser.parse_args();O=args.output
 if O.exists():parser.error('--output must not already exist')
 if args.frame is None and args.audio is None:parser.error('--audio is required for video; no narration is bundled or synthesized')
 if args.audio is not None:
  with wave.open(str(args.audio),'rb') as wav:
   actual_audio_seconds=wav.getnframes()/wav.getframerate()
   if (wav.getnchannels(),wav.getsampwidth(),wav.getframerate())!=(1,2,24000):parser.error('Expected mono 24kHz int16 PCM WAV for this fixed preview')
  if abs(actual_audio_seconds-AUDIO_SECONDS)>.01:parser.error('Audio length differs from the fixed unverified cue template; revise and review cue timing before using this source')
 O.mkdir(parents=True,exist_ok=False);scene.configure(args.host_image,args.font)
 font=ImageFont.truetype(scene.font,30);f14=ImageFont.truetype(scene.font,14)
 if args.frame is not None:
  started=time.perf_counter();im,modeltime=make_frame(args.frame);im.save(O/f'frame-{args.frame:03d}.png')
  (O/'single-frame-metrics.json').write_text(json.dumps({'frame':args.frame,'model_time':modeltime,'render_and_save_seconds':time.perf_counter()-started,'host_enabled':scene.host is not None,'audio_used':False,'subtitle_timing':'estimated, unverified'},indent=2))
  raise SystemExit(0)
 timings={'status':'estimated_pause_based_not_ASR_verified','audio_seconds':AUDIO_SECONDS,'video_seconds':DURATION,'audio_cues':AUDIO_CUES,'model_cues':MODEL_CUES,'interpolation':'monotone PCHIP','sentences':SENTENCES,'audio_speed':1.0,'audio_gain_db':-1,'host_enabled':scene.host is not None,'host':'optional static portrait; no lip sync'}
 (O/'estimated-timings.json').write_text(json.dumps(timings,ensure_ascii=False,indent=2))
 (O/'estimated-subtitles.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(AUDIO_CUES[i])} --> {stamp(AUDIO_CUES[i+1] if i<3 else DURATION)}\n'+ '\n'.join(LINES[i]) for i in range(4)))
 cmd=['ffmpeg','-n','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r',str(FPS),'-i','-','-i',str(args.audio),'-map','0:v:0','-map','1:a:0','-filter:a','volume=-1dB,apad','-t',str(DURATION),'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(O/'P10-section-preview-v2.mp4')]
 start=time.perf_counter();proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 sampled={0,84,228,360,480,N-1};prev=None;diffs=[];modeltimes=[];zero_run=0;maxzero=0
 for f in range(N):
  im,t=make_frame(f);modeltimes.append(t);proc.stdin.write(im.tobytes())
  roi=np.asarray(im)[130:565,170:1035].astype(np.int16)
  if prev is not None:
   delta=float(np.mean(np.abs(roi-prev)));diffs.append(delta);zero_run=zero_run+1 if delta==0 else 0;maxzero=max(maxzero,zero_run)
  prev=roi
  if f in sampled:im.save(O/f'sample-{f:03d}.png')
  if f%48==0:print(json.dumps({'frame':f,'total':N,'elapsed':round(time.perf_counter()-start,2),'model_t':round(t,3)}),flush=True)
 proc.stdin.close();assert proc.wait()==0
 result={'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scene_source_sha256':hashlib.sha256((P/'scene_renderer.py').read_bytes()).hexdigest(),'audio_input_sha256':hashlib.sha256(args.audio.read_bytes()).hexdigest(),'host_enabled':scene.host is not None,'frames':N,'fps':FPS,'duration':DURATION,'render_and_encode_seconds':round(time.perf_counter()-start,3),'model_times_monotone':bool(np.all(np.diff(modeltimes)>=0)),'adjacent_scene_roi_mean_abs_diff':{'mean':float(np.mean(diffs)),'max':max(diffs),'max_at_frame':int(np.argmax(diffs)+1),'median':float(np.median(diffs)),'max_identical_run_frames':maxzero},'sample_frames':sorted(sampled),'fullspeed_playback':'not-run','narration_transcript_verified':False,'subtitle_timing':'estimated'}
 (O/'render-metrics.json').write_text(json.dumps(result,indent=2));np.save(O/'adjacent-scene-differences.npy',np.array(diffs));print(json.dumps(result),flush=True)
