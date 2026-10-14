#!/usr/bin/env python3
"""Local Qwen3 Base voice-clone adapter. No downloads, effects, or saved voice prompts."""
from __future__ import annotations
import argparse
from array import array
import hashlib
import io
from importlib import metadata
import json
import math
import os
from pathlib import Path
import sys
import time
import wave

MODEL_ID = 'Qwen/Qwen3-TTS-12Hz-0.6B-Base'
SAMPLING = dict(do_sample=True, temperature=0.9, top_p=1.0, top_k=50,
                repetition_penalty=1.05, subtalker_dosample=True,
                subtalker_temperature=0.9, subtalker_top_p=1.0, subtalker_top_k=50)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                         separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


def read_reference(path):
    return read_reference_bytes(Path(path).read_bytes())


def read_reference_bytes(raw_file):
    with wave.open(io.BytesIO(raw_file), 'rb') as f:
        if (f.getnchannels(), f.getsampwidth(), f.getframerate(), f.getcomptype()) != (1, 2, 24000, 'NONE'):
            raise ValueError('Reference must already be reviewed mono 24 kHz PCM16 WAV; do not silently downmix')
        count = f.getnframes()
        raw = f.readframes(count)
    if len(raw) != count * 2 or not count:
        raise ValueError('Empty or truncated reference WAV')
    values = array('h', raw)
    if sys.byteorder != 'little':
        values.byteswap()
    if max(abs(v) for v in values) < 32:
        raise ValueError('Reference is silent or too quiet; inspect it before synthesis')
    if any(v <= -32768 or v >= 32767 for v in values):
        raise ValueError('Reference contains full-scale samples; inspect clipping before synthesis')
    return values, count / 24000


def model_identity(directory):
    config = json.loads((directory / 'config.json').read_text(encoding='utf-8'))
    if config.get('tts_model_type') != 'base' or config.get('tts_model_size') != '0b6':
        raise ValueError('This tested adapter requires Qwen3-TTS 0.6B Base')
    if not (directory / 'speech_tokenizer' / 'config.json').is_file():
        raise ValueError('Local model is missing its speech_tokenizer')
    # Bind model/config/tokenizer bytes, without personal absolute paths or caches.
    suffixes = {'.json', '.safetensors', '.txt', '.model', '.tiktoken'}
    paths = sorted(p for p in directory.rglob('*') if p.is_file() and p.suffix in suffixes
                   and not any(part.startswith('.') for part in p.relative_to(directory).parts))
    if not any(p.suffix == '.safetensors' for p in paths):
        raise ValueError('Local safetensors weights are missing')
    records = {str(p.relative_to(directory)): digest(p) for p in paths}
    return fingerprint(records)


def audio_stats(samples, rate):
    if not isinstance(rate, int) or rate <= 0 or len(samples) == 0:
        raise ValueError('Invalid output sample rate or empty speech')
    if not all(math.isfinite(float(v)) for v in samples):
        raise ValueError('Output contains non-finite samples')
    peak = max(abs(float(v)) for v in samples)
    if peak >= 1:
        raise ValueError('Output reaches full scale; review provider output instead of silently limiting')
    rms = math.sqrt(sum(float(v) ** 2 for v in samples) / len(samples))
    if rms < 1e-5:
        raise ValueError('Output is silent or too quiet')
    return {'sample_rate': rate, 'sample_count': len(samples), 'channels': 1,
            'duration_seconds': len(samples) / rate,
            'peak_dbfs': 20 * math.log10(max(peak, 1e-12)),
            'rms_dbfs': 20 * math.log10(max(rms, 1e-12)),
            'full_scale_sample_count': 0}


def write_pcm(path, samples, rate):
    audio_stats(samples, rate)
    pcm = array('h', (round(float(v) * 32767) for v in samples))
    if any(v <= -32768 or v >= 32767 for v in pcm):
        raise ValueError('PCM quantization reaches full scale; inspect output headroom')
    report = audio_stats([v / 32768.0 for v in pcm], rate)
    if sys.byteorder != 'little':
        pcm.byteswap()
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate); f.writeframes(pcm.tobytes())
    with wave.open(str(path), 'rb') as f:
        if f.getnchannels() != 1 or f.getnframes() != report['sample_count']:
            raise ValueError('Written WAV failed mono/sample-count verification')
    report['sha256'] = digest(path)
    return report


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model', type=Path, required=True, help='Existing local model directory')
    p.add_argument('--model-revision', required=True, help='Verified model snapshot revision')
    p.add_argument('--reference', type=Path, required=True)
    p.add_argument('--reference-text', type=Path, required=True, help='Exact UTF-8 transcript of the selected reference')
    p.add_argument('--text', type=Path, required=True, help='Exact final spoken UTF-8 script')
    p.add_argument('--language', required=True)
    p.add_argument('--reference-authorized', action='store_true', help='Acknowledge actual recorded permission; this flag does not grant it')
    p.add_argument('--authorization-evidence', required=True, help='Private task-local user permission reference, not the transcript')
    p.add_argument('--seed', type=int, default=0)
    p.add_argument('--threads', type=int, default=4)
    p.add_argument('--max-new-tokens', type=int, default=650, help='Short-audition budget; not a duration guarantee')
    p.add_argument('--out', type=Path, required=True, help='New private output directory')
    p.add_argument('--check-only', action='store_true', help='Validate local inputs without loading model or creating audio')
    return p


