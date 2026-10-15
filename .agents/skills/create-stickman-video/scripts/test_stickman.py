#!/usr/bin/env python3
"""Run with: python -m unittest discover -s scripts -p 'test_*.py'."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import stickman


def fixture():
    a = {'positions': {'hero': 'left'}, 'props': {'cup': 'hero'}}
    b = {'positions': {'hero': 'center'}, 'props': {'cup': 'hero'}}
    clip = {'id': 'c1', 'duration_s': 1.2, 'environment': 'small room', 'composition': 'wide frame',
            'characters': ['hero'], 'opening_state': a, 'closing_state': b,
            'transition': {'kind': 'cut', 'reason': 'Beginning of story'}, 'narration': '你好，世界。',
            'beats': [{'start_s': 0, 'end_s': 0.5, 'action': 'raise cup', 'camera': 'locked wide', 'sfx': 'soft tap'},
                      {'start_s': 0.5, 'end_s': 1.2, 'action': 'move to center', 'camera': 'locked wide', 'sfx': 'none'}]}
    second = copy.deepcopy(clip)
    second.update(id='c2', duration_s=0.3, opening_state=b, transition={'kind': 'continuous', 'reason': ''}, narration='')
    second['beats'] = [{'start_s': 0, 'end_s': 0.3, 'action': 'hold still', 'camera': 'locked wide', 'sfx': 'none'}]
    return {'version': 1, 'title': 'Cup story', 'source_summary': 'A character lifts a cup.', 'ratio': '16:9',
            'duration_s': 1.5, 'style': 'classic-light', 'language': 'zh-CN',
            'characters': {'hero': 'thin black stick figure, round head, blue scarf', 'friend': 'short red stick figure, square glasses'},
            'voice_lock': 'one warm voice, same timbre and pace', 'palette': ['black', 'blue', 'white'],
            'clips': [clip, second], 'approval': {'status': 'draft', 'digest': ''}}


def authorize(project, status='user-approved'):
    project['approval'] = {'status': status, 'digest': stickman.digest(project), 'evidence': 'User explicitly approved this storyboard in message example-123.'}
    return project


class ContractTests(unittest.TestCase):
    def test_draft_valid_custom_decimal_timings(self):
        p = fixture()
        self.assertEqual(len(stickman.validate(p)), 64)
        with self.assertRaises(stickman.Invalid):
            stickman.compile_project(p)

    def test_standalone_locks_and_exact_narration(self):
        p = authorize(fixture())
        output = stickman.compile_project(p)
        self.assertEqual(output['artifact_type'], 'prompt-package')
        self.assertEqual(output['status'], 'compiled-prompts-only')
        for source, compiled in zip(p['clips'], output['clips']):
            for key in source['characters']:
                self.assertIn(p['characters'][key], compiled['prompt'])
            self.assertNotIn(p['characters']['friend'], compiled['prompt'])
            self.assertIn('MUST NOT appear', compiled['prompt'])
            self.assertIn('AUDIO-ONLY NARRATION', compiled['prompt'])
            self.assertIn('No visible text', compiled['prompt'])
            for lock in [p['voice_lock'], stickman.STYLES[p['style']], p['language'], p['ratio']]:
                self.assertIn(lock, compiled['prompt'])
            self.assertEqual(compiled['narration'], source['narration'])
            self.assertIn('NEGATIVE CONSTRAINTS', compiled['prompt'])
        self.assertEqual(output['clips'][1]['timeline_start_s'], 1.2)

    def test_empty_visible_cast_does_not_summon_characters(self):
        p = fixture()
        p['clips'][0]['characters'] = []
        p['clips'][0]['opening_state'] = {'props': {'cup': 'table'}}
        p['clips'][0]['closing_state'] = {'props': {'cup': 'table'}}
        for beat in p['clips'][0]['beats']:
            beat['action'] = 'Hold on cup resting on table; nobody enters.'
        p['clips'][1]['transition'] = {'kind': 'cut', 'reason': 'Later: hero has picked up the cup.'}
        output = stickman.compile_project(authorize(p))
        self.assertIn('(No characters visible.)', output['clips'][0]['prompt'])
        for anchor in p['characters'].values():
            self.assertNotIn(anchor, output['clips'][0]['prompt'])

    def test_delegation_record(self):
        p = authorize(fixture(), 'delegated-proceed')
        self.assertEqual(stickman.compile_project(p)['proceed_authority'], 'delegated-proceed')
        p['approval']['evidence'] = ''
        with self.assertRaises(stickman.Invalid):
            stickman.compile_project(p)

    def test_stale_authority(self):
        p = authorize(fixture())
        p['clips'][0]['narration'] = 'Different words'
        with self.assertRaisesRegex(stickman.Invalid, 'stale'):
            stickman.compile_project(p)

    def test_recomposition_requires_new_digest_and_state(self):
        p = authorize(fixture())
        p['clips'].reverse()
        with self.assertRaises(stickman.Invalid):
            stickman.compile_project(p)
        p['approval']['status'] = 'draft'
        p['clips'][0]['transition'] = {'kind': 'cut', 'reason': 'Reordered opening'}
        p['clips'][1]['transition'] = {'kind': 'cut', 'reason': 'Flashback'}
        authorize(p)
        self.assertEqual(stickman.compile_project(p)['clips'][0]['id'], 'c2')

    def test_invalid_fields(self):
        for field, value in [('duration_s', True), ('duration_s', float('nan')), ('duration_s', float('inf')),
                             ('duration_s', -1), ('duration_s', 2), ('version', True), ('style', []),
                             ('source_summary', ''), ('characters', []), ('palette', []), ('clips', []), ('language', None)]:
            with self.subTest(field=field, value=value):
                p = fixture()
                p[field] = value
                with self.assertRaises(stickman.Invalid):
                    stickman.validate(p)

    def test_invalid_clips(self):
        mutations = [lambda p: p['clips'][1].update(id='c1'),
                     lambda p: p['clips'][1].update(characters=['ghost']),
                     lambda p: p['clips'][1].update(characters=[{}]),
                     lambda p: p['clips'][1].update(opening_state={'different': True}),
                     lambda p: p['clips'][1].update(transition={'kind': 'cut', 'reason': ''}),
                     lambda p: p['clips'][0]['beats'][1].update(start_s=0.6),
                     lambda p: p['clips'][0]['beats'][1].update(end_s=1.1),
                     lambda p: p['clips'][0]['beats'][1].update(end_s=1.3),
                     lambda p: p['clips'][0]['beats'][0].update(start_s=True),
                     lambda p: p['clips'][0].update(duration_s=0)]
        for mutate in mutations:
            p = fixture()
            mutate(p)
            with self.assertRaises(stickman.Invalid):
                stickman.validate(p)

    def test_canonical_digest(self):
        p = fixture()
        before = stickman.digest(p)
        p = dict(reversed(list(p.items())))
        p['approval'] = {'status': 'draft', 'digest': 'not part of hash'}
        self.assertEqual(before, stickman.digest(p))
        p['title'] += '!'
        self.assertNotEqual(before, stickman.digest(p))

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(Path(stickman.__file__)), *map(str, args)], capture_output=True, text=True)

    def test_clean_cli_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'project.json'
            for content in ['{', '[]', 'null', '{"x":1,"x":2}', '{"duration_s":NaN}', '{"duration_s":1e999}', json.dumps(fixture()).replace('"classic-light"', '[]')]:
                path.write_text(content)
                result = self.run_cli('validate', path)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn('Traceback', result.stderr)
            result = self.run_cli('validate', Path(tmp) / 'missing')
            self.assertEqual(result.returncode, 2)

    def test_cli_compile_and_source_protection(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, out = Path(tmp) / 'story.json', Path(tmp) / 'prompts.json'
            src.write_text(json.dumps(authorize(fixture())), encoding='utf-8')
            before = src.read_bytes()
            self.assertEqual(self.run_cli('compile', src, '--out', out).returncode, 0)
            self.assertEqual(json.loads(out.read_text())['artifact_type'], 'prompt-package')
            self.assertEqual(self.run_cli('compile', src, '--out', src).returncode, 2)
            self.assertEqual(src.read_bytes(), before)

    def test_hardlink_output_cannot_overwrite_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, alias = Path(tmp) / 'story.json', Path(tmp) / 'alias.json'
            src.write_text(json.dumps(authorize(fixture())), encoding='utf-8')
            os.link(src, alias)
            before = src.read_bytes()
            result = self.run_cli('compile', src, '--out', alias)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn('Traceback', result.stderr)
            self.assertEqual(src.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
