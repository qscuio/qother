#!/usr/bin/env python3
"""Small reusable visible-hand renderer; supply authored paths and measured audio timing.
Requires Pillow and FFmpeg/FFprobe. No network, model downloads, or speech synthesis.
Coordinates are always 1280x720; output may be any even-sized 16:9 resolution.
"""
from __future__ import annotations
import argparse, bisect, json, math, shutil, subprocess, sys
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont
from scene_contract import block_items, inspect_style
from production_preflight import sha256_file, delivery_budget, run as production_preflight

ROOT = Path(__file__).resolve().parents[1]
BASE_W, BASE_H = 1280, 720
INK = [42, 48, 52, 255]
# Original single-line alphabet. Each inner list is a separate pen stroke.
GLYPHS = {
'A': [[(0,1),(.5,0),(1,1)],[(.2,.6),(.8,.6)]],
'B': [[(0,1),(0,0),(.6,0),(1,.2),(.8,.45),(0,.5)],[(.5,.5),(1,.6),(1,.8),(.7,1),(0,1)]],
'C': [[(1,.15),(.7,0),(.2,.05),(0,.3),(0,.8),(.3,1),(.8,1),(1,.85)]],
'D': [[(0,1),(0,0),(.5,0),(1,.3),(1,.7),(.5,1),(0,1)]],
'E': [[(1,0),(0,0),(0,1),(1,1)],[(0,.5),(.8,.5)]],
'F': [[(0,1),(0,0),(1,0)],[(0,.5),(.8,.5)]],
'G': [[(1,.2),(.7,0),(.2,.05),(0,.3),(0,.8),(.3,1),(1,1),(1,.55),(.5,.55)]],
'H': [[(0,0),(0,1)],[(1,0),(1,1)],[(0,.5),(1,.5)]],
'I': [[(.5,0),(.5,1)],[(0,0),(1,0)],[(0,1),(1,1)]],
'J': [[(0,0),(1,0)],[(.8,0),(.8,.8),(.5,1),(.1,.9),(0,.7)]],
'K': [[(0,0),(0,1)],[(1,0),(0,.55),(1,1)]],
'L': [[(0,0),(0,1),(1,1)]],
'M': [[(0,1),(0,0),(.5,.55),(1,0),(1,1)]],
'N': [[(0,1),(0,0),(1,1),(1,0)]],
'O': [[(.5,0),(.1,.1),(0,.5),(.1,.9),(.5,1),(.9,.9),(1,.5),(.9,.1),(.5,0)]],
'P': [[(0,1),(0,0),(.7,0),(1,.2),(.9,.5),(0,.5)]],
'Q': [[(.5,0),(.1,.1),(0,.5),(.1,.9),(.5,1),(.9,.9),(1,.5),(.9,.1),(.5,0)],[(.6,.7),(1.1,1.1)]],
'R': [[(0,1),(0,0),(.7,0),(1,.2),(.9,.5),(0,.5)],[(.5,.5),(1,1)]],
'S': [[(1,.15),(.7,0),(.2,.05),(0,.3),(.2,.5),(.8,.5),(1,.7),(.85,.95),(.25,1),(0,.85)]],
'T': [[(0,0),(1,0)],[(.5,0),(.5,1)]],
'U': [[(0,0),(0,.8),(.3,1),(.7,1),(1,.8),(1,0)]],
'V': [[(0,0),(.5,1),(1,0)]],
'W': [[(0,0),(.2,1),(.5,.5),(.8,1),(1,0)]],
'X': [[(0,0),(1,1)],[(1,0),(0,1)]],
'Y': [[(0,0),(.5,.5),(1,0)],[(.5,.5),(.5,1)]],
'Z': [[(0,0),(1,0),(0,1),(1,1)]],
'0': [[(.5,0),(.1,.1),(0,.5),(.1,.9),(.5,1),(.9,.9),(1,.5),(.9,.1),(.5,0)]],
'1': [[(.2,.2),(.5,0),(.5,1)],[(.1,1),(.9,1)]],
'2': [[(0,.2),(.2,0),(.7,0),(1,.2),(.85,.45),(0,1),(1,1)]],
'3': [[(0,0),(1,0),(.5,.45),(1,.6),(1,.85),(.7,1),(0,1)]],
'4': [[(.7,1),(.7,0),(0,.65),(1,.65)]],
'5': [[(1,0),(0,0),(0,.5),(.7,.5),(1,.7),(.9,.95),(0,1)]],
'6': [[(.9,0),(.3,.1),(0,.6),(0,.9),(.4,1),(.9,.9),(1,.65),(.7,.5),(0,.6)]],
'7': [[(0,0),(1,0),(.3,1)]],
'8': [[(.5,.5),(.1,.3),(.1,.1),(.5,0),(.9,.1),(.9,.3),(.5,.5),(0,.7),(.1,.95),(.5,1),(.9,.95),(1,.7),(.5,.5)]],
'9': [[(1,.45),(.3,.5),(0,.3),(.1,.05),(.7,0),(1,.2),(1,.6),(.7,.95),(.2,1)]],
'?': [[(0,.2),(.2,0),(.7,0),(1,.2),(.9,.4),(.5,.6),(.5,.75)],[(.5,.98),(.5,1)]],
'-': [[(0,.5),(1,.5)]], '+': [[(0,.5),(1,.5)],[(.5,0),(.5,1)]],
'.': [[(.5,.98),(.5,1)]], ':': [[(.5,.25),(.5,.27)],[(.5,.75),(.5,.77)]],
'/': [[(0,1),(1,0)]], '·': [[(.5,.49),(.5,.51)]]}

