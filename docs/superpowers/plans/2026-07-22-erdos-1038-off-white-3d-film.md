# Erdős 1038 Off-White 3D Sol Film Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a verified true-3D archival off-white film explaining the proposed solution to Erdős Problem 1038 through the GPT-5.6 Sol Codex CLI pipeline, then feature a curated GIF in the root README.

**Architecture:** Save one self-contained source prompt and pass it to the independent `math-to-manim-sol` CLI. Sol performs the complete long-horizon reasoning, Manim authoring, rendering, frame inspection, and bounded Codex repair inside `runs/sol/`; repository-side work verifies the artifact bundle and packages only the accepted GIF and README feature.

**Tech Stack:** GPT-5.6 Sol, Codex CLI cached ChatGPT login, `sol/`, Python 3.10+, pytest, Manim CE 0.19+, LaTeX, FFmpeg/ffprobe, Markdown.

## Global Constraints

- Use `math-to-manim-sol` and `runs/sol/` only; never route through Mythos.
- Do not modify or import `mythos/` prompts, agents, backends, orchestration, or GIF helpers.
- Do not add a Sol MCP, HTTP API, Responses API client, or API-key fallback.
- Source mathematics is `runs/user-clones/erdos/1038/paper.tex` and `numerical_verifier.py`.
- Every frame uses archival off-white near `#f3ecd8` and dark sepia near `#241a12`.
- No starfield, stars, cosmic void, nebula, black background, or dark fallback frame.
- The scene must be visibly true 3D; `ThreeDScene` inheritance alone is insufficient.
- Use `move_camera()` / `set_camera_orientation()` only; never `.animate` on `self.camera`.
- Every displayed equation uses complete valid LaTeX.
- Preserve the root README star chart and all existing showcase entries.
- Keep transient Sol run artifacts and scratch media out of commits.

---

## File Structure

- `docs/prompts/erdos-1038-off-white-3d.md`: exact UTF-8 prompt consumed by the Sol CLI.
- `tests/test_erdos_1038_prompt.py`: static regression test for provider, mathematics, palette, 3D, and camera requirements.
- `runs/sol/<run-id>/`: Sol-owned reasoning, code, review, render, and repair ledger; never committed.
- `docs/showcase/assets/erdos-1038-potential-landscape.gif`: curated README media.
- `README.md`: root-page feature block.

### Task 1: Add the Sol-Native Source Prompt

**Files:**
- Create: `docs/prompts/erdos-1038-off-white-3d.md`
- Create: `tests/test_erdos_1038_prompt.py`

**Interfaces:**
- Consumes: Erdős 1038 theorem and proof spine.
- Produces: one prompt string accepted as `RunRequest.prompt` by the Sol CLI.

- [ ] **Step 1: Write the failing prompt-contract test**

Create `tests/test_erdos_1038_prompt.py`:

```python
from pathlib import Path


PROMPT = Path("docs/prompts/erdos-1038-off-white-3d.md")


def test_erdos_1038_prompt_targets_sol_and_has_all_hard_contracts():
    text = PROMPT.read_text(encoding="utf-8")

    required = (
        "GPT-5.6 Sol",
        "Erdős Problem 1038",
        r"V_{\mu_f}(x)",
        r"E_{\widetilde\mu}\subseteq E_\mu",
        r"\Lambda(q)",
        "1.834430475762661",
        r"2\sqrt{2}",
        r"(x^2-1)^m",
        "#f3ecd8",
        "#241a12",
        "ThreeDScene",
        "true 3D",
        "move_camera()",
        "complete valid LaTeX",
        "Do not use a starfield",
        "outward interval arithmetic",
        "not attained",
    )
    for item in required:
        assert item in text, item

    assert "Mythos" not in text
    assert "math-to-manim " not in text
```

- [ ] **Step 2: Run the test and confirm the missing-file failure**

Run:

```powershell
& .\.venv\Scripts\pytest.exe tests\test_erdos_1038_prompt.py -q
```

