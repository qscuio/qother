# Narration routes

Use the user's chosen provider or an appropriate already-authorized route. The visual pipeline does not require a particular TTS vendor, an API key, or a voice gender. Human recordings and other synthetic voices can supply the same clause WAV contract.

Produce one file per exact caption clause. Use `spoken_text` for pronunciation expansions while retaining `text` for displayed wording. Normalize all files to the same mono 16-bit PCM sample rate before assembly. Do not time-stretch speech just to match an early storyboard estimate; revise pacing and visual timing instead.

`diagram.py assemble` measures the WAV sample counts, rejects silent/non-PCM inputs, and concatenates them with short lead/tail pauses. For an existing narration master with measured clause timing, use `--master` and `--timing` as documented in the project contract to preserve the original bytes, pauses, and boundaries instead. Caption boundaries are measured clause boundaries. Event fractions inside clauses are explicitly recorded as estimated interpolation, not measured word timestamps. For stricter sync, create shorter meaningful clauses or adapt the contract to externally verified word alignment and keep that method accurately labeled.

## Optional existing local Kokoro setup

`scripts/kokoro_clauses.py` is an adapter for an already installed sherpa-onnx runtime and the multilingual v1.1 Kokoro ONNX layout. It requires explicit `--model` and `--speaker-id`; it has no baked-in male default, network, installer, download, or credential behavior.

```bash
python "$SKILL_DIR/scripts/kokoro_clauses.py" project.json \
  --model /path/to/existing/model-directory --speaker-id SELECTED_ID \
  --out audio --speed 1.0
```

It writes an audio-ready project with relative clause WAV paths. Pass `audio/project.json` to `diagram.py assemble`. Confirm the selected ID's documented language and voice character for the exact model; IDs do not generalize to other models. This adapter expects `model.int8.onnx`, `voices.bin`, `tokens.txt`, `lexicon-us-en.txt`, `lexicon-zh.txt`, and `espeak-ng-data`.

Useful official references to verify when this route is selected:
- https://k2-fsa.github.io/sherpa/onnx/tts/all/Chinese-English/kokoro-multi-lang-v1_1.html
- https://github.com/k2-fsa/sherpa-onnx
- https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh

Test a short sample and listen before batch generation. Label synthetic narration accurately; do not call a preset voice a recording by a real person. If dependency or model setup is missing, inspect available alternatives, then ask only for the setup/action that actually needs permission. Do not invent keys, silently download models, or add repeated approval gates for already-authorized ordinary rendering.