def distance(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])
def path_length(points): return sum(distance(a,b) for a,b in zip(points,points[1:]))
def color(value):
    if len(value) not in (3,4) or any(not isinstance(v,int) or not 0<=v<=255 for v in value):
        raise ValueError('Colors must be RGB or RGBA integer arrays, 0..255')
    return tuple(value) if len(value)==4 else tuple(value)+(255,)
def points(value, minimum=2):
    if len(value)<minimum: raise ValueError(f'Need at least {minimum} points')
    p=[tuple(map(float,x)) for x in value]
    if any(len(x)!=2 or not all(math.isfinite(v) for v in x) for x in p):
        raise ValueError('Points must be finite x,y pairs')
    return p

def text_strokes(item, hanzi_dir):
    x,y=map(float,item['at']);size=float(item.get('size',40));out=[]
    if not all(math.isfinite(v) for v in (x,y,size)) or size<=0:raise ValueError('Text placement and size must be finite, with positive size')
    if not isinstance(item['text'],str) or not item['text'].strip():raise ValueError('Handwriting text must be nonempty')
    for index,ch in enumerate(item['text']):
        if ch==' ': x+=size*.42; continue
        if ch in GLYPHS:
            paths=[[(x+px*size*.58,y+py*size) for px,py in p] for p in GLYPHS[ch]];advance=size*.79
        else:
            src=hanzi_dir/f'{ch}.json'
            if not src.is_file():
                raise ValueError(f'Missing stroke data for {ch!r}. Supply a licensed medians JSON in --hanzi-dir; no font-wipe fallback.')
            data=json.loads(src.read_text(encoding='utf-8'))
            paths=[[(x+px/1024*size,y+(900-py)/1024*size) for px,py in med] for med in data['medians']];advance=size*1.03
        for stroke,p in enumerate(paths):
            out.append(dict(points=points(p),width=float(item.get('width',3.5)),color=color(item.get('color',INK)),tag=f'text:{index}:{ch}:{stroke}'))
        x+=advance
    return out

def fill_strokes(item, name, masks):
    """Split EVERY polygon-interior scanline span. No connectors across concavities."""
    polygon=points(item['polygon'],3);spacing=float(item.get('spacing',16))
    if not spacing>0: raise ValueError('Fill spacing must be positive')
    masks[name]=polygon;out=[];lo=min(y for x,y in polygon);hi=max(y for x,y in polygon)
    # End rows cover edges with brush radius, clipped to the exact polygon.
    rows=max(1,math.ceil((hi-lo)/spacing));step=(hi-lo)/rows
    if step<=0: raise ValueError('Fill polygon has zero height')
    for row in range(rows+1):
        y=lo+min(max(row*step,0.01),hi-lo-0.01);hits=[]
        for a,b in zip(polygon,polygon[1:]+polygon[:1]):
            if min(a[1],b[1])<=y<max(a[1],b[1]):
                hits.append(a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1]))
        hits.sort()
        for i in range(0,len(hits)-1,2):
            a,b=hits[i],hits[i+1]
            if b-a<0.001:continue
            p=[(a,y),(b,y)]
            if row%2:p.reverse()
            out.append(dict(points=p,width=spacing*1.4,color=color(item['color']),tag=f'fill:{name}:{row}:{i//2}',fill_id=name))
    if not out: raise ValueError('Fill polygon produced no interior spans')
    return out

