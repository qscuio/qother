# Separate quality gates

Do not turn one successful technical test into a claim that a video looks or sounds right. Track these independently.

## Before expensive production

- Confirm a new long-form voice using a representative audition the user accepted. Do not revive a rejected preset. Reuse already-approved narration when supplied.
- Establish the continuous master and measured beats; lock its hash and exact script. A drawing revision should not resynthesize speech.
- Check what each illustration makes observable beyond repeating the caption. Keep recurring subject/prop identity, palette and outline weight consistent across scenes.
- Inspect a representative still/contact sheet or approved motion preview containing the most demanding handwriting, contours, paint, captions and hand exit. Store its actual evidence/hash with the storyboard in the project manifest. Do not mark review accepted before viewing it.
- Verify the destination's size limit, derive a realistic delivery bitrate budget, and leave headroom before full rendering. For materially different quality choices, ask the user rather than silently compromising the requested output.

## Technical QA

Run both bundled test suites and --check-only when editing a storyboard. Check original stroke-order isolation, semantic contour/fill sequence, interior frame samples for draw/lift/exit, all four source-cut edges and style bounds. Use qa_sample_times from the audit; it includes adjacent frames around fast transitions, rather than only one midpoint per scene.

For final output, the renderer probes streams, checks duration, decodes the entire MP4 and hashes the file. For an externally assembled final master, do those checks again on that exact artifact:

```bash
ffprobe -v error -show_format -show_streams -of json final.mp4
ffmpeg -v error -xerror -i final.mp4 -map 0:v:0 -map 0:a:0 -f null -
ffmpeg -v error -ss 3.5 -i final.mp4 -frames:v 1 check.png
```

The decode command above assumes a narrated final with audio; omit the audio map only for an intentionally silent preview. Reject error-level output even if a tool returns exit code zero. Do not discard decoder diagnostics.

Verify intended resolution/FPS, no duplicate caption track, actual bytes within the destination limit, and audio/video duration against the authoritative master. A changed final file invalidates its prior decode/hash evidence. These checks do not prove pronunciation, attractive art, accurate caption timing, or user approval.

## Visual QA

Actually view sampled rendered/decoded frames and temporal contact sheets. Check:
- Hand nib at beginning/middle/end of several strokes, source-edge seams at extreme positions, lifted travel without ink, and a deliberate exit/hold
- Later Chinese characters blank until their turn, no missing glyph boxes, no unwanted connecting strokes
- Semantic parts constructed in meaningful order, same-order color completion, only visited brush coverage revealed, no fill spill or gaps at concavities
- Palette/line-weight consistency, recurring subjects recognizable, useful visual explanation, no caption occlusion or clipped text
- Scene transitions and final composition, not merely a finished static screenshot with a hand over it

A numerical anchor or same-endpoint result is geometric evidence, not independent optical tracking. If playback is unavailable, disclose that only still/temporal samples were viewed.

## Listening and audiovisual QA

Listen to the actual voice and final audiovisual file when possible. Check pleasantness for the requested use, names/abbreviations, clipping, awkward joins/pauses, caption boundaries, correspondence of spoken ideas to drawing, and the final syllable. Record exactly what was heard; do not infer listening from waveform analysis, ASR, successful decode, correlation or file hashes. If unavailable, leave listening as not_performed and report that limitation.

## Delivery and source hygiene

Run the delivery-size gate against the exact final file, then deliver only through the authorized destination. Verify access and delivery separately; a local file that fits is not a delivered file. Include useful lightweight storyboard/caption/timeline source and asset licenses when requested. Keep the master only when useful and authorized. Exclude private notes, credentials, model weights, frame caches and incidental QA dumps from source packages.

Explain material limitations briefly: AI-generated hand sprites; median handwriting rather than calligraphy; unavailable listening/playback; or a silent/still preview. Do not call a preview a verified final video or imply external publication.
