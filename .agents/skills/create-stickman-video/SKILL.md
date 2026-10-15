---
name: create-stickman-video
description: Plan stick-figure animated explainers and narrative shorts, with consistent characters, timed physical action and provider-neutral video prompts. Use for 火柴人动画, stickman stories, or stickman-video-director style requests. This is a direction and prompt-package workflow, not a video renderer; visible-hand whiteboard and technical diagram animation remain separate skills.
---

# 火柴人动画导演

Turn the user's source into a coherent visual story, then a reproducible, provider-neutral prompt package. Preserve the requested language, voice, duration and factual scope. The bundled compiler is offline: it produces JSON prompts, not frames, speech or MP4.

## Choose and lock the direction

1. Resolve source, audience, format, duration, language, visual variant and delivery goal from the current task. Ask only for material unresolved choices; state harmless provisional assumptions. Do not silently translate Chinese narration into English or round durations to ten seconds. A provider's clip limits are constraints to negotiate or partition around, not permission to change total duration.
2. Read [direction.md](references/direction.md) for style selection, character anchors, physical beats, framing and continuity. Use a clear question → mechanism → consequence arc for explanation; setup → escalation → payoff for comedy; a meaningful choice and changed state for gentle stories. Do not manufacture a controversy, engagement question or guaranteed retention rate.
3. Preserve source claims and provenance. Label fictional analogy explicitly. A queue enacted by people can explain waiting but does not prove a hardware scheduling mechanism. Avoid extra spectacle that changes causal meaning.
4. Draft a storyboard using [project-contract.md](references/project-contract.md) and [queue-story.example.json](assets/queue-story.example.json). Freeze character identities separately from pose, location and prop ownership. Every beat must say what changes, who causes it, and when. Record cut semantics, rather than demanding identical locations across a story.
5. Present or internally review direction according to the task's existing proceed authority. Where explicit approval is required, wait for this version. Where the user delegated continuation, record `delegated-proceed` with the actual authorization reference and review evidence; never call it `user-approved`. Scope changes, spending and private uploads retain their own authorization requirements.

## Compile and hand off

Use Python 3.10+ standard library only. Set SKILL_DIR to this folder; keep working projects and outputs outside the installed skill.

```bash
python "$SKILL_DIR/scripts/stickman.py" validate project.json
python "$SKILL_DIR/scripts/stickman.py" compile project.json --out prompts.json
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s "$SKILL_DIR/scripts" -p 'test_*.py'
```

Validation reports a content digest. Only record that digest with truthful version-specific proceed evidence. Any storyboard/global change invalidates it; review affected meaning, framing, timing and continuity before refreshing authority. A hash checks version consistency, not whether approval or QA really happened.

The compiler repeats complete visible-character and narrator locks in every independent clip, with environment, composition, exact narration, timed actions, states and negatives. Do not replace them with “same character” or “as before.” Read [provider-and-qa.md](references/provider-and-qa.md) before actual generation: choose an available authorized provider, inspect its real capabilities, then map package fields without inventing an API integration.

For technical Chinese speech, use the repository's shared [pronunciation workflow](../../../pronunciation/README.md) from the repository root; preserve canonical words in script/subtitles and create a separate spoken layer. If installed alone, locate the existing helper explicitly. The prompt compiler itself does not run TTS or substitute pronunciation.

## Acceptance and delivery

Separate four outcomes: direction reviewed, prompt contract passed, footage inspected, audio/final edit accepted. No generated media means footage/audio QA is `not-run`. Actual footage requires checks at action peaks and joins, plus continuous playback/listening; repeated prompt text never proves identity or voice consistency. Subtitles and exact labels belong in post-production by default.

Deliver only what exists: a reviewed storyboard/prompt package now, or actual playable footage after a separately verified generation and assembly path. Report blockers and unperformed checks. Keep private narration/audio, character references, credentials and raw source documents out of public method commits.

Adaptation source, fixed revision and MIT notice: [provenance.md](references/provenance.md).