def expand(item, hanzi_dir, masks, name):
    kind=item['type']
    if kind=='text':return text_strokes(item,hanzi_dir)
    if kind=='fill':return fill_strokes(item,name,masks)
    if kind=='path':
        p=points(item['points'])
        if item.get('closed') and p[-1]!=p[0]:p.append(p[0])
        return [dict(points=p,width=float(item.get('width',4)),color=color(item.get('color',INK)),tag=item.get('tag',name))]
    raise ValueError(f'Unsupported command type: {kind}')

def compile_scene(spec, duration, hanzi_dir):
    if not math.isfinite(duration) or duration<=0:raise ValueError('Scene duration must be finite and positive')
    if not isinstance(spec.get('blocks'),list) or not spec['blocks']:raise ValueError('Scene needs nonempty blocks')
    events=[];masks={};current=(-180.,800.);last=0.
    def append(kind,start,end,p,**extra):
        if not all(math.isfinite(v) for v in (start,end)) or end<=start:raise ValueError('Event times must be finite and increasing')
        ll=[0.]
        for a,b in zip(p,p[1:]):ll.append(ll[-1]+distance(a,b))
        events.append(dict(kind=kind,start=start,end=end,points=p,lengths=ll,length=ll[-1],**extra))
    for bi,block in enumerate(spec['blocks']):
        start,end=float(block['start']),float(block['end'])
        if not all(math.isfinite(v) for v in (start,end)) or start<last-1e-8 or end<=start or end>duration:raise ValueError('Blocks must be ordered, nonoverlapping, and inside audio duration')
        if start>last:append('hold',last,start,[current,current],tag='hold')
        strokes=[]
        for ii,item in enumerate(block_items(block)):
            expanded=expand(item,hanzi_dir,masks,f'{bi}-{ii}')
            for stroke in expanded:
                if '_part_id' in item:stroke.update(part_id=item['_part_id'],phase=item['_phase'])
            strokes+=expanded
        if not strokes: raise ValueError('Empty drawing block')
        weights=[];prior=current
        for s in strokes:
            if not math.isfinite(s['width']) or s['width']<=0:raise ValueError('Stroke width must be finite and positive')
            weights.append((max(.06,distance(prior,s['points'][0])/1600),max(.07,path_length(s['points'])/1300)));prior=s['points'][-1]
        scale=(end-start)/sum(sum(w) for w in weights);t=start
        for s,(lift,draw) in zip(strokes,weights):
            p=s['points'];append('lift',t,t+lift*scale,[current,p[0]],tag='lift');t+=lift*scale
            append('draw',t,t+draw*scale,p,**{k:v for k,v in s.items() if k!='points'});t+=draw*scale;current=p[-1]
        last=end
    exit_cfg=spec.get('exit',{'start':max(last,duration-.9),'end':duration-.4})
    start,end=float(exit_cfg['start']),float(exit_cfg['end'])
    if not all(math.isfinite(v) for v in (start,end)) or start<last-1e-8 or end<=start or end>=duration:raise ValueError('Exit must follow all drawing and finish before audio ends')
    if start>last:append('hold',last,start,[current,current],tag='hold')
    off=(1450.,850.);append('exit',start,end,[current,off],tag='exit')
    if end<duration:append('hold',end,duration,[off,off],tag='hold')
    return events,masks,end

def verify_draw_bounds(spec,events):
    """Check expanded glyph/path bounds, rather than trusting a text origin alone."""
    if 'style' not in spec:return
    bottom=float(spec['style'].get('caption_lane_top',590))
    for e in events:
        if e['kind']!='draw' or e.get('fill_id'):continue
        radius=e['width']/2
        if any(x-radius<0 or x+radius>BASE_W or y-radius<0 or y+radius>bottom for x,y in e['points']):
            raise ValueError(f"Expanded stroke {e['tag']} crosses the canvas or reserved caption lane")


def event_samples(e,fps):
    # Exact event-start frames contain no new stroke/travel, so count interior samples.
    first=math.floor(e['start']*fps+1e-8)+1
    return max(0,math.ceil(e['end']*fps-1e-8)-first)
