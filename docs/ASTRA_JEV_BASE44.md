# The Third Side: Astra, Jev, and the lesson deployment

This grade 8 lesson asks for the shortest straight route between opposite
corners **through the interior** of a rectangular box. It is not the shortest
route constrained to the surface.

A 3 × 4 floor gives a diagonal of 5. That diagonal and the perpendicular height
6 form another right triangle: L² = 25 + 36 = 61, so L = √61 ≈ 7.81.
The three-edge walk is 3 + 4 + 6 = 13. The theorem determines the straight
segment's length; the familiar fact that a straight segment is shortest in
Euclidean space supplies the shortest-path interpretation.

The active examples and curated gallery had no box-diagonal film when this
lesson was added. This is a new teaching treatment of a familiar theorem.

## Production chain

The `sol/` package keeps its existing CLI name for compatibility. Its default
model is now `gpt-6-astra`, with six roles: intent, cartographer, curriculum,
math director, cinematographer, and scene composer. The wrapper validates and
renders the scene. With `--evaluator jev`, a fresh Astra session independently
reviews the source and sampled frames. Rejected candidates return to the
appropriate production stages with evidence and feedback.

This implementation uses the Codex CLI and cached ChatGPT login. Install the
pinned compatible runtime with `npm ci`; the driver prefers the repository's
local executable. `M2M_SOL_CODEX` and `M2M_SOL_MODEL` remain explicit overrides.
The runtime is pinned to 0.156.1: the previously installed 0.146.0 was rejected
by the service for Astra. Resume places sandbox and directory options before
the `resume` subcommand, as required by the CLI. Cache hashes include the
actual writer model, preventing reuse of a different model's stage artifacts.

```bash
pip install -e ".[dev,render]"
npm ci
codex login
math-to-manim-sol run "Explain the diagonal of a 3 by 4 by 6 box with two right triangles for a grade 8 learner" --render -q h --evaluator jev --max-repairs 2
```

Each run retains its stage artifacts, model traces, Manim source, rendering
logs, sampled frames, and Jev attempts in `runs/sol/`. The public showcase
contains the curated scene and media; raw session traces remain local.
The [production record](showcase/the-third-side/production.json) includes the
final assessment and review-attempt history. The
[review contact sheet](showcase/the-third-side/review-contact-sheet.png)
shows sampled visual evidence.
See [Jev's design](JEV.md) for score definitions and limitations. This is a
revision loop at inference time, not an RL weight update.

## Base44 development setup

The merged Base44 onboarding PR provided a Docker Compose recipe, not a
hosted Base44 application. The updated recipe now serves this lesson:

```bash
docker compose -f docker-compose.base44.yml up --build
# http://localhost:3000/ and http://localhost:3000/health
```

Without Docker:

```bash
pip install -e ".[api]"
python -m uvicorn deployment.app:app --host 127.0.0.1 --port 3000
```

The presentation app serves curated files only. Live film generation remains
an operator CLI task, separate from the public web page and other provider
APIs. Existing `mythos.api` remains available through its own command.

## Static production deployment

The same HTML, CSS, JavaScript, and film assets build for GitHub Pages:

```bash
python scripts/build_lesson_site.py
python -m http.server 3000 --directory dist/lesson
```

The `Deploy geometry lesson` workflow uploads `dist/lesson` to GitHub Pages.
The static deployment's health document is `health.json`; the Python app uses
`/health`. Asset URLs are relative, so the page works both at `/` and under
the repository's `/Math-To-Manim/` prefix. The canvas uses local JavaScript
with no CDN dependency, supports keyboard-controlled dimension sliders, and
starts without automatic motion when reduced motion is requested.
