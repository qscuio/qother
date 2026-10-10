"""Resume-safe full chapter assembly. All source narration is used at original speed."""
import os,sys,json,math,time,re,wave,subprocess,importlib.util
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
OUT=None; FPS=24; W,H=1280,720
FONT=None; BOLD=None; fonts={};HOST=None; AUDIO_DIR=None; BOUNDARY_DIR=None; P10_VIDEO=None; TIMELINE={}
PARAS=json.loads((ROOT/'script/paragraphs.json').read_text())['paragraphs']
TITLES=['尚无星辰的宇宙','热密宇宙的膨胀','光，开始远行','岩石的材料尚未齐备','引力点亮恒星','第一批恒星与星系','恒星深处的元素','回到星际空间','孕育太阳的银河','太阳系的形成','年轻太阳附近','尘粒的生长难关','数千万年的吸积','地球内部开始分层','约45.4亿年的年龄','月球的大碰撞解释','月岩留下的证据','地球材料的漫长旅程','历史，尚在开头']
MODULES={}
def configure(args,require_media=False):
 global OUT,FONT,BOLD,fonts,HOST,AUDIO_DIR,BOUNDARY_DIR,P10_VIDEO,TIMELINE
 OUT=args.output.resolve()
 if OUT.exists():raise ValueError('Output must be a new directory; no automatic resume or overwrite')
 timeline=json.loads(args.timeline.read_text());rows=timeline['paragraphs']
 if [r['id'] for r in rows]!=[p['id'] for p in PARAS]:raise ValueError('Timeline must contain exactly P01 through P19, in order')
 for row,para in zip(rows,PARAS):
  if row['text'].strip()!=para['text'].strip():raise ValueError('Timeline text differs from frozen script: '+row['id'])
  if Path(row['filename']).name!=row['filename'] or not row['filename'].endswith('.wav'):raise ValueError('Audio filename must be a plain local WAV basename')
  if not math.isfinite(float(row['duration'])) or row['duration']<=0:raise ValueError('Invalid audio duration')
 TIMELINE={r['id']:r for r in rows}
 candidates=[args.font] if args.font else [Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'),Path('/System/Library/Fonts/PingFang.ttc'),Path('C:/Windows/Fonts/msyh.ttc')]
 FONT=next((str(p) for p in candidates if p and p.is_file()),None)
 if FONT is None:raise ValueError('Supply --font with an installed Chinese font')
 BOLD=str(args.bold_font) if args.bold_font else FONT
 if args.bold_font and not args.bold_font.is_file():raise ValueError('--bold-font does not exist')
 fonts={n:ImageFont.truetype(FONT,n) for n in [15,17,23,30]}
 HOST=Image.open(args.host).convert('RGBA').resize((166,166),Image.Resampling.LANCZOS) if args.host else None
 AUDIO_DIR=args.audio_dir.resolve() if args.audio_dir else None
 BOUNDARY_DIR=args.boundary_dir.resolve() if args.boundary_dir else None
 P10_VIDEO=args.p10_video.resolve() if args.p10_video else None
 if require_media:
  if AUDIO_DIR is None or P10_VIDEO is None:raise ValueError('Full build requires explicit --audio-dir and --p10-video')
  for pid in TIMELINE:audio_info(pid)
  if not P10_VIDEO.is_file():raise ValueError('P10 video does not exist')
 OUT.mkdir(parents=True,exist_ok=False)
 for folder in ['segments','qa']:(OUT/folder).mkdir()
def audio_path(pid):return AUDIO_DIR/TIMELINE[pid]['filename']
def module(pid):
 name='early' if int(pid[1:])<10 else 'late'
 if name not in MODULES:
  spec=importlib.util.spec_from_file_location(name,ROOT/'scenes'/f'{name}.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.FONT=FONT
  if hasattr(mod,'BOLD'):mod.BOLD=BOLD
  mod.font.cache_clear();MODULES[name]=mod
 return MODULES[name]
def audio_info(pid):
 if AUDIO_DIR is None:return float(TIMELINE[pid]['duration']),24000,1
 with wave.open(str(audio_path(pid))) as w:
  if (w.getsampwidth(),w.getframerate(),w.getnchannels())!=(2,24000,1):raise ValueError('Expected int16 mono 24kHz WAV: '+pid)
  seconds=w.getnframes()/w.getframerate()
  if abs(seconds-float(TIMELINE[pid]['duration']))>1/24000:raise ValueError('Audio duration differs from explicit timeline: '+pid)
  return seconds,w.getframerate(),w.getnchannels()
def cues(text,duration,pid=None):
 # Text exactness is mandatory; phrase timing is estimated, not ASR alignment.
 parts=re.findall(r'[^，。；：！？]+[，。；：！？]?|[，。；：！？]',text.strip())
 chunks=[];cur=''
 for p in parts:
  if len(cur+p)>29 and cur:chunks.append(cur);cur=''
  if len(p)>50:
   if cur:chunks.append(cur);cur=''
   while len(p)>28:chunks.append(p[:28]);p=p[28:]
  cur+=p
 if cur:chunks.append(cur)
 assert ''.join(chunks)==text.strip()
 weights=[len(c)+.7*sum(c.count(p) for p in '。；！？') for c in chunks];total=sum(weights)
 out=[];start=0
 for c,w in zip(chunks,weights):
  end=start+duration*w/total;out.append({'start':start,'end':end,'text':c,'timing':'estimated_within_actual_paragraph'});start=end
 if pid:
  bf=BOUNDARY_DIR/f'{pid}.edge.json' if BOUNDARY_DIR else None
  if bf is not None and bf.exists():
   bounds=json.loads(bf.read_text()).get('boundaries',[])
   clean=lambda s:re.sub(r'[^\w\u4e00-\u9fff]','',s)
   source=clean(text);spoken=''.join(clean(b['text']) for b in bounds)
   if spoken==source and bounds:
    char_times=[]
    for b in bounds:
     word=clean(b['text']);char_times.extend([(b['offset']+b['duration']*j/max(len(word),1))/1e7 for j in range(len(word))])
    offset=0
    for item in out:
     item['start']=char_times[offset];offset+=len(clean(item['text']));item['timing']='provider_word_boundary'
    for i,item in enumerate(out):item['end']=out[i+1]['start'] if i+1<len(out) else min(duration,(bounds[-1]['offset']+bounds[-1]['duration'])/1e7+.18)
 return out
def overlay(im,pid,t,raw_duration,cc):
 im=im.convert('RGB');d=ImageDraw.Draw(im)
 d.text((45,34),'地球往事  /  第一章',font=fonts[17],fill='#b7b7aa',stroke_width=1,stroke_fill='#101416')
 d.text((45,68),TITLES[int(pid[1:])-1],font=fonts[23],fill='#e9e5d7',stroke_width=1,stroke_fill='#101416')
 # Fixed original portrait; no generated lip movement or body recomposition.
 if HOST is not None:im.paste(HOST,(1081,527),HOST)
 text=next((c['text'] for c in cc if c['start']<=t<c['end']),cc[-1]['text'] if t<raw_duration+.15 else '')
 if text:
  lines=[];line=''
  for char in text:
   if d.textlength(line+char,font=fonts[30])>970:lines.append(line);line=''
   line+=char
  if line:lines.append(line)
  assert len(lines)<=2
  y=620 if len(lines)==2 else 640
  for line in lines:
   d.text((45,y),line,font=fonts[30],fill='#f4f2e9',stroke_width=3,stroke_fill='#101416');y+=42
 d.text((45,692),'科学示意 · 时间压缩 · 非比例',font=fonts[15],fill='#93988f',stroke_width=1,stroke_fill='#101416')
 return im

def render_scene(pid,preview=False):
 raw,sr,ch=audio_info(pid);duration=math.ceil((raw+(1.0 if pid=='P19' else .45))*FPS)/FPS
 nframes=round(duration*FPS);cc=cues(next(p['text'] for p in PARAS if p['id']==pid),raw,pid)
 target=OUT/'segments'/f'{pid}.mp4';meta=target.with_suffix('.json')
 if target.exists() or meta.exists():raise FileExistsError('Refusing duplicate render: '+pid)
 m=module(pid);start=time.monotonic();samples=[]
 for p in [.03,.5,.95]:
  t=p*raw;tic=time.monotonic();im=overlay(m.render(pid,p,W,H),pid,t,raw,cc);samples.append(time.monotonic()-tic);im.save(OUT/'qa'/f'{pid}-{round(p*100):02d}.png')
 speed=sum(samples)/len(samples)
 result={'id':pid,'narration_duration':raw,'duration':duration,'frames':nframes,'cues':cc,'three_frame_average_seconds':speed,'source_visual_fps':24}
 if preview: print(json.dumps(result,ensure_ascii=False));return result
 log=open(OUT/'segments'/f'{pid}.log','w')
 cmd=['ffmpeg','-hide_banner','-loglevel','warning','-n','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','24','-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','12288','-movflags','+faststart',str(target.with_name(pid+'.partial.mp4'))]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
 try:
  for f in range(nframes):
   t=f/FPS;p=min(t/raw,1);im=overlay(m.render(pid,p,W,H),pid,t,raw,cc);proc.stdin.write(im.tobytes())
   if f%240==0:(OUT/'progress.json').write_text(json.dumps({'paragraph':pid,'frame':f,'total_frames':nframes,'elapsed_seconds':time.monotonic()-start}))
  proc.stdin.close();rc=proc.wait()
  if rc:raise RuntimeError(f'ffmpeg {pid} return {rc}')
 except:proc.kill();raise
 target.with_name(pid+'.partial.mp4').replace(target)
 result['render_wall_seconds']=time.monotonic()-start;meta.write_text(json.dumps(result,ensure_ascii=False,indent=2));print(f'DONE {pid}: {duration:.2f}s in {result["render_wall_seconds"]:.1f}s',flush=True);return result

def p10():
 target=OUT/'segments/P10.mp4';meta=target.with_suffix('.json')
 raw=audio_info('P10')[0];duration=math.ceil((raw+.45)*FPS)/FPS;nframes=round(duration*FPS)
 if target.exists() or meta.exists():raise FileExistsError('Refusing duplicate P10 render')
 source_probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_frames,duration','-of','json',str(P10_VIDEO)]))['streams'][0]
 if (source_probe['width'],source_probe['height'],source_probe['r_frame_rate'])!=(1280,720,'24/1') or abs(float(source_probe['duration'])-551/24)>.01:raise ValueError('Expected original 551-frame 720p24 P10 visual clip')
 if True:
  subprocess.run(['ffmpeg','-v','error','-n','-i',str(P10_VIDEO),'-map','0:v:0','-an','-vf',f'setpts={duration/(551/24):.12f}*PTS,fps=24','-frames:v',str(nframes),'-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','12288',str(target)],check=True)
 result={'id':'P10','narration_duration':raw,'duration':duration,'frames':nframes,'source_visual_fps':24,'reuse':'Existing P10 visuals uniformly retimed; original baked subtitle timing approximate; old audio removed. No second overlay','cues':cues(PARAS[9]['text'],raw,'P10')};meta.write_text(json.dumps(result,ensure_ascii=False,indent=2));return result

