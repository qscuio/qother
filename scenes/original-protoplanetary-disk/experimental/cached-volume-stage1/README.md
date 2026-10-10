# Cached-volume Stage 1: field extraction diagnostics only

This completed bounded stage checks whether the authored disk material can be sampled without replacing its procedural noise. The project subsequently prioritized a 720p 2.5D comparison; method choice remains open to 2D, 2.5D, 3D or mixtures based on quality and total cost. This is a scope change, not a new permission gate or a claim that 3D failed.

## What was measured

- Authored closed mesh: zero boundary and nonmanifold edges.
- 64×64 vertical BVH columns: 1,065 misses, 3,031 two-crossing intervals, no other counts in this small probe. This does not validate a full-resolution mask.
- Geometry Nodes copies upstream Blender material nodes and samples 2,048 object-space positions. Repeated field evaluations are identical. Original fine Noise scale=6, detail=4 is retained.
- Independent 32×32 Cycles-emission diagnostic checks 1,024 constant-coordinate samples. Maximum absolute errors for density/emission/red albedo: 0.000103354454, 0.000001534820, 0.000000089407.
- Maximum relative errors are about 0.007809% density and 0.007807% emission, below 0.0079%, not bitwise equality. **The strict predeclared absolute threshold 1e-4 fails at one density sample.** `recorded/shader-exactness.json` preserves `passed: false`. A post-hoc rtol=1e-4/atol=2e-5 diagnostic passes, but does not replace that original criterion.
- The portable adapter was executed against the canonical static scene and reproduced the original probe values and shader error arrays exactly. It derives existing start/middle/end camera-only poses in memory instead of requiring a completed 48-frame render.

No full density cache, lighting bake, 720p cached-volume scene render, amortized performance measurement, motion-quality verdict or final renderer is supplied. `render_cache.py` and the unexecuted large-bake branch are deliberately omitted. The tiny color-coded shader diagnostic is not an art render.

## Reproduce from the existing canonical build

Use Blender 4.3.2 and its bundled NumPy; no new dependencies or external assets are required. Build the scene without expensive final renders using the already published pipeline:

```sh
python scenes/original-protoplanetary-disk/pipeline.py --output outputs/h10-source --build-only
blender -b -t 2 --python-exit-code 1 --python scenes/original-protoplanetary-disk/experimental/cached-volume-stage1/sample_fields.py -- --scene outputs/h10-source/H10-original-disk.blend --output outputs/field-probe
blender -b -t 2 --python-exit-code 1 --python scenes/original-protoplanetary-disk/experimental/cached-volume-stage1/validate_shader_fields.py -- --scene outputs/h10-source/H10-original-disk.blend --output outputs/shader-probe
```

Each diagnostic requires a new output directory, never overwrites input `.blend`, and does not save scene modifications. Shader validation performs its own small field probe first. Output includes local NPZ/EXR diagnostics and JSON. Do not commit generated binary files. Process completion does not imply the numerical acceptance flag passed: inspect `shader-exactness.json`.

Input must be the existing authored canonical scene with its original mesh/material/object names. Geometry changes or different Blender builds require new validation. Camera poses are a reconstruction of the existing 15° orbit test for metadata only, not density evolution. `recorded/metadata.json` preserves the original motion-scene metadata, with its private absolute input path replaced by a basename; portable output records its own input hash. Blend serialization hashes can differ even when scene fields agree.

## Optional preinstalled EGL capability probe

```sh
python scenes/original-protoplanetary-disk/experimental/cached-volume-stage1/egl_volume_capability_probe.py
```

This Linux/Mesa-specific ctypes script requires already installed EGL/OpenGL libraries and a supported surfaceless context. It makes a 16×16 pbuffer and samples a 2×2×2 R32F texture; it installs nothing and launches no browser. Historical research recorded llvmpipe software rendering and pixel [128,64,191,255], with no GL error. That proves a tiny native backend operation, not hardware acceleration or full-volume speed. Library/context availability is environment-specific; failures must be reported rather than bypassed. Publication reran the field/shader diagnostics, not this EGL capability test.

## Files and provenance

- `sample_fields.py`: bounded field sampling, mesh/BVH checks and metadata export only.
- `validate_shader_fields.py`: independent tiny Cycles shader comparison, preserving the failed strict criterion.
- `recorded/`: public-safe historical metrics and metadata; no raw media or sample arrays.
- `provenance.json`: original and portable source hashes and adaptation notes.
- `validation.json`: checks actually performed on the portable adaptation.

See [research and alternatives](../../../../docs/research/volume-and-25d-rendering.md) for first-party method references and untested options. Scripts are project-authored; no third-party renderer source is copied. Blender runtime licensing does not make this an implementation of the full referenced GPU Gems method.
