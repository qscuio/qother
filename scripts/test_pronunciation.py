#!/usr/bin/env python3
"""Offline pronunciation tests. No provider calls or audio generation."""
import contextlib
import copy
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
            original = 'MAC\r\nIn-LIF\r\n'.encode('utf-8'); src.write_bytes(original)
            argv = ['--text', str(src), '--out', str(out)]
            with self.assertRaises(p.PendingPronunciationError): p.main(argv)
            self.assertFalse(out.exists())
            with contextlib.redirect_stdout(io.StringIO()): p.main([*argv, '--allow-pending'])
            self.assertEqual(src.read_bytes(), original)
            self.assertEqual((out / 'display.txt').read_bytes(), original)
            self.assertEqual((out / 'spoken.txt').read_bytes(), '麦克\r\nin leaf\r\n'.encode('utf-8'))
            report = json.loads((out / 'pronunciation-report.json').read_text())
            self.assertEqual(len(report['lexicon_sha256']), 64)
            self.assertFalse(report['audio_generated'])
            with self.assertRaisesRegex(ValueError, 'already exists'): p.main([*argv, '--allow-pending'])

    def test_input_lexicon_is_not_mutated(self):
        before = copy.deepcopy(self.lexicon)
        self.prepare('MAC VLAN')
        self.assertEqual(self.lexicon, before)


if __name__ == '__main__':
    unittest.main()
