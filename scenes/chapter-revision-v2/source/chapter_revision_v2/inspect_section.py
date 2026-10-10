"""Decode rendered section and extract evidence; not a human viewing/listening claim."""
import subprocess,json,hashlib,sys,wave
from scipy.signal import correlate
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from compositor import R,OLD,ALL_ROWS

def inspect(pid):
 row=ALL_ROWS[pid];video=R/'output/segments'/f'{pid}.mp4';out=R/'qa/sections'/pid;out.mkdir(parents=True,exist_ok=True)
 dec=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True);assert dec.returncode==0,dec.stderr
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));s=probe['streams'][0]
 times=sorted(set([0,row['duration']-1/24]+[round((row['narration_duration'] or row['duration'])*p,4) for p in [.03,.15,.25,.35,.5,.65,.75,.85,.97]]+[max(0,c['start']-.05) for c in row['cues']]))
 samples=[]
 for n,t in enumerate(times):
  target=out/f'{n:02d}-{t:06.2f}s.png';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(video),'-frames:v','1',str(target)],check=True);samples.append({'time':t,'file':str(target.relative_to(R)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
 cols=3;thumb_w=426;thumb_h=264;sheet=Image.new('RGB',(cols*thumb_w,((len(samples)+cols-1)//cols)*thumb_h),'#080d12');d=ImageDraw.Draw(sheet)
 for i,sample in enumerate(samples):
  x=i%cols*thumb_w;y=i//cols*thumb_h;im=Image.open(R/sample['file']).resize((426,240));sheet.paste(im,(x,y));d.text((x+10,y+243),f'{pid} {sample["time"]:.3f}s',fill='white')
 sheet.save(out/'decoded-contact-sheet.jpg',quality=92)
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-vf','scale=160:90','-pix_fmt','gray','-f','rawvideo','-']);a=np.frombuffer(raw,'uint8').reshape(-1,90,160).astype(np.int16);diff=np.abs(np.diff(a,axis=0)).mean(axis=(1,2));zeros=np.where(diff==0)[0].tolist()
 result={'id':pid,'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'full_decode':'pass','frames':len(a),'expected_frames':row['frames'],'dimensions':[s['width'],s['height']],'fps':s['avg_frame_rate'],'difference_min_mean_max':[float(diff.min()),float(diff.mean()),float(diff.max())],'zero_difference_frame_pairs':zeros,'difference_resolution':[160,90],'difference_interpretation':'Downsampled grayscale equality, not exact full-resolution equality or proof of a freeze','samples':samples,'actual_visual_review':'not-run by this script','continuous_playback':'not-run','audio_content_listening':'not-run'}
 (out/'decode-report.json').write_text(json.dumps(result,indent=2))
 if pid!='INSERT-MW':
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-i',str(OLD/'audio'/f'{pid}.edge.wav'),'-filter:a','volume=-1dB,apad','-t',str(row['duration']),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out/f'{pid}-with-current-narration-review.mp4')],check=True)
 if pid!='INSERT-MW':
  mux=out/f'{pid}-with-current-narration-review.mp4'
  audio=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(mux),'-map','0:a:0','-ar','24000','-ac','1','-f','s16le','-']),'<i2').astype(float)/32768
  with wave.open(str(OLD/'audio'/f'{pid}.edge.wav')) as w:
   assert w.getframerate()==24000 and w.getnchannels()==1
   src=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768
  pad=2400;segment=np.pad(audio,(pad,pad));corr=correlate(segment,src,mode='valid',method='fft');lag=int(np.argmax(corr))-pad
  aligned=segment[pad+lag:pad+lag+len(src)]
  result['audio_binding']={'waveform_lag_samples':lag,'waveform_lag_seconds':lag/24000,'correlation':float(np.corrcoef(src,aligned)[0,1]),'gain_expected_db':-1,'peak':float(np.max(np.abs(audio))),'subtitle_text_exact':''.join(c['text'] for c in row['cues'])==row['source_text'],'timing':'existing provider word boundaries; not perceptually verified','mux_sha256':hashlib.sha256(mux.read_bytes()).hexdigest()}
  (out/'decode-report.json').write_text(json.dumps(result,indent=2))
 print(json.dumps({k:v for k,v in result.items() if k!='samples'},indent=2))
if __name__=='__main__':inspect(sys.argv[1])
