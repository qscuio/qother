# Authorized local Qwen narration

## Route and review state

Use the local Qwen3-TTS-12Hz-0.6B-Base route when a cloned voice is requested, the reference speaker and use are authorized, and the actual audition fits the project. Prefer an already accepted project configuration over a rejected preset. A positive audition is evidence for that sample/configuration, not blanket permission to clone other speakers, resume canceled work, produce a long video, or publish voice data. A request to improve this skill alone authorizes no new synthesis or rendering.

Keep authorization and listening acceptance separate. Record the permission reference privately before synthesis; record the user's actual voice decision afterward. Never fill in acceptance just because technical QA passes. Preserve specific criticism, including spacious/echo-like sound, as an unresolved quality issue when applicable. Do not silently revert to Kokoro or another preset if Qwen fails.

## Prepare a clean reference

1. Use a short, single-speaker recording of the authorized speaker, ideally roughly 10–15 seconds of ordinary speech in a quiet, non-reverberant room. This is a useful starting point, not a quality guarantee. Avoid music, overlapping voices, hard clipping and baked-in effects.
2. Inspect source channels before mixing. Compare left/right audio, correlation, polarity, delay and audible room sound when available. Correlation alone cannot prove an acoustic cause. Select the cleaner channel if justified; averaging delayed or phase-shifted microphones can color the voice. Keep the source unchanged.
3. Prepare a reviewed mono 24 kHz PCM16 WAV. Record source hash, selected interval, channel choice, resampling and any conservative gain in a private preparation record. Do not apply automatic dereverberation, EQ, denoising, compression or widening as an assumed improvement. Document and compare any authorized processing experiment.
4. Supply an exact transcript of that selected interval. ASR can draft it, but check wording and omitted syllables. Incorrect reference text can affect synthesis. The script uses reference audio plus text (ICL), with x_vector_only_mode=False; it never assumes a previous user's reference or transcript.

Reference recordings, reference transcripts, generated voice prompts/embeddings, identity, source hashes, local personal paths, project manifests and generated speech are private task artifacts. Keep them out of public skill repositories. Publish only generic code, instructions and synthetic test fixtures. The adapter does not save a reusable voice prompt; if caching one is later authorized, protect it like the source recording.

## Existing local runtime

The exercised route uses qwen-tts 0.1.1, CPU float32, SDPA, non-streaming generation and the 0.6B Base safetensors model including its speech_tokenizer directory. It needs no FlashAttention or API credential. A verified snapshot is 5d83992436eae1d760afd27aff78a71d676296fc; verify any different snapshot/API before use.

A working environment used Python 3.12, torch/torchaudio 2.8.0 CPU, transformers 4.57.3 and accelerate 1.12.0. Treat these as a tested combination, not a promise that every machine or newer package works. Inspect dependencies first; model/runtime installation is a separate authorized step. The adapter only reads existing local files, forces offline loading, rejects remote custom code, and writes to a new task output directory. It hashes model/config/tokenizer bytes and records installed dependency versions. Model-file hashing and CPU synthesis can take time; report measured load/generation time and real-time factor without promising another machine's speed.

Official implementation and model documentation:
- https://github.com/QwenLM/Qwen3-TTS
- https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base

## Generate a representative audition

Resolve variables to existing task-local files. Store private outputs outside the public checkout. The authorization flag acknowledges permission already recorded by the user; it does not grant permission.

```bash
python "$SKILL_DIR/scripts/qwen_narration.py" \
  --model "$LOCAL_QWEN_BASE_MODEL" \
  --model-revision 5d83992436eae1d760afd27aff78a71d676296fc \
  --reference "$PRIVATE_REFERENCE_WAV" \
  --reference-text "$PRIVATE_REFERENCE_TRANSCRIPT" \
  --text "$SPOKEN_SCRIPT" --language Chinese \
  --reference-authorized --authorization-evidence "$PERMISSION_REFERENCE" \
  --max-new-tokens 650 --out "$NEW_PRIVATE_OUTPUT_DIR" --check-only
```

Remove --check-only only when synthesis is authorized. Start with a representative short passage containing a technical term, abbreviation, number and normal pauses. The 650-token default is an audition budget, not a duration/completeness guarantee. The adapter intentionally exposes no effects, speaker widening or automatic gain. It outputs one mono PCM16 master, exact input narration text and audio-manifest.json; no MP3 is required for the renderer.

The manifest binds provider/model/reference/settings, model-file hashes, exact script hash, rate/sample count, output hash and runtime. Its configuration_sha256 uses the same canonical provider/model/id/settings fingerprint as whiteboard production_preflight.py. Copy that voice configuration into the project without dropping settings. Acceptance remains pending, and listening, coverage, likeness, dryness and beat timing remain not_performed until genuinely reviewed. Store an accepted sample's path/hash and user decision separately. Changing reference, transcript, model, processing or settings invalidates the old configuration evidence.

## Make the master authoritative

Reuse an accepted master when possible. Prefer one coherent synthesis per master while within verified model limits. Do not synthesize one chunk per drawing beat. For a genuinely long script that exceeds practical model limits, agree on paragraph-level production, log every join and listen to the assembled continuous master before timing. Check final words for token-budget truncation, dropped/repeated phrases and abbreviation pronunciation. ASR coverage is a diagnostic, not proof of correct pronunciation or voice similarity.

Keep the final reviewed PCM master unchanged through visual edits. Obtain real measured beat boundaries by listening, trustworthy provider timestamps or actual forced alignment; never label text-length interpolation or generic ASR segments as forced alignment. Bind timing to master and script hashes and rebuild it after any audio change. For diagrams, use diagram.py assemble --master narration.wav --timing timing.json to preserve the master. For whiteboard, populate the existing production contract and mux the master once.

## Dry mono and the “stereo/space” complaint

Default to a centered mono dry narration track: no artificial reverb, chorus, stereo widening, delay, doubled voices, speed or pitch effects. Mono describes channel count; it does not prove dryness. One channel can contain room reflections, comb filtering, multiple microphones mixed together, or model artifacts.

Check the actual reference → raw synthesis → gain/encode → delivered file chain with FFprobe and decoded audio. Separate measured facts (channels, rate, clipping, hashes, processing steps) from possible causes. Compare level-matched short excerpts and change one variable at a time. First consider a cleaner/closer reference or a justified single source channel; preserve the original comparison. Do not promise that downmixing or a fixed EQ removes the problem. Ask about playback spatial-audio enhancement only when it is relevant; do not assert it is enabled without evidence.

Qwen's x_vector_only_mode=True is a separate experiment: it omits the reference acoustic/text context used by ICL and may change similarity and prosody. It is not an established dereverberation fix or the accepted default. If explicitly tested, use a separate manifest/configuration, hold the script/reference/seed constant where possible, and obtain listening feedback before adopting it. Do not silently switch this adapter's mode.

Technical decode, sample counts and loudness cannot certify naturalness or absence of audible space. Mark listening unavailable if it was not performed. Before final delivery check the actual encoded file, last syllable, full spoken coverage, no added effects and permitted destination. Preserve source/master hashes even though lossy encoding changes delivered bytes.
