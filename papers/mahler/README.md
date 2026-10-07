# The Shape and Its Shadow

A three-minute 3D pilot explaining polarity, the cube's exact Mahler volume
product, reciprocal deformation and the manuscript's analytic proof route.
The original request, pinned manuscript and source distinctions are in
[source-context.md](source-context.md).

The retained [Astra scene](scene.py) and [renderable artifact](candidate.json)
are ready for a GitHub Actions cloud render. No completed movie is claimed yet.
The real Codex SDK / GPT-6 Astra chain was launched through MCP, with Jev off.

These are actual Manim execution stills from the corrected source:

![The cube, its polar octahedron and their volume product](../../docs/showcase/assets/mahler-cube.png)

![The tilted complex lens used in the manuscript's analytic input](../../docs/showcase/assets/mahler-lens.png)

The [curation record](curation.md) explains the geometry and timing repairs.
An [independent Astra source audit](production/curated-source-audit.json) found
no remaining blocking source defects. Its exact input hashes are retained
in [the audit record](production/curated-source-audit-record.json). Three
subsequent caption refinements identify n as the dimension, t as the imaginary
coordinate, and the cyan construction as the dual hull. These do not change
geometry or timing; the final render has its own source hash and review scope.

Run the retained source without model calls using the **Render a paper film**
workflow, selecting the `codex/mahler-render` branch and quality `m`. The cloud
machine uses Manim CE 0.19.0, LaTeX and FFmpeg; delivery is 1280×720 at 30 fps.
Its artifact includes the full MP4, sampled frames, source, logs and metadata.

The theorem and reported Lean formalization are attributed to the manuscript.
The film does not independently validate the all-dimensional proof. Stills and
source audits do not establish continuous-film quality. No Jev approval is claimed.
