# Visual and motion contract

## Composition

Use a clean white 16:9 canvas, generous breathing room, a short handwritten title toward the upper left, and a concrete narrative illustration in the center. Use warm dark outlines and a small meaningful palette, such as pale blue for the moving object and warm tan for its surroundings. Color should distinguish roles, parts, or states; it is not a full-frame decorative wash. Keep the lower caption lane free of essential artwork. Vary scene composition to fit the story rather than repeating boxes and arrows.

Preserve user-requested references at the level of layout, pacing, texture, and drawing behavior. Do not copy identifiable hands or protected artwork from a screenshot. The bundled sprites are AI-generated transparent cutouts and must be described that way.

## Drawing and paint

- Plan recognizable semantic parts: body, face, tool, connection, label. Prefer a meaningful outline route to a raster scan of an entire picture.
- Drive both revealed ink and nib position from the same path endpoint and time value. During a pen lift, move to the next stroke without drawing a connector.
- Keep each Chinese character isolated: finish its real ordered strokes before starting the next character. Median paths are readable handwriting approximations, not calligraphic outline fonts. Use actual stroke-order data; never claim a generic glyph trace has correct Chinese stroke order.
- Reveal only pixels the brush has traversed. For color, intersect brush coverage with the shape's fill mask. Concave or disconnected regions need separate interior passes with pen lifts; a line crossing empty space cannot stand in for hidden painting elsewhere.
- Choose a consistent ordering: draw all contours then fill semantic parts in that same order, or complete each part's contour and fill before the next part. Use block.parts and ordering so the renderer enforces the choice. Use after dependencies for meaningful construction dependencies; preserve authored order among ready parts. Do not substitute nearest-neighbor path sorting, which can scramble meaning. Neither overall mode is universally required.
- Small organic variation is fine, but do not jitter the hand independently of its anchor or break nib contact. This starter uses translation only; adding rotation requires revalidating every crop edge and anchor transform.
- Sample short events at the final output frame times. Require at least one visible frame per draw/lift, preferably two or more. The starter enforces two interior samples per draw, lift and exit, and automatically selects among 24, 30, 48 and 60 fps. Explicit FPS is honored or rejected with event-level retiming guidance, never silently raised. If it fails, simplify or retime. An unnecessarily high FPS cannot make rushed narration legible.

## Hands, subtitles, and ending

Calibrate the visible nib, not the sprite bounding-box center. Record the actual source resolution; a changed size invalidates calibration. Geometry checks require a finite in-bounds anchor near visible alpha and audit all four opaque source edges. This is still not visual proof that the anchor touches the tip. Preserve genuine alpha transparency. Keep the cutoff at the forearm below the canvas for the entire path, including lift motion. Check all three presets independently because their pivots differ.

Put short readable captions in a charcoal strip with white type; composite them above the hand. Avoid three-line paragraphs. Check Chinese glyph coverage at the actual font and output size. Handwriting labels and captions have different roles: do not write every narration word on the board.

Finish with a deliberate hand exit and a useful still hold of the completed image. Do not cut the voice short to reach an estimated duration. For scene changes, let the old idea settle before resetting the board.
