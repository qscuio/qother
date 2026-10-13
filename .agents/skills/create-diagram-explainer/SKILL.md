---
name: create-diagram-explainer
description: Create narrated dynamic diagram explainers with progressive original line drawings, meaningful flow/state animation, and audio-timed captions. Use for technical processes, system walkthroughs, queue/control flows, or the 流程图动态讲解 style. This style has no visible writing hand; do not substitute it when the user requests a realistic hand drawing on a whiteboard.
---

# 流程图动态讲解

Make the explanation and its changing diagram readable together on the same screen. This is a diagram-animation style, even when its strokes look hand-drawn. Do not call it realistic hand-drawing or add a decorative hand overlay.

## Choose the story and visual contract

- Establish the audience, central question, approximate duration, output format, language, and voice from the request or task context. About two minutes should follow one clear causal thread; scene count is flexible.
- Verify the new topic's claims against supplied material or appropriate primary sources. Record sources and teaching simplifications. No facts or constraints from a prior networking example apply automatically.
- Before rendering, define a stable identity for each focal object, the direction and meaning of each arrow, the state transitions, and the conditions that permit movement. Draw data flow and control flow distinctly. A label is not evidence that the underlying movement is correct.
- Let narration introduce objects, then reveal the relevant strokes and animate the causal change. Use real queue/count/state changes, not decorative particles. Preserve chronology, full script coverage, and one visible instance of each focal identity unless actual copying is explained.
- Read [visual-and-scientific-qa.md](references/visual-and-scientific-qa.md) for style, layout, and final review.

## Build from actual narration

1. Write the complete narration in short clauses and map each clause to its visible focus and event. Keep `narration` exactly equal to the concatenated caption clauses; put pronunciation substitutions in `spoken_text` only.
2. Generate or obtain one representative spoken clause with an available, authorized audio route, check it, then produce the rest. Preserve the requested voice. For continuations of the originating Mandarin project, its established adult male direction may be reused; it is not a default for other users or projects.
3. Measure the actual clause audio. Assemble the timeline from those sample counts before finalizing animation. A keyword positioned by a fraction of a clause is an estimate, not forced word alignment. Rebuild timing after any audio or narration change.
4. Keep captions near the active diagram without covering it. Every narrated clause needs visual support, including the closing conclusion. If audio cannot be produced, report the blocker or offer an explicitly labeled silent preview; never deliver it as a completed narrated video.

## Reusable implementation

Read [project-contract.md](references/project-contract.md) before adapting `assets/queue-example.json`. The example is an invented queue system, not a claim about real hardware. It exercises reveal, queue occupancy, gating, control arrows, movement, and persistent object identity without topic-specific renderer functions.

The starter uses Python 3.10+, Pillow, and FFmpeg/FFprobe. Check availability first; it does not install software, download models, or read credentials. Set `SKILL_DIR` to this installed skill folder and put working copies/output in the task workspace, not in the installed skill.

```bash
python "$SKILL_DIR/scripts/diagram.py" validate project.json
python "$SKILL_DIR/scripts/diagram.py" assemble project.json --out build
python "$SKILL_DIR/scripts/diagram.py" render build/timeline.json --out explainer.mp4
python "$SKILL_DIR/scripts/diagram.py" frames build/timeline.json --out qa
PYTHONDONTWRITEBYTECODE=1 python "$SKILL_DIR/scripts/test_diagram.py"
```

- `assemble` normally combines mono 16-bit PCM clause WAVs with 0.15 s lead/0.30 s tail per scene. If narration already has measured timing, add `--master existing.wav --timing timing.json` to preserve the master byte-for-byte, including padding and gaps. Both modes write a narration master, timeline, and SRT; see the contract for supplied timing.
- `render` creates 1280×720, 24 fps H.264/AAC by default, with progressive line reveal, a warm paper/ink/accent palette, caption wrapping, and one state model per object. Size, rate, font, colors, text, and graph are configurable.
- For layout-only work, `assemble --preview` creates an explicitly labeled silent timing preview. Render that timeline with `--preview`; it cannot pass as a narrated final.
- The renderer is a small adaptable base, not a universal illustration system. Extend primitives for a topic only when needed and retain the timing, identity, and causal checks.
- [audio-providers.md](references/audio-providers.md) covers provider-neutral inputs and the optional local Kokoro adapter. Use it only if that route is appropriate and its dependencies/model already exist or their setup is authorized.

## Verify and deliver

Run validation, inspect early/middle/late decoded frames plus frames around each causal gate, and watch/listen continuously when playback is available. Check direction, gate-before-action, queue counts, identity, all clauses, label safe areas, voice, and pronunciation. Programmatic checks do not prove natural speech or scientific truth.

Deliver the requested playable video and, when useful, narration/storyboard, SRT, timing, source, dependency versions, source citations, and concise QA results. State any unperformed checks. Do not include environments, caches, credentials, model weights, or unnecessary intermediates. Publishing to a third-party host or GitHub is a separate action requiring the appropriate user authorization; this skill does not publish automatically.

Originality and dependencies: [provenance.md](references/provenance.md).
