# README Rebuild and Demo Stabilization Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Replace the outdated root `README.md` with a truthful, current, demo-first guide centered on the actual Math-To-Manim framework, and stabilize the demo path so the README's quickstart works on both Windows Python and WSL.

**Architecture:** Treat the repo as a working prototype with multiple related entry points, not a polished single CLI. The README should lead with the core reverse-knowledge-tree idea, then show the most reliable current path: `scripts/demo_10_minute_pipeline.py` -> `src/agents/orchestrator.py` -> generated artifacts -> Manim render. Before documenting this path as the primary quickstart, fix or clearly document the current orchestrator/API mismatch.

**Tech Stack:** Python 3.10+, Manim CE, FFmpeg, LaTeX, Anthropic SDK / `ANTHROPIC_API_KEY`, optional Gradio UI, optional Gemini/Kimi side pipelines.

---

## Current Context and Root Cause Notes

### User environment observations

The user is already in the repo root in WSL:

```bash
/mnt/c/Users/chris/Math-To-Manim
```

So docs must not say to literally run:

```bash
cd /path/to/Math-To-Manim
```

That placeholder caused this failure:

```text
-bash: cd: /path/to/Math-To-Manim: No such file or directory
```

In WSL, `python3 scripts/demo_10_minute_pipeline.py ...` failed because the WSL Python environment does not have `python-dotenv` installed:

```text
[FAIL] Missing Python dependency: dotenv
```

The repo already has `.env`; the missing piece is not the key. It is the Python dependency environment for whichever Python is being used.

In Windows PowerShell, the demo script got past `.env` and API setup, so Windows Python has the needed dependency and key loading worked. It then failed inside the pipeline:

```text
AttributeError: 'PrerequisiteExplorer' object has no attribute 'explore_async'
```

### Root cause of `explore_async` failure

`src/agents/orchestrator.py` calls:

```python
knowledge_tree = await self.prerequisite_explorer.explore_async(
    analysis['core_concept']
)
```

But `src/agents/prerequisite_explorer.py` defines only the synchronous method:

```python
def explore(self, concept: str, depth: int = 0) -> KnowledgeNode:
    ...
```

The full orchestrator expects async agent methods, but the unified `PrerequisiteExplorer` currently exposes a sync public API. This is a real framework drift issue and the README should not advertise this path as stable until fixed.

### Related issue to check during implementation

`src/agents/orchestrator.py` also has:

```python
if enable_atlas:
    self.prerequisite_explorer.enable_atlas_integration(atlas_dataset)
```

`src/agents/prerequisite_explorer.py` does not currently show `enable_atlas_integration`. It is safe while `enable_atlas=False`, but README should avoid advertising Atlas until this is reconciled.

---

## Proposed README Rebuild Strategy

The new root README should be much shorter, more accurate, and demo-oriented:

1. Hero / one-paragraph pitch.
2. What currently works.
3. 10-minute quickstart.
4. Framework architecture.
5. Demo artifacts and output paths.
6. Entrypoints table.
7. Development setup.
8. Known limitations / prototype status.
9. Links to deeper docs.

Avoid big claims that are not currently backed by runnable code. Use language like "prototype", "experimental", "current primary demo path", and "side pipelines" where appropriate.

---

## Target Root README Outline

### 1. Title

```markdown
# Math-To-Manim

Turn a short educational prompt into a Manim animation using a multi-agent reverse-knowledge-tree pipeline.
```

### 2. Status banner

```markdown
> Current status: active prototype. The core framework is implemented in `src/agents/`; examples and side pipelines are included, but some entry points are experimental. Start with the 10-minute demo path below.
```

### 3. The core idea

Use a compact diagram:

```text
"Explain the Pythagorean theorem"
  -> ConceptAnalyzer
  -> PrerequisiteExplorer: what must be understood before this?
  -> MathematicalEnricher
  -> VisualDesigner
  -> NarrativeComposer
  -> Manim code generator
  -> manim render -> MP4
```

### 4. Quickstart: 10-minute demo

Use commands that match the user's actual location:

```bash
# If you are in Windows PowerShell:
cd C:\Users\chris\Math-To-Manim
python scripts\demo_10_minute_pipeline.py --prompt "Explain the Pythagorean theorem with a visual proof" --depth 2
```

For WSL:

```bash
cd /mnt/c/Users/chris/Math-To-Manim
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,claude,web]"
python3 scripts/demo_10_minute_pipeline.py \
  --prompt "Explain the Pythagorean theorem with a visual proof" \
  --depth 2
```

Important note:

```markdown
The `.env` file provides API keys. The Python environment still needs packages installed. If WSL says `Missing Python dependency: dotenv`, activate the venv and run `pip install -e ".[dev,claude,web]"` inside WSL.
```

### 5. Generated outputs

```markdown
The demo writes artifacts to `output/demo_10_minute/`:

- `*_tree.json` — reverse knowledge tree
- `*_prompt.txt` — verbose generation prompt
- `*_animation.py` — generated Manim source
- `*_result.json` — combined metadata

Manim renders MP4s under `media/videos/...`.
```

