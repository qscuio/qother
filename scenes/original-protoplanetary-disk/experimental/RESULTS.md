# Actual 48-frame camera test results

The two-second silent technical candidate is complete: 48 genuine 1280×720 Cycles frames, encoded at 24fps. The world is unchanged; only the observer moves by 15 degrees. No frame interpolation or denoising was used.

Full video decode produced 48 distinct frames. Every adjacent pair was scanned; no gross flash/freeze flags were raised under the documented heuristic thresholds. Decoded frames 1, 24 and 48 were visually inspected. These checks do not establish final cinematic quality or absence of subtle flicker.

Actual browser playback remains blocked. Local Chromium could not create its required sockets, and the existing cloud browser did not accept the local file URL. No alternate URL or external upload bypass was attempted. There are no presented-frame callbacks or dropped-frame telemetry to claim.

Images, video, raw frames, .blend files, private host assets and Library identifiers are intentionally excluded from this public QA handoff. See results.json for the measured rendering and decode data.

## Historical execution versus portable reproduction

These measurements describe the actual source-author run, which reused three already-rendered benchmark frames and rendered 45 new frames. The published guarded render_camera_batch.py deliberately uses a fresh directory and renders all 48 frames. Its complete rerun is not claimed by this report. Existing four-stage authoring, rendering defaults, overwrite guards and source fingerprints are unchanged.

New utilities are portable adaptations: scan_motion_frames.py accepts --movie and a new --output directory; qa_browser_playback.cjs accepts the same arguments plus optional --chromium. Playwright 1.62.1 is an optional dependency (separate package.json). Browser launch requires an already installed supported Chromium. Do not retry blocked browser operations via alternate URLs or uploads. Browser utility syntax is checked; runtime remains blocked in the measured environment.
