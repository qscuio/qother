"""Short, conspicuously marked fixture tests. Never synthesizes speech.
Usage: python test_shot_pipeline.py --host PRIVATE_GUIDE_PNG --output-dir TEST_DIR
All generated videos say TEST FIXTURE and are not user preview deliverables.
"""
import argparse,array,copy,json,math,subprocess,tempfile,wave
from PIL import Image,ImageDraw,ImageChops
from pathlib import Path
import shot_pipeline as p

def rejected(fn,label):
 try:fn()
 except (AssertionError,ValueError):return label
 raise AssertionError('Expected rejection: '+label)

def main():
 a=argparse.ArgumentParser();a.add_argument('--host',type=Path,required=True);a.add_argument('--output-dir',type=Path,required=True);args=a.parse_args();out=args.output_dir;out.mkdir(parents=True,exist_ok=True);cache=Path(tempfile.mkdtemp(prefix='test-cache-',dir=out))
 specs=[('T01','expansion',24),('T02','nebula',36),('T03','moon',24)];shots=[];start=0
 for sid,kind,n in specs:
  shots.append({'shot_id':sid,'render':{'start_frame':start,'end_frame':start+n,'kind':kind,'act':0,'p_range':[0,1],'visual_revision':'fixture-1'}});start+=n
 board={'mode':'demo','test_fixture':True,'width':1280,'height':720,'fps':24,'duration_s':start/24,'shots':shots};bp=out/'test-storyboard.json';p.jsonwrite(bp,board);board=p.load_board(bp)
 # An individual shot ID can be exported before any other clip exists.
 single=p.render_selected(board,args.host,cache,['T01']);assert len(single)==1 and not single[0]['cache_hit']
 audio=out/'test-silence-not-narration.wav'
 with wave.open(str(audio),'wb') as w:w.setparams((1,2,24000,0,'NONE','not compressed'));w.writeframes(b'\0\0'*int(board['duration_s']*24000))
 cues=out/'test-subtitles.json';p.jsonwrite(cues,[{'start':0,'end':1,'text':'测试片段一：非正式配音。'},{'start':1,'end':2.5,'text':'测试片段二：检查缓存与替换。'},{'start':2.5,'end':3.5,'text':'测试片段三：检查拼接完整性。'}])
 checks=[rejected(lambda:p.assemble(board,args.host,cache,audio,cues,out/'test-missing.mp4'),'Missing shot fails without silent redraw')]
 first=p.render_selected(board,args.host,cache);assert [x['cache_hit'] for x in first]==[True,False,False]
 second=p.render_selected(board,args.host,cache);assert all(x['cache_hit'] for x in second);assert [x['cache_key'] for x in first]==[x['cache_key'] for x in second]
 changed=copy.deepcopy(board);changed['shots'][1]['render']['p_range']=[.2,.8];changed['shots'][1]['render']['visual_revision']='fixture-2'
 replaced=p.render_selected(changed,args.host,cache);assert [x['cache_hit'] for x in replaced]==[True,False,True];assert replaced[0]['cache_key']==first[0]['cache_key'] and replaced[2]['cache_key']==first[2]['cache_key'];assert replaced[1]['cache_key']!=first[1]['cache_key']
 # Changing one scene's code leaves other scene cache identities untouched.
 source=Path(p.art.__file__).read_text();edited=source.replace("q=ease(p);cx,cy=680,365","q=ease(p);cx,cy=681,365")
 assert edited!=source
 assert p.scene_source_hash('collapse',source)!=p.scene_source_hash('collapse',edited)
 assert p.scene_source_hash('expansion',source)==p.scene_source_hash('expansion',edited)
 # Absolute timeline shifts do not invalidate unchanged later visual content.
 shifted=copy.deepcopy(changed)
 for s in shifted['shots'][1:]:s['render']['start_frame']+=12;s['render']['end_frame']+=12
 for i in [1,2]:assert p.signature(shifted['shots'][i],args.host,True)==p.signature(changed['shots'][i],args.host,True)
 full=p.assemble(changed,args.host,cache,audio,cues,out/'test-assembled.mp4');assert full['frames']==84 and full['duration_s']==3.5
 subset=p.assemble(changed,args.host,cache,audio,cues,out/'test-subset.mp4',['T01','T02']);assert subset['frames']==60 and subset['duration_s']==2.5
 later=p.assemble(changed,args.host,cache,audio,cues,out/'test-later-subset.mp4',['T02','T03']);assert later['frames']==60 and later['source_start_frame']==24
 checks.append(rejected(lambda:p.assemble(changed,args.host,cache,audio,cues,out/'test-noncontiguous.mp4',['T01','T03']),'Noncontiguous assembly selection rejected'))
 checks.append(rejected(lambda:p.assemble(changed,args.host,cache,audio,cues,out/'final.mp4'),'Fixture output without test filename rejected'))
 wrong=out/'test-wrong-size-fps.mp4';subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=black:s=320x180:r=12','-frames:v','10',str(wrong)],check=True)
 checks.append(rejected(lambda:p.assert_media(wrong,10),'Wrong dimensions/frame rate rejected'))
 checks.append(rejected(lambda:p.assert_media(first[0]['clip'],999),'Wrong frame count rejected'))
 # Locked production audio identity is enforced; no production artifact is exported.
 locked=copy.deepcopy(changed);locked['mode']='production';locked['test_fixture']=False;locked['audio_sha256']='0'*64
 checks.append(rejected(lambda:p.assemble(locked,args.host,cache,audio,cues,out/'test-wrong-audio.mp4'),'Wrong production audio hash rejected'))
 # Exercise the within-chapter dissolve as well as the chapter wipe above.
 dissolve_board=copy.deepcopy(changed);dissolve_board['duration_s']=2
 dissolve_board['shots']=[{'shot_id':'T04','render':{'start_frame':0,'end_frame':24,'kind':'impact','act':0,'p_range':[0,1],'visual_revision':'fixture-1'}},copy.deepcopy(changed['shots'][2])]
 dissolve_board['shots'][1]['render']['start_frame']=24;dissolve_board['shots'][1]['render']['end_frame']=48
 p.render_selected(dissolve_board,args.host,cache)
 dissolve=p.assemble(dissolve_board,args.host,cache,audio,cues,out/'test-intra-chapter-dissolve.mp4');assert dissolve['frames']==48
 # Text/timing integrity checks, including non-finite and overlapping cues.
 valid=json.loads(cues.read_text())
 for label,change in [
  ('negative time',lambda c:c[0].update(start=-.1)),
  ('non-finite time',lambda c:c[0].update(end=float('nan'))),
  ('overlap',lambda c:c[1].update(start=.5)),
  ('out of range',lambda c:c[-1].update(end=4)),
  ('missing cues',lambda c:c.clear())]:
  bad=copy.deepcopy(valid);change(bad);badpath=out/'test-bad-cues.json';p.jsonwrite(badpath,bad)
  checks.append(rejected(lambda:p.assemble(changed,args.host,cache,audio,badpath,out/'test-bad-caption.mp4'),'Rejected '+label+' subtitles'))
 locked['audio_sha256']=p.digest(audio);locked['subtitle_sha256']='0'*64
 checks.append(rejected(lambda:p.assemble(locked,args.host,cache,audio,cues,out/'test-wrong-subtitle.mp4'),'Wrong production subtitle hash rejected'))
 # Different deterministic tones verify actual seek, not just silent duration.
 tones=out/'test-tones-not-narration.wav';samples=array.array('h')
 for n in range(int(3.5*24000)):
  t=n/24000;freq=330 if t<1 else 660 if t<2.5 else 990
  samples.append(round(5000*math.sin(2*math.pi*freq*t)))
 with wave.open(str(tones),'wb') as w:w.setparams((1,2,24000,0,'NONE','not compressed'));w.writeframes(samples.tobytes())
 tone_video=out/'test-tone-offset.mp4';p.assemble(changed,args.host,cache,tones,cues,tone_video,['T02','T03'])
 pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(tone_video),'-vn','-ar','24000','-ac','1','-f','f32le','-']);signal=array.array('f');signal.frombytes(pcm)
 frequencies=[]
 for seconds,expected in [(.2,660),(1.8,990)]:
  chunk=signal[round(seconds*24000):round(seconds*24000)+2400];powers={}
  for f in [330,660,990]:
   powers[f]=sum(x*math.cos(2*math.pi*f*i/24000) for i,x in enumerate(chunk))**2+sum(x*math.sin(2*math.pi*f*i/24000) for i,x in enumerate(chunk))**2
  actual=max(powers,key=powers.get);assert actual==expected;frequencies.append(actual)
 # Verify burned subtitle glyphs use source time after the middle-segment seek.
 subtitle_ious=[]
 for seconds,text in [(.2,valid[1]['text']),(1.8,valid[2]['text'])]:
  raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(seconds),'-i',str(tone_video),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
  frame=Image.frombytes('RGB',(1280,720),raw);crop=(0,630,1280,700)
  actual=frame.crop(crop).convert('L').point(lambda x:255 if x>170 else 0,mode='1')
  expected=Image.new('L',(1280,720),0);p.art.txt(ImageDraw.Draw(expected),(640,637),text,26,255,anchor='mt');expected=expected.crop(crop).point(lambda x:255 if x>170 else 0,mode='1')
  intersection=ImageChops.logical_and(actual,expected).histogram()[255];union=ImageChops.logical_or(actual,expected).histogram()[255];iou=intersection/union
  assert iou>.75,f'Subtitle source offset failed: {iou}';subtitle_ious.append(round(iou,4))
 result={'status':'passed','test_fixture':True,'not_a_deliverable':True,'no_speech_generated':True,'single_shot_export':True,'second_run_all_cache_hits':True,'replacement_cache_hits':[x['cache_hit'] for x in replaced],'upstream_shift_preserves_unmodified_keys':True,'scene_specific_source_dependency_test':True,'intra_chapter_dissolve_frames':48,'full_assembly':full,'opening_subset':subset,'later_subset':later,'rejection_checks':checks,'middle_subset_audio_frequencies_hz':frequencies,'middle_subset_caption_glyph_iou':subtitle_ious}
 p.jsonwrite(out/'test-results.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
