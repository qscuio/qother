# Narration and timing

## Choose and accept the voice before a long render

Reuse approved supplied narration when available. Preserve its words and master PCM unless the user requests a change. Otherwise select an authorized provider/model/voice that supports the language and pronunciation, and obtain a brief representative audition before expensive full synthesis. For long-form narration, the user's acceptance of that actual voice is a production gate; record it using [production-contract.md](production-contract.md). Do not assume that a locally installed voice is acceptable. A previously rejected voice must not become the default or a silent fallback. There is no preferred Kokoro route or fixed male/Chinese preset in this skill.

Do not clone a person, create keys, install models, or transmit private source text to a new service without the relevant authorization. If no acceptable route is available, stop the dependent audio work and report the choice needed. Do not replace a rejected voice with another unreviewed full-length synthesis. A canceled video request stays canceled; improving this skill does not authorize another sample, TTS call, or render.

For an authorized cloned narrator, read [qwen-voice-clone.md](qwen-voice-clone.md): existing local Qwen3 0.6B Base, matched reference transcript, input/configuration hashes, private output manifest and short audition. Keep the actual accepted project configuration; no personal recording, voice identity or acceptance is bundled with the skill. Default to dry mono with no artificial space effects, and investigate spacious sound even when the file is mono.

## One continuous narration master

1. Establish a coherent final spoken script before visual segmentation, using any script-review checkpoint the user requested. Prefer one continuous synthesis where the chosen service supports the duration. If a real service limit forces paragraph-level synthesis, disclose that limitation, assemble and listen to a coherent master first, and record joins/edits. Never secretly synthesize one audio chunk per drawing beat.
2. Record the master file, SHA-256, actual duration/sample rate, exact UTF-8 script and its hash, provider/model/voice when known, and any authorized edits. A change to the voice, words, pace or master bytes invalidates timing/review evidence.
3. Measure final duration with FFprobe or PCM sample counts. Obtain clause/word timings from trustworthy provider timestamps, real audio-text forced alignment, or listening and measuring the actual audio. This skill validates supplied timing records; it does not implement an aligner or infer phoneme boundaries.
4. Use ordered beat IDs/text/timings and make the drawings fit them. Character/word-count interpolation is preview-only and must never be labeled forced alignment or measured synchronization. Let an idea span more than one drawing; a caption boundary is not a page cut.
5. Keep the approved narration master authoritative through visual scene changes. Render visual segments on its timeline and mux the continuous master once at final assembly. Do not trim speech, add a silence between every scene, or silently stretch/resynthesize passages to fit drawings. Simplify or retime the drawings instead.

For the single-canvas renderer, --audio is muxed once across the complete drawing timeline. Multi-scene assembly is not automated by this starter. If an editor requires temporary audio slices for previews, cut on measured sample boundaries, keep the untouched master, and use it for the final mux; a sequence of independently AAC-encoded slices is not evidence of continuous original PCM.

## Caption record

```json
{
  "caption_timing": "manual_measured",
  "captions": [
    {"start": 0.2, "end": 2.8, "text": "这个小包先到入口。"},
    {"start": 2.9, "end": 5.4, "text": "再根据标记选择方向。"}
  ]
}
```

These are schema examples, not measured timings for any bundled audio. Valid final methods are manual_measured, provider_timestamps, forced_alignment; use preview_only for layout experiments. The renderer checks ordered nonoverlapping bounds, not whether a declared method was actually performed. Keep one visible caption owner: this renderer burns them in, so do not add a duplicate subtitle track in final assembly. An explicitly requested editable subtitle sidecar is fine.

## Review and export

Listen to the selected voice and actual final audiovisual output when playback is available. Check pronunciation of names/abbreviations, audible clipping, awkward pauses, boundary accuracy, the final syllable and whether each drawing illustrates what is spoken. Loudness, correlations, hashes and successful decode cannot establish pleasant speech or correct pronunciation. Record listening as not performed if unavailable.

AAC export changes encoded audio bytes. Preserve and fingerprint the source master; do not claim byte-identical MP4 audio. The renderer checks stream durations against the master with one-frame plus 30 ms encoder tolerance and fully decodes the encoded output. That technical check does not replace listening or establish that every phoneme is present.