Expected: FAIL with `FileNotFoundError`.

- [ ] **Step 3: Create the complete Sol production prompt**

Create `docs/prompts/erdos-1038-off-white-3d.md` with this exact content:

```markdown
# ERDŐS 1038 — THE POTENTIAL LANDSCAPE

Use the complete GPT-5.6 Sol film pipeline to create a gorgeous,
mathematically faithful explanation of the proposed complete solution to
Erdős Problem 1038.

The problem. Let \(f\) range over all nonconstant monic real polynomials
whose roots, counted with multiplicity, lie in \([-1,1]\):
\[
f(x)=\prod_{j=1}^{n}(x-r_j),\qquad r_j\in[-1,1].
\]
Determine the infimum and supremum of
\[
E_f=\{x\in\mathbb R:|f(x)|<1\},\qquad |E_f|.
\]

The answer the film must earn is
\[
\inf_f |E_f|=L=1.834430475762661\ldots,
\qquad
\sup_f |E_f|=2\sqrt{2}.
\]
The lower value is not attained by any finite polynomial. It is the exact
number \(L=\Lambda(q_*)\), where \(q_*\) is the unique certified minimizer
described below. The upper value is attained exactly by
\[
f(x)=(x^2-1)^m,\qquad m\ge1.
\]

Use the proof's actual potential-theoretic spine. Introduce
\[
\mu_f=\frac1n\sum_{j=1}^{n}\delta_{r_j}
\]
and transform the polynomial into
\[
V_{\mu_f}(x)
=\int\log|x-t|\,d\mu_f(t)
=\frac1n\log|f(x)|.
\]
Therefore
\[
E_f=\{x:V_{\mu_f}(x)<0\}.
\]
Make this the central visual mechanism: roots become physical sources,
\(V_{\mu_f}\) becomes a sculpted 3D landscape, level \(0\) becomes a
translucent plane, and the footprint below it is exactly \(E_f\).

Visualize simultaneous component atomization. Root mass in each sublevel
component collapses to its barycentre. The potential outside rises, so the
negative region cannot grow:
\[
E_{\widetilde\mu}\subseteq E_\mu.
\]
Show an actual geometric before-and-after transformation.

Morph the finite atoms into the one-cut limiting measure
\[
\mu_q=A(q)\delta_{-1}+
\frac{t+1-2A(q)s(q)}
{\pi(t+1)\sqrt{(t-a(q))(1-t)}}
\mathbf 1_{(a(q),1)}\,dt,
\]
where
\[
H(q)=\frac{2q}{(1+q)^2},\qquad
s(q)=\frac{1-q}{1+q},\qquad
A(q)=\frac{\log H(q)}{\log q}.
\]
Give the endpoint atom and continuous density different but coherent 3D
forms.

Build
\[
\Lambda(q)=H(q)\left(
u_-(q)+u_-(q)^{-1}
-u_+(q)-u_+(q)^{-1}
\right)
\]
as a physical raised curve or valley. Travel along it and isolate
\[
0.025715536866527<q_*<0.025715536866528
\]
before revealing
\[
1.834430475762661<L<1.834430475762662.
\]
Explain that global comparison, circle rearrangement, and uniform parameter
certificates prove no finite root configuration can do better. The enclosure
is certified by directed outward interval arithmetic, not a sampled graph.
Do not imply that the scalar plot alone proves global optimality.

For the opposite extreme, transform the scene into equal endpoint masses at
\(-1\) and \(1\). Show that
\[
f(x)=(x^2-1)^m
\]
reduces the condition to
\[
|x^2-1|<1
\]
and gives width \(2\sqrt{2}\). Contrast the attained maximum with the
unattained lower limit in the final tableau.

Beat plan:

1. "The question has a shape." Introduce roots and \(E_f\).
2. "A polynomial becomes terrain." Reveal the potential, zero plane, and
   below-zero footprint.
3. "Collapse without expansion." Animate atomization and
   \(E_{\widetilde\mu}\subseteq E_\mu\).
4. "The limiting one-cut shape." Morph atoms into endpoint mass plus density.
5. "The certified floor." Travel along \(\Lambda(q)\), mark \(q_*\), reveal
   \(L\), state non-attainment, and name the certificate boundary.
6. "The opposite extreme." Expand to the endpoint-root maximizer and finish
   with both extremal values.

Hard production contract:

- Produce one self-contained Manim `ThreeDScene`, 60–90 seconds.
- It must read as true 3D. Class inheritance alone does not count. Use
  meaningful depth, raised root pillars or wells, a genuine potential surface
  or extruded ribbon, a translucent zero plane, a sculpted one-cut density,
  and a raised \(\Lambda(q)\) valley.
- Use at least four perspective-changing calls to `move_camera()` or
  `set_camera_orientation()` so parallax is unmistakable. Never call
  `.animate` on `self.camera`.
- Set every frame to archival off-white near `#f3ecd8`. Use dark sepia
  `#241a12` for text and axes, with muted oxide red, verdigris, indigo, and
  old gold accents.
