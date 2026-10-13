# Working renderer contract

## Scope and dependencies

scripts/render_whiteboard.py is a working Python/Pillow renderer for one continuously accumulating whiteboard. It takes authored paths and measured narration, produces H.264/AAC MP4, and emits a sibling .timeline.json and .audit.json. It does not generate illustrations, synthesize speech, align audio, clear the canvas mid-scene, or fetch missing data. The example is a generic envelope travelling toward A; no DNX-specific architecture or previous project directory is required.

Requires Python 3.10+, Pillow >=10, and FFmpeg/FFprobe. Captions require a user-selected installed font with the necessary glyphs. Noto Sans CJK is a suitable installed option, not a bundled font. Check what is available first; install dependencies only under the active authorization policy. Do not add API keys or network/model downloads to this starter.

Coordinates use a 1280×720 reference canvas. --width and --height allow other even-sized 16:9 outputs, using the same layout. A portrait request requires adapting layout/renderer rather than stretching this sample. --supersample 2 improves stroke antialiasing at higher render cost. --hand selects cream_pen, marker, or pencil; --font supplies caption typeface; --hanzi-dir replaces the directory searched for stroke JSONs.

## Storyboard schema

See assets/storyboard.example.json for a complete runnable silent example. Author each production storyboard in the task workspace:

- version: 1
- audio: optional path relative to the storyboard; --audio overrides it. The file's measured duration controls the video.
- preview_duration: seconds, used only with --silent-preview and no audio
- caption_timing: method label documented in audio-and-timing.md
- captions: ordered, nonoverlapping objects with start, end (seconds), and text
- blocks: ordered, nonoverlapping start/end intervals inside the measured duration, each with nonempty items
- exit: start/end after drawing, with room left for the final hold

Every block expands into explicit draw and pen-lift events. Allocation is based on path length with a minimum weight for short strokes and travel. The supplied window is respected exactly. Check the result rather than treating the allocation as an audio alignment algorithm.

Items:

```json
{"type":"path","points":[[100,200],[300,200]],"width":4,"color":[42,48,52,255],"tag":"arrow"}
{"type":"path","points":[[100,200],[300,200],[300,300],[100,300]],"closed":true}
{"type":"text","text":"小包 A","at":[84,70],"size":44,"width":4}
{"type":"fill","polygon":[[100,200],[300,200],[300,300],[100,300]],"color":[190,220,235,255],"spacing":18}
```

All points are finite x,y pairs. Use simple non-self-intersecting polygons; holes need separate authored masks/renderer adaptation. Colors are integer RGB/RGBA arrays. A fill generates independent interior scanline spans and lifts between them, preventing concavity-crossing ink. Fill coverage is clipped to its polygon and composited below contours. Make the contour region match the fill region and inspect the result.

The built-in original single-line alphabet supports uppercase A–Z, digits, and basic punctuation. Lowercase/custom scripts need additional authored strokes; missing characters fail clearly. Chinese reads each medians array in source order from Hanzi Writer Data JSON. The bundled subset is: 业、机、小、交、配、由、口、置、看、域、包、务、头、路、入、换 (check the actual directory before choosing labels). Supply additional licensed data for a new topic; preserve its attribution. A caption font is not handwriting stroke data.

## Run and adapt

For a silent motion preview, run the command in SKILL.md. For a narrated video, replace example intervals with timings derived from the actual audio, add measured captions, then pass --audio. Do not merely attach an unrelated audio file to the example and claim synchronization.

Use --still 5.0 --output /task/frame.png to inspect a frame, and --debug to mark the path nib. Snapshot rendering still requires a valid scene and either audio or --silent-preview. Timeline/crop checks run before a still or video render. Full-video output overwrites the explicit --output path; choose a fresh path unless replacement was intended.

The renderer enlarges each sprite as needed so its bottom source-cut edge stays below the frame. It uses no rotation. If replacing assets, also inspect side/top cut edges and verify the nib anchor at the actual image resolution. A numeric anchor check alone cannot guarantee visual calibration.

For multi-scene work, split narration at measured boundaries, author scene-local timings, render each scene, and concatenate streams with consistent resolution/FPS/codecs or re-encode a final master. Check joined audio duration, caption continuity, and scene transitions. Never silently drop speech between clips. Keep the hand exit/hold at meaningful breaks rather than at every clause.

## Deterministic checks

Run scripts/self_test.py. It verifies isolated Chinese character sequencing, shared nib/ink endpoint, no ink during lifts, partial/clipped paint, rejection of missing Hanzi and unmeasured final captions, motion frame sampling, and crop geometry for all three hands. Optional --output-dir writes inspectable PNGs and a report outside the skill.

These checks are structural, not a substitute for viewing the encoded MP4 and listening. The audit describes geometric synchronization, never independent optical tracking or a listening review.