def select_fps(events,requested):
    candidates=[int(requested)] if requested!='auto' else [24,30,48,60]
    for fps in candidates:
        if fps<1 or fps>240:raise ValueError('FPS must be 1..240 or auto')
        if all(event_samples(e,fps)>=2 for e in events if e['kind'] in ('draw','lift','exit')):return fps
    bad=[e for e in events if e['kind'] in ('draw','lift','exit') and event_samples(e,candidates[-1])<2]
    detail=', '.join(f"{e['kind']} {e['tag']} at {e['start']:.3f}s ({e['end']-e['start']:.4f}s)" for e in bad[:3])
    raise ValueError(f'Undersampled motion at {candidates[-1]} fps: {detail}. Lengthen these blocks/transitions or simplify strokes/fill rows. Auto FPS is capped at 60; explicit FPS is never raised.')
def along(e,f):
    f=max(0.,min(1.,f));d=e['length']*f;ls=e['lengths'];i=min(max(0,bisect.bisect_right(ls,d)-1),len(ls)-2)
    a,b=e['points'][i:i+2];u=(d-ls[i])/(ls[i+1]-ls[i] or 1)
    p=(a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u)
    return p,e['points'][:i+1]+[p]
def at(events,t):
    idx=min(bisect.bisect_right([e['end'] for e in events],t),len(events)-1);e=events[idx]
    u=max(0.,min(1.,(t-e['start'])/(e['end']-e['start'])))
    if e['kind'] in ('lift','exit'):
        u=u*u*(3-2*u);p,_=along(e,u);p=(p[0],p[1]-7*math.sin(math.pi*u))
    else:p,_=along(e,u)
    return e,p,u

def find_font(explicit):
    if explicit:
        if not Path(explicit).is_file():raise ValueError(f'Font not found: {explicit}')
        return explicit
    for name in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(name).is_file():return name
    raise ValueError('Captions require an installed font; pass --font. No font is downloaded automatically.')

def media_duration(path):
    if not path.is_file():raise ValueError(f'Audio not found: {path}')
    proc=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(path)],capture_output=True,text=True,check=True)
    return float(json.loads(proc.stdout)['format']['duration'])

def validate_hand(raw, preset):
    """Reject stale anchors/sizes; opacity near the anchor is only a geometric check."""
    a=preset.get('nib_anchor',[])
    if len(a)!=2 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in a):
        raise ValueError('Hand nib_anchor must contain two finite coordinates')
    if not (0<=a[0]<raw.width and 0<=a[1]<raw.height-1):
        raise ValueError('Hand nib anchor must lie inside the actual asset, above its bottom edge')
    if preset.get('source_size',list(raw.size))!=list(raw.size):
        raise ValueError('Hand source_size is stale; recalibrate against the actual asset')
    h=preset.get('render_height')
    if not isinstance(h,(int,float)) or not math.isfinite(h) or h<=0:
        raise ValueError('Hand render_height must be finite and positive')
    x,y=map(round,a);radius=4
    region=raw.getchannel('A').crop((max(0,x-radius),max(0,y-radius),min(raw.width,x+radius+1),min(raw.height,y+radius+1)))
    if region.getextrema()[1]<32:
        raise ValueError('Nib anchor is far from visible alpha; inspect and recalibrate the tip')
    return {'status':'geometry_pass','source_size':list(raw.size),'nib_anchor':a,
            'visual_tip_review':'not_performed','rotation_degrees':0}


def opaque_edge_spans(raw):
    """Conservative spans of source-cut pixels, including all four asset edges."""
    alpha=raw.getchannel('A');w,h=raw.size;result=[]
    for name,coords in (('top',[(x,0) for x in range(w)]),('bottom',[(x,h-1) for x in range(w)]),
                        ('left',[(0,y) for y in range(h)]),('right',[(w-1,y) for y in range(h)])):
        opaque=[p for p in coords if alpha.getpixel(p)>16]
        if opaque:result.append((name,opaque[0],opaque[-1]))
    return result


