import json,subprocess,math,wave,hashlib,time
from pathlib import Path
import numpy as np
from scipy.signal import resample_poly
from PIL import Image,ImageDraw,ImageFont
from build import ROOT,OUT,PARAS,TITLES,FPS,FONT,HOST,audio_path
from validate_manifest import validate_manifest
REFERENCES=[('宇宙早期与第一批恒星','https://science.nasa.gov/universe/overview/'),('太阳系形成','https://science.nasa.gov/solar-system/solar-system-facts/'),('月球起源及其证据','https://science.nasa.gov/moon/formation/'),('地球年龄与放射性测年','https://pubs.usgs.gov/gip/geotime/age.html')]
def stamp(t):
 m,s=divmod(int(round(t*1000)),60000);h,m=divmod(m,60);return f'{h:02d}:{m:02d}:{s//1000:02d},{s%1000:03d}'
def assemble():
 start=time.monotonic();rows=[];cursor=0;pcm=[];sr=24000
 for p in PARAS:
  row=json.loads((OUT/'segments'/f'{p["id"]}.json').read_text());row['start']=cursor;row['end']=cursor+row['duration'];row['text']=p['text'].strip();row['heading']=TITLES[int(p['id'][1:])-1];cursor=row['end'];rows.append(row)
  with wave.open(str(audio_path(p['id']))) as w:
   assert w.getsampwidth()==2
   x=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.float64)/32768
   if w.getnchannels()>1:x=x.reshape(-1,w.getnchannels()).mean(axis=1)
   if w.getframerate()!=sr:
    g=math.gcd(sr,w.getframerate());x=resample_poly(x,sr//g,w.getframerate()//g)
  n=round(row['duration']*sr);assert len(x)<=n
  # A fixed -1 dB safety gain, with no time stretching or internal edits.
  x=x*10**(-1/20);pcm.append(np.pad(x,(0,n-len(x))))
 end_duration=8
 im=Image.new('RGB',(1280,720),'#070b10');d=ImageDraw.Draw(im);f=lambda s:ImageFont.truetype(FONT,s)
 d.text((70,70),'地球往事  /  第一章',font=f(23),fill='#d5d0be');d.text((70,130),'从宇宙早期，到地球与月球',font=f(34),fill='#f0e7d5')
 d.text((70,224),'科学参考',font=f(22),fill='#adafa6')
 for i,(label,url) in enumerate(REFERENCES):
  y=267+i*73;d.text((70,y),label,font=f(22),fill='#d4d8d9');d.text((70,y+34),url.replace('https://',''),font=f(18),fill='#89949c')
 d.text((70,583),'全章预览 · 合成男声暂用 · 角色图层可选；P10沿用输入画面',font=f(20),fill='#aba998')
 d.text((70,622),'字幕依据服务端词边界（P10段内估时）；画面为科学示意，非比例、非精确物理模拟。',font=f(18),fill='#838a8d')
 im.save(OUT/'qa/endcard.png')
 subprocess.run(['ffmpeg','-v','error','-n','-loop','1','-i',str(OUT/'qa/endcard.png'),'-t',str(end_duration),'-r','24','-an','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','12288',str(OUT/'segments/END.mp4')],check=True)
 pcm.append(np.zeros(sr*end_duration));combined=np.concatenate(pcm)
 with wave.open(str(OUT/'full_narration.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(np.rint(np.clip(combined,-1,1)*32767).astype('<i2').tobytes())
 concat=OUT/'concat.txt';concat.write_text(''.join(f"file 'segments/{p['id']}.mp4'\n" for p in PARAS)+"file 'segments/END.mp4'\n")
 final=OUT/'地球往事_第一章_完整预览_v1.mp4'
 subprocess.run(['ffmpeg','-v','warning','-n','-f','concat','-safe','1','-i',str(concat),'-i',str(OUT/'full_narration.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)],check=True)
 manifest={'host_enabled_outside_p10':HOST is not None,'p10_baked_overlays':'Input P10 video may retain its original host and captions even when no --host is supplied','title':'地球往事 第一章 完整预览','resolution':[1280,720],'fps':24,'total_duration':cursor+end_duration,'frozen_character_count':sum(p['characters'] for p in PARAS),'paragraphs':rows,'references':REFERENCES,'limitations':['合成男声为临时占位，未获音色认可','角色为可选静态图层；P10保留输入视频原图层','段落边界由实际音频测得，字幕依据服务端词边界；P10内嵌字幕为估时','未进行外部ASR或持续浏览器播放测试','P10复用已完成视频，其余为连续参数驱动示意动画'],'text_source_commit':'e04f0556e983a75efcca7599278b04014ffe917c','assembly_wall_seconds':time.monotonic()-start}
 validate_manifest(manifest,PARAS)
 (OUT/'content_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 srt=[];i=1
 for row in rows:
  for c in row['cues']:srt.append(f'{i}\n{stamp(row["start"]+c["start"])} --> {stamp(row["start"]+c["end"])}\n{c["text"]}\n');i+=1
 (OUT/'完整字幕_词边界.srt').write_text('\n'.join(srt))
 md=['# 地球往事｜第一章完整预览','',f'总时长：{cursor+end_duration:.3f} 秒；1280×720；24 fps。','', '19 段冻结稿完整保留。男声为临时占位；讲解员为可选静态圆形图层，P10沿用输入画面。段落边界依据实测音频，字幕依据服务端词边界；P10段内估时。','','## 逐段内容与时间']
 for row in rows:md.extend(['',f'### {row["id"]} {row["heading"]}｜{stamp(row["start"])} – {stamp(row["end"])}',row['text'],'',f'旁白 {row["narration_duration"]:.3f} 秒；画面 {row["duration"]:.3f} 秒。'])
 md+=['','## 科学参考']+[f'- [{a}]({b})' for a,b in REFERENCES]+['','## 检查边界','完整解码与实际抽帧检查另见 QA 报告。持续浏览器播放未运行；不以技术解码代替听感审片。']
 (OUT/'第一章_内容清单与分镜.md').write_text('\n'.join(md));print(str(final),flush=True)
# Invoke via run.py after explicit local input configuration.