- Do not use a starfield, stars, black background, cosmic void, nebula, or
  deep-space motif. Do not flash through a dark fallback between scenes.
- All displayed mathematics must use complete valid LaTeX. Build important
  formulas from addressable `MathTex` parts.
- Headline before symbols. Zoom into the active term or 3D object, then pull
  back to restore context and create whitespace.
- Keep at most one headline or two short text blocks visible. Replace
  captions; never stack them.
- Geometry must carry the argument; do not place paragraphs on screen.
- Keep labels readable at a 720-pixel-wide README size.
- End on a strong off-white 3D master frame containing the potential
  landscape, certified lower value, and endpoint-root maximum.

Render and inspect the film. Record frame/contact-sheet evidence and any
repairs in `review.json`. The result is acceptable only when:

- the background remains off-white throughout with no stars or dark flashes;
- perspective, depth, and parallax make the film unmistakably 3D;
- the zero plane and potential surface make \(E_f\) geometrically legible;
- atomization, \(\Lambda(q)\), the certified enclosure, non-attainment,
  \(2\sqrt{2}\), and \((x^2-1)^m\) appear accurately;
- every formula fits with complete LaTeX;
- camera pull-backs create whitespace;
- the final frame works as a README showcase image.
```

- [ ] **Step 4: Run the prompt-contract test**

Run:

```powershell
& .\.venv\Scripts\pytest.exe tests\test_erdos_1038_prompt.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit the prompt**

```powershell
git add docs/prompts/erdos-1038-off-white-3d.md tests/test_erdos_1038_prompt.py
git commit -m "docs: add Sol prompt for Erdős 1038"
```

### Task 2: Verify the Sol Silo and Rehearse Offline

**Files:**
- Read: `sol/`, `docs/SOL_5_6_SILO.md`
- Generate, do not commit: `runs/sol/<offline-run-id>/`

**Interfaces:**
- Consumes: installed Sol CLI and exact prompt.
- Produces: a schema-valid offline Sol bundle and authenticated Codex runtime.

- [ ] **Step 1: Run the Sol-specific tests**

Run:

```powershell
& .\.venv\Scripts\pytest.exe tests\test_sol_silo.py tests\test_erdos_1038_prompt.py -q
```

Expected: exit code 0.

- [ ] **Step 2: Rehearse the exact prompt through Sol**

Run:

```powershell
$prompt = Get-Content -Raw docs\prompts\erdos-1038-off-white-3d.md
& .\.venv\Scripts\math-to-manim-sol.exe run $prompt --offline
```

Expected: exit code 0 and a new `runs/sol/` directory containing
`request.json`, `CONTRACT.md`, `01_intent.json` through
`06_scene_spec.json`, `sol_scene.py`, `review.json`, and `manifest.json`.

- [ ] **Step 3: Validate the newest offline ledger**

Run:

