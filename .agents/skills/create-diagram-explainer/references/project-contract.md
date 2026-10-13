# Project and timing contract

The editable project is UTF-8 JSON. Copy `assets/queue-example.json` to the task workspace and edit the data, not topic-specific renderer code. Coordinates use the selected canvas pixels. Default font discovery supports common Noto CJK/DejaVu installations; pass `font` for a known local font. Verify its glyph coverage visually.

## Project

- `title`, `example_notice`: short title and optional visible teaching-simplification notice.
- `width`, `height`, `fps`: defaults 1280, 720, 24. The layout scales from 720p. Frame sizes must be positive even integers.
- `font`: optional font file, relative to the project or an explicit local path.
- `colors`: optional `paper`, `ink`, `accent`, `control`, `muted` hex colors.
- `audio_kind`: `narration` for real speech. A preview uses `preview` and cannot render as a final.
- `audio_provenance`: provider/recording source, voice, and synthetic/human indication; metadata is recorded, not verified by the renderer.
- `scenes`: ordered scenes; each has unique `id`, `title`, `narration`, `clauses`, `elements`, `events`.

## Clauses and exact coverage

Each clause has unique `id`, `text`, optional `spoken_text`, `wav` (path relative to project), and `focus` (nonempty existing element IDs). `narration` must equal `''.join(clause.text)` exactly. The scene's initial state must have visible focus for its first clause, or a reveal must occur by that clause's beginning. A `preview_seconds` estimate is allowed only for silent preview assembly.

Every spoken clause is retained as a caption. WAVs must be mono signed 16-bit PCM, nonempty/non-silent, with one common sample rate. Never use test tones or unrelated audio labeled as narration.

## Elements

All elements have a unique `id`, `kind`, optional `visible` (default false), and short `label`.

- `node`: `box: [x,y,width,height]`, optional `state` string.
- `queue`: node fields plus integer `capacity`, initial integer `count`, optional `state`. Count includes the focal item if present.
- `token`: `position: [x,y]`, optional `inside_queue` naming its containing queue. Exactly one model/drawing exists per ID; move events update that position.
- `edge`: `from`, `to` node/queue IDs; `flow` is `data`, `control`, or `relation`; `points: [[x,y], ...]` is an explicit directional path from the source boundary to the target boundary. `label` appears near its midpoint. Validation checks endpoints are close to their named nodes and that the path has positive length. Keep paths clear of text.

## Events and causality

Each event has `id`, `kind`, `target`, `at: {clause: ID, fraction: 0..1}`, optional `duration` in seconds (default 0.5) or `until` with the same anchor structure, and a concise `meaning`. Prefer `until` when matching a move completion to a queue update: both can share the exact same clause fraction across changing audio durations. Fractions use estimated linear interpolation inside measured audio. They are not forced alignment. Events execute in chronological order; same-time order follows list order.

- `reveal`, `hide`: progressively reveal or remove the target.
- `state`: set target `value` to a short status string, effective at event start.
- `queue`: set target queue `count`, effective at event start.
- `move`: token only; requires `edge`, optional `requires: [{target: ID, state: STRING}]`. The edge must be a visible `data` edge. The token must start at that edge's source point. All declared conditions must be true before movement begins. `inside_queue` is cleared at movement start; optional `arrive_queue` is set at completion and must match the edge destination.

Every move is forward along its directed edge. Use a separately declared reverse edge for reverse motion. Concurrent moves for the same token and overlapping reveals/moves of that token fail validation. At each event boundary, tokens inside queues must fit within the queue count; queue cells exclude those visible focal tokens so no duplicate is drawn.

A move out of a queue does not silently alter occupancy: author the matching `queue` event at the correct instant. The same applies to arrival. Synchronize the count update and the move boundary deliberately. The validator checks a consistent count, but cannot infer unrelated real arrivals/departures.

## Preserve an existing measured narration master

Use this mode when audio and exact clause timing already exist; it does not add/remove padding, alter speech, or reassemble the PCM:

```bash
python "$SKILL_DIR/scripts/diagram.py" assemble project.json --out build \
  --master audio/narration_master.wav --timing audio/timing.json
```

The supplied timing JSON requires `sample_rate`, `sample_count`, `duration`, and ordered `scenes`. Each scene requires absolute `start`, `duration`, optional absolute `end`, and `captions` (or `clauses`) with `text` and scene-relative `start`/`end`; optional `sample_count` is checked. Scenes and clauses match the project by order and exact text, so source scene IDs can differ. A supplied scene `narration`, when present, must match exactly. All times must be exact PCM sample boundaries; scenes must span the complete master without overlap/gaps, while pauses inside a scene, between clauses, and at either end are retained.

The master must use the same mono 16-bit PCM format. Clause `wav` paths are optional in this mode; when present, their PCM must exactly equal the corresponding master slice. Without separate WAVs the tool verifies boundaries, text, and non-silence, but cannot establish what was spoken without listening. The master file is copied unchanged and its hash plus the supplied timing hash are recorded. `--master` and `--timing` must be supplied together and cannot be combined with `--preview`. The regular clause-assembly route retains its 0.15 s lead/0.30 s tail defaults.

## Generated outputs and limitations

Assembly emits `timeline.json`, `narration.wav`, and `captions.srt`. Timelines store the input data, script hash, real audio sample count and sample rate, scene/caption boundaries, and resolved event times. The renderer uses only that timeline and its narration file; keep them together or update the relative path explicitly.

The engine covers compact diagrams, not arbitrary SVG artwork, morphs, a writing hand, live speech alignment, or complex camera choreography. Multiple scenes are supported; repeat relevant objects with deliberate identity continuity. Layout, scientific claims, and speech content require human/agent review beyond deterministic validation.
