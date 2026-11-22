---
name: motion-repair
description: Stage 6 of the motion chain. Message to the scene coder session after a failed render or failed QA - fix exactly the listed failures, re-check with a draft, keep everything that passed.
model: inherit
---

REPAIR LOOP {loop} of {max_loops}.

The harness rendered your scene at full quality and checked it. Fix exactly
what is listed below. Everything not listed passed: do not change it unless a
fix requires it.

{failures}

Method: edit the file, render a draft with render_draft, extract the frames
that show each listed failure, Read them, and confirm the fix before you
stop. Then reply with a short note: what you changed for each failure, and
any you could not fix and why.
