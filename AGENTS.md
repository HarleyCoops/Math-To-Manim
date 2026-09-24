# Agent guide

Math-To-Manim's primary product is the Astra-native Codex SDK chain in `astra/`.
The user's September 24, 2026 direction supersedes the former multi-provider
homepage and requirement to preserve its featured GIF block. Keep the star
chart and older showcase files; feature new verified Astra films on the homepage.

## Architecture

- `astra/cli.py`: primary `math-to-manim`, `m2m`, `math-to-manim-astra` commands.
- `astra/pipeline.py`: brief -> mathematics -> storyboard -> scene -> render,
  with an independent jev gate at EVERY step and bounded backward repair.
- `astra/bridge.mjs`: official Codex SDK, GPT-6 Astra, cached ChatGPT login.
- `astra/prompts.py`: specialist and evaluator charters.
- `astra/rendering.py`: static source checks, local Manim and frame extraction.
- `docs/JEV.md`, `docs/ASTRA_PIPELINE.md`: evaluation and architecture contracts.
- `mythos/`, `sol/`, `grok/`, `glm/`, `mimo/`: compatibility pipelines, accessed
  by explicit provider commands; do not route Astra through their orchestration.

## Working rules

1. Use Codex login, never an API-key fallback, for the Astra chain. Remove API
   credentials from model and renderer child environments; never print secrets.
2. Authors and evidence auditors use `gpt-6-astra`. Real TypeSafe Jev uses
   `jev-1.13.0` through typesafe-sdk with TYPESAFE_API_KEY. Never substitute
   Astra for Jev or claim that Jev sees images; it receives text observations.
3. Keep failed attempts, review feedback and actual render evidence in
   `runs/astra/`. Do not claim success without a completed manifest and MP4.
4. Use `move_camera` and `set_camera_orientation` for ThreeDScene cameras.
5. Jev approval is scoped to evidence. Stills do not prove continuous motion.
6. Reject invalid evidence and exhausted budgets. Never bypass the gate to
   publish a render. Upstream repairs invalidate downstream work.
7. Local Manim execution is not an OS/container sandbox. Do not describe static
   source screening as a complete security boundary.
8. Test offline with `python -m pytest`. Live model/render runs need explicit
   task authorization; the current full-film request provides it.
9. Do not modify `archive/` or `legacy/`. Preserve other providers' implementation
   boundaries and their existing explicit commands.

## Verification

```bash
npm ci
pip install -e ".[dev,render]"
python -m pytest
math-to-manim doctor
math-to-manim run "Explain a new mathematical idea" -q h
```
