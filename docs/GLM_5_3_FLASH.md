# GLM-5.3-Flash In This Repository

This note was written by **GLM-5.3-Flash** (Z.ai). Flash authored the root
[README](../README.md) rebuild and published it through the GitHub Contents
API on branch `main`.

**Update:** Flash now also lives here natively. There is a full `glm/`
package — a complete, independent GLM silo — and the `math-to-manim-glm`
(`m2m-glm`) executable.

What Flash built and maintains in this silo:

- `glm/client.py` — Z.ai Coding Plan chat/completions client for
  glm-5.3-flash. Thinking is always enabled; effort low/high/max tunes
  sampling latitude. Keys resolve from `ZHIPU_API_KEY`, `ZAI_API_KEY`, or
  OpenCode's `zai-coding-plan` entry, and are never printed.
- `glm/agents/*.md` — six stage charters (intent, cartographer, curriculum,
  math-director, cinematographer, composer).
- `glm/harness.py`, `service.py`, `cli.py` — the live chain
  intent → cartographer → curriculum → math-director → cinematographer →
  composer → verify → optional render, run ledger under `runs/glm/`, CLI.
- `glm/offline.py` — deterministic zero-network rehearsal whose scene class
  is `GlmOfflineStory` on a paper `#f3ecd8` stage; camera moves are
  restricted to `set_camera_orientation` / `move_camera`.
- `examples/glm/glm_flash_magnetic_monopole.py` — **The Lone Pole**, a ~68 s
  film proving four previously-unused Manim CE capabilities at once.

Architecture and deployment details: [GLM_5_3_SILO.md](GLM_5_3_SILO.md).

The older generation paths (Mythos, Sol, Grok) are untouched and separate.
`glm/` imports none of them.

— GLM-5.3-Flash
