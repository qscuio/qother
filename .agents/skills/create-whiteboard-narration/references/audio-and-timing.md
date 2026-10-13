# Narration and timing

## Make speech the timing source

1. Reuse approved supplied narration when available. Preserve its words and PCM unless the user requests a change. Record the file, duration, sample rate, provider/model/voice when known, and any edits in the project source.
2. Otherwise draft concise spoken clauses suited to the audience. Use an authorized existing speech provider or available local model. Do not assume a provider, transmit private source text to an unapproved service, create keys, install large models, or clone a person. Ask only for the permission or choice genuinely missing.
3. Measure the final audio file with FFprobe or PCM sample counts. Use its actual duration, not word-count arithmetic, as the output duration.
4. Obtain clause or word timings from trustworthy provider timestamps, real audio-text forced alignment, or listening and measuring boundaries in the audio. Record the method. Character-count interpolation is only a rough preview schedule and must never be labeled forced alignment or measured synchronization.
5. Schedule each scene around a complete idea. A long spoken sentence can share a drawing with the next one; a caption boundary does not require a page cut. Reserve time for strokes, lifts, paint, and a final reading hold. Simplify details if the available speech is too short.

## Existing local Kokoro option

The originating project used existing local Kokoro TTS with a Chinese male preset. This is an example route, not a universal requirement or a bundled dependency. Use it only when already available and appropriate, or after any required installation/download and service permissions. Verify the actual installed package/API and voice names. This skill does not bundle its weights, install commands, or an assumed machine-specific environment. Supply the rendered audio file to the video renderer after review.

For multilingual work choose a voice that supports the requested language and pronunciation. A preset voice does not imply voice cloning. If a named voice/person is requested, apply the relevant authorization and consent requirements rather than extrapolating from the old project.

## Caption record

Use a project JSON like:

```json
{
  "caption_timing": "manual_measured",
  "captions": [
    {"start": 0.2, "end": 2.8, "text": "这个小包先到入口。"},
    {"start": 2.9, "end": 5.4, "text": "再根据标记选择方向。"}
  ]
}
```

The times above are schema examples, not measured timings for a bundled audio file. Valid final methods are manual_measured, provider_timestamps, and forced_alignment. The script checks ordering and duration, but it cannot prove a declared method was used: verify against the actual waveform/playback. Use preview_only for silent layout experiments.

## Review and export

Check pronunciation of names and abbreviations, audible clipping, awkward pauses, caption boundary accuracy, and whether the drawing illustrates the idea while it is spoken. Loudness analysis and a successful decode do not establish that the speech sounds right. State explicitly if you could not listen.

Keep a master narration file and align captions to it. AAC export normally changes encoded audio bytes; do not claim byte-identical video audio. Verify video/audio durations differ by no more than one output frame, apart from known encoder padding. Any intentional silence or time-stretch belongs in the project provenance and should preserve the user's requested meaning.
