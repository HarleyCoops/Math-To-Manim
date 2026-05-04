# Math-To-Manim: 10-Minute Multi-Agent Demo Runbook

Goal: show the full path from a basic text prompt to a rendered MP4 while the audience watches the agent pipeline work.

Use a visual calculus prompt for the live demo so the tree stays small, the render is fast, and the audience sees a real geometric aha moment:

```text
Explain why derivatives are slopes
```

The important live story is:

```text
simple prompt
  -> ConceptAnalyzer
  -> PrerequisiteExplorer / reverse knowledge tree
  -> MathematicalEnricher
  -> VisualDesigner
  -> NarrativeComposer
  -> Manim code generation + syntax validation / repair
  -> manim render
  -> MP4 file
```

## 0. Pre-demo setup

Run from the repository root. In the user's WSL setup, the repo is already at `/mnt/c/Users/chris/Math-To-Manim`.

```bash
# From WSL, if the repo is on the Windows C: drive:
cd /mnt/c/Users/chris/Math-To-Manim

# If you are already in the repo root, just confirm with:
pwd

python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,claude,web]"
```

Note: `.env` only supplies API keys. Windows Python and WSL Python are separate environments, so WSL still needs its own installed Python packages. If WSL says `Missing Python dependency: dotenv`, activate the WSL venv above and run the `pip install` command there.

System dependencies must already be available:

```bash
ffmpeg -version
manim --version
latex --version
```

Create `.env` with the Claude key used by the `src/` pipeline:

```bash
ANTHROPIC_API_KEY=your_key_here
```

Optional quick sanity check:

```bash
python3 -m py_compile src/agents/orchestrator.py scripts/demo_10_minute_pipeline.py
```

## 1. The 10-minute live script

### Minute 0-1: frame the project

Say:

"Math-To-Manim takes a short educational prompt and turns it into a Manim animation. The key idea is not just asking an LLM for code. We run a multi-agent pipeline that first builds a reverse knowledge tree: for the target concept, it repeatedly asks, 'what must someone understand before this?' Then later agents add equations, visual design, narration, and finally executable Manim Python."

Point to:

```bash
src/agents/orchestrator.py
```

The orchestrator has six visible stages printed to the terminal.

### Minute 1-2: type the prompt

Run this exact command:

```bash
python3 scripts/demo_10_minute_pipeline.py \
  --prompt "Explain why derivatives are slopes" \
  --depth 1 \
  --style cinematic \
  --model claude-opus-4-7
```

Why `--depth 1` for the demo: it keeps the reverse knowledge tree small enough for a live presentation while still showing prerequisites like slope, graphs, limits, and secant lines. For richer offline runs, use `--depth 2` or `--depth 3`.

### Minute 2-6: narrate the agent output

As the terminal runs, call out each banner:

1. `STEP 1: CONCEPT ANALYSIS`
   - Converts the sentence into a core concept, domain, level, and goal.

2. `STEP 2: PREREQUISITE EXPLORATION`
   - This is the reverse knowledge tree.
   - It recursively asks what needs to be known before the target concept.
   - The terminal prints the tree when it is built.

3. `STEP 3: MATHEMATICAL ENRICHMENT`
   - Adds definitions, examples, and LaTeX equations to the nodes.

4. `STEP 4: VISUAL DESIGN`
   - Adds visual specifications: colors, layout, animation ideas, transitions.

5. `STEP 5: NARRATIVE COMPOSITION`
   - Walks the tree from foundations to the target concept.
   - Produces a long, structured prompt for code generation.

6. `STEP 6a: MANIM CODE GENERATION`
   - Turns the verbose prompt into a runnable Python file using Manim Community Edition.
   - The demo runner validates generated Python syntax and can ask Claude to repair malformed code before saving.

### Minute 6-8: show generated files

The demo runner writes artifacts under:

```bash
output/demo_10_minute/
```

Typical files:

```text
<Concept>_tree.json       # structured reverse knowledge tree
<Concept>_prompt.txt      # verbose prompt produced by NarrativeComposer
<Concept>_animation.py    # generated Manim scene
<Concept>_result.json     # metadata and combined output
```

Useful commands while presenting:

```bash
ls -lh output/demo_10_minute
python3 - <<'PY'
from pathlib import Path
for p in Path('output/demo_10_minute').glob('*_animation.py'):
    print('\n===', p, '===')
    print('\n'.join(p.read_text().splitlines()[:40]))
PY
```

### Minute 8-10: render and show the MP4

The demo runner renders automatically unless `--no-render` is used. It infers the first generated `Scene` or `ThreeDScene` class and runs Manim roughly like:

```bash
python -m manim -ql output/demo_10_minute/<Concept>_animation.py <SceneName>
```

The final video appears under Manim's media directory, usually:

```text
media/videos/<generated_file_name>/480p15/<SceneName>.mp4
```

The runner prints the detected final MP4 path at the end.

On WSL, open the file from Windows Explorer with:

```bash
explorer.exe "$(wslpath -w media/videos)"
```

Or open the specific file if the runner printed it:

```bash
explorer.exe "$(wslpath -w /absolute/path/to/file.mp4)"
```

## 2. If you want to show code generation only

For a faster talk track, skip rendering during the live agent run:

```bash
python3 scripts/demo_10_minute_pipeline.py \
  --prompt "Explain why derivatives are slopes" \
  --depth 1 \
  --style cinematic \
  --model claude-opus-4-7 \
  --no-render
```

Then render manually after checking the generated scene class:

```bash
python3 - <<'PY'
import ast
from pathlib import Path
for p in Path('output/demo_10_minute').glob('*_animation.py'):
    tree = ast.parse(p.read_text())
    scenes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    print(p, scenes)
PY

python -m manim -pql output/demo_10_minute/<Concept>_animation.py <SceneName>
```

## 3. Backup plan for live demos

Live LLM-generated Manim can occasionally need a small code fix. If that happens, keep the demo moving:

1. Say: "The agent has completed its creative pipeline; now Manim is acting as the compiler. If the generated code has a syntax or LaTeX issue, we can inspect and patch the generated Python exactly like normal code."
2. Open `output/demo_10_minute/<Concept>_animation.py`.
3. Fix the reported line.
4. Rerun:

```bash
python -m manim -pql output/demo_10_minute/<Concept>_animation.py <SceneName>
```

Also keep a known-good example ready:

```bash
manim -pql examples/physics/black_hole_symphony.py BlackHoleSymphony
```

## 4. Optional: launch the Gradio UI

The UI path is useful to show a friendly frontend, but the terminal demo is better for watching the agents.

```bash
python3 src/app_claude.py
```

Then open:

```text
http://localhost:7860
```

## 5. Speaker notes: concise explanation

"The input is intentionally tiny. The system expands it into structure before asking for code. First the ConceptAnalyzer identifies the target. Then the PrerequisiteExplorer builds a dependency tree by asking what comes before. The enrichment and visual agents add math and animation design. The NarrativeComposer turns the tree into a detailed production prompt. Finally the code generator writes Manim Python, and Manim compiles that Python into an MP4. So the final video is not generated directly by the LLM; the LLM produces executable animation code, and Manim renders the actual video."
