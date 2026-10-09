"""Build locked production storyboard from measured audio cue files.
No estimated timings and no synthetic production hashes.
"""
import argparse,json,hashlib,re,math,subprocess
from pathlib import Path
from shot_design import DESIGN,SOURCES,ACTIONS
from render import CHAPTERS
from cue_validation import validate_cues

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return ''.join(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',s))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--through-paragraph',type=int,help='Opening sample: measured cues must exactly cover the first N complete frozen paragraphs');ap.add_argument('--test-fixture',action='store_true',help='Synthetic timing tests only: write demo-mode fixture outputs, never final storyboard');ap.add_argument('--host',type=Path,required=True);ap.add_argument('--audio-dir',type=Path,required=True);ap.add_argument('--script-dir',type=Path,required=True);ap.add_argument('--audio',type=Path,required=True);a=ap.parse_args();root=Path(__file__).parent
 sentences=json.loads((a.audio_dir/'sentence_cues.json').read_text());captions=json.loads((a.audio_dir/'subtitle_cues.json').read_text());frozen=json.loads((a.script_dir/'narration-cues.json').read_text())
 assert sha(a.script_dir/'narration.txt')==frozen['narration_sha256']
 selected_paragraphs=frozen['paragraphs'][:a.through_paragraph] if a.through_paragraph is not None else frozen['paragraphs']
 if a.through_paragraph is not None:assert 1<=a.through_paragraph<=len(frozen['paragraphs'])
 assert norm(''.join(s['text'] for s in sentences))==norm(''.join(p['text'] for p in selected_paragraphs)),'Audio cue text differs from selected complete frozen paragraphs'
 actual=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(a.audio)]))
 validate_cues(sentences,actual,''.join(p['text'] for p in selected_paragraphs))
 validate_cues(captions,actual,''.join(p['text'] for p in selected_paragraphs))
 endframe=math.ceil(actual*24)+48
 byp={p['id']:[s for s in sentences if s['paragraph_id']==p['id']] for p in selected_paragraphs}
 specs=[]
 design=[x for x in DESIGN if x[0]<=len(selected_paragraphs)]
 for n,(para,si,phrase,kind,act,prange) in enumerate(design):
  pid=f'CO2-P{para:02d}';sentence=byp[pid][si-1];time=sentence['start'];method='DUMMY fixture sentence onset, not ASR' if a.test_fixture else 'ASR sentence onset'
  if phrase:
   candidate=[c for c in captions if c['end']>sentence['start']-.02 and c['start']<sentence['end']+.02]
   joined=''.join(norm(c['text']) for c in candidate);where=joined.find(norm(phrase));assert where>=0,f'Cannot find phrase {phrase} in measured subtitle cues'
   offset=0
   for cue in candidate:
    if offset+len(norm(cue['text']))>where:time=cue['start'];break
    offset+=len(norm(cue['text']))
   method='Nearest measured subtitle onset containing phrase: '+phrase
  frame=round(time*24) if n else 0
  assert not specs or frame>specs[-1]['start_frame'],f'Non-increasing scene boundary {pid}, {phrase}'
  specs.append(dict(shot_id=f'CO2-S{n+1:02d}',start_frame=frame,paragraph_id=pid,paragraph_num=para,sentence_id=sentence['id'],timing_method=method,kind=kind,act=act,p_range=prange))
 for i,s in enumerate(specs):s['end_frame']=specs[i+1]['start_frame'] if i+1<len(specs) else endframe
 assets=[]
 for aid,path,rights in [('guide','user-assets/guide.png','User-selected intact generated character; source-image provenance and rights not independently verified. Asset excluded from public source and supplied separately for private delivery; no face/head/body edits.'),('renderer','render.py','Original procedural illustrations and animation code created for this project.'),('shot-design','shot_design.py','Original narration-linked shot design.')]:
  assets.append(dict(id=aid,version='1.0.0',sha256=sha(a.host if aid=='guide' else root/path),path=path,rights=rights,intact=True))
 src=json.loads((a.script_dir/'sources.json').read_text());sources=[dict(id=s['id'],kind='factual',url=s['url'],supports=s['supports']) for s in src]
 shots=[]
 for i,s in enumerate(specs):
  pid=s['paragraph_id'];txt=next(p['text'] for p in frozen['paragraphs'] if p['id']==pid)
  shots.append(dict(shot_id=s['shot_id'],start_s=s['start_frame']/24,end_s=s['end_frame']/24,narration=pid+': '+txt,visual=CHAPTERS[s['kind']][1]+'；'+CHAPTERS[s['kind']][2],action=ACTIONS[s['kind']],camera='固定正交机位；事件主体动作驱动叙事，无循环推拉。章节转换为12帧纸面扫入，章内12帧溶接。',assets=[dict(asset_id=x['id'],version=x['version']) for x in assets],source_ids=SOURCES[s['paragraph_num']],continuity={'in':f'state-{i:02d}','out':f'state-{i+1:02d}'},audio=('DUMMY静音时序测试，不是配音：' if a.test_fixture else '完整临时合成中文旁白；实际音轨/ASR边界 ')+s['sentence_id'],qa=['核对物理过程与模型标签','向导完整144px，不遮字幕','首中末帧、字幕和转场解码检查'],render=s))
 board=dict(schema_version=1,mode='demo' if a.test_fixture else 'production',style_id='earthstory-paper-2d',width=1280,height=720,fps=24,duration_s=endframe/24,expected_shot_count=len(shots),sources=sources,assets=assets,guide={'asset_id':'guide','version':'1.0.0','height_fraction':.2,'bbox':[28/1280,452/720,96/1280,.2]},captions={'bbox':[.1,618/720,.8,80/720]},voice={'status':'temporary','note':'Generic synthetic Mandarin, not a real person imitation; voice selection remains deferred.'},shots=shots,narration_sha256=frozen['narration_sha256'],audio_sha256=sha(a.audio),measured_audio_duration_s=actual)
 stem='storyboard-fixture' if a.test_fixture else 'storyboard-opening' if a.through_paragraph is not None else 'storyboard'
 board['scope']='opening_sample' if a.through_paragraph is not None else 'full_episode'
 board['included_paragraph_ids']=[p['id'] for p in selected_paragraphs]
 if a.test_fixture:
  board['test_fixture']=True;board['voice']={'status':'deferred','note':'Synthetic dummy timing and silent audio fixture. NOT actual narration or a deliverable.'}
 subtitle_blob=json.dumps(captions,ensure_ascii=False,indent=2)
 board['subtitle_sha256']=hashlib.sha256(subtitle_blob.encode()).hexdigest()
 board['subtitle_text_sha256']=hashlib.sha256(norm(''.join(p['text'] for p in selected_paragraphs)).encode()).hexdigest()
 (root/(stem+'.json')).write_text(json.dumps(board,ensure_ascii=False,indent=2))
 (root/('subtitle_cues-fixture.json' if a.test_fixture else 'subtitle_cues-opening.json' if a.through_paragraph is not None else 'subtitle_cues.json')).write_text(subtitle_blob)
 lines=['# '+('合成时序测试样例（不是正式配音或分镜）' if a.test_fixture else '地球的来处：实测音轨分镜'),'',f'共{len(shots)}镜；'+('测试静音文件' if a.test_fixture else '旁白实测')+f'{actual:.3f}秒，画面{endframe/24:.3f}秒，含2秒收尾。',('无实际配音；合成时序测试，不是交付物。' if a.test_fixture else '旁白身份：临时通用合成中文；所有宇宙形成画面为示意或艺术化复原。'),'']
 for s in shots:lines.extend([f"## {s['shot_id']} · {s['start_s']:.3f}–{s['end_s']:.3f}s",s['narration'],'',s['visual'],s['action'],s['camera'],'来源：'+', '.join(s['source_ids']),'时序：'+s['render']['timing_method'],''])
 (root/(stem+'.md')).write_text('\n'.join(lines))
 print(json.dumps({'test_fixture':a.test_fixture,'shots':len(shots),'audio_duration':actual,'video_duration':endframe/24},ensure_ascii=False))
if __name__=='__main__':main()
