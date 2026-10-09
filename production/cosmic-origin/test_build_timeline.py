"""Portable full/prefix builder test with explicitly dummy timings and silence.
Needs frozen script input and the repository validator; no speech service calls.
"""
import argparse,json,re,shutil,subprocess,sys,tempfile,wave
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--host',type=Path,required=True);ap.add_argument('--script-dir',type=Path,required=True);ap.add_argument('--validator',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args();root=Path(__file__).resolve().parent;results=[]
 with tempfile.TemporaryDirectory(prefix='cosmic-dummy-builder-') as temp:
  temp=Path(temp);code=temp/'code';code.mkdir();cues=temp/'dummy-cues';cues.mkdir()
  for p in root.glob('*.py'):shutil.copy(p,code/p.name)
  paragraphs=json.loads((a.script_dir/'narration-cues.json').read_text())['paragraphs']
  for count in [len(paragraphs),2]:
   sentences=[];subtitles=[];t=.1
   for paragraph in paragraphs[:count]:
    for text in re.findall(r'[^。！？]+[。！？]?',paragraph['text']):
     st=t
     for clause in re.findall(r'[^，；。！？]+[，；。！？]?',text):
      while clause:
       chunk=clause[:28];clause=clause[28:];end=t+len(chunk)*.025
       if not re.search(r'[\u4e00-\u9fffA-Za-z0-9]',chunk):
        subtitles[-1]['text']+=chunk;subtitles[-1]['end']=round(end,4);t=end;continue
       subtitles.append({'id':f'test-sub-{len(subtitles)}','paragraph_id':paragraph['id'],'text':chunk,'start':round(t,4),'end':round(end,4),'timing_method':'DUMMY, not ASR'});t=end
     sentences.append({'id':f'test-s-{len(sentences)}','paragraph_id':paragraph['id'],'text':text,'start':round(st,4),'end':round(t,4),'timing_method':'DUMMY, not ASR'});t+=.12
    t+=.2
   (cues/'sentence_cues.json').write_text(json.dumps(sentences,ensure_ascii=False));(cues/'subtitle_cues.json').write_text(json.dumps(subtitles,ensure_ascii=False));wav=temp/'TEST_SILENCE_NOT_NARRATION.wav'
   with wave.open(str(wav),'wb') as w:w.setparams((1,2,8000,0,'NONE','not compressed'));w.writeframes(b'\0\0'*int((t+.5)*8000))
   cmd=[sys.executable,str(code/'build_timeline.py'),'--test-fixture','--host',str(a.host),'--audio-dir',str(cues),'--script-dir',str(a.script_dir),'--audio',str(wav)]
   if count<len(paragraphs):cmd+=['--through-paragraph',str(count)]
   result=subprocess.run(cmd,capture_output=True,text=True);assert result.returncode==0,result.stderr
   bpath=code/'storyboard-fixture.json';b=json.loads(bpath.read_text());assert b['mode']=='demo' and b['test_fixture'];assert not (code/'storyboard.json').exists();assert not (code/'storyboard-opening.json').exists()
   expected=47 if count==len(paragraphs) else 4;assert len(b['shots'])==expected;assert len(b['included_paragraph_ids'])==count
   subprocess.run([sys.executable,str(a.validator),str(bpath)],check=True,capture_output=True)
   rejected=subprocess.run([sys.executable,str(a.validator),str(bpath),'--production'],capture_output=True);assert rejected.returncode!=0
   # Missing subtitle text and invalid zero prefix must fail before export.
   (cues/'subtitle_cues.json').write_text(json.dumps(subtitles[:-1],ensure_ascii=False))
   assert subprocess.run(cmd,capture_output=True).returncode!=0
   (cues/'subtitle_cues.json').write_text(json.dumps(subtitles,ensure_ascii=False))
   assert subprocess.run(cmd+['--through-paragraph','0'],capture_output=True).returncode!=0
   results.append({'subtitle_coverage_guard':'passed','zero_prefix_guard':'passed','paragraph_count':count,'shots':expected,'scope':b['scope'],'demo_validation':'passed','production_guard':'rejected_fixture_as_expected'})
 report={'status':'passed','test_fixture':True,'no_speech_generated':True,'not_actual_timings':True,'cases':results,'temporary_fixture_files_deleted':True}
 a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
