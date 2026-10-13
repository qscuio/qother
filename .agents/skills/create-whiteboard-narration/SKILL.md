---
name: create-whiteboard-narration
description: Create narrated whiteboard videos with a visible writing hand, genuine progressive strokes, isolated handwritten Chinese characters, and purposeful flat-color illustrations synchronized to actual speech. Use for 带手白板、手绘口播、边讲边画 or visible-hand illustration animation. Do not use for hand-free technical diagram explainers, static sketch slides, or voice cloning.
---

# 带手白板手绘口播

Create an illustration-led scene that grows while the narration explains it. Keep the visible nib attached to the newly appearing stroke. The three bundled hand sprites are original AI-generated images, not filmed hands.

## Workflow

1. Establish the topic, audience, source facts, language, voice, duration, output destination, and any existing audio. Reuse choices already given. Default to 1280×720, 16:9, white background, cream-sleeve fountain pen. Chinese narration and a male preset are defaults for the originating project only; honor other languages, voices, and formats. Do not infer permission to clone a voice, buy a service, or publish externally.
2. Outline a few spoken ideas and concrete scenes before writing paths. Research factual claims when needed; distinguish illustrative metaphors from facts. Use drawings to explain, short handwritten labels to orient, and captions for the spoken words. Read [visual-rules.md](references/visual-rules.md) for the visual/motion contract.
3. Obtain authorized narration and measure its real duration and clause boundaries. Make the drawing timeline fit the audio. Read [audio-and-timing.md](references/audio-and-timing.md). Do not call character-proportional timing forced alignment. If speech is unavailable, label any silent output as a motion preview and report what is missing.
4. Author semantic contour paths, separate writing strokes, and clipped paint regions. Choose either whole-scene contours followed by fills or consistent per-object outline/fill. Never move a hand over a finished static image and call it hand drawing. Read [renderer-contract.md](references/renderer-contract.md) before using or adapting the starter.
5. Render a representative segment containing Chinese writing, illustration, paint, captions, and the hand exit. Inspect it yourself and fix it; request user feedback only when a meaningful creative choice is unresolved or they asked for a checkpoint. Do not impose repeated mandatory approvals.
6. Render the full piece, decode the final media, inspect timed frames and motion, and listen to the narration when playback is available. Use [quality-checks.md](references/quality-checks.md). Report review limitations honestly. Deliver the requested video and useful reusable source; do not upload or publish outside the authorized destination.

## Reusable starter

The bundled renderer is a small working, single-canvas engine for authored vector strokes. It is not a prompt-to-cartoon generator or a complete long-form production system. Extend the storyboard and artwork for the topic; for long work, render measured scene segments and join them after verifying continuity. See the contract for limits and dependencies.

Resolve SKILL_DIR to this installed skill directory. Write generated files into the current task's output directory, never back into the installed skill.

```bash
python "$SKILL_DIR/scripts/self_test.py"
python "$SKILL_DIR/scripts/render_whiteboard.py" \
  "$SKILL_DIR/assets/storyboard.example.json" \
  --silent-preview --output "$OUTPUT_DIR/envelope-motion-preview.mp4"
python "$SKILL_DIR/scripts/render_whiteboard.py" "$OUTPUT_DIR/storyboard.json" \
  --audio "$OUTPUT_DIR/narration.wav" --font "$CJK_FONT" \
  --output "$OUTPUT_DIR/whiteboard.mp4"
```

Use --hand cream_pen, marker, or pencil. Use --still SECONDS --output frame.png for an inspectable frame and --debug for the nib marker. FPS defaults to automatic motion-sampling validation; if short events fail, lengthen the drawing window or simplify instead of blindly forcing 24 fps.

## Assets and boundaries

- Read [attribution.md](references/attribution.md) when adapting, distributing, or replacing assets. Preserve the bundled Hanzi data license and provenance in redistributed source.
- Read hand_variants.json for actual nib anchors. Keep cut forearm edges offscreen throughout every frame.
- The small Hanzi dataset is intentionally limited. Missing characters must use supplied or lawfully obtained real stroke data, not a horizontal text wipe. The script never downloads assets, models, fonts, or credentials.
- Keep technical diagram explainers without a visible hand on their separate workflow. A whiteboard video should explain through scenes and purposeful drawing, not become that earlier format with a cursor added.
