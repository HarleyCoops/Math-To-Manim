# OpenAI Mathematics in 3D

A public film series built from the [OpenAI manuscript map](https://github.com/HarleyCoops/math).
Each episode turns one paper into a spatial explanation: actual 3D geometry,
camera motion and zooms, readable LaTeX, numerical examples, and an attributed
outline of the paper's argument.

The opportunity is to make a large mathematical release navigable through
its ideas. Each film earns one conclusion: what the question asks, what the
source reports, how the argument works, and what remains beyond its scope.
The films are an independent educational project. Publication here does
not certify the manuscripts or imply OpenAI sponsorship.

Production uses the existing **Codex SDK / GPT-6 Astra chain**. Real TypeSafe
Jev remains available through its separate API. This pilot explicitly disables
Jev and retains independent Astra evidence audits. Published films will link their source,
production records and actual render evidence; a source file or proposed
storyboard is not a finished episode.

| Episode | Paper | Status |
| --- | --- | --- |
| 01 · The Shape and Its Shadow | [Symmetric Mahler and its equality cases](mahler/source-context.md), family 087 | Source checked and production brief prepared; film pending |
| 02 · A Frontier for the Zeros | [The Quasi-Riemann hypothesis](quasi-riemann/README.md), family 003 | Current flagship; source checked and Astra authoring launched; film pending |

The Quasi-Riemann episode uses a bone background, deep teal numerical
surfaces, copper phase curves and gold frontier geometry. A camera journey
connects primes, the critical strip, winding around a sampled zero, and the
paper's reciprocal-L continuation argument. The target is 210-230 seconds
with a 1080p/60 fps delivery and a separate inspection copy.

## Curated next episodes

These are proposals from the map; detailed source checks and production
have not begun. The Quasi-Riemann film takes priority.

| Family | Subject | Spatial teaching opportunity |
| --- | --- | --- |
| 017 | The irrationality exponent of pi is 2 | Rational approximations as competing scales, zooms into error bounds, and the Flint-Hills series |
| 032 | Rational Hodge for CM abelian varieties | Cycles, intersections and cohomology as carefully labeled low-dimensional models |
| 167 | Planar distinct distances and unit-distance bounds | Lifted point configurations, distance shells and the manuscript's power saving |
| 347 | Counterexamples to stable-Morse and Arnold bounds | Critical points and Hamiltonian fixed points, with explicit limits on high-dimensional visualization |

All are source-reported claims. Each episode will pin its manuscript version
and keep the statement's hypotheses visible. Three-dimensional models of
higher-dimensional objects must identify what they represent.

The pilot begins with a cube and its polar octahedron, computes the exact
volume product, follows inverse-transpose duality, and reveals the manuscript's
analytic lens and integrated simplex-volume argument. Its all-dimensional
result is attributed to the manuscript. The film does not certify the Lean
formalization or independently prove the analytic input.

## Production workflow

Install the project and pinned SDK following the root README. The existing
Codex ChatGPT login supplies Astra access. Jev-off mode needs no TypeSafe key.
To enable advisory or gated Jev reviews later, save `TYPESAFE_API_KEY=...` in
the git-ignored `.env.local`. Never commit that file.

```bash
python scripts/drive_astra_mcp.py papers/mahler --quality m --review-mode off --no-render
python scripts/drive_astra_mcp.py papers/mahler --inspect <run-id>
python scripts/drive_astra_mcp.py papers/quasi-riemann --quality h --effort max --review-mode off --no-render
python scripts/export_paper_candidate.py papers/quasi-riemann runs/astra/<run-id>
```

This client uses the real MCP protocol. The new Astra MCP front door invokes
`astra.pipeline.Pipeline` without replacing its orchestration. The client keeps
the connection open while the worker records progress and SDK evidence under
`runs/astra/<run-id>/`. With `--no-render`, this phase produces scene code.
Its `astra_only` label describes Astra audits, never Jev approval.

The `Render a paper film` GitHub Actions workflow accepts a paper folder
and renders its retained `candidate.json`, with no model calls or API keys. It installs
FFmpeg alongside the pinned Manim image and saves the MP4, sampled frames,
contact sheet, source and logs as a 30-day artifact. That separate render is
`not_reviewed` until actual rendered evidence is inspected. Public media
publication remains pending; no finished episode is claimed here.

The export command checks the completed run's source bindings and retains
the exact scene plus its Astra audit record in `production.json`. It does
not turn completed authoring into a claim that a film has been rendered.

The `Quasi-Riemann preview and final film` workflow launches separate 480p
and 1080p cloud jobs from the same retained Astra source. Evidence lives in
`runs/astra/` within each artifact. Stills assess composition and readability;
continuous playback must assess motion. Only verified completed films will
be featured as finished episodes on the homepage.
