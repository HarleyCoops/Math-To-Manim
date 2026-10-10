# How Close Can Fractions Get to Pi?

An episode of **OpenAI Mathematics in 3D**, built through Math-To-Manim's
Codex SDK / GPT-6 Astra pipeline from manuscript family 017.

The fraction 355/113 gets remarkably close to π. But one exceptional fraction
does not tell us how accurately fractions can approximate π infinitely often.
This film follows that distinction from magnified errors and logarithmic
plots into the manuscript's determinant argument, then into the surprising
spikes of the Flint–Hills series.

Bone backgrounds, teal geometry, coral approximations and a gold target keep
the representations connected. Camera moves follow the mathematics; readable
LaTeX and explanatory sentences earn each step.

## Film

Production is in progress. A completed movie, verified delivery metadata and
rendered preview will replace this status after rendering and inspection.

## What the source reports

OpenAI's September 24, 2026 manuscript reports that the irrationality exponent
of π is exactly 2. For every ε > 0, every fraction with sufficiently large
denominator satisfies

$$
\left|\pi-\frac pq\right|\ge q^{-2-\varepsilon}.
$$

The denominator threshold depends on ε and is ineffective in the paper.
This does not assert a uniform positive lower bound of the form c/q².
The film explains the reported contradiction between an arithmetic lower
bound and an analytic upper bound on one nonzero determinant. Its small
matrices, coefficient simplex and graphical bounds are labeled schematics.

The paper also reports convergence of

$$
\sum_{n=1}^{\infty}\frac{1}{n^3\sin^2 n},
$$

with angles in radians. The film connects the actual n = 355 spike to the
fraction 355/113, then explains why spacing controls the total contribution
of spikes in successively doubled ranges.

## Source and scope

[Read the source dossier](source-context.md) ·
[Inspect the pinned source hashes](provenance.json) ·
[See independently computed examples](computation.json)

The manuscript is pinned to OpenAI's public revision
`fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`.
The [retained LaTeX](source/main.tex) includes its complete sections and
bibliography, distributed under the [upstream Apache 2.0 license](source/LICENSE).

The [upstream Lean scope](source/lean-scope.md) covers the exponent-two
statement and explicitly excludes the Flint–Hills convergence consequence.
This production does not run Lean or independently verify the complete
research proof. Finite examples and plots illustrate the mathematics.
The film is an independent educational project.

## Reproduction

```bash
python scripts/compute_pi_episode.py
python scripts/drive_astra_mcp.py papers/pi-approximations --quality m --effort high --review-mode off --no-render
python scripts/export_paper_candidate.py papers/pi-approximations runs/astra/<run-id>
python scripts/render_pi_episode.py --candidate papers/pi-approximations/candidate.json --authoring-run runs/astra/<run-id> --output runs/astra/pi-delivery --quality m
```

The retained production brief records the initial source location used by
the authoring sessions. For reproduction, replace that location with your
checkout's `papers/pi-approximations/source/` directory. Authoring and
independent evidence audits use the cached Codex ChatGPT login. Jev is off
for this episode; no Jev approval is claimed. Rendering the saved candidate
uses zero model calls. The episode-specific delivery helper uses the existing
Math-To-Manim Manim worker and checks the longer reading budget explicitly.
The ordinary retained-scene command has a 240-second ceiling.

## Attribution

OpenAI, *The irrationality exponent of π is 2*, September 24, 2026.
[Pinned manuscript](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/The-irrationality-exponent-of-pi-is-2-September-24-2026/paper.pdf),
family 017 of the [October 6 mathematics release](https://openai.com/index/sharing-ai-progress-in-mathematics/).
The manuscript's supplied citation is retained in [source/README.md](source/README.md).
