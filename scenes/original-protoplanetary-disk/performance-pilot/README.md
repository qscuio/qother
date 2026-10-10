# Bounded same-camera Cycles performance pilot

## Result

A lighter native Cycles configuration is promising for internal previews: 128 samples maximum, 32 minimum, adaptive threshold 0.03, volume step rate 1.6. It took **31.66 seconds** for the unchanged 1280×720 first-frame camera, versus the historical identical-camera 256/64, threshold 0.02, step 0.4 render at **79.38 seconds**: observed 2.51× speedup / 60.1% less time. This is not an approved production replacement. Increased fine grain is visible and temporal behavior has not been tested.

Only three candidate renders were made. No new packages, external renderer, uploaded assets, image planes, denoising or geometry removal were used. No canonical scene, production frame or frozen story was changed. All outputs are isolated here. The measured pilot made no changes to production defaults. This directory publishes its reviewed source and records only.

## Settings and measured times

| Candidate | Volume step | Samples max/min | Threshold | Seconds | Historical speedup |
|---|---:|---:|---:|---:|---:|
| Reference (existing exact-camera frame) | 0.4 | 256/64 | 0.02 | 79.38 | 1.00× |
| A | 1.6 | 256/64 | 0.02 | 66.89 | 1.19× |
| B | 3.2 | 256/64 | 0.02 | 60.23 | 1.32× |
| C | 1.6 | 128/32 | 0.03 | 31.66 | 2.51× |

All three run in one Blender 4.3.2 background CPU process with 8 threads; each independently reloads the canonical scene. Each timing is render-call wall time, including initialization/compositing/write, excluding process launch and scene loading. Historical reference timings come from motion-benchmark/timings.json. No simultaneous fresh reference was rerendered, so host-load differences can affect the percentages. Baseline sample settings were overridden by its original benchmark script; the saved hero scene itself is 512/96. Seed 46109, non-animated seed, 1280×720, unchanged camera and material graphs; no denoising. Source SHA256: 0831572d873e1d54458fabe39774ddae1bd4386883da495e00692261152fa4b0.

## Actual pixel inspection

Inspected the baseline and A/B full-resolution images, plus four-way whole-frame and native-size core/far-rim/near-rim crops. All retain the central compact light, irregular continuous flattened disk, near/far spatial structure and dark dust lanes. No gross shape collapse, opaque slab, external-image projection or washed-away dust texture appears in these first-frame tests.

A and B have close-looking grain to the reference; B subtly changes the integrated cloud shading. C retains the same broad structures but shows plainly coarser speckled grain, particularly around the core and bright far-side disk. C does not solve the existing soft edges or restricted color range.

Measured on reference pixels with mean RGB >0.08, in display-encoded RGB: A/B/C mean brightness ratios 1.011/1.016/1.008; Gaussian-lowpass (sigma=2px) RGB mean absolute difference 0.00707/0.00810/0.00755 on 0–1 scale. High-frequency RMS is 0.01906/0.01908/0.02528 versus reference 0.01853, or approximately +3%/+3%/+36%. This includes both detail and noise and is not a perceptual quality or physics score. No gold-standard image is assumed.

## Usability and stopping condition

- A: conservative modest speed gain, single-frame structure preserved.
- B: modest speed gain, single-frame structure preserved; increased volume step can produce view-dependent integration changes.
- C: meaningful speed gain for a preview candidate, with increased visible noise. Final-quality approval not given.
- Static-frame inspection does not establish acceptable temporal grain or volume-step aliasing. The responsible reviewer inspected both comparison panels and retained C only as an internal preview candidate. A/B do not offer enough gain to justify changing the final default. A separately authorized bounded camera check could then compare actual frames at the same original path, including adjacent frames near fastest motion. Three widely spaced views alone would not establish flicker-free motion.

At the measured C time, 48 frames would take roughly 25 minutes if costs stayed similar, rather than roughly an hour. This is only a linear estimate, not a completed accelerated animation or a guarantee. Full-resolution production would still be materially expensive.

The requested first phase is complete and stopped after exactly three settings. No long sequence is queued.

## Reproduction and local output files (images are not published)

- benchmark_volume_settings.py: three settings, actual Blender rendering. Run: blender -b -t 8 --python benchmark_volume_settings.py -- --scene PATH_TO/H10-original-disk.blend --output NEW_EMPTY_OUTPUT_DIRECTORY
- pilot.log: raw render progress.
- timings.json: measured times, input settings, camera values and source hash.
- A-step1.6.png, B-step3.2.png, C-step1.6-s128.png: actual render outputs.
- compare_volume_settings.py: pixel metrics and comparison crops, requiring Pillow/NumPy/SciPy. Run: python compare_volume_settings.py --reference SAME_CAMERA_REFERENCE.png --renders RENDER_DIRECTORY --output NEW_COMPARISON_DIRECTORY
- comparison-full.png: downscaled four-way composition comparison.
- comparison-crops.png: native-pixel crop comparison; columns reference/A/B/C.
- pixel-metrics.json: measured display-space values.

This remains a science-inspired three-dimensional art scene, with unchanged objects and no physical formation simulation or narration claim.

## Publication scope

Only these two scripts, this report and measured JSON records are included in the public-safe package. Rendered images and scene assets are excluded. Runtime paths are supplied explicitly by the person reproducing the test. The public-safe scripts are parameterized equivalents of the measured local scripts; their argument help and syntax were checked, and the parameterized comparison script reproduced the measured pixel-metrics JSON byte-for-byte, but the parameterized render script was not used to launch an additional rendering batch. The measured batch used the same candidate settings and render loop. Original production defaults remain unchanged.

Verified runtime dependencies: Blender 4.3.2; comparison script used Python with Pillow 12.3.0, NumPy 2.3.5 and SciPy 1.17.0. No dependency installation was performed.

The comparison adapter requires a fresh output directory to avoid overwriting existing evidence. Its recomputed pixel metrics were checked against these historical records; no additional renders were launched during publication.