def prepare(args):
    if not args.reference_authorized or not args.authorization_evidence.strip():
        raise ValueError('Record actual authorization for this reference and use before cloning')
    if args.threads < 1 or args.max_new_tokens < 1 or not 0 <= args.seed < 2**32:
        raise ValueError('Invalid threads, token budget or seed')
    if not args.model_revision.strip() or not args.language.strip():
        raise ValueError('Model revision and language must be explicit')
    if args.out.exists():
        raise ValueError('Output directory already exists; preserve prior evidence and select a new directory')
    reference_bytes = args.reference.read_bytes()
    reference, duration = read_reference_bytes(reference_bytes)
    script_bytes = args.text.read_bytes()
    reference_text_bytes = args.reference_text.read_bytes()
    text = script_bytes.decode('utf-8')
    ref_text = reference_text_bytes.decode('utf-8')
    if not text.strip() or not ref_text.strip():
        raise ValueError('Both narration and reference transcript must be nonempty')
    model_hash = model_identity(args.model)
    versions = {}
    for name in ('qwen-tts', 'torch', 'torchaudio', 'transformers', 'accelerate', 'numpy', 'soundfile', 'librosa'):
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = 'not_installed'
    settings = {'model_revision': args.model_revision, 'model_files_sha256': model_hash,
                'reference_sha256': hashlib.sha256(reference_bytes).hexdigest(),
                'reference_text_sha256': hashlib.sha256(reference_text_bytes).hexdigest(),
                'adapter_sha256': digest(Path(__file__)),
                'language': args.language, 'device': 'cpu', 'dtype': 'float32', 'attention': 'sdpa',
                'x_vector_only_mode': False, 'non_streaming_mode': True,
                'max_new_tokens': args.max_new_tokens, 'sampling': SAMPLING.copy(),
                'seed': args.seed, 'threads': args.threads, 'interop_threads': 1,
                'python_version': sys.version.split()[0], 'versions': versions, 'postprocessing': {'gain_db': 0, 'effects': [], 'channels': 1}}
    voice = {'provider': 'local qwen-tts', 'model': MODEL_ID,
             'id': 'reference-' + settings['reference_sha256'], 'settings': settings}
    record = {'schema_version': 1, 'synthetic': True, 'voice': voice,
              'configuration_sha256': fingerprint(voice), 'script_sha256': hashlib.sha256(script_bytes).hexdigest(),
              'reference_duration_seconds': duration,
              'authorization_evidence': args.authorization_evidence,
              'acceptance': {'status': 'pending', 'user_evidence': None},
              'review': {'listening': 'not_performed', 'transcript_coverage': 'not_performed',
                         'voice_similarity': 'not_performed', 'dryness': 'not_performed'},
              'timing': {'method': 'not_performed', 'beats': []}}
    return reference, ref_text, text, record, script_bytes


def run(args):
    reference, ref_text, text, record, script_bytes = prepare(args)
    if args.check_only:
        print(json.dumps({'status': 'inputs_checked', 'configuration_sha256': record['configuration_sha256'],
                          'synthesis': 'not_performed'}, indent=2))
        return
    if record['voice']['settings']['versions']['qwen-tts'] != '0.1.1':
        raise ValueError('Tested runtime is qwen-tts 0.1.1; verify a changed API before adapting this script')
    args.out.mkdir(mode=0o700, parents=True, exist_ok=False)
    # Keep library caches local and forbid implicit network/model downloads.
    for key, value in {'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1',
                       'TOKENIZERS_PARALLELISM': 'false', 'OMP_NUM_THREADS': str(args.threads),
                       'MKL_NUM_THREADS': str(args.threads), 'OPENBLAS_NUM_THREADS': '1'}.items():
        os.environ[key] = value
    for key, child in {'HF_HOME': 'hf_cache', 'NUMBA_CACHE_DIR': 'numba_cache', 'MPLCONFIGDIR': 'mpl_cache'}.items():
        os.environ[key] = str((args.out / child).resolve())
    import numpy as np
    import torch
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(args.threads); torch.set_num_interop_threads(1)
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    start = time.monotonic()
    model = Qwen3TTSModel.from_pretrained(str(args.model.resolve()), device_map='cpu', dtype=torch.float32,
        attn_implementation='sdpa', local_files_only=True, trust_remote_code=False, use_safetensors=True)
    load_seconds = time.monotonic() - start
    start = time.monotonic()
    wavs, rate = model.generate_voice_clone(text=text, language=args.language,
        ref_audio=(np.asarray(reference, dtype=np.float32) / 32768.0, 24000), ref_text=ref_text,
        x_vector_only_mode=False, non_streaming_mode=True, max_new_tokens=args.max_new_tokens, **SAMPLING)
    elapsed = time.monotonic() - start
    if len(wavs) != 1 or np.asarray(wavs[0]).ndim != 1:
        raise ValueError('Expected one mono waveform; inspect unexpected output instead of downmixing')
    report = write_pcm(args.out / 'narration.wav', wavs[0], rate)
    # No content-completeness claim: a token budget may truncate the final words.
    record.update(audio={'path': 'narration.wav', **report}, runtime={'load_seconds': load_seconds,
                  'generation_seconds': elapsed, 'real_time_factor': elapsed / report['duration_seconds']})
    (args.out / 'narration.txt').write_bytes(script_bytes)
    (args.out / 'audio-manifest.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'generated_pending_review', 'duration_seconds': report['duration_seconds'],
                      'channels': 1, 'manifest': str(args.out / 'audio-manifest.json')}, indent=2))


if __name__ == '__main__':
    try:
        run(parser().parse_args())
    except (ValueError, OSError, wave.Error) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(2)
