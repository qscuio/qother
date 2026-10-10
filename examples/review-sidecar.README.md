# Structural review sidecar v1

This original, standalone contract is additive. It neither changes storyboard v1
nor changes or invokes a renderer. It uses only Python's standard library and
never opens referenced media, accesses the network, or executes upstream code.

## Run

From the repository root:

```sh
python scripts/validate_review_sidecar.py examples/review-sidecar.valid.json
python -m unittest discover -s scripts -p 'test_review_sidecar.py' -v
```

The CLI returns 0 for structurally valid documents and 1 for invalid documents,
with the first error on stderr. API: import `validate`, `load`, and
`ValidationError` from `validate_review_sidecar`; `validate(document)` returns
None on success. `load(path)` also rejects duplicate JSON keys and nonstandard
NaN/Infinity tokens. Structural errors identify a JSON path; parse errors are
reported by the JSON decoder. Duplicate-key errors identify the document and key.

## Contract

See `review-sidecar.valid.json` for a complete example. All object keys are strict;
unknown keys are errors. All IDs are nonempty strings and globally unique.

- `schema`: exactly `review-sidecar/v1`.
- `timeline`: `fps: {num, den}` and positive integer `duration_frames`.
- `sources`: nonempty array of `{id, fps: {num, den}, duration_frames}`. Source
  duration is measured in that source's own frames, not timeline frames.
- `shots`: nonempty array of `{id, source_id, source_range, timeline_range, rate}`.
  Both ranges have integer `start` and `end` with `0 <= start < end`. Ranges are
  half-open. A source range uses source fps; a timeline range uses timeline fps.
  `rate: {num, den}` is positive source seconds per timeline second. Reverse
  playback and freeze frames are intentionally outside this minimal contract.
- Each shot must satisfy `(source_end-source_start)/source_fps =
  (timeline_end-timeline_start)/timeline_fps * rate`, exactly. No implicit
  frame rounding or tolerance is allowed. Both ranges must fit declared durations.
- A range may additionally include `start_seconds` and/or `end_seconds`. These
  finite numbers must agree with their frame index divided by the relevant fps
  within 1e-9 seconds. They are redundant cross-checks, never authoritative units.
- Optional `policy`: boolean `allow_gaps` and/or `allow_overlaps`, default false.
  These apply only to shots, including leading/trailing timeline gaps. Permission
  does not certify transition semantics. Overlapping shots are only declared
  overlaps; there is no compositing or dissolve model.
- Optional `cues`: array of `{id, role, shot_id, source_range, timeline_range}`.
  Roles: `caption`, `narration`, `music`, `sfx`. Each cue is contained in its
  referenced shot and must use that shot's exact endpoint mapping. Optional
  nonempty `text` is descriptive. Captions require nonempty
  `coverage_source_ranges`, an array of source-frame ranges whose union covers
  the cue's declared source range with no holes or out-of-range claims. The same
  optional coverage field may be provided on other cue roles. Overlapping
  coverage evidence is allowed. Cues may overlap and intentional silence or
  uncaptained time is allowed; full timeline caption or speech coverage is NOT
  required. Cues spanning cuts must be split across referenced shots.
- Optional `audio_groups`: array of `{id, role, cue_ids}`. Role must be narration,
  music, or sfx. Each group has at least one cue reference, each cue's role must
  match, and a cue may belong to only one group. Groups are organizational;
  independent audio edit tracks, gain, fades and ducking are not modeled.

Positive rational numerators/denominators must be integers (unreduced fractions
are accepted). Booleans, floating-point frames and nonfinite numbers are rejected.

## Evidence boundary

Passing proves consistency of declarations only. It does not prove the source
exists, reported duration matches a file, a caption matches audible words, all
speech is captioned, a rendered video uses these edits, perceptual synchronization,
subtitle readability, loudness, clipping, silence, mixing, or ducking quality.
Those require actual media inspection or measurement with independently recorded
evidence. Do not present this structural pass as audiovisual acceptance.

The invalid JSON fixtures are intentionally structurally invalid examples. The
nonfinite fixture uses JSON-legal `1e999`, which overflows Python's float parser;
unit tests additionally cover literal NaN/Infinity and in-memory nonfinite values.