```powershell
$run = Get-ChildItem runs\sol -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
$manifest = Get-Content -Raw (Join-Path $run.FullName "manifest.json") |
  ConvertFrom-Json
if ($manifest.status -ne "completed") { throw $manifest.error }
if ($manifest.backend -ne "codex-cli") { throw "Wrong backend" }
if (-not $manifest.offline) { throw "Expected offline rehearsal" }
Get-ChildItem $run.FullName -File | Select-Object Name,Length
```

Expected: completed Codex CLI backend, offline true, and every required
artifact present.

- [ ] **Step 4: Preflight Codex and rendering dependencies**

Run:

```powershell
& .\.venv\Scripts\math-to-manim-sol.exe doctor
& .\.venv\Scripts\manim.exe --version
& ffmpeg -version
& latex --version
```

Expected: Sol reports a ready cached ChatGPT login for model `gpt-5.6-sol`;
Manim, FFmpeg, and LaTeX return version information.

### Task 3: Run the Complete Codex-Native Production

**Files:**
- Generate, do not commit: `runs/sol/<real-run-id>/`

**Interfaces:**
- Consumes: exact source prompt, Codex CLI login, and Sol film contract.
- Produces: complete reasoning artifacts, one validated `sol_scene.py`,
  `review.json`, manifest, logs, frame evidence, and a low-quality MP4.

- [ ] **Step 1: Run Sol with render and bounded repair**

Run:

```powershell
$prompt = Get-Content -Raw docs\prompts\erdos-1038-off-white-3d.md
& .\.venv\Scripts\math-to-manim-sol.exe run $prompt `
  --render -q l --reasoning-effort high --max-repairs 3
```

Expected: exit code 0. Sol runs `codex exec --model gpt-5.6-sol`, renders,
inspects evidence, repairs validation failures up to three times, and prints
a completed manifest.

- [ ] **Step 2: Verify provider provenance and final status**

Run:

```powershell
$run = Get-ChildItem runs\sol -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
$manifest = Get-Content -Raw (Join-Path $run.FullName "manifest.json") |
  ConvertFrom-Json
$request = Get-Content -Raw (Join-Path $run.FullName "request.json") |
  ConvertFrom-Json
$sourcePrompt = Get-Content -Raw docs\prompts\erdos-1038-off-white-3d.md
if ($manifest.status -ne "completed") { throw $manifest.error }
if ($manifest.backend -ne "codex-cli") { throw "Wrong backend" }
if ($manifest.model -ne "gpt-5.6-sol") { throw "Wrong model" }
if ($request.prompt -ne $sourcePrompt) { throw "Prompt mismatch" }
if (-not $manifest.render_requested) { throw "Render not requested" }
$manifest | Format-List
```

Expected: completed, `codex-cli`, `gpt-5.6-sol`, exact prompt match, and a
nonempty relative `video_path`.

- [ ] **Step 3: Confirm the complete artifact contract**

Run:

```powershell
$run = Get-ChildItem runs\sol -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
$required = @(
  "01_intent.json",
  "02_knowledge_map.json",
  "03_curriculum.json",
  "04_math_dossier.json",
  "05_shot_list.json",
  "06_scene_spec.json",
  "sol_scene.py",
  "review.json",
  "manifest.json"
)
foreach ($name in $required) {
  $path = Join-Path $run.FullName $name
  if (-not (Test-Path $path)) { throw "Missing $name" }
}
Get-ChildItem $run.FullName -File | Select-Object Name,Length
```

Expected: no missing artifact.

### Task 4: Audit Code, Mathematics, and Media

**Files:**
- Read: selected `runs/sol/<real-run-id>/` bundle
- Generate, do not commit: contact sheet and three representative JPEGs

**Interfaces:**
- Consumes: completed Sol run.
- Produces: evidence that the film meets all hard requirements or a concrete
  defect list for one bounded repair.

- [ ] **Step 1: Compile and statically inspect `sol_scene.py`**

Run:

```powershell
$run = Get-ChildItem runs\sol -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
$scene = Join-Path $run.FullName "sol_scene.py"
& .\.venv\Scripts\python.exe -B -m py_compile $scene
$code = Get-Content -Raw $scene
if ($code -notmatch 'class\s+\w+\s*\(\s*ThreeDScene\s*\)') {
  throw "Scene is not ThreeDScene"
}
if ($code -notmatch '#f3ecd8') { throw "Missing off-white background" }
if ($code -match 'starfield|#0c0c0b|background_color\s*=\s*BLACK') {
  throw "Forbidden dark/starfield motif"
}
if (($code | Select-String -Pattern 'move_camera|set_camera_orientation' -AllMatches).Matches.Count -lt 4) {
  throw "Insufficient perspective camera choreography"
}
if ($code -match 'self\.camera\.animate') { throw "Forbidden camera animation" }
```

Expected: compilation and all static checks pass.

- [ ] **Step 2: Audit the mathematical artifacts**

Read `04_math_dossier.json`, `05_shot_list.json`, `06_scene_spec.json`, and
`review.json`. Confirm these exact mathematical obligations are present:

```text
V_{\mu_f}(x) = (1/n)\log|f(x)|
E_{\widetilde\mu} \subseteq E_\mu
\Lambda(q)
1.834430475762661...
directed outward interval arithmetic
infimum not attained
2\sqrt{2}
(x^2-1)^m
```

Expected: all eight are represented accurately and `review.json` records
render/frame inspection rather than only Python compilation.

- [ ] **Step 3: Verify MP4 metadata**

Run:

```powershell
$run = Get-ChildItem runs\sol -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
$manifest = Get-Content -Raw (Join-Path $run.FullName "manifest.json") |
  ConvertFrom-Json
