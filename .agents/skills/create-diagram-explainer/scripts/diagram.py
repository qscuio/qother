#!/usr/bin/env python3
"""Topic-independent diagram animation; no network, credentials, or asset downloads."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import wave


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def wav_info(path):
    with wave.open(str(path), "rb") as w:
        require(w.getnchannels() == 1 and w.getsampwidth() == 2 and w.getcomptype() == "NONE",
                f"Expected mono 16-bit PCM: {path}")
        rate, count = w.getframerate(), w.getnframes()
        raw = w.readframes(count)
    require(count > 0 and len(raw) == count * 2, f"Empty/truncated audio: {path}")
    peak = max(abs(x[0]) for x in struct.iter_unpack("<h", raw))
    require(peak > 32, f"Silent or near-silent narration: {path}")
    require(peak < 32767, f"Full-scale/clipped audio: {path}")
    return rate, count, raw


def write_wav(path, raw, rate):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(raw)


def check_project(p):
    require(p.get("scenes"), "No scenes")
    w, h = p.get("width", 1280), p.get("height", 720)
    require(all(isinstance(v, int) and v >= 320 and v % 2 == 0 for v in [w, h]), "Canvas sizes must be even integers >= 320")
    require(1 <= p.get("fps", 24) <= 60, "fps must be 1..60")
    ids = set()
    for s in p["scenes"]:
        sid = s["id"]
        require(sid not in ids, f"Duplicate scene {sid}")
        ids.add(sid)
        clauses = s.get("clauses", [])
        require(clauses and "".join(c["text"] for c in clauses) == s["narration"], f"Narration coverage mismatch: {sid}")
        elements = s.get("elements", [])
        es = {e["id"]: e for e in elements}
        require(len(es) == len(elements), f"Duplicate object identity: {sid}")
        cs = set()
        for c in clauses:
            require(c["id"] not in cs and c["text"], f"Empty/duplicate clause: {sid}")
            cs.add(c["id"])
            require(c.get("focus") and all(x in es for x in c["focus"]), f"Missing visual focus: {c['id']}")
        for e in elements:
            kind = e["kind"]
            require(kind in {"node", "queue", "edge", "token"}, f"Unsupported element {kind}")
            if kind in {"node", "queue"}:
                x, y, bw, bh = e["box"]
                require(bw > 0 and bh > 0 and x >= 30*w/1280 and x+bw <= w-30*w/1280 and y >= 130*h/720 and y+bh <= 570*h/720,
                        f"Object outside diagram safe zone: {e['id']}")
            if kind == "queue":
                require(isinstance(e["capacity"], int) and e["capacity"] > 0, "Queue capacity must be a positive integer")
                require(isinstance(e["count"], int) and 0 <= e["count"] <= e["capacity"], "Invalid queue count")
            if kind == "token":
                require(len(e["position"]) == 2, "Token requires position")
                if e.get("inside_queue"):
                    require(e["inside_queue"] in es and es[e["inside_queue"]]["kind"] == "queue", "Unknown containing queue")
            if kind == "edge":
                require(e["flow"] in {"data", "control", "relation"}, "Edge needs an explicit flow meaning")
                pts = e["points"]
                require(len(pts) >= 2 and sum(math.dist(a,b) for a,b in zip(pts,pts[1:])) > 0, "Edge needs a nonzero path")
                for key, point in [("from", pts[0]), ("to", pts[-1])]:
                    require(e[key] in es and es[e[key]]["kind"] in {"node", "queue"}, "Edge endpoint must name a node/queue")
                    x,y,bw,bh = es[e[key]]["box"]
                    require(x-30 <= point[0] <= x+bw+30 and y-30 <= point[1] <= y+bh+30,
                            f"Arrow geometry disagrees with {key}: {e['id']}")
        event_ids = set()
        for e in s.get("events", []):
            require(e["id"] not in event_ids and e.get("meaning"), "Events need unique IDs and causal meanings")
            event_ids.add(e["id"])
            require(e["target"] in es, f"Unknown event target {e['target']}")
            require(e["kind"] in {"reveal", "hide", "state", "queue", "move"}, "Unknown event kind")
            for a in [e["at"]] + ([e["until"]] if "until" in e else []):
                require(a["clause"] in cs and 0 <= a.get("fraction", 0) <= 1, "Invalid clause anchor")
            target = es[e["target"]]
            if e["kind"] == "queue":
                require(target["kind"] == "queue" and isinstance(e["count"], int) and 0 <= e["count"] <= target["capacity"], "Invalid queue update")
            if e["kind"] == "state":
                require(target["kind"] in {"node", "queue"} and isinstance(e["value"], str), "State belongs on a node/queue")
            if e["kind"] == "move":
                require(target["kind"] == "token", "Only tokens can move")
                require(e["edge"] in es and es[e["edge"]]["kind"] == "edge" and es[e["edge"]]["flow"] == "data", "Move must follow a data edge")
                if e.get("arrive_queue"):
                    require(e["arrive_queue"] == es[e["edge"]]["to"] and es[e["arrive_queue"]]["kind"] == "queue", "Arrival queue must match edge destination")
                for gate in e.get("requires", []):
                    require(gate["target"] in es and es[gate["target"]]["kind"] in {"node", "queue"}, "Unknown gate")


def resolve_events(s):
    cs = {c["id"]: c for c in s["clauses"]}
    def anchor(a):
        c = cs[a["clause"]]
        return c["start"] + (c["end"]-c["start"])*a.get("fraction", 0)
    for i,e in enumerate(s.get("events", [])):
        e["start"] = anchor(e["at"])
        instant = e["kind"] in {"state", "queue", "hide"}
        e["end"] = e["start"] if instant else (anchor(e["until"]) if "until" in e else e["start"]+e.get("duration", .5))
        e["order"] = i
        require(e["end"] >= e["start"] and e["end"] <= s["duration"]+1e-6, f"Event outside scene: {e['id']}")
        if not instant:
            require(e["end"] > e["start"], f"Zero-length animation: {e['id']}")
    s["events"] = sorted(s.get("events", []), key=lambda e:(e["start"], e["order"]))


def path_point(pts, fraction):
    lengths = [math.dist(a,b) for a,b in zip(pts,pts[1:])]
    remain = max(0,min(1,fraction))*sum(lengths)
    for a,b,dist in zip(pts,pts[1:],lengths):
        if remain <= dist and dist:
            q=remain/dist
            return [a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q]
        remain -= dist
    return list(pts[-1])


def state_at(s, t):
    state = {e["id"]: copy.deepcopy(e) for e in s["elements"]}
    for e in state.values():
        e["progress"] = 1.0 if e.get("visible", False) else 0.0
    for ev in s["events"]:
        if ev["start"] > t+1e-8:
            break
        obj=state[ev["target"]]
        kind=ev["kind"]
        q=1 if ev["end"]==ev["start"] else min(1,max(0,(t-ev["start"])/(ev["end"]-ev["start"])))
        if kind=="reveal": obj["progress"]=q
        elif kind=="hide": obj["progress"]=0
        elif kind=="state": obj["state"]=ev["value"]
        elif kind=="queue": obj["count"]=ev["count"]
        elif kind=="move":
            obj["position"]=path_point(state[ev["edge"]]["points"], q*q*(3-2*q))
            obj["inside_queue"]=ev.get("arrive_queue") if q>=1-1e-8 else None
    return state


def validate_timeline(tl):
    check_project(tl)
    total=0
    for s in tl["scenes"]:
        require(abs(s["start"]-total)<1e-6, "Scene chronology has a gap/overlap")
        require(s["duration"]>0, "Empty scene")
        prev=0
        for c in s["clauses"]:
            require(prev <= c["start"] < c["end"] <= s["duration"], "Caption chronology invalid")
            prev=c["end"]
        resolve_events(s)
        es={e["id"]:e for e in s["elements"]}
        occupied={}
        for ev in s["events"]:
            if ev["kind"] in {"move", "reveal"} and es[ev["target"]]["kind"]=="token":
                require(ev["start"] >= occupied.get(ev["target"], -1)-1e-6, "Concurrent motion/reveal of focal identity")
                occupied[ev["target"]]=ev["end"]
            if ev["kind"]=="move":
                before=state_at(s,ev["start"]-1e-5)
                # State/queue/reveal at the same instant can precede a move in authored order.
                for prior in s["events"]:
                    if prior["start"]==ev["start"] and prior["order"]<ev["order"]:
                        o=before[prior["target"]]
                        if prior["kind"]=="state":o["state"]=prior["value"]
                        if prior["kind"]=="queue":o["count"]=prior["count"]
                edge=before[ev["edge"]]
                require(edge["progress"]>=.999, f"Movement uses unrevealed edge: {ev['id']}")
                require(before[ev["target"]]["progress"]>=.999, "Moving token is not fully visible")
                require(math.dist(before[ev["target"]]["position"], edge["points"][0])<.02, f"Token teleports to edge start: {ev['id']}")
                for gate in ev.get("requires", []):
                    require(before[gate["target"]].get("state")==gate["state"], f"Causal gate not satisfied: {ev['id']}")
        boundaries={0,s["duration"]}
        for ev in s["events"]:boundaries.update([ev["start"],ev["end"]])
        for b in boundaries:
            st=state_at(s,b)
            for q in [x for x in st.values() if x["kind"]=="queue"]:
                n=sum(x["kind"]=="token" and x.get("inside_queue")==q["id"] and x["progress"]>0 for x in st.values())
                require(n<=q["count"], f"Queue count omits focal item: {q['id']}")
                x,y,w,h=q["box"]
                for obj in st.values():
                    if obj["kind"]=="token" and obj.get("inside_queue")==q["id"]:
                        xx,yy=obj["position"]
                        require(x<=xx<=x+w and y<=yy<=y+h, f"Focal item is outside its containing queue: {obj['id']}")
        for c in s["clauses"]:
            st=state_at(s,min(c["end"]-1e-5,c["start"]+.1))
            require(any(st[x]["progress"]>0 for x in c["focus"]), f"No visible focus during clause: {c['id']}")
        total+=s["duration"]
    require(abs(total-tl["duration"])<1e-6, "Total duration mismatch")


def import_master_timing(p, base, master_path, timing_path):
    """Preserve supplied PCM/timing; positional text matching permits different scene IDs."""
    supplied=read_json(timing_path)
    rate,count,raw=wav_info(master_path)
    require(supplied.get("sample_rate")==rate and supplied.get("sample_count")==count,
            "Supplied master sample rate/count disagrees with timing")
    def samples(seconds):
        value=float(seconds)*rate
        require(math.isfinite(value) and abs(value-round(value))<1e-4,
                "Supplied boundary is not an exact PCM sample boundary")
        return round(value)
    require(samples(supplied["duration"])==count,"Supplied master duration disagrees with timing")
    require(len(supplied["scenes"])==len(p["scenes"]),"Supplied scene count differs from project")
    previous=0
    for scene,source in zip(p["scenes"],supplied["scenes"]):
        start=samples(source["start"]);duration=samples(source["duration"]);end=start+duration
        require(start==previous and duration>0 and end<=count,"Supplied scene chronology is invalid")
        require("end" not in source or samples(source["end"])==end,"Supplied scene end disagrees with duration")
        require(source.get("narration",scene["narration"])==scene["narration"],"Supplied narration differs from project")
        captions=source.get("captions",source.get("clauses",[]))
        require(len(captions)==len(scene["clauses"]),"Supplied clause count differs from project")
        prior=0
        for clause,caption in zip(scene["clauses"],captions):
            require(clause["text"]==caption["text"],"Supplied caption text differs from project")
            first=samples(caption["start"]);last=samples(caption["end"]);n=last-first
            require(prior<=first<last<=duration,"Supplied caption chronology is invalid")
            require(caption.get("sample_count",n)==n,"Supplied caption sample count disagrees with boundaries")
            pcm=raw[(start+first)*2:(start+last)*2]
            require(any(abs(x[0])>32 for x in struct.iter_unpack("<h",pcm)),"Supplied caption interval is silent")
            if clause.get("wav"):
                r,cn,cr=wav_info(base/clause["wav"])
                require(r==rate and cn==n and cr==pcm,"Supplied master does not preserve clause PCM bytes")
            clause.update(start=first/rate,end=last/rate,sample_count=n)
            prior=last
        scene.update(start=start/rate,end=end/rate,duration=duration/rate)
        previous=end
    require(previous==count,"Supplied scenes do not cover the entire master")
    p.update(duration=count/rate,sample_rate=rate,sample_count=count,audio_file="narration.wav",
             timing_method="supplied exact PCM clause boundaries; intra-clause event fractions are estimated interpolation",
             supplied_timing_sha256=hashlib.sha256(Path(timing_path).read_bytes()).hexdigest())


def assemble(project, out, preview=False, master=None, timing=None):
    p=read_json(project)
    check_project(p)
    p=copy.deepcopy(p)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    base=Path(project).resolve().parent
    p["script_sha256"]=hashlib.sha256(Path(project).read_bytes()).hexdigest()
    if p.get("font"):
        p["font"]=str((base/p["font"]).resolve())
    p["audio_kind"]="preview" if preview else p.get("audio_kind")
    require(preview or p["audio_kind"]=="narration", "Final assembly requires audio_kind=narration")
    require(preview or p.get("audio_provenance"), "Document the narration source/voice")
    require((master is None)==(timing is None), "Supply --master and --timing together")
    require(not (preview and master is not None), "Supplied narration cannot be combined with --preview")
    if master is not None:
        import_master_timing(p,base,master,timing)
        validate_timeline(p)
        if Path(master).resolve()!=(out/"narration.wav").resolve():
            shutil.copyfile(master,out/"narration.wav")
    else:
        rate=None; raw_parts=[]; global_count=0
        for s in p["scenes"]:
            files=[]
            for c in s["clauses"]:
                if preview:
                    r=24000;n=round(c.get("preview_seconds",3)*r);raw=b"\x00\x00"*n
                    require(n>0,"Preview clause duration must be positive")
                else:
                    r,n,raw=wav_info(base/c["wav"])
                if rate is None:rate=r
                require(rate==r, "All clause WAVs must have the same sample rate")
                files.append((c,n,raw))
            lead=round(.15*rate);tail=round(.3*rate)
            parts=[b"\x00\x00"*lead];local_count=lead
            s["start"]=global_count/rate
            for c,n,raw in files:
                c["start"]=local_count/rate;c["sample_count"]=n
                parts.append(raw);local_count+=n;c["end"]=local_count/rate
            parts.append(b"\x00\x00"*tail);local_count+=tail
            s["duration"]=local_count/rate;global_count+=local_count
            s["end"]=global_count/rate
            raw_parts.extend(parts)
        p.update(duration=global_count/rate,sample_rate=rate,sample_count=global_count,
                 audio_file="narration.wav",timing_method="silent preview estimates" if preview else "measured clause PCM boundaries; intra-clause event fractions are estimated interpolation")
        validate_timeline(p)
        write_wav(out/"narration.wav",b"".join(raw_parts),rate)
    p["audio_sha256"]=hashlib.sha256((out/"narration.wav").read_bytes()).hexdigest()
    write_json(out/"timeline.json",p)
    def stamp(t):
        ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);sec,ms=divmod(ms,1000)
        return f"{h:02}:{m:02}:{sec:02},{ms:03}"
    captions=[]
    for s in p["scenes"]:
        for c in s["clauses"]:
            captions.append(f"{len(captions)+1}\n{stamp(s['start']+c['start'])} --> {stamp(s['start']+c['end'])}\n{c['text']}\n")
    (out/"captions.srt").write_text("\n".join(captions),encoding="utf-8")
    return p


def find_font(p):
    candidates=[p.get("font"),os.environ.get("DIAGRAM_FONT"),
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for f in candidates:
        if f and Path(f).is_file():return f
    raise ValueError("No usable font. Set project.font or DIAGRAM_FONT to an installed font.")


class Renderer:
    def __init__(self,p):
        from PIL import Image,ImageDraw,ImageFont
        self.Image,self.ImageDraw,self.ImageFont=Image,ImageDraw,ImageFont
        self.p=p;self.w=p.get("width",1280);self.h=p.get("height",720);self.scale=self.h/720
        self.font_path=find_font(p);self.fonts={}
        self.colors={"paper":"#F6F1E6","ink":"#263B43","accent":"#4F92A3","control":"#D9755C","muted":"#788780",**p.get("colors",{})}
    def font(self,n):
        n=max(10,round(n*self.scale))
        if n not in self.fonts:self.fonts[n]=self.ImageFont.truetype(self.font_path,n)
        return self.fonts[n]
    def text(self,xy,text,size=24,color="ink",anchor="mm",max_width=None):
        f=self.font(size)
        require(max_width is None or self.d.textlength(text,font=f)<=max_width,f"Text too wide; shorten/reflow: {text}")
        self.d.text(xy,text,font=f,fill=self.colors.get(color,color),anchor=anchor)
    def stroke(self,pts,p=1,color="ink",width=3,dashed=False):
        if p<=0:return
        lengths=[math.dist(a,b) for a,b in zip(pts,pts[1:])];remaining=sum(lengths)*min(1,p)
        output=[tuple(pts[0])]
        for a,b,dist in zip(pts,pts[1:],lengths):
            if dist<=remaining:output.append(tuple(b));remaining-=dist
            elif dist:
                output.append(tuple(a[k]+(b[k]-a[k])*remaining/dist for k in range(2)));break
        if len(output)>1:
            if dashed:
                length=sum(math.dist(a,b) for a,b in zip(output,output[1:]))
                for i in range(0,math.ceil(length),16):
                    self.d.line([tuple(path_point(output,i/length)),tuple(path_point(output,min(i+9,length)/length))],fill=self.colors[color],width=max(1,round(width*self.scale)))
            else:self.d.line(output,fill=self.colors[color],width=max(1,round(width*self.scale)),joint="curve")
    def frame(self,t):
        p=self.p
        s=next((s for s in p["scenes"] if s["start"]<=t<s["end"]),p["scenes"][-1]);local=t-s["start"]
        im=self.Image.new("RGB",(self.w,self.h),self.colors["paper"]);self.d=self.ImageDraw.Draw(im)
        self.text((self.w/2,40*self.scale),p.get("title",""),30,max_width=self.w-80*self.scale)
        self.text((self.w/2,88*self.scale),s["title"],24,"muted",max_width=self.w-80*self.scale)
        st=state_at(s,local)
        for e in sorted(st.values(),key=lambda e: {"edge":0,"node":1,"queue":1,"token":2}[e["kind"]]):
            q=e["progress"]
            if q<=0:continue
            kind=e["kind"]
            if kind=="edge":
                pts=e["points"];col="control" if e["flow"]=="control" else ("accent" if e["flow"]=="data" else "muted")
                self.stroke(pts,q,col,3,e["flow"]=="control")
                if q>.95:
                    a,b=pts[-2:];ang=math.atan2(b[1]-a[1],b[0]-a[0]);r=13*self.scale
                    self.stroke([[b[0]-r*math.cos(ang-.45),b[1]-r*math.sin(ang-.45)],b,[b[0]-r*math.cos(ang+.45),b[1]-r*math.sin(ang+.45)]],1,col)
                if q>.8 and e.get("label"):
                    x,y=path_point(pts,.5);self.text((x,y-23*self.scale),e["label"],18,col,max_width=260*self.scale)
            elif kind in {"node","queue"}:
                x,y,w,h=e["box"]
                self.stroke([[x,y],[x+w,y],[x+w,y+h],[x,y+h],[x,y]],q)
                if q>.6:
                    self.text((x+w/2,y+25*self.scale),e.get("label",""),23,max_width=w-16*self.scale)
                    if e.get("state"):self.text((x+w/2,y+h-24*self.scale),e["state"],18,"control",max_width=w-16*self.scale)
                    if kind=="queue":
                        tokens=[z for z in st.values() if z["kind"]=="token" and z.get("inside_queue")==e["id"] and z["progress"]>0]
                        need=e["count"]-len(tokens);cy=y+h*.52
                        slots=[(x+(i+.5)*w/e["capacity"],cy) for i in range(e["capacity"])]
                        for xx,yy in reversed(slots):
                            if need<=0:break
                            if any(math.dist(z["position"],[xx,yy])<36*self.scale for z in tokens):continue
                            r=11*self.scale;self.d.rectangle((xx-r,yy-r,xx+r,yy+r),outline=self.colors["muted"],width=2);need-=1
                        require(need==0,f"Queue artwork lacks room: {e['id']}")
                        self.text((x+w/2,y+h+23*self.scale),f"{e['count']} / {e['capacity']}",19,"muted")
            elif kind=="token":
                x,y=e["position"];r=16*self.scale
                self.stroke([[x-r,y-r],[x+r,y-r],[x+r,y+r],[x-r,y+r],[x-r,y-r]],q,"accent",4)
                if q>.8:
                    self.d.ellipse((x-4*self.scale,y-4*self.scale,x+4*self.scale,y+4*self.scale),fill=self.colors["accent"])
                    if e.get("label"):self.text((x,y-30*self.scale),e["label"],17,"accent",max_width=180*self.scale)
        caption=next((c["text"] for c in s["clauses"] if c["start"]<=local<c["end"]),"")
        lines=[];line="";f=self.font(27);safe=self.w-110*self.scale
        for ch in caption:
            if self.d.textlength(line+ch,font=f)>safe:lines.append(line);line=""
            line+=ch
        if line:lines.append(line)
        require(len(lines)<=2,"Caption exceeds two lines; split the narration clause")
        for i,line in enumerate(lines):self.text((self.w/2,(616+i*36)*self.scale),line,27,max_width=safe)
        notice="SILENT PREVIEW / 静音预览" if p["audio_kind"]=="preview" else p.get("example_notice","")
        if notice:self.text((self.w/2,698*self.scale),notice,15,"control",max_width=self.w-40*self.scale)
        return im


def preflight(timeline, preview=False):
    p=read_json(timeline);validate_timeline(p)
    audio=Path(timeline).resolve().parent/p["audio_file"]
    require(hashlib.sha256(audio.read_bytes()).hexdigest()==p["audio_sha256"], "Narration hash changed; reassemble timing")
    require(preview or p["audio_kind"]=="narration", "Silent preview requires --preview; it is not a narrated final")
    if p["audio_kind"]=="narration":
        rate,n,_=wav_info(audio)
        require(rate==p["sample_rate"] and n==p["sample_count"], "Narration no longer matches timing; reassemble")
    else:
        require(preview,"Preview flag required")
    return p,audio


def render(timeline,out,preview=False):
    p,audio=preflight(timeline,preview)
    require(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg and FFprobe are required")
    r=Renderer(p);fps=p.get("fps",24);n=math.ceil(p["duration"]*fps)
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pixel_format","rgb24","-video_size",f"{r.w}x{r.h}","-framerate",str(fps),"-i","pipe:0","-i",str(audio),"-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","fast","-crf","21","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-movflags","+faststart",str(out)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for i in range(n):proc.stdin.write(r.frame(i/fps).tobytes())
        proc.stdin.close()
        require(proc.wait()==0,"FFmpeg encode failed")
    except BaseException:
        proc.kill();proc.wait();raise
    subprocess.run(["ffmpeg","-v","error","-i",str(out),"-f","null","-"],check=True)
    info=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(out)]))
    streams=info["streams"];video=next(x for x in streams if x["codec_type"]=="video");a=next(x for x in streams if x["codec_type"]=="audio")
    require(video["codec_name"]=="h264" and a["codec_name"]=="aac","Unexpected codecs")
    require(abs(float(video["duration"])-float(a["duration"]))<=1/fps+.03,"Audio/video duration mismatch")
    info["checks"]={"decode":"passed","timing":"measured clauses with interpolated events","continuous_playback":"not performed by this script","speech_content":"requires listening","audio_kind":p["audio_kind"]}
    write_json(out.with_suffix(".qa.json"),info)
    return info


def frames(timeline,out):
    p=read_json(timeline);validate_timeline(p);r=Renderer(p)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for i,s in enumerate(p["scenes"]):
        times={s["duration"]*q for q in [.05,.5,.95]}
        for ev in s["events"]:
            if ev["kind"] in {"move","state","queue"}:
                times.update(max(0,min(s["duration"]-.001,z)) for z in [ev["start"]-.05,ev["start"]+.05,ev["end"]-.05,ev["end"]+.05])
        for j,t in enumerate(sorted(times)):r.frame(s["start"]+t).save(out/f"scene_{i+1:02}_{j:02}_{t:.3f}.png")


def main():
    ap=argparse.ArgumentParser(description=__doc__);sp=ap.add_subparsers(dest="cmd",required=True)
    a=sp.add_parser("validate");a.add_argument("project",type=Path)
    a=sp.add_parser("assemble");a.add_argument("project",type=Path);a.add_argument("--out",type=Path,required=True);a.add_argument("--preview",action="store_true");a.add_argument("--master",type=Path);a.add_argument("--timing",type=Path)
    a=sp.add_parser("render");a.add_argument("timeline",type=Path);a.add_argument("--out",type=Path,required=True);a.add_argument("--preview",action="store_true")
    a=sp.add_parser("frames");a.add_argument("timeline",type=Path);a.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    if args.cmd=="validate":check_project(read_json(args.project));print("Project structure valid; assemble to check timed causality.")
    elif args.cmd=="assemble":p=assemble(args.project,args.out,args.preview,args.master,args.timing);print(f"Assembled {p['duration']:.3f}s ({p['audio_kind']}); {args.out / 'timeline.json'}")
    elif args.cmd=="render":render(args.timeline,args.out,args.preview);print(f"Encoded and decoded successfully: {args.out}")
    else:frames(args.timeline,args.out);print(f"Frames: {args.out}")


if __name__=="__main__":main()