### 6. Entrypoints table

| Use case | Command | Status |
| --- | --- | --- |
| 10-minute terminal demo | `python scripts/demo_10_minute_pipeline.py ...` | Primary demo path after orchestrator fix |
| Gradio UI | `python src/app_claude.py` | Useful UI / prompt expansion path |
| Render existing example | `manim -pql examples/physics/black_hole_symphony.py BlackHoleSymphony` | Good backup demo |
| Gemini side pipeline | `python Gemini3/run_pipeline.py --prompt ...` | Experimental side pipeline |
| Kimi side pipeline | `python KimiK2.5Swarm/examples/...` | Experimental side pipeline |

### 7. Architecture files

```markdown
Core framework:
- `src/agents/orchestrator.py`
- `src/agents/prerequisite_explorer.py`
- `src/agents/mathematical_enricher.py`
- `src/agents/visual_designer.py`
- `src/agents/narrative_composer.py`
- `src/agents/threejs_code_generator.py`

Demo docs:
- `docs/10_MINUTE_MULTI_AGENT_DEMO.md`
```

### 8. Environment setup

Include both Windows and WSL warnings:

```markdown
Windows Python and WSL Python are separate environments. Installing packages in PowerShell does not install them in WSL. Use one environment consistently for a demo.
```

### 9. Known limitations

```markdown
Known limitations:
- Generated Manim code may require small manual fixes; Manim acts as the compiler.
- The repo contains older experimental docs and side pipelines that may lag behind `src/agents/`.
- Some async/sync framework boundaries are currently being reconciled.
```

---

## Implementation Tasks

### Task 1: Fix the 10-minute demo doc's placeholder path

**Objective:** Remove the literal `/path/to/Math-To-Manim` command that caused user confusion.

**Files:**
- Modify: `docs/10_MINUTE_MULTI_AGENT_DEMO.md`

**Change:** Replace:

```bash
cd /path/to/Math-To-Manim
```

with:

```bash
# From WSL, if the repo is on the Windows C: drive:
cd /mnt/c/Users/chris/Math-To-Manim
```

Also add a generic alternative:

```bash
# Or, if you are already in the repo root, confirm with:
pwd
```

**Verification:**

```bash
grep -n "/path/to/Math-To-Manim" docs/10_MINUTE_MULTI_AGENT_DEMO.md
```

Expected: no matches.

---

### Task 2: Stabilize the orchestrator/prerequisite explorer API mismatch

**Objective:** Make `scripts/demo_10_minute_pipeline.py` progress past prerequisite exploration.

**Files:**
- Modify: `src/agents/prerequisite_explorer.py` or `src/agents/orchestrator.py`
- Test: add or update a focused test if a suitable test file exists, likely under `tests/unit/` or `tests/test_agent_pipeline.py`

**Preferred minimal fix:** Add an async wrapper to `PrerequisiteExplorer` so existing async orchestrators can call it without changing multiple call sites.

Add near the existing `explore` method:

```python
async def explore_async(self, concept: str, depth: int = 0, **_: object) -> KnowledgeNode:
    """Async-compatible wrapper around `explore` for orchestrator pipelines."""
    return self.explore(concept, depth=depth)
```

Why this fix:
- `PrerequisiteExplorer` is currently sync because `LLMClient.query()` is sync.
- `orchestrator.py` and `agent_orchestrator.py` already expect `explore_async`.
- This restores compatibility with minimal code churn.

**Important:** The wrapper accepts `**_` because `agent_orchestrator.py` calls `explore_async(core_concept, verbose=self.verbose)`. The current `orchestrator.py` does not pass `verbose`, but supporting it avoids a second mismatch.

**Verification:**

```bash
python -m py_compile src/agents/prerequisite_explorer.py src/agents/orchestrator.py scripts/demo_10_minute_pipeline.py
```

Then with a real API key and dependencies:

```bash
python scripts/demo_10_minute_pipeline.py \
  --prompt "Explain the Pythagorean theorem with a visual proof" \
  --depth 2 \
  --no-render
```

Expected: It reaches generated artifacts under `output/demo_10_minute/` or reveals the next real framework issue.

---

### Task 3: Make dependency error messaging clearer

**Objective:** Avoid confusion between missing `.env` and missing Python dependencies.

**Files:**
- Modify: `scripts/demo_10_minute_pipeline.py`
- Modify: `docs/10_MINUTE_MULTI_AGENT_DEMO.md`

**Change:** The script already says missing dependency. Improve docs to explicitly say:

```markdown
`.env` only supplies keys. If WSL fails on `dotenv`, install Python dependencies in WSL; Windows Python packages do not carry over.
```

Optionally update script output to include current interpreter:

```python
print(f"Python executable: {sys.executable}")
```

so users can see whether they are running Windows Python or WSL Python.

**Verification:**

```bash
python3 scripts/demo_10_minute_pipeline.py --help
```

Expected: help still works without importing project-only dependencies.

---

### Task 4: Draft replacement README in a temporary file

**Objective:** Build the new root README content without clobbering the current one until reviewed.

