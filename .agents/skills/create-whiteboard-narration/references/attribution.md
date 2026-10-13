# Asset provenance and reuse

## Original components

The renderer, original single-line Latin glyphs, example envelope paths, and scheduling logic were authored for this workflow. Three transparent hand PNGs were originally generated with OpenAI image generation on 2026-10-13. They depict a non-identifiable adult right hand with a cream knit sleeve/fountain pen, pale-blue sleeve/marker, or bare forearm/pencil. They are AI-generated sprites, not filmed hands, not reference-video cutouts, and not the reference author's assets. Their preserved generation prompts and metadata are in assets/hand-provenance.json; calibrated pivots and sizes are in assets/hand_variants.json. Apply the originating generation service's applicable terms when reusing generated output; do not invent a third-party license grant or endorsement.

## Chinese stroke data

The unmodified per-character JSON subset in assets/hanzi comes from Hanzi Writer Data 2.0.1:
https://github.com/chanind/hanzi-writer-data

Its upstream data is Make Me A Hanzi:
https://github.com/skishore/makemeahanzi

The bundled data uses the Arphic Public License. Preserve the complete assets/hanzi/ARPHICPL.TXT and assets/hanzi/PROVENANCE.json alongside redistributed data. Rendering reads only medians and applies coordinate scaling; this does not replace the license. For newly obtained characters record their version/source and verify applicable licenses. Never execute downloaded JSON as code.

## Fonts and reference direction

No font binary is bundled. If using Noto Sans CJK, obtain it from an authorized installed source and preserve its SIL Open Font License when distributing the font itself:
https://github.com/notofonts/noto-cjk

Visual/workflow inspiration was the visible-hand narrative whiteboard style in the public project:
https://github.com/threerocks/sweety-handdraw-video

The project was consulted for broad semantic-part drawing, anchor calibration, caption placement, and speech-led pacing. No upstream renderer code, reference screenshot, or hand asset is included here. This implementation permits both per-object outline/fill and whole-scene outline-then-fill with consistent ordering. Do not describe this skill as that author's official skill or imply endorsement. If future work copies upstream code or substantial text, inspect and preserve the current license/attribution requirements first.
