"""Clean P10 adapter. Original material renderer; current provider cue retiming."""
from pathlib import Path
import sys,json,re,numpy as np
from scipy.interpolate import PchipInterpolator
sys.path.insert(0,str(Path(__file__).resolve().parent))
import scene_renderer as engine
R=Path(__file__).resolve().parents[2];old=R.parent/'full_chapter_v1'
data=json.loads((old/'audio/P10.edge.json').read_text());clean=lambda x:re.sub(r'[^\w\u4e00-\u9fff]','',x)
times=[]
for b in data['boundaries']:
 w=clean(b['text']);times.extend([(b['offset']+b['duration']*j/max(len(w),1))/1e7 for j in range(len(w))])
raw=next(p['narration_duration'] for p in json.loads((R/'timeline.json').read_text())['paragraphs'] if p['id']=='P10')
sentences=re.findall(r'[^。！？]+[。！？]?',data['text']);offs=np.cumsum([0]+[len(clean(s)) for s in sentences]);cuts=[0]+[times[i] for i in offs[1:-1]]+[raw]
map_time=PchipInterpolator(cuts,[0,5,13,23,28])
def render(pid,p,w=1280,h=720):
 assert pid=='P10' and (w,h)==(1280,720)
 return engine.render(float(map_time(np.clip(p,0,1)*raw)))
