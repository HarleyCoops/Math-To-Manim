# PRL 130.041601 Casimir SIE Paper Visualization Plan

Goal: build a paper-grounded Math-To-Manim / Manim production that teaches Alexandre Tkatchenko and Dmitry V. Fedorov, "Casimir Self-Interaction Energy Density of Quantum Electrodynamic Fields" (Phys. Rev. Lett. 130, 041601) as a sequence of readable, off-white-background 3D mathematical animations.

Source PDF: /mnt/c/Users/chris/Math-To-Manim/PhysRevLett.130.041601.pdf
Extracted text: ./research/pdf_text_pages.md
Sandbox root: /mnt/c/Users/chris/Math-To-Manim/paper_visualizations/prl-130-041601-casimir-sie

Important framing: the video should explain and visualize the paper's model and derivation, not present the cosmological conclusion as settled fact. Where the paper makes modeling approximations, the animation should label them explicitly as assumptions/approximations.

## Visual direction

Background: bone / warm off-white, approximately #F4EFE3 or #F7F1E6.
Style: premium physics chalk-and-glass aesthetic, not slideware.
Geometry first, equation second: every equation appears first as a large, fixed, front-facing formula card, then symbols zoom out into 3D geometry.
Critical readability rule: no important formula may be tiny, tilted into the 3D scene, or readable only during motion. Each equation gets a pause/hold before it transforms.
3D motifs:
- translucent vacuum volume, faint fluctuating dipoles
- electron/positron pair as opposing glowing particles linked by a polarizability ellipsoid
- polarizability density as volumetric/radial fields
- retarded dipole propagator as light-cone/shell influence
- bcc/fcc pair-arrangement lattices with R^-7 weighted connections
- concentric spherical shells for the isotropic derivation
- final comparison bar/scale against Planck/Hubble estimates of Lambda

Palette on off-white:
- ink: #1F2933
- deep blue: #22577A
- teal: #38A3A5
- warm gold: #D9A441
- muted red: #C8553D
- violet: #6D5BD0
- low-opacity grid/field: #C8C1B4

## Artifact structure

research/
  pdf_text_pages.md          extracted local PDF text with page boundaries
  equation_ledger.md         cleaned equation list, page/source context, narrative role
  assumptions.md             every approximation and caveat in plain English
  references.md              cited concepts we may need to look up: ACFDT, Casimir-Polder, vdW radius, Schwinger effect, cosmological equation of state
