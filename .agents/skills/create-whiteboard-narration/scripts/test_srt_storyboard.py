import copy
import unittest
from srt_storyboard import compile_storyboard, parse_srt

SRT='1\n00:00:00,200 --> 00:00:03,000\n小包到达。\n\n2\n00:00:03,100 --> 00:00:06,000\n随后转发。\n'
def plan():
    part={'id':'packet','outline':[{'type':'path','points':[[100,100],[200,100]],'width':4}], 'fills':[]}
    return {'duration_ms':7500,'caption_timing':'preview_only','beats':[
        {'id':'arrival','narrative_role':'对象出现','cue_ids':[1],'start_ms':200,'end_ms':2800,'parts':[part]},
        {'id':'forward','narrative_role':'因果变化','cue_ids':[2],'start_ms':3100,'end_ms':6000,'parts':[part]}]}
class Tests(unittest.TestCase):
    def test_compile(self):
        p=plan(); old=copy.deepcopy(p); result=compile_storyboard(SRT,p)
        self.assertEqual(result['background'],[245,235,215]); self.assertEqual(p,old)
        self.assertEqual(result['captions'][1]['start'],3.1)
        self.assertEqual(result['exit']['end'],6.5)
    def test_bom_crlf_multiline(self):
        cues=parse_srt('\ufeff'+SRT.replace('小包到达。','小包\n到达。').replace('\n','\r\n'))
        self.assertEqual(cues[0]['text'],'小包\n到达。')
    def test_invalid_srt(self):
        for s in ['',SRT.replace('00:00:03,100','00:00:02,100'),SRT.replace('\n2\n','\n1\n'),SRT.replace('00:00:03,000','00:60:03,000')]:
            with self.subTest(s=s),self.assertRaises(ValueError): parse_srt(s)
    def test_bad_plan(self):
        for key in ['coverage','overlap','hold','cue','timing','parts','range','duplicate','boolean']:
            p=plan()
            if key=='coverage': p['beats'].pop()
            if key=='overlap': p['beats'][1]['start_ms']=2000
            if key=='hold': p['duration_ms']=6500
            if key=='cue': p['beats'][1]['cue_ids']=[999]
            if key=='timing': p['caption_timing']='SRT proves alignment'
            if key=='parts': p['beats'][0]['parts']=[]
            if key=='range': p['beats'][1]['start_ms']=6100;p['beats'][1]['end_ms']=6400
            if key=='duplicate': p['beats'][1]['id']='arrival'
            if key=='boolean': p['beats'][0]['start_ms']=True
            with self.subTest(key=key),self.assertRaises(ValueError): compile_storyboard(SRT,p)

class RendererThemeTests(unittest.TestCase):
    def test_theme_pixels_and_legacy_default(self):
        import render_whiteboard as wb
        p=plan(); spec=compile_storyboard(SRT,p);spec['captions']=[]
        events,masks,exit_end=wb.compile_scene(spec,7.5,wb.ROOT/'assets/hanzi')
        for background,expected in [([245,235,215],(245,235,215)),(None,(255,255,255))]:
            candidate=copy.deepcopy(spec)
            if background is None:candidate.pop('background')
            else:candidate['background']=background
            renderer=wb.Renderer(candidate,events,masks,exit_end,'cream_pen')
            self.assertEqual(renderer.frame(0).getpixel((1200,20))[:3],expected)
    def test_invalid_background(self):
        import render_whiteboard as wb
        spec=compile_storyboard(SRT,plan());spec['captions']=[]
        events,masks,exit_end=wb.compile_scene(spec,7.5,wb.ROOT/'assets/hanzi')
        for bad in [[256,0,0],[0,0],['245',235,215],[True,0,0]]:
            spec['background']=bad
            with self.subTest(bad=bad),self.assertRaises(ValueError):wb.Renderer(spec,events,masks,exit_end,'cream_pen')

if __name__=='__main__':unittest.main()