def check_hand_edges(events,renderer,fps,duration):
    violations=[];sx,sy=renderer.hand_scale;px,py=renderer.pivot
    # Include exact event endpoints and middle as well as every delivered frame.
    times={i/fps for i in range(math.ceil(duration*fps))}
    for e in events:times.update((e['start'],(e['start']+e['end'])/2,e['end']))
    for t in sorted(times):
        if t>=renderer.exit_end:continue
        _,(x,y),_=at(events,t)
        for name,a,b in renderer.source_edges:
            ax,ay=x+a[0]*sx-px,y+a[1]*sy-py
            bx,by=x+b[0]*sx-px,y+b[1]*sy-py
            # One-pixel margin covers interpolation around an otherwise just-hidden edge.
            if max(ax,bx)>=-1 and min(ax,bx)<=BASE_W+1 and max(ay,by)>=-1 and min(ay,by)<=BASE_H+1:
                violations.append({'time':round(t,6),'edge':name})
                if len(violations)>=12:return violations
    return violations


def qa_sample_times(events,fps,duration):
    """Use exact delivered frames around motion boundaries, never just scene midpoint."""
    final=max(0,math.ceil(duration*fps)-1);indices={0,final}
    for e in events:
        if e['kind'] not in ('draw','lift','exit'):continue
        first=math.ceil(e['start']*fps-1e-8);last=math.ceil(e['end']*fps-1e-8)-1
        indices.update((first-1,first,(first+last)//2,last,last+1))
    return [round(i/fps,9) for i in sorted(indices) if 0<=i<=final]


def caption_layout(text,font):
    """Measure every caption before an encode can start; cache this exact layout."""
    if not isinstance(text,str) or not text.strip():raise ValueError('Empty caption')
    measure=ImageDraw.Draw(Image.new('RGB',(1,1)));lines=[]
    for paragraph in text.split('\n'):
        current=''
        for ch in paragraph:
            if measure.textlength(current+ch,font=font)>1090:
                lines.append(current);current=ch
            else:current+=ch
        lines.append(current)
    if len(lines)>2:raise ValueError('Caption requires more than two lines; split into shorter measured clauses')
    return {'lines':lines,'width':max(measure.textlength(line,font=font) for line in lines)+52,'height':43*len(lines)+12}


class Renderer:
    def __init__(self,spec,events,masks,exit_end,hand,font=None,ss=1):
        self.events=events;self.ends=[e['end'] for e in events];self.exit_end=exit_end;self.ss=ss;self.next=0;self.last=-1
        self.ink=Image.new('RGBA',(BASE_W*ss,BASE_H*ss));self.fills=self.ink.copy();self.masks={}
        for key,p in masks.items():
            m=Image.new('L',self.ink.size);ImageDraw.Draw(m).polygon([(x*ss,y*ss) for x,y in p],fill=255);self.masks[key]=m
        presets=json.loads((ROOT/'assets/hand_variants.json').read_text())['variants']
        if hand not in presets:raise ValueError('Unknown hand: '+hand)
        v=presets[hand];raw=Image.open(ROOT/'assets'/v['file']).convert('RGBA');a=v['nib_anchor']
        self.calibration=validate_hand(raw,v)
        self.source_edges=opaque_edge_spans(raw)
        # No rotation in this minimal renderer. Extend all source bottom-cut pixels offscreen.
        min_y=min(p[1] for e in events for p in e['points'])-7
        needed=math.ceil((BASE_H+20-min_y)/(1-a[1]/raw.height))
        height=max(v['render_height'],needed);scale=height/raw.height
        self.hand=raw.resize((round(raw.width*scale),height),Image.Resampling.LANCZOS)
        self.pivot=(a[0]*scale,a[1]*scale);self.crop_bottom_offset=(raw.height-a[1])*scale
        self.hand_scale=(self.hand.width/raw.width,self.hand.height/raw.height)
        self.pivot=(a[0]*self.hand_scale[0],a[1]*self.hand_scale[1])
        self.paper=spec.get('background', [255,255,255])
        if not isinstance(self.paper,list) or len(self.paper)!=3 or any(type(v) is not int or not 0<=v<=255 for v in self.paper):
            raise ValueError('background must be three RGB integers')
        self.paper=tuple(self.paper)+(255,)
        self.captions=spec.get('captions',[])
        self.font=ImageFont.truetype(find_font(font),28) if self.captions else None
        if self.captions and any(any(ord(ch)>127 for ch in c['text']) for c in self.captions):
            if not font and 'NotoSansCJK' not in find_font(None):raise ValueError('Non-ASCII captions need --font with the correct glyph coverage')
        self.caption_layouts={c['text']:caption_layout(c['text'],self.font) for c in self.captions}
    def stroke(self,im,p,c,w):
        p=[(round(x*self.ss),round(y*self.ss)) for x,y in p];w=max(1,round(w*self.ss));d=ImageDraw.Draw(im)
        d.line(p,fill=c,width=w,joint='curve');r=w/2
        for x,y in (p[0],p[-1]):d.ellipse((x-r,y-r,x+r,y+r),fill=c)
    def paint(self,e,u,ink,fills):
        _,p=along(e,u)
        if e.get('fill_id'):
            m=Image.new('L',ink.size);self.stroke(m,p,255,e['width']);m=ImageChops.darker(m,self.masks[e['fill_id']])
            if e['color'][3]!=255:m=m.point(lambda alpha:round(alpha*e['color'][3]/255))
            patch=Image.new('RGBA',ink.size,e['color']);patch.putalpha(m);fills.alpha_composite(patch)
        else:self.stroke(ink,p,e['color'],e['width'])
    def frame(self,t,debug=False):
        if t<self.last:raise ValueError('Render times must be monotonic; create a fresh Renderer for earlier frames')
        self.last=t
        while self.next<len(self.events) and self.events[self.next]['end']<=t:
            e=self.events[self.next]
            if e['kind']=='draw':self.paint(e,1,self.ink,self.fills)
            self.next+=1
        ink,fills=self.ink.copy(),self.fills.copy();e,nib,u=at(self.events,t)
        if e['kind']=='draw':self.paint(e,u,ink,fills)
        image=Image.new('RGBA',ink.size,self.paper);image.alpha_composite(fills);image.alpha_composite(ink)
        image=image.resize((BASE_W,BASE_H),Image.Resampling.LANCZOS)
        if t<self.exit_end:
            x,y=nib;px,py=self.pivot
            hand=self.hand.transform((BASE_W,BASE_H),Image.Transform.AFFINE,(1,0,px-x,0,1,py-y),Image.Resampling.BICUBIC)
            image.alpha_composite(hand)
        caption=next((c['text'] for c in self.captions if c['start']<=t<c['end']),'')
        d=ImageDraw.Draw(image)
        if caption:
            layout=self.caption_layouts[caption];lines=layout['lines']
            width,height=layout['width'],layout['height'];x=(BASE_W-width)/2;y=BASE_H-20-height
            d.rounded_rectangle((x,y,x+width,y+height),12,fill=(40,48,51,255))
            for i,s in enumerate(lines):d.text((BASE_W/2,y+6+i*43),s,font=self.font,fill='white',anchor='mt')
        if debug:
            x,y=nib;d.ellipse((x-5,y-5,x+5,y+5),outline='red',width=1)
            d.text((20,580),f'{t:.3f}s / {e["kind"]} / {e["tag"]}',fill='red')
        return image.convert('RGB')

def verify_captions(spec,duration,production):
    allowed={'manual_measured','provider_timestamps','forced_alignment'}
    if production and spec.get('captions') and spec.get('caption_timing') not in allowed:
        raise ValueError('Final captions require caption_timing: manual_measured, provider_timestamps, or forced_alignment. Character interpolation is preview-only.')
    last=0
    for c in spec.get('captions',[]):
        if not isinstance(c['text'],str) or not c['text'].strip():raise ValueError('Empty caption')
        if not 0<=c['start']<c['end']<=duration+.0001 or c['start']<last:raise ValueError('Captions must be ordered, nonoverlapping, and within audio')
        last=c['end']

def audit(events,renderer,fps,duration):
    frame_count=math.ceil(duration*fps);motions=[e for e in events if e['kind'] in ('draw','lift','exit')]
    minimum=min((event_samples(e,fps) for e in motions),default=0)
    crop=min(at(events,i/fps)[1][1]+renderer.crop_bottom_offset for i in range(frame_count) if i/fps<renderer.exit_end)
    edge_violations=check_hand_edges(events,renderer,fps,duration)
    return dict(hand_calibration=renderer.calibration,visible_cut_edges=edge_violations,all_cut_edges_offscreen=not edge_violations,qa_sample_times=qa_sample_times(events,fps,duration),duration=duration,fps=fps,frame_count=frame_count,draw_events=sum(e['kind']=='draw' for e in events),lift_events=sum(e['kind']=='lift' for e in events),minimum_motion_event_frames=minimum,minimum_bottom_crop_y=round(crop,3),crop_edge_offscreen=crop>BASE_H,nib_ink_geometry='same path endpoint; no independent optical tracking',hands='AI-generated transparent sprites, not filmed hands')

def verify_media(path,fps,duration,has_audio):
    """Inspect and fully decode the actual output, without claiming visual/listening QA."""
    result=subprocess.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)],capture_output=True,text=True,check=True)
    media=json.loads(result.stdout);streams=media.get('streams',[])
    videos=[s for s in streams if s.get('codec_type')=='video']
    audios=[s for s in streams if s.get('codec_type')=='audio']
    if len(videos)!=1 or len(audios)!=int(has_audio):raise ValueError('Final media has unexpected video/audio stream count')
    if any(s.get('codec_type')=='subtitle' for s in streams):raise ValueError('Captions are burned in; unexpected second subtitle track')
    durations=[float(videos[0].get('duration',media['format']['duration']))]
    if has_audio:durations.append(float(audios[0].get('duration',media['format']['duration'])))
    if any(not math.isfinite(d) or abs(d-duration)>1/fps+.03 for d in durations) or max(durations)-min(durations)>1/fps+.03:
        raise ValueError('Final audio/video duration differs from the master by more than one frame plus 30 ms encoder tolerance')
    decode=['ffmpeg','-v','error','-xerror','-i',str(path),'-map','0:v:0']
    if has_audio:decode+=['-map','0:a:0']
    decoded=subprocess.run(decode+['-f','null','-'],capture_output=True,text=True,check=True)
    if decoded.stderr.strip():raise ValueError('Final media decode reported errors: '+decoded.stderr.strip()[:500])
    return {'status':'pass','full_decode':'pass','stream_durations':durations,
            'size_bytes':path.stat().st_size,'sha256':sha256_file(path),
            'visual_review':'not_performed','listening_review':'not_performed'}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('storyboard',type=Path);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--audio',type=Path);parser.add_argument('--silent-preview',action='store_true')
    parser.add_argument('--project',type=Path,help='Reviewed production manifest; required for final videos >=60 seconds')
    parser.add_argument('--max-output-mib',type=float,help='Delivery budget; constrains bitrate and checks actual final size')
    parser.add_argument('--check-only',action='store_true',help='Validate and write audit/timeline, without creating any image, audio, or video')
    parser.add_argument('--hand',default='cream_pen');parser.add_argument('--hanzi-dir',type=Path,default=ROOT/'assets/hanzi')
    parser.add_argument('--font');parser.add_argument('--fps',default='auto');parser.add_argument('--width',type=int,default=1280);parser.add_argument('--height',type=int,default=720)
    parser.add_argument('--supersample',type=int,choices=[1,2],default=1);parser.add_argument('--still',type=float);parser.add_argument('--debug',action='store_true')
    args=parser.parse_args(argv)
    try:
        if args.width<=0 or args.height<=0 or args.width%2 or args.height%2 or args.width*9!=args.height*16:raise ValueError('This starter supports even-sized 16:9 output. Adapt layout before changing aspect ratio.')
        spec=json.loads(args.storyboard.read_text(encoding='utf-8'))
        if spec.get('version')!=1:raise ValueError('Storyboard version must be 1')
        audio=args.audio
        if audio is None and spec.get('audio'):audio=args.storyboard.parent/spec['audio']
        if audio is None and not args.silent_preview:raise ValueError('Final video needs --audio or storyboard.audio. Use --silent-preview only for explicitly labeled motion previews.')
        if audio is not None:
            if not shutil.which('ffprobe'):raise ValueError('Install or provide FFprobe before reading audio duration')
            duration=media_duration(audio)
        else:duration=float(spec['preview_duration'])
        if not math.isfinite(duration) or duration<=0:raise ValueError('Invalid duration')
        audio_hash=sha256_file(audio) if audio is not None else None
        project_report=None;delivery_limit=args.max_output_mib
        final_video=audio is not None and not args.silent_preview and args.still is None
        if final_video and duration>=60 and args.project is None:
            raise ValueError('Final videos of 60 seconds or longer require --project with accepted voice, measured master, reviewed scenes, and delivery budget')
        if args.project is not None:
            project=json.loads(args.project.read_text(encoding='utf-8'))
            project_report=production_preflight(project,args.project.parent,'render')
            scene_paths={(args.project.parent/s['storyboard']['path']).resolve() for s in project['scenes']}
            if args.storyboard.resolve() not in scene_paths:raise ValueError('Current storyboard is absent from reviewed project scenes')
            master=(args.project.parent/project['narration']['master']['path']).resolve()
            if audio is None or audio.resolve()!=master:raise ValueError('Use the reviewed continuous audio master from the project')
            limit=project['delivery']['limit_mib'];delivery_limit=min(delivery_limit,limit) if delivery_limit is not None else limit
        budget=delivery_budget(duration,delivery_limit,160 if audio is not None else 0) if delivery_limit is not None else None
        verify_captions(spec,duration,audio is not None and not args.silent_preview)
        style_report=inspect_style(spec)
        if style_report['issues']:raise ValueError('Style contract failed: '+'; '.join(style_report['issues']))
        events,masks,exit_end=compile_scene(spec,duration,args.hanzi_dir)
        verify_draw_bounds(spec,events);fps=select_fps(events,args.fps)
        renderer=Renderer(spec,events,masks,exit_end,args.hand,args.font,args.supersample)
        report=audit(events,renderer,fps,duration)
        report.update(input_hashes={'storyboard':sha256_file(args.storyboard),'audio_master':audio_hash,'renderer':sha256_file(Path(__file__)),'scene_contract':sha256_file(ROOT/'scripts/scene_contract.py'),'hand_config':sha256_file(ROOT/'assets/hand_variants.json'),'hand_asset':sha256_file(ROOT/'assets'/json.loads((ROOT/'assets/hand_variants.json').read_text())['variants'][args.hand]['file'])},production_preflight=project_report,delivery_budget=budget,media_verification={'status':'not_performed'},style=style_report,visual_review='not_performed',listening_review='not_performed',mode='motion_preview' if args.silent_preview else 'narrated_video',caption_timing=spec.get('caption_timing','none'))
        if not report['crop_edge_offscreen'] or not report['all_cut_edges_offscreen']:raise ValueError('Hand crop edge enters frame; adjust hand asset or path layout')
        args.output.parent.mkdir(parents=True,exist_ok=True)
        if args.check_only:
            report['mode']='validation_only'
        elif args.still is not None:
            report['mode']='still_preview'
            if not 0<=args.still<=duration:raise ValueError('Still time lies outside timeline')
            renderer.frame(args.still,args.debug).resize((args.width,args.height),Image.Resampling.LANCZOS).save(args.output)
        else:
            if not shutil.which('ffmpeg'):raise ValueError('Install or provide FFmpeg before encoding')
            cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{args.width}x{args.height}','-r',str(fps),'-i','-']
            if audio is not None:cmd+=['-i',str(audio)]
            cmd+=['-map','0:v:0']
            if audio is not None:cmd+=['-map','1:a:0']
            cmd+=['-c:v','libx264','-preset','veryfast','-pix_fmt','yuv420p']
            if budget:
                rate=str(budget['video_target_kbps'])+'k'
                cmd+=['-b:v',rate,'-maxrate',rate,'-bufsize',str(budget['video_target_kbps']*2)+'k']
            else:cmd+=['-crf','19']
            if audio is not None:cmd+=['-c:a','aac','-b:a','160k','-ar','48000']
            cmd+=['-t',str(duration),'-movflags','+faststart',str(args.output)]
            proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
            try:
                for i in range(report['frame_count']):
                    im=renderer.frame(i/fps)
                    if im.size!=(args.width,args.height):im=im.resize((args.width,args.height),Image.Resampling.LANCZOS)
                    proc.stdin.write(im.tobytes())
            finally:
                proc.stdin.close()
                code=proc.wait()
            if code:raise ValueError(f'FFmpeg failed with exit {code}')
            report['media_verification']=verify_media(args.output,fps,duration,audio is not None)
            if audio is not None and sha256_file(audio)!=audio_hash:raise ValueError('Audio master changed during rendering; output is not approved')
            if budget and args.output.stat().st_size>budget['limit_bytes']:
                raise ValueError('Encoded video exceeds delivery budget; lower bitrate/resolution or choose an approved destination with more capacity')
        timeline_path=args.output.with_suffix('.timeline.json')
        audit_path=args.output if args.check_only else args.output.with_suffix('.audit.json')
        report['artifacts']={'audit':str(audit_path),'timeline':str(timeline_path)}
        timeline_path.write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')
        audit_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({'output':str(args.output),**report},ensure_ascii=False))
        return 0
    except (ValueError,KeyError,TypeError,OSError,subprocess.CalledProcessError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())