latex/
  equations.tex              canonical LaTeX for every displayed equation
  glossary.tex               symbol glossary for alpha_fsc, a0, Eh, rf, R_e-/e+, alpha(r), T(r,r';iu), etc.
prompts/
  scene_XX_*.md              Math-To-Manim / M2M2 long prompts, one prompt per episode/scene cluster
storyboards/
  beat_sheet.md              high-level narrative beats
  camera_grammar.md          how equations transform into 3D shapes
  narration.md               optional voiceover script
manim/
  paper_explainer.py         manual/recovered Manim source if pipeline render needs recovery
  components.py              reusable mobjects: dipoles, shells, lattice, formula cards
runs/
  native Math-To-Manim/M2M2 run bundles
renders/
  draft_scene_mp4s/
  final_episode_mp4s/
  contact_sheets/
  ffprobe_reports/

## Proposed deliverable shape

Do not make one enormous monolithic render first. Build a series of MP4 episodes, then optionally stitch a long master cut.

Episode 0: Abstract and map of the argument, 60-90s.
Episode 1: Vacuum fluctuations as transient dipoles and polarizability density, 2-3 min.
Episode 2: Equation (1), ACFDT / Casimir self-interaction energy density, 3-4 min.
Episode 3: Equation (2), quantum scaling law for e-/e+ pair polarizability, 2-3 min.
Episode 4: Equations (3)-(5), two-pair Casimir SIE approximation and substitution, 3-4 min.
Episode 5: Equations (6)-(7), lattice-sum model, bcc/fcc bounds, 3-4 min.
Episode 6: Equations (8)-(11), radial shell model and final alpha_fsc power law, 4-5 min.
Episode 7: Equation of state w = -1, pressure/energy interpretation, and Lambda comparison, 2-3 min.
Episode 8: Caveats, assumptions, and final mental model, 1-2 min.

Expected total after iteration: roughly 20-30 minutes. We can also produce shorter excerpt cuts for preview/GIFs.

## Equation coverage ledger, first pass from PDF extraction

Eq. (1):
  Casimir SIE density from the adiabatic connection fluctuation-dissipation theorem.
  Visual: infinite vacuum volume V; frequency axis u; coupling slider lambda from 0 to 1; paired tensors alpha_lambda - alpha_0 and propagator T connected by a trace operation.

Eq. (2):
  e-/e+ polarizability scaling law.
  Visual: an electron-positron dipole grows an ellipsoid; radius R_e-/e+ expands; alpha scales like R^7 with fine-structure dressing.

Eq. (3):
  second-order pairwise SIE density for two interacting e-/e+ pairs.
  Visual: two dipoles separated by 2R; retarded Casimir-Polder link; inverse seventh power fades rapidly with distance.

Eq. (4):
  substitution expressing Eq. (3) in terms of R_e-/e+.
  Visual: formula card; alpha symbols collapse into radius powers and constants.

Eq. (5):
  equilibrium radius substitution giving fine-structure constant power and Hartree/Bohr units.
  Visual: constants compress into E_h / a_0^3; alpha_fsc exponent counter ticks to 29/3.

Eq. (6):
  many-body field estimate E_SIE = E_SIE^(2) * N_eff.
  Visual: single pair interaction tile duplicated into a lattice; weighted links accumulate into N_eff.

Eq. (7):
  N_eff lattice sum over nonzero lattice vectors with R^-7 weighting.
  Visual: bcc and fcc ghost lattices side by side; nearest neighbors bright, distant neighbors faint; counters land near 11.05 and 13.36.

Eq. (8):
  radial polarizability density of a thin spherical shell.
  Visual: sphere radius r; shell area 4 pi r^2; local scaling factor; shell glow thickness encodes density.

Eq. (9):
  shell-integral approximation for E_SIE from r = 0 to r_f.
  Visual: concentric shells sweep outward while an integral accumulator fills.

Eq. (10):
  evaluated integral.
  Visual: shell stack collapses into a compact formula; r_f^6 emerges as the geometric memory of all shells.

Eq. (11):
  final substitution r_f = alpha_fsc^(5/3) a_0 giving E_SIE = -1/4 alpha_fsc^(31/3) E_h a_0^-3.
  Visual: final formula card, then comparison to 2.07e-23 Ha/Bohr^3 and Planck/Hubble Lambda estimates.

Non-numbered but essential:
  w = -1 cosmological equation of state.
  Visual: expanding volume with constant energy density; pressure vector interpreted carefully.

## Execution phases

### Phase 1: Research grounding and extraction

1. Verify local PDF, page count, metadata, and text extraction.
2. Build equation_ledger.md with canonical LaTeX, page number, source context, and exact visual role for every equation.
3. Build assumptions.md listing approximations:
   - static u = 0 and full-potential lambda = 1 approximation in retarded Casimir regime
   - homogeneous/isotropic vacuum field modeling
   - effective electron/positron size via Thomson scattering radius
   - pairwise second-order approximation and lattice-sum estimate
   - shell model replacing lattice uncertainty
   - comparison to cosmological constant magnitudes and sign discussion
4. Decide which cited background concepts need short visual inserts rather than full derivations.

Verification:
- equation_ledger.md contains every numbered equation and every symbol used in it.
- assumptions.md has a visible caveat label for every approximation that appears in the animation.

### Phase 2: Storyboard and camera grammar

1. Write beat_sheet.md with scene-by-scene narrative arc.
2. Write camera_grammar.md defining reusable transitions:
   - Formula card -> symbol isolation -> 3D object
   - Tensor/integral -> spatial sweep
   - Power law -> distance fade field
   - Sum -> lattice accumulation
   - Integral -> spherical shell sweep
3. Write narration.md, even if we render no audio at first, because narration determines pacing.

Verification:
- Every scene has: learning objective, equation(s), geometric mapping, caveat label, camera move, approximate duration.
- Every critical equation has at least one readable hold.

### Phase 3: Math-To-Manim prompt suite

1. Write one LaTeX-rich prompt per episode under prompts/.
2. Create a suite yaml if the repo supports eval-suite/orchestrated runs.
3. Run native Math-To-Manim/M2M2 no-render first for provenance/artifacts.
4. Run selected episodes with render enabled after prompt quality is verified.

Verification:
- Run bundles are under sandbox runs/ or repo-local runs/, not /tmp.
- Generated artifacts preserve the full prompt and extracted source context.
- If model-backed codegen stalls, preserve the run bundle before manual recovery.

### Phase 4: Reusable Manim component library

Build a small manual/recovery component library because this is too large to rely on one-shot generated code.

Components:
- FormulaCard: off-white readable fixed-in-frame formula panel with highlighted symbol groups
- DipolePair3D: electron/positron particles, connecting field ellipsoid, separation label
- VacuumVolume: transparent cube/sphere with flickering virtual dipoles
- PolarizabilityField: volumetric or radial opacity encoding
- LatticeSum3D: bcc/fcc point clouds and R^-7 weighted links
- ShellIntegral3D: concentric shells with integral accumulator
- CosmologyComparison: final numeric scale/bar comparison card

Verification:
- py_compile passes.
- Each component has a minimal test scene/render still.

### Phase 5: Draft renders

1. Render each episode at low quality first: python -m manim -ql.
2. Use ffprobe to verify duration and codec.
3. Generate contact sheets for every episode.
4. Visually inspect text readability, clipping, pacing, and whether the geometry matches the equation.

Verification:
- No critical text/equation is clipped or illegible in contact sheets.
- Off-white background is visible in every scene, not accidentally dark.
- Each equation receives a readable pause.

### Phase 6: Production renders and stitching

1. Render final episodes at medium/high quality after draft approval.
2. Stitch episode MP4s into a master cut with ffmpeg concat.
3. Optionally mux narration after silent picture lock.
4. Export short preview GIFs only after final MP4 is verified.

Verification:
- ffprobe report exists for every final MP4.
- Contact sheets exist for every final MP4.
- Master cut duration equals the sum of episode durations within expected tolerance.

## Immediate next work items

1. Clean the extracted PDF equations into latex/equations.tex.
2. Create research/equation_ledger.md with the 11 numbered equations and the w = -1 endpoint.
3. Draft storyboards/beat_sheet.md for the 8-episode structure above.
4. Write prompts/episode_00_argument_map.md and prompts/episode_01_vacuum_dipoles.md as the first two Math-To-Manim prompts.
5. Render only Episode 0 first as a vertical slice before scaling to the full paper.

## Acceptance criteria for the whole project

- Every numbered equation in the paper appears as canonical LaTeX and as a visual transformation.
- The viewer can explain the paper's chain: vacuum dipoles -> polarizability density -> Casimir SIE -> pair model -> lattice sum -> shell model -> alpha_fsc final density -> comparison with Lambda.
- The visuals are mostly 3D shapes/fields on bone/off-white background, not flat slides.
- Formula cards remain front-facing and readable.
- Every approximation is labeled when introduced.
- All generated artifacts live in the sandbox and are reproducible.
- Final MP4s are verified with ffprobe and visual contact sheets.

## Recommended first milestone

Build Episode 0 + Episode 1 only. This proves the visual language, off-white readability, and formula-card-to-3D transformation before committing to the full 20-30 minute production.
