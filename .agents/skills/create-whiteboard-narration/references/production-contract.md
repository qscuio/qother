# Production acceptance and size preflight

Use this contract before expensive full narration/full rendering, especially for long-form work. The checker is local and read-only: it does not synthesize audio, align words, view an image, listen, or send anything. Start from assets/project.template.json in the task workspace. Its pending/null values intentionally fail until real decisions and artifacts exist; never invent approval or evidence to make it pass.

## Stage 1: accepted voice

If reusing user-supplied audio, set narration.source to provided; no new audition is needed. For newly synthesized long-form narration, set source to synthesized and identify the exact provider/model/id. Obtain a short, representative audition through an authorized route, have the user accept it, and record the message/reference as user_evidence. The audition should include the actual language, a technical abbreviation/name, and normal sentence rhythm. No default voice is considered accepted just because it is installed.

Store the audition path and SHA-256 in voice.acceptance.sample. Bind the exact provider/model/id/settings using voice.acceptance.configuration_sha256, printed by running the same script with --voice-fingerprint (this records no approval). Set status to accepted only after the decision. A changed provider, model, voice or settings invalidates that acceptance fingerprint. Existing active rejections are exact provider/model/id records in rejected_voices; a rejected choice cannot silently return as a fallback. Resolve a conflicting accepted/rejected record using the user's explicit changed decision, not by deleting history to satisfy a check. A changed audition hash requires renewed review.

```bash
python "$SKILL_DIR/scripts/production_preflight.py" project.json --stage voice
```

This gate verifies a recorded decision and file identity. It cannot infer genuine consent, pleasantness, or voice identity from audio bytes. It never calls a TTS service.

## Stage 2: one master, measured beats, reviewed scenes

narration.master and narration.script each have path and sha256. Paths are relative to the manifest. duration_seconds must match FFprobe within 20 ms. Set continuous_master to true, visual_edit_audio_policy to preserve_master, and timing_method to manual_measured, provider_timestamps, or forced_alignment only when that work actually happened. Ordered beats have unique id, start, end, and text; concatenating their text must reproduce the exact UTF-8 script, including whitespace. Their bounds must be finite, increasing/nonoverlapping, and inside the actual master. Gaps for natural pauses are allowed.

Keep narration.edits as an honest production log of any authorized assembly or changes. The authoritative hash is always the reviewed final master. The script checks identity and timing bounds, not semantic pronunciation or whether a declared alignment method was truthful. Do not edit beats to disguise missing or resynthesized words.

Each scene records:
- id, a unique stable identifier
- storyboard, with path and SHA-256 of the reviewed storyboard
- narration_quote, an exact relevant spoken passage, and explains, what the drawing makes observable
- visual_review.status = accepted, reviewer, and concrete evidence of what was inspected
- visual_review.sample, with path and SHA-256 of the inspected still/contact sheet

Use the same style_id across the project and each storyboard's style.id. The structural style check covers palette, stroke widths and basic layout; the renderer also checks expanded glyph/path bounds. It does not prove likeness, expressive quality, semantic accuracy, or absence of every overlap. Human/model visual inspection must check those, including recurring props and character identity. A changed storyboard or sample invalidates its recorded hash.

```bash
python "$SKILL_DIR/scripts/production_preflight.py" project.json --stage render --output preflight.json
```

The single-canvas renderer accepts --project project.json and requires it for final videos of at least 60 seconds. It checks that the current storyboard belongs to the reviewed scenes and that --audio is the same reviewed master. Short diagnostic stills and silent previews do not force this gate. Multi-scene assembly remains a separate workflow: run the project-level gate before producing its segments, then mux the one master once at final export.

## Stage 3: a file that fits its destination

Record delivery.destination and the destination's currently verified limit_mib (MiB = 1,048,576 bytes). The preflight derives a video bitrate budget after reserving audio_kbps (default 160) and 5% for container/encoder variance. Reject implausibly small budgets before rendering. This is a target, never a claim that a CRF encode has a predictable size.

The renderer's --max-output-mib uses that target to constrain encoding and checks actual final bytes afterward. A project manifest supplies its own limit; an explicit lower CLI limit is respected. If an encoded file is too large, it fails delivery readiness and retains the local file for diagnosis. Re-encode within the approved quality/size constraints or use another authorized destination. Never quietly remove narration or shorten the content to fit.

Add delivery.final_file after the final file exists, then run:

```bash
python "$SKILL_DIR/scripts/production_preflight.py" project.json --stage delivery
```

A pass proves only the declared contract, file identities and actual size fit. It does not prove upload success or recipient access. Check those separately when delivery is authorized.