$mp4 = Join-Path $run.FullName $manifest.video_path
if (-not (Test-Path $mp4)) { throw "Manifest video missing" }
& ffprobe -v error `
  -show_entries format=duration,size `
  -show_entries stream=width,height,r_frame_rate `
  -of json $mp4
```

Expected: nonzero duration and size, landscape dimensions, and a readable
frame rate.

- [ ] **Step 4: Extract a contact sheet and representative frames**

Run:

```powershell
$run = Get-ChildItem runs\sol -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
$manifest = Get-Content -Raw (Join-Path $run.FullName "manifest.json") |
  ConvertFrom-Json
$mp4 = Join-Path $run.FullName $manifest.video_path
$sheet = Join-Path $run.FullName "contact-sheet.jpg"
& ffmpeg -y -i $mp4 `
  -vf "fps=1/7,scale=480:-1,tile=4x3:padding=8:margin=8" `
  -frames:v 1 $sheet
$duration = [double](& ffprobe -v error -show_entries format=duration `
  -of default=noprint_wrappers=1:nokey=1 $mp4)
$middle = [math]::Round($duration / 2, 2)
& ffmpeg -y -ss 1 -i $mp4 -frames:v 1 (Join-Path $run.FullName "frame-first.jpg")
& ffmpeg -y -ss $middle -i $mp4 -frames:v 1 (Join-Path $run.FullName "frame-middle.jpg")
& ffmpeg -y -sseof -1 -i $mp4 -frames:v 1 (Join-Path $run.FullName "frame-final.jpg")
```

Expected: one contact sheet and three JPEG frames.

- [ ] **Step 5: Apply the visual acceptance checklist**

View all four images. The film passes only if every statement is true:

```text
[ ] Every sampled frame is warm off-white; no frame flashes black.
[ ] No stars, starfield, cosmic void, or nebula appears.
[ ] Perspective, depth, and parallax make the scene unmistakably 3D.
[ ] Root wells/pillars, potential terrain, zero plane, density, and Lambda
    valley are geometric objects rather than flat labels.
[ ] No formula or label overlaps, clips, or becomes unreadable.
[ ] LaTeX is complete for the potential, atomization inclusion, Lambda,
    certified L enclosure, 2 sqrt(2), and endpoint-root extremizer.
