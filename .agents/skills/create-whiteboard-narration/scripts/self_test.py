#!/usr/bin/env python3
"""Deterministic invariants. Generates nothing unless --output-dir is supplied."""
import argparse, copy, importlib.util, json, math, subprocess, sys
from pathlib import Path
from PIL import Image, ImageChops
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import render_whiteboard as wb

def main():
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path);args=p.parse_args()
    spec=json.loads((wb.ROOT/'assets/storyboard.example.json').read_text())
    events,masks,end=wb.compile_scene(spec,10,wb.ROOT/'assets/hanzi')
    fps=wb.select_fps(events,'auto')
    assert all(wb.event_samples(e,fps)>=2 for e in events if e['kind'] in ('draw','lift'))
    tags=[e['tag'].split(':')[2] for e in events if e['kind']=='draw' and e['tag'].startswith('text:')]
    assert tags.index('包')>max(i for i,v in enumerate(tags) if v=='小'), 'Characters must not interleave'
    draw=next(e for e in events if e['kind']=='draw')
    t=(draw['start']+draw['end'])/2;e,nib,u=wb.at(events,t);inkpoint,_=wb.along(e,u)
    assert nib==inkpoint, 'Nib and current ink must use same endpoint'
    lift=next(e for e in events if e['kind']=='lift' and e['start']>draw['end'])
    r=wb.Renderer(spec,events,masks,end,'cream_pen');r.frame(lift['start']);before=r.ink.copy();r.frame((lift['start']+lift['end'])/2)
    assert ImageChops.difference(before,r.ink).getbbox() is None, 'Lift added ink'
    fill=next(e for e in events if e.get('fill_id'));r=wb.Renderer(spec,events,masks,end,'cream_pen')
    ink=Image.new('RGBA',(1280,720));partial=ink.copy();full=ink.copy()
    r.paint(fill,.2,ink,partial);r.paint(fill,1,ink,full)
    pa=partial.getchannel('A');fa=full.getchannel('A')
    assert sum(i*n for i,n in enumerate(pa.histogram()))<sum(i*n for i,n in enumerate(fa.histogram())), 'Fill leaked before brush traversal'
    assert ImageChops.subtract(pa,r.masks[fill['fill_id']]).getbbox() is None, 'Fill escaped polygon'
    try:wb.text_strokes({'text':'不存在的数据','at':[0,0]},wb.ROOT/'assets/hanzi')
    except ValueError:pass
    else:raise AssertionError('Missing Hanzi must fail, not fake a reveal')
    try:wb.select_fps(events,'1')
    except ValueError:pass
    else:raise AssertionError('Undersampled strokes/lifts must fail')
    try:wb.verify_captions({'caption_timing':'character_interpolation','captions':[{'start':0,'end':1,'text':'A'}]},10,True)
    except ValueError:pass
    else:raise AssertionError('Character interpolation is not measured timing')
    reports={}
    for hand in ('cream_pen','marker','pencil'):
        r=wb.Renderer(spec,events,masks,end,hand);reports[hand]=wb.audit(events,r,fps,10)
        assert reports[hand]['crop_edge_offscreen'] and reports[hand]['all_cut_edges_offscreen']
    if args.output_dir:
        args.output_dir.mkdir(parents=True,exist_ok=True)
        for hand in reports:
            for t in (1.0,5.0,9.5):
                wb.Renderer(spec,events,masks,end,hand).frame(t).save(args.output_dir/f'{hand}-{t:.1f}.png')
        (args.output_dir/'self-test.json').write_text(json.dumps(reports,indent=2))
    print(json.dumps({'status':'PASS','fps':fps,'events':len(events),'checks':['isolated characters','nib/ink endpoint','pen lifts add no ink','partial fill only','polygon clipping','missing Hanzi rejection','undersampled motion rejection','unmeasured caption rejection','all four source-cut edges offscreen for all hands']},indent=2))
if __name__=='__main__':main()
