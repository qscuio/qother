# Provider boundary and acceptance

## What is implemented

The local adapter validates a structured storyboard and emits standalone text prompts in a JSON package. It makes no network requests, reads no credentials, downloads no models, renders no imagery and spends no credits. No provider/model is certified by this integration. Upstream model names, quality/retention promises, prices and promotional-account advice are not adopted.

## Mapping to a real provider

Before making calls, verify the selected provider's current official interface, supported input/reference types, clip durations, ratio/resolution/fps options, audio behavior, cost and rights. Honor the user's existing provider choice. Obtain required authority for new costs, uploads or account actions. Do not silently choose a paid backend or create credentials.

Map each clip's prompt and requested duration/ratio into that provider's actual interface. Retain the package digest, clip ID, actual model/version/settings, input reference hashes, job ID and output file hash in the task workspace. Mark requested values separately from measured output. If clip length is fixed, plan padding/trimming or repartition at natural speech/action boundaries and re-review the changed storyboard; never stretch narration blindly.

The compiler is a seam for a later SDK/UI adapter, not an implemented external-video API. A future adapter must expose explicit submit/status/download operations, bounded retries, idempotency/job tracking and authentic error states. Keep credentials external. Do not count a URL, job acceptance or prompt package as delivered video.

## Media review gates

- Structure: valid durations, complete beats, cast references, version authority and state joins. Automated checks cannot inspect visual meaning.
- Visual: decode actual footage; inspect first/middle/final frames, reaching/release/turn/walk peaks, and both sides of every cut. Check limbs, head proportions, clothing, line/palette stability, duplicate objects, prop transfers, occlusion, layout and unintended text. Record frame/time evidence and fix failed clips locally.
- Temporal: watch continuously at full speed for flicker, jitter, foot sliding, unexplained state changes, dead time and camera discontinuity. Sparse snapshots cannot certify every frame.
- Audio: listen through the actual track for exact wording, missing/repeated phrases, narrator drift, technical pronunciation, clipped endings, timing and music/SFX balance. Text matching alone cannot prove speech quality.
- Final edit: assemble in approved order, align captions to measured voice, verify joins and full decoding, then play the complete exported file with sound. Report measured duration/format, evidence and remaining failures. If playback is unavailable, say which checks are not run.

A passing mechanical validator is only `prompt-contract-pass`. Use `not-run`, `fail` or `pass-with-evidence` for actual footage/audio checks. A preview with known defects is allowed only when clearly labeled and within scope; it is not final acceptance.
