# Production brief

The film has exactly these three chapters, in this order, with these titles unchanged:

1. **Local smoothing and the Kakeya conjecture**
2. **The Exponential Time Hypothesis is false**
3. **Existence of quantum chromodynamics and completions of the Standard Model**

These are the user's original titles. They must appear verbatim in the film, storyboard, transcript, chapter timestamps and root README. Line breaks may wrap a title; the wording and capitalization stay unchanged. There is no replacement umbrella title.

## Content and visual direction

### 1. Local smoothing and the Kakeya conjecture

Center the announced proof of local smoothing in every spatial dimension and its claimed implications for the Kakeya and Stein restriction conjectures. Explain the contrast between concentration at one instant and a space-time estimate, unpack the local smoothing inequality, then explore the Kakeya statement through needle directions in 3D. The finite tube scene is illustrative; full Hausdorff dimension does not imply positive volume. Introduce the historical two-dimensional local smoothing and three-dimensional Kakeya results before explaining the new all-dimensional claim.

### 2. The Exponential Time Hypothesis is false

Center the reported refutation and its implications for conditional complexity results. Teach satisfiability through a checked Boolean example, explain ETH, and distinguish the released formalized running-time bound from the manuscript's sharper bound. Connect the asymptotic result to the research questions it reopens in algorithms. Subexponential time is not polynomial time; the announcement does not settle P versus NP or establish practical benchmark performance.

### 3. Existence of quantum chromodynamics and completions of the Standard Model

Give explicit treatment to both QCD existence and the announced unified completion containing the Standard Model gauge fields and fermions. Explain what constructing an interacting four-dimensional quantum field theory means, using a 3D spatial slice, gauge transport, correlation functions and a continuum-limit illustration. Pure Yang-Mills existence is an included subproblem. A positive mass gap is a separate question. Mathematical existence of a completion is not experimental confirmation, and the film must not invent an unspecified gauge group or an unpublished proof.

## Film design

- Complete, static, frontal explanation pages: no scrolling, perspective crawl or typewriter reveal.
- Every concept exploration uses a true Manim ThreeDScene, LaTeX, purposeful rotations, zooms and settled reading holds.
- Warm off-white 3D stage with charcoal, teal, coral and gold; readable full-screen prose between explorations.
- One substantial chapter per original discovery, with no four-minute cap. Initial pacing target: 9–12 minutes at 720p30.
- A written transcript and chapter timestamps let fast readers move ahead.
- Explanatory geometry supports the discoveries; it does not replace them with a general survey.

## Pipeline and execution

Use only the Math-To-Manim Astra pipeline and GPT-6 Astra for authoring and evidence audits, authenticated through cached Codex ChatGPT login. Orchestration and Manim rendering run on the local Windows workstation. No cloud execution job is requested. The optional TypeSafe reviewer is off; retained Astra audits must not be described as Jev approval.

The authoritative [production request](prompt.txt) contains the exact title contract, equations, source distinctions and shot requirements. The long-form renderer removes the duration ceiling, checks a complete video decode and samples frames throughout the film.

## Current status

The earlier renamed preview is superseded. The local production request, chapter text, preview source and launcher have been corrected to preserve the three original titles and center the stated discoveries.

Local Manim and LaTeX rendering work. The full Astra authoring run has encountered Windows access denial during Codex startup, before its first model response. A preview is not a completed Astra film. Publication of the final movie requires its real MP4, manifest, frame review and source evidence.

## Primary sources

- [OpenAI announcement](https://openai.com/index/building-scientific-understanding-with-academic-communities/).
- [Local smoothing: released Lean scope](https://github.com/openai/math/blob/main/lean/docs/079.md) and [manuscript](https://github.com/openai/math/blob/main/preprints/Local-smoothing-for-the-Euclidean-wave-equation-October-25-2026/paper.pdf).
- [ETH: released Lean scope](https://github.com/openai/math/blob/main/lean/docs/378.md) and [manuscript](https://github.com/openai/math/blob/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf).
- [Guth, Wang and Zhang](https://annals.math.princeton.edu/2020/192-2/p06); [Wang and Zahl](https://www.ias.edu/news/once-century-proof-settles-maths-kakeya-conjecture).
- [Clay Yang-Mills problem statement](https://www.claymath.org/wp-content/uploads/2022/06/yangmills.pdf).

Attribute newly announced results to their released work. This film does not independently verify the full proofs or Lean builds. The announcement describes the physics writeup as forthcoming from the collaboration.
