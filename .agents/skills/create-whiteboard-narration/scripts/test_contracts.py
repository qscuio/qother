#!/usr/bin/env python3
"""Regression tests use authored vectors, synthetic pixels and inert bytes; no TTS/video."""
import copy
import contextlib
import io
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
import production_preflight as pf
import render_whiteboard as wb
from scene_contract import block_items, inspect_style, ordered_parts


class SemanticTests(unittest.TestCase):
    def parts(self):
        return [
            {'id': 'roof', 'after': ['body'], 'outline': [{'type': 'path', 'points': [[20,20],[40,10]]}],
             'fills': [{'type':'fill','polygon':[[20,20],[40,10],[40,20]],'color':[190,220,235]}]},
            {'id': 'body', 'outline': [{'type': 'path', 'points': [[20,20],[20,40],[40,40]]}],
             'fills': [{'type':'fill','polygon':[[20,20],[40,20],[40,40],[20,40]],'color':[190,220,235]}]},
        ]

    def test_same_order_outlines_then_fills(self):
        items = block_items({'parts': self.parts()})
        self.assertEqual([(i['_part_id'],i['_phase']) for i in items],
                         [('body','outline'),('roof','outline'),('body','fill'),('roof','fill')])

    def test_per_part_order(self):
        items = block_items({'parts': self.parts(),'ordering':'per_part'})
        self.assertEqual([(i['_part_id'],i['_phase']) for i in items],
                         [('body','outline'),('body','fill'),('roof','outline'),('roof','fill')])

    def test_legacy_and_source_unchanged(self):
        items=[{'type':'path','points':[[0,0],[2,2]],'tag':'legacy'}]
        self.assertEqual(block_items({'items':items}),items)
        p=self.parts();old=copy.deepcopy(p);block_items({'parts':p});self.assertEqual(p,old)

    def test_invalid_orders(self):
        for case in ('duplicate','cycle','unknown','mixed','bad_fill'):
            with self.subTest(case=case),self.assertRaises(ValueError):
                parts=self.parts();block={'parts':parts}
                if case=='duplicate':parts[0]['id']='body'
                if case=='cycle':parts[1]['after']=['roof']
                if case=='unknown':parts[0]['after']=['window']
                if case=='mixed':block['items']=[]
                if case=='bad_fill':parts[0]['fills']=[{'type':'path'}]
                block_items(block)

    def test_compile_tracks_semantic_phases(self):
        spec={'blocks':[{'start':0,'end':9,'parts':self.parts()}],'exit':{'start':9,'end':9.5}}
        events,_,_=wb.compile_scene(spec,10,wb.ROOT/'assets/hanzi')
        phases=[]
        for e in events:
            if e['kind']=='draw' and (e['part_id'],e['phase']) not in phases:phases.append((e['part_id'],e['phase']))
        self.assertEqual(phases,[('body','outline'),('roof','outline'),('body','fill'),('roof','fill')])