[ ] The film distinguishes the certified enclosure from the exact definition.
[ ] The infimum is not attained; the maximum is attained.
[ ] Pull-backs create whitespace before new explanations.
[ ] The final frame can stand alone in the README.
```

- [ ] **Step 6: Repair only evidence-backed defects**

If the run failed application validation, the Sol harness already invokes
up to three Codex repair passes. If the completed MP4 still has a visual
defect, identify the exact timestamp and scene-code lines, make one surgical
run-local edit with `apply_patch`, then rerender in the same run directory:

```powershell
$run = Get-ChildItem runs\sol -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
$manifest = Get-Content -Raw (Join-Path $run.FullName "manifest.json") |
  ConvertFrom-Json
$scene = Join-Path $run.FullName "sol_scene.py"
$sceneName = $manifest.scene_name
$media = Join-Path $run.FullName "manual-repair-media"
& .\.venv\Scripts\manim.exe -ql --media_dir $media $scene $sceneName
```

Permitted run-local edits are limited to background constants, camera
phi/theta/zoom/frame center, object scale/position, caption replacement,
MathTex splitting/scaling, surface opacity/resolution, and beat timing. Do
not alter theorem values or proof direction. Repeat Steps 3–5 against the new
MP4 before accepting it.

### Task 5: Package the Curated GIF

**Files:**
- Create: `docs/showcase/assets/erdos-1038-potential-landscape.gif`
- Generate, do not commit: a run-local 22-second highlight MP4

**Interfaces:**
- Consumes: visually accepted Sol MP4.
- Produces: a 720-pixel-wide optimized GIF without importing Mythos code.

- [ ] **Step 1: Cut the final 22-second teaching sequence**

Run:

```powershell
$run = Get-ChildItem runs\sol -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
$manifest = Get-Content -Raw (Join-Path $run.FullName "manifest.json") |
  ConvertFrom-Json
$mp4 = Join-Path $run.FullName $manifest.video_path
$highlight = Join-Path $run.FullName "erdos-1038-readme-highlight.mp4"
& ffmpeg -y -sseof -22 -i $mp4 -t 22 -an $highlight
```

Expected: a playable clip containing the certified minimum and endpoint-root
finale.

- [ ] **Step 2: Create the GIF with the established FFmpeg recipe**

Run:

```powershell
$run = Get-ChildItem runs\sol -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
$highlight = Join-Path $run.FullName "erdos-1038-readme-highlight.mp4"
& ffmpeg -y -i $highlight `
  -vf "fps=12,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=96[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5" `
  docs\showcase\assets\erdos-1038-potential-landscape.gif
```

Expected: a palette-optimized GIF at the exact asset path.

- [ ] **Step 3: Inspect GIF quality**

Run:

```powershell
$run = Get-ChildItem runs\sol -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
$gifSheet = Join-Path $run.FullName "gif-contact-sheet.jpg"
& ffmpeg -y -i docs\showcase\assets\erdos-1038-potential-landscape.gif `
  -vf "fps=1/4,scale=480:-1,tile=3x2:padding=8:margin=8" `
  -frames:v 1 $gifSheet
& ffprobe -v error -show_entries format=duration,size -of json `
  docs\showcase\assets\erdos-1038-potential-landscape.gif
```

Expected: nonzero duration/size and six sample frames retaining off-white
contrast, readable formulas, and 3D depth.

### Task 6: Feature the Accepted Film in the Root README

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: accepted curated GIF and reproducible source prompt.
- Produces: root-page showcase block without altering existing features.

- [ ] **Step 1: Insert the feature block**

After the introductory italic paragraph and before the existing
`traitor-axis.gif` block, add:

