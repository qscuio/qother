# Quality gate

## Before full render

- Verify facts against the supplied sources; preserve audience, duration, language, voice, and destination choices.
- Inspect one representative segment containing the most complex handwriting, an outline and fill, caption text, and an exit. Confirm it looks like an illustration being drawn rather than a hand over a completed slide.
- Check rendered Chinese characters against the intended labels. Later characters must stay blank until their turn, and lifts must not leave connectors.
- Inspect nib alignment visually at beginning, middle, and end of several paths, then verify the same endpoint drives both hand and ink. Distinguish visual/geometric checks from measured optical tracking.
- Check color reveals only under the brush and that fill paths stay inside semantic regions; inspect concave parts especially. Check cutoff edges at every final frame time and visually at the highest/leftmost/rightmost nib positions.
- Count frame samples for every draw and lift. Require visible sampling; prefer at least two frames per event. Change timing/complexity when events are rushed.

## Final media

Use FFprobe for dimensions, codec, frame rate/count, duration, and the presence of an audio stream. Decode the final deliverable, not only source images:

```bash
ffprobe -v error -show_format -show_streams -of json final.mp4
ffmpeg -v error -i final.mp4 -f null -
ffmpeg -v error -ss 3.5 -i final.mp4 -frames:v 1 check.png
```

Sample opening handwriting, each scene's construction and paint phase, caption transitions, hand exit, and completed still. View small temporal contact sheets around fast transitions. Confirm no missing-glyph boxes, forearm crop seam, spill outside a fill shape, subtitle occlusion, early character reveal, static-slide fake drawing, or clipped composition.

Listen or play the actual audiovisual output when possible. Verify pronunciation, caption boundaries, useful pauses, and audiovisual idea synchronization. If only waveform/structural checks were possible, disclose that limit rather than claiming listening or uninterrupted playback. Compare audio/video duration against one frame and check there is no missing final syllable.

## Delivery and source hygiene

Deliver the requested MP4 and, when useful/requested, lightweight reusable source with captions, exact timeline, hand anchors/provenance, and applicable asset licenses. Include the audio master only when useful and authorized. Keep raw screenshots, private research notes, credentials, model weights, generated frame caches, and temporary QA dumps out of reusable packages.

Explain material limitations briefly: AI-generated hand sprites; approximate median handwriting rather than calligraphy; a silent preview if speech was unavailable; or review you could not perform. Do not imply external publishing, an approved cloned voice, or a verified final video when only a still has been rendered.
