# Working renderer contract

## Scope and dependencies

scripts/render_whiteboard.py is a Python/Pillow renderer for one continuously accumulating whiteboard. It consumes authored paths and supplied measured narration, produces H.264/AAC MP4, and emits sibling .timeline.json and .audit.json files. It does not generate illustrations, synthesize speech, align audio, clear the canvas, automatically assemble multiple scenes, or fetch data. The example is a generic envelope travelling toward A; it does not depend on DNX or an earlier project folder.

Requires Python 3.10+, Pillow >=10, and FFmpeg/FFprobe for narrated/encoded media. Stills and silent --check-only validation need no FFmpeg. Captions need an installed font with the required glyphs. Check existing dependencies first; install only under active authorization. No API keys, model downloads or network calls are in these scripts.

Coordinates use a 1280×720 reference canvas. --width/--height allow positive even-sized 16:9 outputs; portrait needs an adapted layout, not stretching. --supersample 2 improves antialiasing. --hand selects cream_pen, marker or pencil; --font supplies captions; --hanzi-dir overrides stroke-data lookup.

## Storyboard schema, version 1

Existing flat item storyboards remain valid. See assets/storyboard.example.json for a runnable semantic-part example. Write production files in the task workspace.

- version: 1
- audio: optional path relative to the storyboard; --audio overrides it. Its measured duration is authoritative.
- preview_duration: positive seconds, only when using --silent-preview without audio
- caption_timing and captions: measured method plus ordered nonoverlapping start/end/text records
- blocks: ordered, nonoverlapping, finite start/end seconds inside the duration
- exit: finite start/end after drawing; must end before the audio so a final hold exists
- style: optional structural baseline, strongly recommended and required by the project acceptance gate

A block contains either legacy items or semantic parts, never both. Use parts for new illustrations:

```json
{
  "start": 0.2, "end": 8.0,
  "ordering": "outlines_then_fills",
  "parts": [
    {
      "id": "body",
      "outline": [{"type":"path","points":[[100,200],[300,200],[300,400],[100,400]],"closed":true}],
      "fills": [{"type":"fill","polygon":[[100,200],[300,200],[300,400],[100,400]],"color":[190,220,235]}]
    },
    {
      "id": "roof", "after": ["body"],
      "outline": [{"type":"path","points":[[80,200],[200,100],[320,200]],"closed":true}],
      "fills": [{"type":"fill","polygon":[[80,200],[200,100],[320,200]],"color":[224,194,150]}]
    }
  ]
}
```

Part IDs must be unique inside a block. after is an optional dependency list; unknown/self dependencies and cycles fail. Stable dependency ordering preserves the author order where possible. outlines_then_fills (default) emits every part's outline, then its fills in the identical part order. per_part emits each outline/fill pair before the next part. Each part requires path/text outline items and may have fill items. Events retain part_id and phase for inspectable tests/QA. Semantic correctness of the parts and justified occlusion choices still require review; this is not an image-to-parts extractor.

### Items

```json
{"type":"path","points":[[100,200],[300,200]],"width":4,"color":[42,48,52,255],"tag":"arrow"}
{"type":"path","points":[[100,200],[300,200],[300,300],[100,300]],"closed":true}
{"type":"text","text":"小包 A","at":[84,70],"size":44,"width":4}
{"type":"fill","polygon":[[100,200],[300,200],[300,300],[100,300]],"color":[190,220,235,255],"spacing":18}
```

All points/placements are finite x,y pairs. Widths, sizes and fill spacing are positive. Colors are RGB/RGBA integer arrays. Use simple, non-self-intersecting fill polygons; holes need separate masks/adaptation. Each polygon's interior scanline spans are separate brush strokes with lifts across concavities. Coverage is clipped to the mask and composited below contours. The engine does not verify that an authored fill polygon exactly matches its semantic outline; inspect it.

Chinese characters use medians in original Hanzi Writer Data order, completing each character before the next. The bundled subset is 业、机、小、交、配、由、口、置、看、域、包、务、头、路、入、换. The original Latin single-line alphabet covers A–Z, digits and basic punctuation. Missing glyphs fail clearly; do not use a font wipe or raster skeleton as a fake stroke-order substitute. Supply licensed medians for new characters and preserve attribution.

### Style baseline

```json
"style": {
  "id": "warm-flat-v1",
  "palette": [[42,48,52],[190,220,235],[224,194,150]],
  "outline_width_range": [3,5],
  "caption_lane_top": 590
}
```

The checker validates palette, width range and basic art placement. After expansion, the renderer checks actual glyph/path coordinates plus pen radius against canvas/caption boundaries. Fill brushes use their clipped polygon bounds. Identity, expressiveness, exact text glyph coverage, usefulness of the drawing and composition are visual-review responsibilities, not machine-certified properties.

## Timing, hand safety and QA

Block windows allocate time by path length with minimum weights for short strokes and lifted travel. This is drawing scheduling, never audio alignment. There must be at least two interior output-frame samples per draw, lift and exit. Auto tries 24/30/48/60 fps; explicit FPS 1–240 is honored or rejected, never raised. An error lists offending event times so the author can lengthen blocks or simplify paths/fill rows. High FPS cannot repair illegibly rushed narration.

Hand presets bind source size to finite nib anchors near alpha. Translation uses the same endpoint as newly appearing ink, and lifted travel adds no ink. The audit conservatively checks all four opaque source-cut edges at every delivered frame plus event start/middle/end. It also exports qa_sample_times, which are actual output frame times around motion boundaries. Rotation and tilt are not supported; adding them requires anchor transforms and fresh edge checks. Numerical safety cannot establish that the visible nib looks correctly calibrated.

--still SECONDS --output frame.png renders an inspectable still. --debug overlays a nib marker. --check-only --output preflight.json writes its audit to exactly preflight.json plus a sibling preflight.timeline.json, without creating any media. Still/check-only audits explicitly say media, visual and listening review were not performed. Outputs are written only to the explicit destination; use a fresh path unless replacing a file was intended.

For full video, the renderer fingerprints inputs, muxes the supplied audio once, probes stream count/durations, fully decodes the encoded output and hashes the final file. Captions are burned in and duplicate subtitle tracks are rejected. It rechecks that the source master did not change. Stream tolerance is one frame plus 30 ms for encoder padding. Final visual/listening review remain not_performed until somebody actually performs them; a decode pass does not change that.

Use --project for the accepted production manifest and --max-output-mib for a verified delivery budget; see [production-contract.md](production-contract.md). Final videos of 60 seconds or longer require --project. Bitrate planning reserves audio/overhead and actual output size is checked before delivery readiness. Multi-scene assembly remains manual and must retain one narration master rather than resynthesized per-scene speech.

## Regression tests

```bash
python "$SKILL_DIR/scripts/self_test.py"
python -m unittest discover -s "$SKILL_DIR/scripts" -p 'test_*.py'
```

Tests cover original drawing/Hanzi behavior, semantic order and dependencies, no-ink lifts, partial clipped paint, all-hand/all-edge geometry, bounded/explicit FPS, finite timings, style mismatch, rejected/stale voice evidence, continuous master/script identity, stale scene reviews, and delivery size. They use vectors, synthetic pixels and inert byte fixtures; they perform no TTS or video production. self_test.py --output-dir can additionally produce inspectable still PNGs outside the installed skill.
