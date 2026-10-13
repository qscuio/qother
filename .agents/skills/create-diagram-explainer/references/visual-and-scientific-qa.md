# Visual and scientific checks

## Style and pacing

Use a quiet paper background, dark ink, and one focal accent plus a clearly different control/status accent. Reveal strokes progressively with stable geometry; frame-random jitter reads as flicker. Avoid presenting the finished slide and merely moving a cursor over it. A visible hand is outside this style.

Default to 16:9 720p at 24 fps when unspecified; these are starter settings, not restrictions. Leave a title zone, a central diagram zone, and a two-line caption zone. Show compact diagram labels rather than duplicating all narration. Reflow dense scenes instead of shrinking text until it becomes unreadable. The starter fails on overlong title, label, or caption text so the author can fix it.

One arrow means one relationship. Specify `data`, `control`, or `relation`; explain legends where needed. Choose meaningful action: enter a stage, wait in a queue, consume a resource, change a field, release a gate, or depart. Keep explanatory labels outside movement lanes. Avoid irrelevant zooms, constant bouncing, and loops implying repeated processing.

## Claim ledger before animation

For every substantive claim, keep a small task-local record: claim; supplied/primary source and section; scope/version; caveat; visual consequence. For an invented example explicitly say it is illustrative. Distinguish identity, destination, metadata, physical placement, and order of operations. Do not infer a universal architecture from one product's documentation.

For each causal step write an observable assertion such as “the release indicator becomes true before the item leaves waiting” or “the control arrow points from the worker back to the queue.” An apparent direction, extra copy, premature byte edit, or count is a scientific claim too.

## Review the actual artifact

- Check every scene's early, middle, and late frames, and boundary frames around gate/move/count changes.
- Trace a focal object across scenes. Confirm no accidental old-position copy or unexplained color/shape identity change.
- Confirm each statement has a contemporaneous visual focus; never omit the final spoken clause to hit an arbitrary duration.
- Check queue counts against arrivals/departures, including whether the focal object is counted. In the starter `count` includes the focal token when `inside_queue` is set, so background cells subtract it.
- Decode the final MP4, not only source images. Confirm video/audio streams, duration difference below a frame where practical, captions within safe areas, and no encoding failures.
- Inspect audio levels and clipping numerically, and listen to naturalness, acronym pronunciation, pauses, and sync. Report numeric checks, sampled-frame checks, and continuous audiovisual playback separately. Nonzero PCM energy alone cannot establish speech quality.

The starter validates declared gates and directions mechanically. It cannot establish whether a gate represents the real-world system, or whether a human will understand the explanation. That remains a content and viewing check.
