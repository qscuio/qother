"""Independent shot cache and final assembly. No network or speech synthesis.

Cached clips contain only local-time visual layers. Audio, captions, global
progress and transitions are applied at assembly; upstream timing shifts do not
invalidate unrelated same-duration shots. Demo inputs remain visibly marked.
"""
import argparse,ast,bisect,hashlib,inspect,json,math,os,subprocess,tempfile
from pathlib import Path
from PIL import Image,ImageDraw,__version__ as PILLOW_VERSION
import render as art
from cue_validation import validate_cues,normalized_text
W,H,FPS=art.W,art.H,art.FPS
HANDLES=12
FRAME_BYTES=W*H*3

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def jsonwrite(path,data):
 path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2));tmp.replace(path)
def probe(path):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]))
def assert_media(path,frames):
 p=probe(path);v=[s for s in p['streams'] if s['codec_type']=='video'];assert len(v)==1,'Expected one video stream'
 v=v[0];assert (v['width'],v['height'],v['r_frame_rate'])==(W,H,f'{FPS}/1'),'Clip dimensions/fps differ'
 assert int(v['nb_read_frames'])==frames,f'Frame count mismatch: {v.get("nb_read_frames")} != {frames}'
 return p

def load_board(path):
 b=json.loads(Path(path).read_text());assert (b['width'],b['height'],b['fps'])==(W,H,FPS),'Unsupported render specification'
 assert b.get('mode') in ['production','demo'];assert b['shots'],'No shots'
 if b['mode']=='demo':assert b.get('test_fixture') is True,'Demo input must explicitly be a test fixture'
 last=0;ids=set()
 for s in b['shots']:
  r=s['render'];assert s['shot_id'] not in ids;ids.add(s['shot_id'])
  assert r['start_frame']==last and r['end_frame']>last,'Noncontiguous timeline'
  assert r['kind'] in art.CHAPTERS;assert len(r['p_range'])==2
  last=r['end_frame']
 assert abs(b['duration_s']*FPS-last)<1e-6,'Duration mismatch'
 return b

def select_shots(board,ids=None):
 if not ids:return board['shots']
 ids=set(ids);result=[s for s in board['shots'] if s['shot_id'] in ids]
 assert len(result)==len(ids),'Unknown shot ID'
 return result

def scene_source_hash(kind,source=None):
 # Separate the selected scene branch from unrelated branches. Shared helpers,
 # composition and common initialization still invalidate every dependent clip.
 source=source if source is not None else Path(art.__file__).read_text()
 tree=ast.parse(source);common=[];chosen=None;chapter=None
 def scene_if(node):
  return isinstance(node,ast.If) and isinstance(node.test,ast.Compare) and isinstance(node.test.left,ast.Name) and node.test.left.id=='kind' and len(node.test.comparators)==1 and isinstance(node.test.comparators[0],ast.Constant)
 for node in tree.body:
  if isinstance(node,ast.FunctionDef) and node.name in ['preview','render_full']:continue
  if isinstance(node,ast.If) and isinstance(node.test,ast.Compare) and isinstance(node.test.left,ast.Name) and node.test.left.id=='__name__':continue
  if isinstance(node,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='CHAPTERS' for x in node.targets):
   chapter=ast.literal_eval(node.value)[kind];continue
  if isinstance(node,ast.FunctionDef) and node.name=='draw_scene':
   for stmt in node.body:
    if scene_if(stmt):
     branch=stmt
     while scene_if(branch):
      if branch.test.comparators[0].value==kind:chosen=[ast.dump(x,include_attributes=False) for x in branch.body]
      branch=branch.orelse[0] if len(branch.orelse)==1 else None
    else:common.append(ast.dump(stmt,include_attributes=False))
  else:common.append(ast.dump(node,include_attributes=False))
 assert chosen is not None and chapter is not None,'Scene dependency fingerprint not found'
 return hashlib.sha256(json.dumps({'common':common,'scene':chosen,'chapter':chapter},sort_keys=True).encode()).hexdigest()

def signature(shot,host,fixture):
 r=shot['render']
 return dict(version=1,pillow_version=PILLOW_VERSION,cache_algorithm_sha256=hashlib.sha256(inspect.getsource(render_shot).encode()).hexdigest(),renderer_component_sha256=scene_source_hash(r['kind']),font_sha256=[digest(art.FONT),digest(art.BOLD)],host_sha256=digest(host),width=W,height=H,fps=FPS,handles=HANDLES,shot_id=shot['shot_id'],frames=r['end_frame']-r['start_frame'],kind=r['kind'],act=r['act'],p_range=r['p_range'],visual_revision=r.get('visual_revision','1'),test_fixture=fixture,encoding={'codec':'ffv1','pixel_format':'bgr0'})
