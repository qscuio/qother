# Revised chapter reproducibility code

地球往事｜序章：地球的来处

This additive source archive preserves the project-authored procedural scene,
composition, rendering, assembly and QA code, the public frozen narration text,
and a generic claim-planning template. Earlier preview history is unchanged.

This is a code archive, not a distributable video project with all inputs.
Private presenter art, audio, images, video, actual provider cues/timing,
media fingerprints and original QA measurements are excluded. Obtain your own
authorized local inputs. The full portable workflow has not been rerun; this
archive grants no scientific, audiovisual, voice or user acceptance.

## Source lineage and adaptations

`provenance.json` records archived source hashes. `paragraph-source-map.json`
records the selected code variants for each paragraph; it carries no media
hashes or measurements. The original production used different stellar and
planet renderer versions for different paragraphs. The adapter selects those
recorded code versions instead of substituting a single latest module.

P10 retains the original deterministic material engine from public commit
`e04f0556e983a75efcca7599278b04014ffe917c`, with baked presenter/typography
removed from the clean engine. Its source snapshot was made during the active
render and checked against launch/completion code hashes; that distinction is
retained in the code-lineage record.

Measured voice durations embedded in stellar code are replaced by reads from
explicit local metadata. Where adapted, original CODE hashes and archived CODE
hashes are distinguished. The compositor still reads the local timeline. Current
fail-closed locking/gating code drives portable rendering; historical integration
code versions are retained for lineage, not silently executed. No original
approval is carried over. A production-specific approval binder is excluded:
rerunning that stage tool alone would not recreate subsequent review amendments.

Illustrations are authored, time-compressed and not to scale. Provider timing
metadata cannot establish spoken correctness, intelligibility or listening.

## Explicit local inputs

Requirements: Linux/POSIX (section locks use fcntl), Python 3.12, NumPy, SciPy,
Pillow, FFmpeg/ffprobe, C++17 with OpenMP, and installed CJK fonts. Versions are
not locked across platforms, so bit-identical pixels are not promised.

1. Read `private-input-contract.json`. It contains only logical input roles and
   the relative runtime layout. Supply authorized local narration WAVs and
   provider boundary metadata, duration registry, exact chapter timeline,
   claim/cue storyboard, presenter, cover, continuity stills and benchmark.
   No input can be retrieved automatically from this archive.
2. Copy `private-inputs.example.json` outside the checkout and fill it with local
   paths. Run `python run.py manifest --private-inputs LOCAL_MAP.json --output
   NEW_PRIVATE_MANIFEST.json`. Hashes are computed only locally. Keep both files
   private and outside version control.
3. Run `python run.py setup --private-inputs NEW_PRIVATE_MANIFEST.json --font
   FONT.ttc --repository-root REPOSITORY_ROOT --runtime NEW_PRIVATE_DIRECTORY`.
   Setup verifies your local manifest, refuses an existing runtime, and copies
   inputs into an isolated layout. Plain local-path maps are also accepted;
   setup records their hashes locally. No rendering, TTS, ASR or network request
   occurs during setup. Supplied media equivalence to the original production
   cannot be established from this public archive.
4. Run `python run.py compile-native --runtime PRIVATE_DIRECTORY`. It builds
   only the included C++ source; no binary is distributed.
5. Run `python run.py frame --runtime PRIVATE_DIRECTORY --paragraph P01` for
   composed review stills. The recorded code variant is selected first and its
   native helper is compiled if needed. Review your actual local pixels.

`section --paragraph Pxx` selects the same code variant, then requires a new
accountable actual-frame content/visual/keyframe-sequence approval with current
renderer, compositor and dependency hashes. Adapted font paths and different
local inputs need fresh reviews. `inspect --paragraph Pxx` extracts decoded
samples and local technical evidence; those numbers do not replace listening
or continuous playback. `review_boundaries.py` extracts cut endpoints without
assigning a verdict. Every action takes `--runtime PRIVATE_DIRECTORY`.

After all input/output dependencies stop changing, `snapshot` computes local
fingerprints. Bind real scoped reviews in the private runtime ledger/evidence
manifest. `assemble` requires the repository-wide gate and an explicit runtime
root-assembly decision. `qa --video LOCAL_VIDEO.mp4` performs local technical
and waveform checks without declaring final acceptance. The public ledger
starts pending and contains no actual provider cues; setup binds only the local
timeline/storyboard you explicitly supplied, and resets review statuses.

The repository's canonical `docs/production-workflow.md` and
`scripts/validate_production_gate.py` remain the only active workflow. Their
commit and validator hash are in `gate-reference.json`. Setup verifies that
validator and copies it only as an immutable private build input. No competing
scene-local workflow or gate is published.

Scene-relative dependencies are intentional: early transitions use the next
stellar gas scene; the planet opening uses a clean P10 end; the recap calls the
stellar module; stellar materials call P10's material engine. Local files must
match the intended role and be reviewed, never silently substituted.

## Optional cover and bounded checks

`cover/render_cover.py` requires explicit local 16:9 hero art, a rights statement,
title and chapter label; it does not load a presenter. The title `地球的|来处`
with chapter label `序章` matches the frozen text. Configure its installed
serif/sans CJK font constants for your platform. A newly generated cover needs
new actual-pixel title and visual review.

Run `python test_sources.py` for fast source parsing, source-lineage hashes,
public frozen-text consistency, excluded-payload checks, CLI help and missing
input rejection. See `validation.json` for bounded code checks performed.
Those checks are not a complete portable render or audiovisual acceptance.