**Files:**
- Create: `docs/README_REBUILD_DRAFT.md`

**Content sections:**
1. Project title and one-line pitch.
2. Current status / prototype note.
3. Core pipeline diagram.
4. Quickstart: Windows PowerShell.
5. Quickstart: WSL.
6. Demo output artifacts.
7. Entrypoints table.
8. Architecture map.
9. Examples / backup render command.
10. Known limitations.
11. Further docs.

**Verification:**

```bash
python - <<'PY'
from pathlib import Path
p = Path('docs/README_REBUILD_DRAFT.md')
text = p.read_text(encoding='utf-8')
required = [
    '10-minute',
    'reverse knowledge tree',
    'scripts/demo_10_minute_pipeline.py',
    'output/demo_10_minute',
    'Windows Python and WSL Python are separate',
]
missing = [x for x in required if x not in text]
assert not missing, missing
print('README draft sanity check passed')
PY
```

---

### Task 5: Replace root README after review

**Objective:** Promote the reviewed draft to `README.md`.

**Files:**
- Modify: `README.md`
- Keep: `docs/README_REBUILD_DRAFT.md` optional, or delete after promotion

**Change:** Replace the outdated long README with the concise new README. Keep useful existing assets like `public/hero.jpeg` and selected GIFs only if still accurate.

**Verification:**

```bash
grep -n "/path/to/Math-To-Manim\|echo \"ANTHROPIC_API_KEY=\*\*\* >> .env\|python Gemini3/run_pipeline.py \" README.md
```

Expected: no stale/broken snippets.

Also verify current key commands appear:

```bash
grep -n "scripts/demo_10_minute_pipeline.py\|src/agents/orchestrator.py\|output/demo_10_minute" README.md
```

Expected: matches for all.

---

### Task 6: End-to-end smoke test the README quickstart

**Objective:** Confirm the README's main command actually works in the chosen environment.

**Files:**
- No planned source edits unless the smoke test exposes another mismatch.

**Windows PowerShell smoke test:**

```powershell
cd C:\Users\chris\Math-To-Manim
python scripts\demo_10_minute_pipeline.py --prompt "Explain the Pythagorean theorem with a visual proof" --depth 2 --no-render
```

**WSL smoke test:**

```bash
cd /mnt/c/Users/chris/Math-To-Manim
source .venv/bin/activate
python3 scripts/demo_10_minute_pipeline.py \
  --prompt "Explain the Pythagorean theorem with a visual proof" \
  --depth 2 \
  --no-render
```

**Render smoke test:**

```bash
manim -ql output/demo_10_minute/*_animation.py <DetectedSceneName>
```

or let the demo runner render without `--no-render` after code generation works.

---

## Recommended README Tone

Use truthful, current language:

- "active prototype" instead of "production-ready"
- "primary demo path" instead of "official CLI"
- "experimental side pipeline" for Gemini/Kimi unless fully verified
- "Manim compiles generated Python into an MP4" instead of "AI generates video directly"

Avoid:

- future-dated release notes
- very long embedded mermaid image URLs
- invalid shell snippets with unterminated quotes
- claiming Claude Code plugin is the main path unless it is verified separately

---

## Immediate User-Facing Correction

For the user's current terminal state:

### If using Windows PowerShell

They already proved Windows Python can load `.env` and dependencies. The next blocker is the `explore_async` mismatch. Fix Task 2 first, then rerun:

```powershell
cd C:\Users\chris\Math-To-Manim
python scripts\demo_10_minute_pipeline.py --prompt "Explain the Pythagorean theorem with a visual proof" --depth 2 --no-render
```

### If using WSL

They are already in the repo root. Do not `cd /path/to/Math-To-Manim`. Run:

```bash
cd /mnt/c/Users/chris/Math-To-Manim
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,claude,web]"
python3 scripts/demo_10_minute_pipeline.py \
  --prompt "Explain the Pythagorean theorem with a visual proof" \
  --depth 2 \
  --no-render
```

The `.env` file can already exist; the venv setup is for Python packages, not API keys.

---

## Risks and Open Questions

1. After fixing `explore_async`, the next stages may reveal additional async/sync drift or model/dependency issues.
2. Generated Manim code may fail to render because LLM-generated code often needs a compile/fix loop.
3. Windows vs WSL Manim/LaTeX/FFmpeg availability may differ. README should tell users to choose one environment and install dependencies there.
4. The root README should not over-index on Gemini/Kimi until those paths are smoke-tested.
5. The existing repo has many modified files; implementation should avoid broad formatting or unrelated cleanup.

---

## Definition of Done

- `docs/10_MINUTE_MULTI_AGENT_DEMO.md` no longer contains misleading placeholder setup.
- `scripts/demo_10_minute_pipeline.py --help` still works without importing heavy dependencies.
- The orchestrator no longer fails at `PrerequisiteExplorer.explore_async`.
- A new README draft exists and reflects the current framework accurately.
- The root `README.md` is replaced after review.
- At least one documented quickstart path is smoke-tested through artifact generation.