def cache_key(sig):return hashlib.sha256(json.dumps(sig,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def cache_paths(cache,key):return Path(cache)/(key+'.mkv'),Path(cache)/(key+'.json')
def read_frame(proc):
 raw=bytearray()
 while len(raw)<FRAME_BYTES:
  part=proc.stdout.read(FRAME_BYTES-len(raw))
  if not part:break
  raw.extend(part)
 if not raw:return None
 assert len(raw)==FRAME_BYTES,'Truncated decoded frame'
 return Image.frombytes('RGB',(W,H),bytes(raw))

def render_shot(shot,host,cache,fixture=False):
 cache=Path(cache);cache.mkdir(parents=True,exist_ok=True);sig=signature(shot,host,fixture);key=cache_key(sig);clip,meta=cache_paths(cache,key)
 expected=sig['frames']+2*HANDLES
 if clip.exists() and meta.exists():
  old=json.loads(meta.read_text())
  if old.get('signature')==sig and old.get('clip_sha256')==digest(clip):
   assert_media(clip,expected)
   return {'shot_id':shot['shot_id'],'cache_key':key,'cache_hit':True,'clip':str(clip),'content_frames':sig['frames']}
 art.configure_host(host);tmp=clip.with_suffix('.partial.mkv');log=clip.with_suffix('.encode.log')
 cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','ffv1','-level','3','-pix_fmt','bgr0',str(tmp)]
 with log.open('wb') as err:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=err)
  try:
   for local_frame in range(-HANDLES,sig['frames']+HANDLES):
    u=max(0,min(1,local_frame/max(1,sig['frames']-1)));p=art.lerp(*sig['p_range'],u)
    im=art.compose(sig['kind'],p,local_frame/FPS,sig['act'],'',True,0,timeline_overlay=False)
    if fixture:art.txt(ImageDraw.Draw(im),(W//2,130),'TEST FIXTURE · 非正式样片',23,art.OCHRE,anchor='mm')
    proc.stdin.write(im.tobytes())
   proc.stdin.close();assert proc.wait()==0,'Shot encoder failed'
  except BaseException:
   proc.kill();proc.wait();raise
 assert_media(tmp,expected);tmp.replace(clip)
 jsonwrite(meta,{'signature':sig,'clip_sha256':digest(clip),'frames_including_handles':expected,'test_fixture':fixture})
 return {'shot_id':shot['shot_id'],'cache_key':key,'cache_hit':False,'clip':str(clip),'content_frames':sig['frames']}

def render_selected(board,host,cache,ids=None):
 return [render_shot(s,host,cache,board['mode']=='demo') for s in select_shots(board,ids)]

def overlay(im,caption,progress,fixture):
 d=ImageDraw.Draw(im);bg=im.getpixel((0,650));fg=art.LIGHT if sum(bg)<300 else art.INK
 # This area is intentionally kept blank in all cached scenes.
 d.rectangle((0,618,W,H),fill=bg)
 if caption:
  assert len(caption)<=74,'Subtitle cue too long; split into measured clauses first'
  rows=[caption[i:i+37] for i in range(0,len(caption),37)]
  for i,row in enumerate(rows):art.txt(d,(640,637+i*33),row,26,fg,anchor='mt')
 art.line(d,[(42,709),(1238,709)],art.MUTED,2);art.line(d,[(42,709),(42+1196*progress,709)],art.OCHRE,2)
 if fixture:art.txt(d,(W//2,130),'TEST FIXTURE · 非正式样片',23,art.OCHRE,anchor='mm')
 return im

def assemble(board,host,cache,audio,subtitles,output,ids=None):
 shots=select_shots(board,ids)
 for a,b in zip(shots,shots[1:]):assert a['render']['end_frame']==b['render']['start_frame'],'Assembly selection must be contiguous'
 start=shots[0]['render']['start_frame'];end=shots[-1]['render']['end_frame'];total=end-start;fixture=board['mode']=='demo'
 if not fixture:
  assert not board.get('test_fixture'),'Fixture cannot become production'
  assert board.get('audio_sha256')==digest(audio),'Audio differs from locked storyboard'
  assert board.get('subtitle_sha256')==digest(subtitles),'Subtitles differ from locked storyboard'
 cues=json.loads(Path(subtitles).read_text())
 audio_duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(audio)]))
 validate_cues(cues,audio_duration)
 if not fixture:assert board.get('subtitle_text_sha256')==hashlib.sha256(normalized_text(''.join(c['text'] for c in cues)).encode()).hexdigest(),'Subtitle text coverage differs from locked text'
 cstarts=[c['start'] for c in cues]
 # Assembly never silently redraws missing shots. Export/replacement is explicit.
 entries=[]
 for s in shots:
  sig=signature(s,host,fixture);key=cache_key(sig);clip,meta=cache_paths(cache,key)
  assert clip.exists() and meta.exists(),f'Missing cached shot: {s["shot_id"]}; render it first'
  m=json.loads(meta.read_text());assert m['signature']==sig and m['clip_sha256']==digest(clip),'Invalid cache entry'
  assert_media(clip,sig['frames']+2*HANDLES);entries.append((s,clip,sig))
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 if fixture:assert 'test' in output.stem.lower() or 'fixture' in output.stem.lower(),'Test output filename must say test or fixture'
 tmp=output.with_suffix('.partial.mp4');log=output.with_suffix('.encode.log')
 cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-ss',str(start/FPS),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','96k','-af','apad','-t',str(total/FPS),'-movflags','+faststart',str(tmp)]
 written=0;prev_tail=[];prev_kind=None
 with log.open('wb') as err:
  enc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=err)
  try:
   for shot,clip,sig in entries:
    dec=subprocess.Popen(['ffmpeg','-v','error','-i',str(clip),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
     for _ in range(HANDLES):assert read_frame(dec) is not None
     for n in range(sig['frames']):
      im=read_frame(dec);assert im is not None,'Missing cached content frame'
      if prev_tail and n<min(HANDLES,sig['frames']) and prev_kind!=sig['kind']:
       old=prev_tail[n];alpha=art.ease(n/(HANDLES-1))
       if art.CHAPTERS[prev_kind][0]!=art.CHAPTERS[sig['kind']][0]:
        old=old.copy();x=round(W*alpha);old.paste(im.crop((0,0,x,H)),(0,0));im=old
       else:im=Image.blend(old,im,alpha)
      global_frame=shot['render']['start_frame']+n;t=global_frame/FPS;ci=bisect.bisect_right(cstarts,t)-1
      cap=cues[ci]['text'] if ci>=0 and t<cues[ci]['end']+.05 else ''
      im=overlay(im,cap,written/max(1,total-1),fixture);enc.stdin.write(im.tobytes());written+=1
     prev_tail=[read_frame(dec) for _ in range(HANDLES)];assert all(x is not None for x in prev_tail)
     assert read_frame(dec) is None,'Unexpected extra cache frames';assert dec.wait()==0,'Cache decoder failed';prev_kind=sig['kind']
    finally:
     if dec.poll() is None:dec.kill();dec.wait()
   enc.stdin.close();assert enc.wait()==0,'Assembly encoder failed'
  except BaseException:
   enc.kill();enc.wait();raise
 assert written==total;media=assert_media(tmp,total);assert any(s['codec_type']=='audio' for s in media['streams'])
 subprocess.run(['ffmpeg','-v','error','-i',str(tmp),'-f','null','-'],check=True)
 tmp.replace(output)
 report={'test_fixture':fixture,'shot_ids':[s['shot_id'] for s in shots],'frames':written,'duration_s':total/FPS,'source_start_frame':start,'width':W,'height':H,'fps':FPS,'decoded_all':True,'output_sha256':digest(output),'audio_sha256':digest(audio)}
 jsonwrite(output.with_suffix('.qa.json'),report);return report

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['render','assemble']);p.add_argument('--storyboard',type=Path,required=True);p.add_argument('--host',type=Path,required=True);p.add_argument('--cache',type=Path,required=True);p.add_argument('--shot-ids',nargs='*');p.add_argument('--audio',type=Path);p.add_argument('--subtitles',type=Path);p.add_argument('--output',type=Path);p.add_argument('--report',type=Path);a=p.parse_args();board=load_board(a.storyboard)
 if a.action=='render':result=render_selected(board,a.host,a.cache,a.shot_ids)
 else:
  assert a.audio and a.subtitles and a.output,'Assembly requires audio, subtitles and output';result=assemble(board,a.host,a.cache,a.audio,a.subtitles,a.output,a.shot_ids)
 if a.report:jsonwrite(a.report,result)
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