class MotionTests(unittest.TestCase):
    def spec(self):
        return json.loads((wb.ROOT/'assets/storyboard.example.json').read_text())

    def test_all_hands_edges_and_transition_samples(self):
        spec=self.spec();events,masks,end=wb.compile_scene(spec,10,wb.ROOT/'assets/hanzi')
        fps=wb.select_fps(events,'auto');self.assertLessEqual(fps,60)
        for name in ('cream_pen','marker','pencil'):
            renderer=wb.Renderer(spec,events,masks,end,name)
            report=wb.audit(events,renderer,fps,10)
            self.assertTrue(report['all_cut_edges_offscreen'])
            self.assertEqual(report['hand_calibration']['visual_tip_review'],'not_performed')
            self.assertEqual(report['qa_sample_times'][-1],round((math.ceil(10*fps)-1)/fps,9))
            for time in report['qa_sample_times']:
                self.assertAlmostEqual(time*fps,round(time*fps),places=6)

    def test_stale_or_invalid_hand_anchor(self):
        image=Image.new('RGBA',(20,20),'white')
        for preset in ({'nib_anchor':[2,20],'render_height':30},
                       {'nib_anchor':[float('nan'),2],'render_height':30},
                       {'nib_anchor':[2,2],'render_height':30,'source_size':[21,20]}):
            with self.assertRaises(ValueError):wb.validate_hand(image,preset)
        with self.assertRaises(ValueError):
            wb.validate_hand(Image.new('RGBA',(20,20)),{'nib_anchor':[10,10],'render_height':30})

    def test_visible_side_edge_is_rejected(self):
        spec=self.spec();events,masks,end=wb.compile_scene(spec,10,wb.ROOT/'assets/hanzi')
        renderer=wb.Renderer(spec,events,masks,end,'cream_pen')
        renderer.source_edges=[('left',(0,0),(0,20))]
        renderer.pivot=(0,0);renderer.hand_scale=(1,1)
        self.assertTrue(wb.check_hand_edges(events,renderer,30,10))

    def test_explicit_fps_not_raised_and_auto_bounded(self):
        events=[{'kind':'draw','tag':'dense','start':0,'end':.02}]
        with self.assertRaisesRegex(ValueError,'capped at 60'):wb.select_fps(events,'auto')
        with self.assertRaisesRegex(ValueError,'at 24 fps'):wb.select_fps(events,'24')
        self.assertEqual(wb.select_fps(events,'120'),120)

    def test_exit_sampling_is_checked(self):
        with self.assertRaises(ValueError):
            wb.select_fps([{'kind':'exit','tag':'exit','start':1,'end':1.001}],'auto')
        self.assertEqual(wb.event_samples({'start':0,'end':.1},30),2)

    def test_nonfinite_times_and_text(self):
        for target in ('block','exit'):
            spec=self.spec()
            if target=='block':spec['blocks'][0]['start']=float('nan')
            else:spec['exit']['end']=float('inf')
            with self.assertRaises(ValueError):wb.compile_scene(spec,10,wb.ROOT/'assets/hanzi')
        with self.assertRaises(ValueError):wb.text_strokes({'at':[0,0],'size':float('nan'),'text':'A'},wb.ROOT/'assets/hanzi')

    def test_caption_overlap_rejected(self):
        with self.assertRaises(ValueError):
            wb.verify_captions({'caption_timing':'manual_measured','captions':[
                {'start':0,'end':2,'text':'A'},{'start':1,'end':3,'text':'A'}]},10,True)

    def test_check_only_writes_the_exact_requested_path(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'requested-preflight.json'
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                code=wb.main([str(wb.ROOT/'assets/storyboard.example.json'),'--silent-preview','--check-only','--output',str(output)])
            self.assertEqual(code,0);self.assertTrue(output.is_file())
            self.assertEqual(json.loads(output.read_text())['mode'],'validation_only')
            self.assertEqual(json.loads(stdout.getvalue())['output'],str(output))
            self.assertTrue(output.with_suffix('.timeline.json').is_file())
            self.assertEqual({p.suffix for p in Path(directory).iterdir()},{'.json'})

    def test_check_only_rejects_late_caption_overflow(self):
        with tempfile.TemporaryDirectory() as directory:
            spec=self.spec();spec['captions']=[{'start':9,'end':9.9,'text':'A'*1000}]
            storyboard=Path(directory)/'scene.json';storyboard.write_text(json.dumps(spec))
            output=Path(directory)/'preflight.json'
            with contextlib.redirect_stderr(io.StringIO()) as stderr:
                code=wb.main([str(storyboard),'--silent-preview','--check-only','--output',str(output)])
            self.assertEqual(code,2);self.assertIn('more than two lines',stderr.getvalue());self.assertFalse(output.exists())

    def test_expanded_text_bounds(self):
        spec=self.spec();spec['blocks'][0]['items'][0].update(text='AAAA',at=[1250,100])
        events,_,_=wb.compile_scene(spec,10,wb.ROOT/'assets/hanzi')
        with self.assertRaisesRegex(ValueError,'Expanded stroke'):wb.verify_draw_bounds(spec,events)

    def test_style_mismatch(self):
        spec=self.spec();self.assertEqual(inspect_style(spec)['status'],'pass')
        spec['blocks'][0]['items'][0]['color']=[255,0,0]
        self.assertEqual(inspect_style(spec)['status'],'fail')
        spec=self.spec();spec['blocks'][0]['items'][0]['at']=[20,600]
        self.assertEqual(inspect_style(spec)['status'],'fail')


class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        # These are inert byte fixtures, never encoded media or a synthesized voice.
        (self.root/'master.fixture').write_bytes(b'unchanged-authoritative-master')
        (self.root/'audition.fixture').write_bytes(b'approved-audition')
        (self.root/'frame.fixture').write_bytes(b'reviewed-frame')
        (self.root/'script.txt').write_text('One idea. Another idea.',encoding='utf-8')
        spec=json.loads((wb.ROOT/'assets/storyboard.example.json').read_text())
        (self.root/'scene.json').write_text(json.dumps(spec))
        file=lambda p:{'path':p,'sha256':pf.sha256_file(self.root/p)}
        self.project={'version':1,'style_id':spec['style']['id'],'rejected_voices':[],
            'narration':{'source':'synthesized','master':file('master.fixture'),'script':file('script.txt'),
                         'duration_seconds':10,'continuous_master':True,'timing_method':'manual_measured',
                         'visual_edit_audio_policy':'preserve_master',
                         'beats':[{'id':'a','start':0,'end':4,'text':'One idea. '},
                                  {'id':'b','start':4,'end':9.9,'text':'Another idea.'}],
                         'voice':{'provider':'Example','model':'v1','id':'neutral',
                                  'acceptance':{'status':'accepted','user_evidence':'test approval fixture','sample':file('audition.fixture')}}},
            'scenes':[{'id':'one','storyboard':file('scene.json'),'narration_quote':'One idea.',
                       'explains':'Envelope movement','visual_review':{'status':'accepted','reviewer':'test fixture','evidence':'test fixture','sample':file('frame.fixture')}}],
            'delivery':{'destination':'authorized chat','limit_mib':10,'audio_kbps':160}}

        voice=self.project['narration']['voice']
        voice['acceptance']['configuration_sha256']=pf.voice_configuration_hash(voice)

    def tearDown(self):self.temp.cleanup()

    def test_voice_decision_and_rejected_voice(self):
        self.assertEqual(pf.voice_gate(self.project,self.root)['status'],'accepted_record')
        voice=self.project['narration']['voice'];voice['acceptance']['status']='pending'
        with self.assertRaises(ValueError):pf.voice_gate(self.project,self.root)
        voice['acceptance']['status']='accepted'
        self.project['rejected_voices']=[{**{k:voice[k] for k in ('provider','model','id')},'reason':'user rejected fixture'}]
        with self.assertRaisesRegex(ValueError,'rejected'):pf.voice_gate(self.project,self.root)

    def test_provided_audio_does_not_require_new_voice(self):
        self.project['narration']['source']='provided';del self.project['narration']['voice']
        self.assertEqual(pf.voice_gate(self.project,self.root)['status'],'provided_audio')

    def test_changed_voice_configuration_rejected(self):
        self.project['narration']['voice']['settings']={'speed':1.2}
        with self.assertRaisesRegex(ValueError,'configuration changed'):pf.voice_gate(self.project,self.root)

    def test_scene_quote_must_match_narration(self):
        self.project['scenes'][0]['narration_quote']='Not spoken'
        with self.assertRaisesRegex(ValueError,'absent'):pf.scene_gate(self.project,self.root)

    def test_changed_audition_rejected(self):
        (self.root/'audition.fixture').write_bytes(b'new voice')
        with self.assertRaisesRegex(ValueError,'Changed'):pf.voice_gate(self.project,self.root)

    @patch.object(pf,'measured_duration',return_value=10)
    def test_complete_readonly_preflight(self,_):
        report=pf.run(self.project,self.root,'render')
        self.assertEqual(report['status'],'pass');self.assertEqual(report['listening_review'],'not_performed')

    @patch.object(pf,'measured_duration',return_value=10)
    def test_master_script_and_timing_mutations_rejected(self,_):
        for target in ('master','script','beats','retime','continuous','policy','nan'):
            with self.subTest(target=target):
                p=copy.deepcopy(self.project)
                if target in ('master','script'):p['narration'][target]['sha256']='0'*64
                if target=='beats':p['narration']['beats'].reverse()
                if target=='retime':p['narration']['duration_seconds']=12
                if target=='continuous':p['narration']['continuous_master']=False
                if target=='policy':p['narration']['visual_edit_audio_policy']='resynthesize_each_scene'
                if target=='nan':p['narration']['beats'][0]['end']=float('nan')
                with self.assertRaises(ValueError):pf.narration_gate(p,self.root)

    def test_shared_style_values_must_match_across_scenes(self):
        scene=copy.deepcopy(self.project['scenes'][0]);scene['id']='two'
        spec=json.loads((self.root/'scene.json').read_text());spec['style']['outline_width_range']=[2,6]
        path=self.root/'scene-two.json';path.write_text(json.dumps(spec))
        scene['storyboard']={'path':path.name,'sha256':pf.sha256_file(path)}
        self.project['scenes'].append(scene)
        with self.assertRaisesRegex(ValueError,'shared palette'):pf.scene_gate(self.project,self.root)

    def test_stale_scene_and_sample_reviews(self):
        for target in ('storyboard','sample','status'):
            p=copy.deepcopy(self.project)
            if target=='storyboard':p['scenes'][0]['storyboard']['sha256']='0'*64
            if target=='sample':p['scenes'][0]['visual_review']['sample']['sha256']='0'*64
            if target=='status':p['scenes'][0]['visual_review']['status']='pending'
            with self.assertRaises(ValueError):pf.scene_gate(p,self.root)

    def test_delivery_budget_and_actual_size(self):
        plan=pf.delivery_budget(60,10)
        self.assertLess(plan['video_target_kbps']+160,10*1024*1024*8/60/1000)
        self.assertFalse(plan['guaranteed_size'])
        with self.assertRaises(ValueError):pf.delivery_budget(3600,1)
        with self.assertRaises(ValueError):pf.delivery_budget(float('nan'),10)
        p=copy.deepcopy(self.project);p['delivery']['final_file']='large.fixture';p['delivery']['limit_mib']=1
        (self.root/'large.fixture').write_bytes(b'0'*(1024*1024+1))
        with self.assertRaisesRegex(ValueError,'exceeds'):pf.delivery_gate(p,self.root,{'duration_seconds':10})

    def test_delivery_rejects_directory_or_empty_file(self):
        for name in ('.','empty.fixture'):
            (self.root/'empty.fixture').write_bytes(b'')
            self.project['delivery']['final_file']=name
            with self.assertRaises(ValueError):pf.delivery_gate(self.project,self.root,{'duration_seconds':10})

    @patch.object(pf,'measured_duration',return_value=10)
    def test_delivery_needs_actual_file(self,_):
        with self.assertRaisesRegex(ValueError,'final_file'):pf.run(self.project,self.root,'delivery')


class EncodedAuditTests(unittest.TestCase):
    @patch.object(wb.subprocess,'run')
    def test_decode_result_is_separate_from_subjective_review(self,run):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'inert.fixture';path.write_bytes(b'not an encoded video')
            run.return_value.stderr=''
            run.return_value.stdout=json.dumps({'format':{'duration':'10'},'streams':[
                {'codec_type':'video','duration':'10'},{'codec_type':'audio','duration':'10.02'}]})
            report=wb.verify_media(path,30,10,True)
            self.assertEqual(report['status'],'pass')
            self.assertEqual(report['listening_review'],'not_performed')
            self.assertEqual(run.call_count,2)
            self.assertIn('ffmpeg',run.call_args.args[0]);self.assertIn('-xerror',run.call_args.args[0])
            run.return_value.stderr='Error while decoding stream #0:0: Invalid data found when processing input'
            with self.assertRaisesRegex(ValueError,'decode reported errors'):wb.verify_media(path,30,10,True)
            run.return_value.stderr=''
            run.return_value.stdout=json.dumps({'format':{'duration':'10'},'streams':[
                {'codec_type':'video','duration':'10'},{'codec_type':'audio','duration':'9'}]})
            with self.assertRaises(ValueError):wb.verify_media(path,30,10,True)


if __name__=='__main__':unittest.main()
