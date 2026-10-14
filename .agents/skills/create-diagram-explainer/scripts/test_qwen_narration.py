#!/usr/bin/env python3
"""Offline regression tests with ephemeral PCM fixtures and a mocked model; no TTS."""
from array import array
import contextlib
import io
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
import wave
import qwen_narration as q


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.model = self.root / 'model'
        (self.model / 'speech_tokenizer').mkdir(parents=True)
        (self.model / 'config.json').write_text(json.dumps({'tts_model_type': 'base', 'tts_model_size': '0b6'}))
        (self.model / 'speech_tokenizer/config.json').write_text('{}')
        (self.model / 'model.safetensors').write_bytes(b'inert model fixture, never loaded')
        self.ref = self.root / 'reference.wav'
        self.wav(self.ref)
        (self.root / 'reference.txt').write_text('Reference fixture.', encoding='utf-8')
        (self.root / 'script.txt').write_text('Narration fixture.\n', encoding='utf-8')
        self.args = q.parser().parse_args(['--model', str(self.model), '--model-revision', 'test-revision',
            '--reference', str(self.ref), '--reference-text', str(self.root / 'reference.txt'),
            '--text', str(self.root / 'script.txt'), '--language', 'English', '--reference-authorized',
            '--authorization-evidence', 'test permission fixture', '--out', str(self.root / 'output')])

    def tearDown(self):
        self.temp.cleanup()

    def wav(self, path, channels=1, rate=24000, sample=1000):
        a = array('h', [sample, -sample] * 120)
        if sys.byteorder != 'little':
            a.byteswap()
        with wave.open(str(path), 'wb') as f:
            f.setnchannels(channels); f.setsampwidth(2); f.setframerate(rate); f.writeframes(a.tobytes())

    def test_permission_required_before_output(self):
        for key, value in [('reference_authorized', False), ('authorization_evidence', ' ')]:
            with self.subTest(key=key):
                old = getattr(self.args, key); setattr(self.args, key, value)
                with self.assertRaisesRegex(ValueError, 'authorization'):
                    q.prepare(self.args)
                setattr(self.args, key, old)
                self.assertFalse(self.args.out.exists())

    def test_invalid_reference_channels_rate_silence_clipping(self):
        for params in ({'channels': 2}, {'rate': 48000}, {'sample': 0}, {'sample': 32767}):
            with self.subTest(params=params):
                self.wav(self.ref, **params)
                with self.assertRaises(ValueError):
                    q.read_reference(self.ref)

    def test_missing_wrong_or_changed_model(self):
        original = q.model_identity(self.model)
        (self.model / 'model.safetensors').write_bytes(b'different inert fixture')
        self.assertNotEqual(original, q.model_identity(self.model))
        (self.model / 'config.json').write_text('{"tts_model_type":"custom_voice"}')
        with self.assertRaises(ValueError):
            q.model_identity(self.model)

    def test_configuration_and_script_bindings(self):
        _, _, text, first, _ = q.prepare(self.args)
        self.assertEqual(text, 'Narration fixture.\n')
        self.assertEqual(first['configuration_sha256'], q.fingerprint(first['voice']))
        for key in ('reference_sha256', 'reference_text_sha256', 'model_files_sha256'):
            self.assertEqual(len(first['voice']['settings'][key]), 64)
        for path in (self.ref, self.model, self.root / 'reference.txt'):
            self.assertNotIn(str(path), json.dumps(first))
        (self.root / 'script.txt').write_text('Different narration.')
        second = q.prepare(self.args)[3]
        self.assertEqual(first['configuration_sha256'], second['configuration_sha256'])
        self.assertNotEqual(first['script_sha256'], second['script_sha256'])
        (self.root / 'reference.txt').write_text('Changed reference transcript.')
        self.assertNotEqual(first['configuration_sha256'], q.prepare(self.args)[3]['configuration_sha256'])
        self.args.seed += 1
        self.assertNotEqual(second['configuration_sha256'], q.prepare(self.args)[3]['configuration_sha256'])

    def test_check_only_does_not_import_or_generate(self):
        self.args.check_only = True
        with contextlib.redirect_stdout(io.StringIO()) as output, patch.dict(sys.modules, {'qwen_tts': None}):
            q.run(self.args)
        self.assertEqual(json.loads(output.getvalue())['synthesis'], 'not_performed')
        self.assertFalse(self.args.out.exists())

    def test_existing_output_or_invalid_parameters_fail(self):
        for key, value in [('seed', -1), ('threads', 0), ('max_new_tokens', 0), ('language', ''), ('model_revision', ' ')]:
            old = getattr(self.args, key); setattr(self.args, key, value)
            with self.assertRaises(ValueError): q.prepare(self.args)
            setattr(self.args, key, old)
        self.args.out.mkdir()
        with self.assertRaisesRegex(ValueError, 'already exists'): q.prepare(self.args)

    def test_reject_invalid_output_before_write(self):
        for values in ([], [0.0] * 10, [float('nan')], [float('inf')], [1.0], [-1.2], [0.999999], [0.000012]):
            path = self.root / 'bad.wav'
            with self.assertRaises(ValueError): q.write_pcm(path, values, 24000)
            self.assertFalse(path.exists())

    @unittest.skipUnless(importlib.util.find_spec('numpy') is not None, 'Optional Qwen runtime NumPy is not installed')
    def test_pcm_and_honest_pending_manifest_with_mocked_runtime(self):
        import numpy as np
        model = MagicMock()
        original_script = (self.root / 'script.txt').read_bytes()
        def generate(**kwargs):
            (self.root / 'script.txt').write_text('Changed during synthesis.')
            return [np.array([0.1, -0.1] * 120, dtype=np.float32)], 24000
        model.generate_voice_clone.side_effect = generate
        factory = MagicMock(return_value=model)
        fake_qwen = SimpleNamespace(Qwen3TTSModel=SimpleNamespace(from_pretrained=factory))
        fake_torch = MagicMock()
        fake_torch.float32 = 'test-float32'
        with patch.object(q.metadata, 'version', return_value='0.1.1'), \
             patch.dict(sys.modules, {'qwen_tts': fake_qwen, 'torch': fake_torch}), \
             patch.dict(q.os.environ, {}, clear=False), contextlib.redirect_stdout(io.StringIO()):
            q.run(self.args)
        manifest = json.loads((self.args.out / 'audio-manifest.json').read_text())
        self.assertEqual(manifest['audio']['channels'], 1)
        self.assertEqual(manifest['audio']['sample_count'], 240)
        self.assertEqual(manifest['acceptance']['status'], 'pending')
        self.assertTrue(all(v == 'not_performed' for v in manifest['review'].values()))
        self.assertEqual(manifest['timing']['beats'], [])
        self.assertEqual((self.args.out / 'narration.txt').read_bytes(), original_script)
        self.assertEqual(manifest['script_sha256'], q.digest(self.args.out / 'narration.txt'))
        self.assertFalse((self.args.out / 'reference.wav').exists())
        self.assertFalse((self.args.out / 'reference.txt').exists())
        self.assertEqual(manifest['audio']['sha256'], q.digest(self.args.out / 'narration.wav'))
        loader = factory.call_args.kwargs
        self.assertTrue(loader['local_files_only']); self.assertFalse(loader['trust_remote_code'])
        self.assertTrue(loader['use_safetensors']); self.assertEqual(loader['attn_implementation'], 'sdpa')
        generation = model.generate_voice_clone.call_args.kwargs
        self.assertFalse(generation['x_vector_only_mode']); self.assertTrue(generation['non_streaming_mode'])
        self.assertEqual(generation['ref_audio'][1], 24000)
        self.assertEqual(generation['text'], 'Narration fixture.\n')
        self.assertEqual(manifest['voice']['settings']['postprocessing'], {'gain_db': 0, 'effects': [], 'channels': 1})


if __name__ == '__main__':
    unittest.main()
