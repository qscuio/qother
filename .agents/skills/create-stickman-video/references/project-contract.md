# Storyboard contract v1

UTF-8 JSON, Python 3.10+ standard library. This is separate from qother's existing renderer schemas; neither whiteboard nor diagram renderer consumes it.

## Project

Required fields: `version: 1`, nonempty `title`, `source_summary`, `language`, `voice_lock`; `ratio` (`16:9` or `9:16`); `style` (one preset in direction.md); positive finite `duration_s`; nonempty `characters` object mapping stable IDs to complete anchor strings; nonempty `palette` list of ordinary color-name strings; nonempty `clips`; and `approval`.

Keep exact canonical narration in the source language. A single project-wide voice lock is supported. Source summary states what is known and what is a fictional analogy; detailed fact citations may be kept in the task's accompanying provenance document. Narrative truth, anchor completeness and palette semantics require review, not just type checks.

## Clip

- `id`: unique nonempty ID; `duration_s`: positive number. Sum must equal project duration.
- `environment`, `composition`: nonempty direction strings, matched to the selected style and ratio.
- `characters`: list of known distinct cast IDs visible here; an empty list permits a prop-only insert.
- `narration`: exact string, empty for deliberate silence.
- `opening_state`, `closing_state`: nonempty objects describing visible positions/directions and prop ownership; use the same key structure throughout. Extensible JSON values are permitted; semantics require human/agent review.
- `transition`: the INCOMING cut into this clip. `kind` is `continuous` or `cut`; `reason` is a string, nonempty for a cut. A continuous join after the first clip requires the opening state to equal the preceding closing state. A cut can change place/time but its reason must explain what changes and what persists. First clip can use continuous with “opening” as reason.
- `beats`: nonempty list of objects with `start_s`, `end_s`, `action`, `camera`, `sfx`. Times are relative to the clip, contiguous from zero through full duration, with positive lengths. Use “none” for absent SFX and “locked camera” for no camera motion. Numeric precision is compared using decimal representations; use consistent explicit decimal boundaries.

Durations are provisional planning values until measured audio exists. The compiler does not measure or generate speech. No forced ten-second multiples, scene count, English translation or generic words-per-minute quota.

## Version-specific authority

`approval` is a record, not a permission grant. Fields:

- `status`: `draft`, `user-approved`, or `delegated-proceed`.
- `digest`: empty for a new draft; otherwise the SHA256 reported by validate.
- `evidence`: required nonempty string for either proceed status, identifying the actual authorization and review evidence in the current task. Do not publish private conversation contents; use a task-local reference.

The digest is SHA256 over UTF-8 JSON with sorted keys, compact separators, literal Unicode and finite values, excluding the entire `approval` object. Any other field change invalidates it. Reset to draft after revisions, validate, review affected design, then record truthful current authority. Compilation checks the record and version only; it cannot authenticate user approval or validate review evidence. It never auto-approves.

## Output

`compile` emits an artifact marked `prompt-package` and `compiled-prompts-only`, with storyboard digest, proceed status, target ratio/duration and ordered clip objects containing ID, duration, timeline offset, exact narration and standalone prompt. Prompts include visible cast anchors, voice/style/palette, scene composition, opening/closing states, incoming transition, timed beats and negative constraints. Preserve the storyboard alongside the package for audit/editing. Private sources should remain in the task workspace.

`validate` reports a digest for a well-formed draft. `compile` rejects a draft, stale authority, invalid timing/continuity or malformed input. Both return nonzero for errors; no files are sent externally. Compiler refuses an output path identical to the source. Review output paths before use; an existing different output file may be replaced.
