import json,subprocess,wave,argparse
from pathlib import Path
import numpy as np
from scipy.signal import correlate
from validate_manifest import validate_manifest
parser=argparse.ArgumentParser(description='Waveform alignment only, not speech recognition or voice approval')
parser.add_argument('--video',type=Path,required=True)
parser.add_argument('--manifest',type=Path,required=True)
parser.add_argument('--timeline',type=Path,required=True)
parser.add_argument('--audio-dir',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True,help='New JSON report file')
a=parser.parse_args()
if a.output.exists():parser.error('Output report already exists')
manifest=json.loads(a.manifest.read_text());video=a.video
paras=json.loads(Path(__file__).with_name('script').joinpath('paragraphs.json').read_text())['paragraphs'];validate_manifest(manifest,paras)
timeline=json.loads(a.timeline.read_text())['paragraphs']
if [r['id'] for r in timeline]!=[p['id'] for p in paras]:parser.error('Timeline must contain exactly ordered P01–P19')
for row,p in zip(timeline,paras):
 if row['text'].strip()!=p['text'].strip() or Path(row['filename']).name!=row['filename']:parser.error('Invalid timeline text or filename')
filenames={r['id']:r['filename'] for r in timeline}
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-vn','-ac','1','-ar','24000','-f','s16le','-']);decoded=np.frombuffer(raw,'<i2').astype(float)/32768
rows=[];margin=1200
for p in manifest['paragraphs']:
 with wave.open(str(a.audio_dir/filenames[p['id']])) as w:
  assert (w.getsampwidth(),w.getframerate(),w.getnchannels())==(2,24000,1),'Expected mono24k int16 WAV'
  x=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768
 expected=round(p['start']*24000);lo=max(0,expected-margin);hi=min(len(decoded),expected+len(x)+margin);y=decoded[lo:hi]
 c=correlate(y,x,mode='valid',method='fft');best=int(c.argmax());actual=lo+best;aligned=decoded[actual:actual+len(x)];rho=float(np.corrcoef(x,aligned)[0,1])
 # Check first/last 0.5 s waveform correlation if sufficient voiced signal.
 n=12000
 first=float(np.corrcoef(x[:n],aligned[:n])[0,1]);last=float(np.corrcoef(x[-n:],aligned[-n:])[0,1])
 row={'id':p['id'],'expected_start_sample':expected,'best_start_sample':actual,'lag_samples':actual-expected,'lag_ms':(actual-expected)/24,'correlation':rho,'first_half_second_correlation':first,'last_half_second_correlation':last};rows.append(row)
 assert abs(actual-expected)<=24,row
 assert rho>.97,row
 assert first>.9 and last>.9,row
report={'method':'Decoded final AAC compared with all 19 exact source WAVs using +/-50ms waveform cross-correlation at final timeline offsets; no ASR/phoneme/listening claim','sample_rate':24000,'decoded_samples':len(decoded),'decoded_duration':len(decoded)/24000,'paragraphs':rows,'all_pass':True,'audio_strategy':'One continuous frame-padded PCM master encoded once, not per-segment AAC concatenation; P10 old audio excluded'}
a.output.parent.mkdir(parents=True,exist_ok=True)
with a.output.open('x') as f:f.write(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
