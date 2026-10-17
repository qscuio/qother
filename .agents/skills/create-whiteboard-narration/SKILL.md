---
name: create-whiteboard-narration
description: Create narrated whiteboard videos with a visible writing hand, genuine progressive strokes, isolated handwritten Chinese characters, and purposeful flat-color illustrations synchronized to actual speech. Use for 带手白板、手绘口播、边讲边画、SRT 驱动手绘、暖纸流式笔迹 or visible-hand illustration animation. Do not use for hand-free technical diagram explainers, static sketch slides, or standalone voice-cloning requests.
---

# 带手白板手绘口播

Create an illustration-led scene that grows while the narration explains it. Keep the visible nib attached to the newly appearing stroke. The three bundled hand sprites are original AI-generated images, not filmed hands.

## Workflow

1. Establish the topic, audience, source facts, language, voice, duration, output destination, and any existing audio. Reuse choices already given. Default to 1280×720, 16:9, white background, cream-sleeve fountain pen. Choose language and voice from the current request or accepted source audio; no historic TTS preset is a default. Do not infer permission to clone a voice, buy a service, or publish externally.
2. Outline a few spoken ideas and concrete scenes before writing paths. Research factual claims when needed; distinguish illustrative metaphors from facts. Use drawings to explain, short handwritten labels to orient, and captions for the spoken words. Read [visual-rules.md](references/visual-rules.md) for the visual/motion contract.
3. Reuse approved audio, or get an accepted short audition before expensive long-form synthesis. Keep one continuous narration master and measure its real duration and clause boundaries. Make the drawing timeline fit that master. Read [audio-and-timing.md](references/audio-and-timing.md). For an authorized cloned narrator, use [qwen-voice-clone.md](references/qwen-voice-clone.md) and its local Qwen adapter. Keep narration dry and mono by default; mono alone does not prove an echo-free sound. Do not call character-proportional timing forced alignment. If speech is unavailable, label any silent output as a motion preview and report what is missing.
4. Author named semantic parts with independent contour strokes and clipped paint regions. Use the same explicit part order for outline and fill, either all outlines then fills or consistently per part. Lock recurring subjects, props, palette and line weights across scenes. Never move a hand over a finished static image and call it hand drawing. Read [renderer-contract.md](references/renderer-contract.md) before using or adapting the starter.
5. Render a representative preview containing Chinese writing, illustration, paint, captions, and the hand exit. Use still/contact-sheet review first when it resolves the question without a movie. Inspect it yourself and fix it; request user feedback only when a meaningful creative choice is unresolved or they asked for a checkpoint. Do not impose repeated mandatory approvals.
6. Run [production-contract.md](references/production-contract.md) before expensive production: accepted voice, unchanged master/script, reviewed scene samples and a verified delivery-size budget. Render the full piece, decode the final media, inspect timed frames and motion, and listen to the narration when playback is available. Use [quality-checks.md](references/quality-checks.md). Report review limitations honestly. Deliver the requested video and useful reusable source; do not upload or publish outside the authorized destination.

## SRT and warm-paper theme

For SRT-driven drawing or 暖米黄纸张流式手绘, read [srt-paper-stream.md](references/srt-paper-stream.md). The bundled SRT compiler binds measured subtitle cues to authored vector parts and selects a warm paper background. It does not infer artwork or run a third-party raster renderer. Keep existing vector and white-background projects unchanged unless this theme is requested.

## Shared technical pronunciation

Use the repository's [versioned pronunciation lexicon](../../../pronunciation/README.md) before preparing technical speech. Keep canonical narration, captions and labels unchanged; generate separate `spoken_text` with `scripts/apply_pronunciation.py` from the repository root. Both skills share that one lexicon. Candidate engine spellings remain pending until actually auditioned for the selected voice/configuration; `--allow-pending` prepares a draft, never approves synthesis. If this skill is installed without the repository, locate the same lexicon/helper explicitly rather than creating a divergent replacement table.

## Reusable starter

The bundled renderer is a small working, single-canvas engine for authored vector strokes. It is not a prompt-to-cartoon generator or a complete long-form production system. Extend the storyboard and artwork for the topic; for long work, render measured visual segments and mux the continuous narration master once after joining them. See the contract for limits and dependencies.

Resolve SKILL_DIR to this installed skill directory. Write generated files into the current task's output directory, never back into the installed skill.

```bash
python "$SKILL_DIR/scripts/self_test.py"
python -m unittest discover -s "$SKILL_DIR/scripts" -p 'test_*.py'
python "$SKILL_DIR/scripts/render_whiteboard.py" \
  "$SKILL_DIR/assets/storyboard.example.json" \
  --silent-preview --check-only --output "$OUTPUT_DIR/preflight.json"
python "$SKILL_DIR/scripts/render_whiteboard.py" \
  "$SKILL_DIR/assets/storyboard.example.json" \
  --silent-preview --output "$OUTPUT_DIR/envelope-motion-preview.mp4"
python "$SKILL_DIR/scripts/render_whiteboard.py" "$OUTPUT_DIR/storyboard.json" \
  --audio "$OUTPUT_DIR/narration.wav" --font "$CJK_FONT" \
  --output "$OUTPUT_DIR/whiteboard.mp4"
```

Use --hand cream_pen, marker, or pencil. Use --still SECONDS --output frame.png for an inspectable frame and --debug for the nib marker. Auto FPS selects 24/30/48/60 only; an explicit FPS is never raised. If drawing, lift or exit events are undersampled, lengthen the window or simplify. Use --check-only for validation without media generation. Long final videos (at least 60 seconds) require --project; --max-output-mib adds a delivery budget.

## Assets and boundaries

- Read [attribution.md](references/attribution.md) when adapting, distributing, or replacing assets. Preserve the bundled Hanzi data license and provenance in redistributed source.
- Read hand_variants.json for actual nib anchors and source sizes. The audit checks all four source-cut edges through output frames and transition boundaries; inspect visible nib calibration separately.
- The small Hanzi dataset is intentionally limited. Missing characters must use supplied or lawfully obtained real stroke data, not a horizontal text wipe. The script never downloads assets, models, fonts, or credentials.
- Keep technical diagram explainers without a visible hand on their separate workflow. A whiteboard video should explain through scenes and purposeful drawing, not become that earlier format with a cursor added.