```html
<p align="center">
  <img src="docs/showcase/assets/erdos-1038-potential-landscape.gif" alt="Erdős Problem 1038 visualized on an archival off-white 3D logarithmic-potential landscape: roots carve wells beneath a zero plane, barycentric atomization contracts the sublevel region, a one-cut density reaches the certified lower width, and endpoint roots expand to the sharp upper width" width="85%" />
</p>

<p align="center"><em><strong>ERDŐS 1038: THE POTENTIAL LANDSCAPE.</strong> This proposed solution for monic real polynomials with every root in [-1,1] turns the root measure into a 3D logarithmic potential, so |f(x)|&lt;1 becomes the terrain below a zero plane. Barycentric atomization leads to the one-cut limiting shape and the certified, unattained infimum L = 1.834430475762661&hellip;; equal endpoint masses give the attained supremum 2&radic;2 through f(x) = (x<sup>2</sup>&minus;1)<sup>m</sup>. <a href="docs/prompts/erdos-1038-off-white-3d.md">Read the complete Sol film prompt &rarr;</a></em></p>

<br />
```

- [ ] **Step 2: Verify README preservation and references**

Run:

```powershell
if (-not (Test-Path docs\showcase\assets\erdos-1038-potential-landscape.gif)) {
  throw "Missing curated GIF"
}
$readme = Get-Content -Raw README.md
foreach ($required in @(
  "api.star-history.com/chart",
  "docs/showcase/assets/traitor-axis.gif",
  "docs/showcase/assets/erdos-1038-potential-landscape.gif",
  "docs/prompts/erdos-1038-off-white-3d.md"
)) {
  if ($readme -notmatch [regex]::Escape($required)) { throw "Missing $required" }
}
```

Expected: no exception.

- [ ] **Step 3: Commit the curated media and README**

```powershell
git add README.md docs/showcase/assets/erdos-1038-potential-landscape.gif
git commit -m "docs: feature Sol film for Erdős 1038"
```

### Task 7: Final Verification and Handoff

**Files:**
- Verify all committed deliverables.
- Do not add pre-existing `scripts/*.ps1`, `tmp/`, `runs/`, or `media/`.

**Interfaces:**
- Consumes: final repository and selected Sol run.
- Produces: evidence-backed completion report.

- [ ] **Step 1: Run the full offline suite**

Run:

```powershell
& .\.venv\Scripts\pytest.exe -q
```

Expected: exit code 0 with zero failed tests.

- [ ] **Step 2: Verify provider isolation**

Run:

```powershell
$promptText = Get-Content -Raw docs\prompts\erdos-1038-off-white-3d.md
if ($promptText -match 'Mythos') { throw "Prompt crossed provider silos" }
$run = Get-ChildItem runs\sol -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
$manifest = Get-Content -Raw (Join-Path $run.FullName "manifest.json") |
  ConvertFrom-Json
if ($manifest.backend -ne "codex-cli" -or $manifest.model -ne "gpt-5.6-sol") {
  throw "Selected run is not Sol-native"
}
```

Expected: no exception.

- [ ] **Step 3: Verify formatting and committed scope**

Run:

```powershell
git diff --check 9382e4b..HEAD
git status --short
git log -5 --oneline
```

Expected: no whitespace errors. Only pre-existing unrelated untracked
`scripts/make_gifs.ps1`, `scripts/make_traitor_gif.ps1`, and `tmp/` may remain.

- [ ] **Step 4: Reconfirm final media**

Run:

```powershell
$run = Get-ChildItem runs\sol -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
$manifest = Get-Content -Raw (Join-Path $run.FullName "manifest.json") |
  ConvertFrom-Json
$mp4 = Join-Path $run.FullName $manifest.video_path
& ffprobe -v error -show_entries format=duration,size -of json $mp4
& ffprobe -v error -show_entries format=duration,size -of json `
  docs\showcase\assets\erdos-1038-potential-landscape.gif
```

Expected: both files have nonzero duration and size.

- [ ] **Step 5: Report exact artifact paths**

The final handoff must name:

```text
source prompt
selected runs/sol run directory
sol_scene.py
final MP4
contact sheet
curated GIF
README
test command and zero-failure result
any skipped higher-quality render, with reason
```
