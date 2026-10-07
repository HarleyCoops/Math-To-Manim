# Math-To-Manim — Astra bundle pathway

This distribution runs **GPT-6 Astra through the official Codex SDK**. Astra
develops the learning brief, mathematics, storyboard and Manim scene, with an
independent Astra evidence audit at every checkpoint. The primary commands are
`math-to-manim`, `math-to-manim-astra` and `m2m`.

The bundle includes the Python wheel and source distribution, locked Codex
runtime manifests, the complete Quasi-Riemann film, its retained scene and
source audits, the cloud-render evidence, and SHA-256 checksums.

## Install from the bundle

Install Python 3.10+, Node.js 18+ and npm. Rendering also needs Manim's native
dependencies, FFmpeg and LaTeX; see the
[Manim installation guide](https://docs.manim.community/en/stable/installation.html).
After extracting the bundle, open a terminal in its directory:

```bash
python -m venv .venv
# Activate .venv using the command for your shell.
python -m pip install "./packages/math_to_manim-2.0.0-py3-none-any.whl[astra]"
math-to-manim setup
math-to-manim login
math-to-manim doctor --review-mode off
math-to-manim run "Explain a mathematical idea through 3D geometry" -q m --review-mode off
```

`setup` installs the pinned Codex SDK and CLI **0.156.1** in a user-writable
cache. Package installs work outside a repository checkout. The runtime uses
your cached Codex ChatGPT login; the Astra chain accepts no API-key fallback.
See the official [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk) and
[authentication](https://learn.chatgpt.com/docs/auth) documentation.

Runs and evidence are written under `runs/astra/` in your working directory.
At `-q m`, delivery is 1280×720 at 30 fps. The included film is silent, with
on-screen LaTeX and captions.

## Watch the included film

Open `films/quasi-riemann-720p.mp4`: **A Frontier for the Zeros**, 221.03
seconds at 720p/30 fps. Bone backgrounds, numerical zeta landscapes, phase
winding and reciprocal-L continuation geometry explain the September 30,
2026 manuscript's reported zero-free half-plane Re(s) > 7/8.

[Public film and render evidence](https://github.com/HarleyCoops/Math-To-Manim/releases/tag/quasi-riemann-film-2026-10-07)
and [original LaTeX manuscript](https://github.com/HarleyCoops/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/build/paper.tex).
The full Riemann hypothesis remains open in the source. The film illustrates
the manuscript's argument; this project has not independently verified its
complete proof or Lean artifacts.

`bundle.json` identifies the source revision and exact delivered movie.
`SHA256SUMS.txt` binds the included packages, scene evidence and media.

## Review choices

The default is **advisory Jev review**. To use it, configure `TYPESAFE_API_KEY`
in your environment or working directory's git-ignored `.env.local`.
TypeSafe SDK **0.7.2** calls **jev-1.13.0**; reviews do not trigger retries or
extra investigations. `--review-mode gated` opts into strict gates.

The installation example uses `--review-mode off`, which needs no TypeSafe
credential and keeps independent Astra audits. Such authoring is labeled
`astra_only`. The included cloud movie was rendered from saved source with
zero model calls and retains `not_reviewed` status. No Jev approval is claimed.

To render saved scene code, initialize a run directory containing
`manifest.json` with `{"events": []}`, then run:

```bash
math-to-manim render-existing runs/astra/my-render --candidate papers/quasi-riemann/candidate.json -q m
```

This command makes zero model/API calls and preserves existing review
records. Local Manim executes Python; static source checks are not an OS or
container sandbox. Use trusted scene sources.

The wheel retains the other providers' explicit commands, including
`math-to-manim-mythos` and `math-to-manim-sol`. Astra has its own orchestration;
see [the pipeline contract](https://github.com/HarleyCoops/Math-To-Manim/blob/main/docs/ASTRA_PIPELINE.md).
