# Three Frontiers: Waves, Computation, Matter

## Film brief

Create a substantial 9–12 minute educational film with one chapter for each
October 26, 2026 announcement. There is no four-minute ceiling. Use the
Math-To-Manim pipeline with GPT-6 Astra through Codex ChatGPT login.

**Latest design decision: static full-screen text, with no scrolling.**
Each chapter alternates complete, readable explanation pages with a real 3D
stage. Use rotations, zoom and LaTeX while exploring the concepts. Keep the
text pages frontal and still; show the complete paragraph immediately.
Provide chapter timestamps and a transcript for readers who prefer to move ahead.

The storyboard specialist also owns the writing: introduce a clear question,
define unfamiliar terms, explain the intuition, state the reported result, and
distinguish potential implications from established consequences. Allow generous
reading holds without a crawl or typewriter reveal.

| Chapter | Tour | Limits to explain |
| --- | --- | --- |
| The brief life of a wave's focus | Wave concentration, averaging across time, tubes in many directions, frequency-space geometry | A finite bundle illustrates Kakeya; full Hausdorff dimension does not imply positive volume. |
| Beyond the exponential wall | Boolean assignments, a worked satisfiability example, growth rates, the ETH refutation claim | Subexponential does not mean polynomial; P versus NP and practical speed remain separate questions. |
| A world built from fields | Gauge transport, a lattice spatial slice, continuum limits, QCD and Yang–Mills existence | Existence and a positive mass gap are distinct. Mathematical existence is not experimental confirmation of a completion. |

## Evidence and production status

The film illustrates newly announced research claims. It must not claim to
independently verify their full natural-language proofs or Lean developments.
The physics materials are not public in the announcement, so it must not invent
the unpublished construction.

The full production instructions, mathematical statements and source URLs are in
[prompt.txt](prompt.txt).

A six-panel Manim design collage has been rendered locally, pairing static text
pages with 3D concept views. The LaTeX renderer works using the existing TeX Live
installation. The full Astra authoring run is still blocked before its first
response by restricted Windows access during nested Codex startup. A design
preview is not a completed Astra film.

The local pipeline changes remove the duration ceiling and add full-video decode
validation and expanded frame sampling. Thirty-four focused tests pass, and a
245-second geometry-only test movie rendered and decoded. These code changes
have not been published as part of this brief.

## Primary sources

- [OpenAI announcement](https://openai.com/index/building-scientific-understanding-with-academic-communities/)
- [Local smoothing: Lean scope](https://github.com/openai/math/blob/main/lean/docs/079.md)
- [Local smoothing manuscript](https://github.com/openai/math/blob/main/preprints/Local-smoothing-for-the-Euclidean-wave-equation-October-25-2026/paper.pdf)
- [ETH: Lean scope](https://github.com/openai/math/blob/main/lean/docs/378.md)
- [ETH manuscript](https://github.com/openai/math/blob/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf)
- [Guth–Wang–Zhang](https://annals.math.princeton.edu/2020/192-2/p06)
- [Wang–Zahl](https://www.ias.edu/news/once-century-proof-settles-maths-kakeya-conjecture)
- [Clay Yang–Mills problem](https://www.claymath.org/wp-content/uploads/2022/06/yangmills.pdf)

The announcement and two Lean scope summaries were read for this request.
Complete proofs and Lean builds have not been independently checked here.
