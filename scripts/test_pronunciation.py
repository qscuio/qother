#!/usr/bin/env python3
"""Offline pronunciation tests. No provider calls or audio generation."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import apply_pronunciation as p


class PronunciationTests(unittest.TestCase):
    def setUp(self):
        self.lexicon = p.load_lexicon()

    def prepare(self, text):
        return p.prepare_spoken_text(text, self.lexicon, allow_pending=True)

    def test_release_versions_and_v1_0_0_preserved(self):
        previous_path = p.DEFAULT_LEXICON.with_name('technical-zh-CN.v1.0.0.json')
        self.assertEqual(hashlib.sha256(previous_path.read_bytes()).hexdigest(),
                         'ea1ccf5a3435fbf5ba2efafd0b9b796ddfad59d5cc76d877f522c0a7afb270e8')
        previous = p.load_lexicon(previous_path)
        self.assertEqual(previous['version'], '1.0.0')
        self.assertEqual(self.lexicon['version'], '1.1.0')
        self.assertEqual(self.lexicon['schema_version'], previous['schema_version'])
        self.assertEqual(self.lexicon['entries'][:-1], previous['entries'])
        old_result = p.prepare_spoken_text('Ethernet MAC', previous, allow_pending=True)
        self.assertEqual(old_result['spoken_text'], 'Ethernet 麦克')
        self.assertEqual(old_result['lexicon_version'], '1.0.0')

    def test_seven_terms_and_exact_candidate_inputs(self):
        expected = {'MAC': '麦克', 'VLAN': 'V lan', 'In-LIF': 'in leaf',
                    'Out-LIF': 'out leaf', 'LIF': 'leaf', 'RIF': 'riff',
                    'Ethernet': 'E zer net'}
        self.assertEqual({e['display']: e['tts']['input'] for e in self.lexicon['entries']}, expected)
        text = 'Ethernet帧的MAC地址属于VLAN。In-LIF和Out-LIF，以及LIF、RIF。'
        result = self.prepare(text)
        self.assertEqual(result['display_text'], text)
        self.assertEqual(result['spoken_text'], 'E zer net帧的麦克地址属于V lan。in leaf和out leaf，以及leaf、riff。')
        self.assertEqual(result['pending_terms'], sorted(expected))
        self.assertEqual(len(result['replacements']), 7)
        self.assertEqual(result['lexicon_version'], '1.1.0')
        self.assertFalse(result['audio_generated'])
        for change in result['replacements']:
            self.assertEqual(text[change['start']:change['end']], change['matched'])
            self.assertEqual(change['audition_status'], 'pending_for_profile')

    def test_ethernet_is_explicit_and_pending(self):
        ethernet = self.lexicon['entries'][-1]
        self.assertEqual(ethernet, {'display': 'Ethernet', 'aliases': [],
            'oral_reading': 'E zer net', 'tts': {'engine': 'qwen3-tts',
            'input': 'E zer net', 'audition': {'status': 'pending', 'profile': None, 'evidence': None}}})
        text = 'ethernet ETHERNET EtherNet FastEthernet GigabitEthernet Ethernet0 Ethernet_MAC E zer net'
        self.assertEqual(self.prepare(text)['spoken_text'], text)
        self.assertEqual(self.prepare(text)['replacements'], [])

    def test_all_spellings_prose_boundaries(self):
        for entry in self.lexicon['entries']:
            for spelling in [entry['display'], *entry['aliases']]:
                for template in ('{}', '中文{}接口', '“{}”，', '（{}）', '{}.\n', '{}；', '( {})'):
                    text = template.format(spelling)
                    with self.subTest(spelling=spelling, text=text):
                        result = self.prepare(text)
                        self.assertEqual(result['display_text'], text)
                        self.assertEqual(result['spoken_text'], template.format(entry['tts']['input']))
                        self.assertEqual(len(result['replacements']), 1)

    def test_all_spellings_identifier_and_protected_boundaries(self):
        templates = ('x{}', '{}x', '_{}', '{}_ID', '{}1', '{}１', 'é{}', '{}é',
                     '{}\u0301', 'pre-{}', '{}-like', 'net.{}', '{}.value',
                     'ns::{}', '{}::value', '{}()', '`{}`', '```\n{}\n```',
                     '~~~\n{}\n~~~', '`{}', '```\n{}', '~~~\n{}',
                     'https://example.test/{}', 'www.example.test/{}',
                     '/tmp/{}', './{}', '../{}', 'C:\\folder\\{}')
        for entry in self.lexicon['entries']:
            for spelling in [entry['display'], *entry['aliases']]:
                for template in templates:
                    text = template.format(spelling)
                    with self.subTest(spelling=spelling, text=text):
                        result = self.prepare(text)
                        self.assertEqual(result['spoken_text'], text)
                        self.assertEqual(result['replacements'], [])

    def test_all_candidates_fail_closed_until_audition(self):
        for entry in self.lexicon['entries']:
            with self.subTest(term=entry['display']):
                with self.assertRaises(p.PendingPronunciationError):
                    p.prepare_spoken_text(entry['display'], self.lexicon)

    def test_current_candidates_are_text_idempotent_not_acceptance(self):
        texts = [e['display'] for e in self.lexicon['entries']]
        texts += [' '.join(texts), 'Ethernet与MAC、VLAN、In-LIF、Out-LIF、LIF、RIF。`Ethernet MAC`']
        for text in texts:
            with self.subTest(text=text):
                first = self.prepare(text)
                second = self.prepare(first['spoken_text'])
                self.assertEqual(second['spoken_text'], first['spoken_text'])
                self.assertEqual(second['replacements'], [])
                self.assertEqual(first['pronunciation_status'], 'pending_audition')
                self.assertEqual(second['pronunciation_status'], 'no_pending_replacements')
                self.assertFalse(second['audio_generated'])

    def test_six_terms_and_display_preserved(self):
        text = 'MAC地址属于VLAN。In-LIF和Out-LIF，以及LIF、RIF。'
        result = self.prepare(text)
        self.assertEqual(result['display_text'], text)
        self.assertEqual(result['spoken_text'], '麦克地址属于V lan。in leaf和out leaf，以及leaf、riff。')
        self.assertEqual(len(result['replacements']), 6)
        self.assertEqual(result['pronunciation_status'], 'pending_audition')
        self.assertFalse(result['audio_generated'])
        for change in result['replacements']:
            self.assertEqual(text[change['start']:change['end']], change['matched'])

    def test_longest_match_single_pass(self):
        result = self.prepare('Out-LIF/In-LIF/LIF')
        self.assertEqual(result['spoken_text'], 'out leaf/in leaf/leaf')
        self.assertEqual([c['display'] for c in result['replacements']], ['Out-LIF', 'In-LIF', 'LIF'])
        altered = copy.deepcopy(self.lexicon)
        altered['entries'][0]['tts']['input'] = 'VLAN'
        self.assertEqual(p.prepare_spoken_text('MAC', altered, allow_pending=True)['spoken_text'], 'VLAN')

    def test_only_explicit_typographic_hyphen_aliases(self):
        self.assertEqual(self.prepare('In‐LIF Out‑LIF')['spoken_text'], 'in leaf out leaf')
        self.assertEqual(self.prepare('IN-LIF out-lif InLIF Out_LIF')['spoken_text'], 'IN-LIF out-lif InLIF Out_LIF')

    def test_no_common_word_case_or_unknown_acronym_conversion(self):
        text = 'mac Mac vlan leaf riff in out PP TM IP DNX SDK CPU MACsec MACSEC VLAN100 LIF2'
        self.assertEqual(self.prepare(text)['spoken_text'], text)

    def test_identifier_boundaries(self):
        text = 'MAC_ADDRESS get_MAC xMAC MACx RIF_ID In-LIF_ID bcm_lif_t pre-MAC MAC-like net.MAC MAC.value ns::LIF RIF() éMAC MACé MAC１'
        self.assertEqual(self.prepare(text)['spoken_text'], text)

    def test_punctuation_and_chinese_boundaries(self):
        text = '“MAC”，VLAN；（LIF）RIF（接口）。MAC.\nVLAN。'
        self.assertEqual(self.prepare(text)['spoken_text'], '“麦克”，V lan；（leaf）riff（接口）。麦克.\nV lan。')

    def test_code_fences_inline_code_links_and_paths(self):
        text = 'MAC `MAC VLAN`\n```python\nLIF RIF\n```\nVLAN\n~~~\nOut-LIF\n~~~\nIn-LIF https://example.test/MAC www.example.test/VLAN /tmp/LIF ./MAC ../RIF C:\\MAC\\file'
        expected = text.replace('MAC `', '麦克 `', 1).replace('```\nVLAN\n', '```\nV lan\n').replace('~~~\nIn-LIF https', '~~~\nin leaf https')
        self.assertEqual(self.prepare(text)['spoken_text'], expected)

    def test_unclosed_code_is_protected(self):
        for suffix in ('`MAC VLAN', '```\nMAC VLAN', '~~~\nMAC VLAN'):
            self.assertEqual(self.prepare('RIF\n' + suffix)['spoken_text'], 'riff\n' + suffix)

    def test_pending_fails_closed_without_output(self):
        with self.assertRaises(p.PendingPronunciationError):
            p.prepare_spoken_text('MAC', self.lexicon)
        result = p.prepare_spoken_text('No listed term.', self.lexicon)
        self.assertEqual(result['spoken_text'], 'No listed term.')
        self.assertEqual(result['pronunciation_status'], 'no_pending_replacements')

    def test_acceptance_requires_exact_profile_and_evidence(self):
        entry = self.lexicon['entries'][0]
        entry['tts']['audition'] = {'status': 'accepted', 'profile': 'synthetic-fixture-profile', 'evidence': 'synthetic-fixture-review', 'input': entry['tts']['input'], 'engine': entry['tts']['engine']}
        self.assertEqual(p.prepare_spoken_text('MAC', self.lexicon, profile='synthetic-fixture-profile')['pending_terms'], [])
        for profile in (None, 'different-profile'):
            with self.assertRaises(p.PendingPronunciationError):
                p.prepare_spoken_text('MAC', self.lexicon, profile=profile)
        for key in ('input', 'engine'):
            original = entry['tts'][key]
            entry['tts'][key] = 'changed-candidate'
            with self.assertRaises(p.PendingPronunciationError):
                p.prepare_spoken_text('MAC', self.lexicon, profile='synthetic-fixture-profile')
            result = p.prepare_spoken_text('MAC', self.lexicon, profile='synthetic-fixture-profile', allow_pending=True)
            self.assertEqual(result['pending_terms'], ['MAC'])
            entry['tts'][key] = original
        del entry['tts']['audition']['evidence']
        with self.assertRaises(ValueError):
            p.validate_lexicon(self.lexicon)

    def test_invalid_schema_and_duplicates(self):
        for data in ([], {'schema_version': 2}, {'schema_version': 1, 'version': '1', 'language':'zh', 'entries': []}):
            with self.assertRaises(ValueError): p.validate_lexicon(data)
        self.lexicon['entries'][1]['aliases'] = ['MAC']
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            p.validate_lexicon(self.lexicon)

    def test_cli_preserves_bytes_and_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); src = root / 'canonical.txt'; out = root / 'out'
            original = 'Ethernet\r\nMAC\r\nIn-LIF\r\n'.encode('utf-8'); src.write_bytes(original)
            argv = ['--text', str(src), '--out', str(out)]
            with self.assertRaises(p.PendingPronunciationError): p.main(argv)
            self.assertFalse(out.exists())
            with contextlib.redirect_stdout(io.StringIO()): p.main([*argv, '--allow-pending'])
            self.assertEqual(src.read_bytes(), original)
            self.assertEqual((out / 'display.txt').read_bytes(), original)
            self.assertEqual((out / 'spoken.txt').read_bytes(), 'E zer net\r\n麦克\r\nin leaf\r\n'.encode('utf-8'))
            report = json.loads((out / 'pronunciation-report.json').read_text())
            self.assertEqual(len(report['lexicon_sha256']), 64)
            self.assertEqual(report['lexicon_sha256'], hashlib.sha256(p.DEFAULT_LEXICON.read_bytes()).hexdigest())
            self.assertEqual(report['lexicon_version'], '1.1.0')
            self.assertEqual(report['pending_terms'], ['Ethernet', 'In-LIF', 'MAC'])
            self.assertFalse(report['audio_generated'])
            with self.assertRaisesRegex(ValueError, 'already exists'): p.main([*argv, '--allow-pending'])

    def test_cli_can_pin_v1_0_0(self):
        previous_path = p.DEFAULT_LEXICON.with_name('technical-zh-CN.v1.0.0.json')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); src = root / 'canonical.txt'; out = root / 'out'
            src.write_text('Ethernet MAC', encoding='utf-8')
            with contextlib.redirect_stdout(io.StringIO()):
                p.main(['--text', str(src), '--out', str(out), '--lexicon', str(previous_path), '--allow-pending'])
            self.assertEqual((out / 'spoken.txt').read_text(encoding='utf-8'), 'Ethernet 麦克')
            report = json.loads((out / 'pronunciation-report.json').read_text(encoding='utf-8'))
            self.assertEqual(report['lexicon_version'], '1.0.0')
            self.assertEqual(report['lexicon_sha256'], hashlib.sha256(previous_path.read_bytes()).hexdigest())
            self.assertEqual(report['pending_terms'], ['MAC'])

    def test_input_lexicon_is_not_mutated(self):
        before = copy.deepcopy(self.lexicon)
        self.prepare('MAC VLAN')
        self.assertEqual(self.lexicon, before)


if __name__ == '__main__':
    unittest.main()
