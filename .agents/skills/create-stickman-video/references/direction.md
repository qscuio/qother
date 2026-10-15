# Visual direction and continuity

## Variants

- `classic-light`: hollow-head black line figure on a flat white field; limited accent colors on props, stable line weight, no realistic depth.
- `classic-dark`: inverse polarity, white line figure on a black field; keep figure monochrome.
- `studio-tech`: a simple clothed 2D stick character in a sparse bright studio, restrained floor grid and icon-only floating panels. Avoid accidental circuit-board walls or busy UI. Clothing is a project choice, not a mandatory borrowed mascot.
- `cinematic-story`: the same clean 2D character language in colored narrative settings with deliberate lighting and depth. Do not turn the figure into a realistic human or 3D avatar.
- `prehistoric-comedy`: rough outlines, expressive light-filled heads, stick limbs, story-specific clothing and earthy settings. Distinct cast identities are allowed. Modern workplace analogies remain fiction, not archaeological reconstructions. A held reaction can carry the joke.
- `cozy-story`: simple expressive characters in full-color 2D locations; varied shots and motivated location cuts. Preserve character, narrator, important props and screen direction across locations. Do not force every scene into the same room or add a visible drawing hand.

These are direction presets, not measured model support claims. Do not import planned upstream styles as implemented features.

## Character bible

Give each recurring role a stable ID and complete anchor: head shape/fill, face rules, body/limb design, proportions, line weight, clothing/accessories and colors. For minimal stick figures, require two arms/two legs, connected limbs, and one current pose per limb. Motion replaces the previous pose; it must not leave duplicate arms. Separate static design from acting instructions. Do not impose a faceless/empty-head rule on expressive filled-head variants.

Reference sheets, when available and authorized, should show the same identity across useful angles and poses. Record asset hashes outside public examples. A seed or reference image is a control, not a consistency guarantee. Repeat the full anchor even for independently generated later clips.

## Beats and action

Use a few meaningful timed physical beats per clip; 0–3/3–7/7–10 seconds is merely a ten-second example. Choose intervals from actual speech when available. Put intent, movement, contact and outcome in sequence: reach toward token → grip it → carry it → release into tray. Do not ask a token to be simultaneously held and on the tray. Avoid vague “energy transformation” or unrelated morphing as a substitute for causality.

Describe camera behavior explicitly; a deliberate locked camera is valid. Reserve reaction holds and readability pauses when they serve meaning. Effects and motion must not obscure identity or make scientific claims unsupported by narration.

## Framing and cuts

For 16:9 stage lateral relationships and leave label space. For 9:16 recompose in depth or vertically, maintain readable silhouettes, and reserve platform-specific UI safe areas after checking the target. Changing the ratio requires actual restaging, not replacing one string.

Opening/closing state maps track persistent positions, directions, visible cast and prop ownership. For a continuous join, states must match. For a deliberate location/time cut, describe what changes and why; review what still persists. Never use a cut to hide an unexplained duplicate prop or identity reset. Every adjacent pair needs an inspectable join.

## Voice and text

One full narrator lock per project: language/accent, timbre/register, pace, emotional range and recording treatment. Dialogue roles need a separately designed multi-speaker extension; this initial contract supports one narrator only. Keep exact spoken words audio-only in prompts. Place subtitles and exact technical text on a post-production track, not inside generated art. If generated voices drift, an authorized continuous external narration master can replace them; measure its actual cues and revisit timing.
