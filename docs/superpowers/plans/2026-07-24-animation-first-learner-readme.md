# Animation First Learner README Implementation Plan

> **For agentic workers:** REQUIRED SUB SKILL: Use
> `superpowers:subagent-driven-development` or
> `superpowers:executing-plans` to
> implement this plan one task at a time. Steps use checkbox syntax for
> tracking.

**Goal:** Rebuild the root README around six visual explainers, a learner first
product story, useful prompt examples, clear reasoning stages, and practical
MCP and command line onboarding.

**Architecture:** Keep the root README as one curated document with four clear
layers: featured explainers, learner guidance, first use instructions, and
technical reference. Preserve the complete archive in the existing showcase.
Use focused README tests as the contract for ordering, copy, links, commands,
provider boundaries, and the prose rule.

**Tech Stack:** Markdown, HTML image blocks, Python, pytest, regular
expressions, existing GIF and MP4 assets

## Global Constraints

1. Keep the star chart intact.
2. Erdős 1038 must remain the first local GIF.
3. Call user facing outputs visual explainers or explainers.
4. Use film, scene, render, and animation only for implementation details or
   file types.
5. Never use hyphens, en dashes, or em dashes in written prose.
6. Dashes remain valid in filenames, commands, code, links, identifiers, and
   markup syntax.
7. Keep Mythos and Sol native and independent.
8. Describe Kimi as related work in a separate repository.
9. Do not delete showcase assets.
10. Do not modify unrelated local scripts or the `tmp/` directory.

---

## File Map

1. `README.md`

   Owns the complete public reader journey. It will be rewritten in place.

2. `tests/test_erdos_1038_readme.py`

   Keeps the existing Erdős media and ordering regression checks. One expected
   phrase changes from film to visual explainer.

3. `tests/test_readme_learner_first.py`

   New focused contract for the six featured explainers, learner examples,
   reasoning flow, MCP onboarding, native pipeline boundaries, Kimi link,
   legacy removal, and dash free prose.

4. `docs/superpowers/specs/2026-07-24-animation-first-learner-readme-design.md`

   Read only design authority for this implementation.

### Task 1: Curate The Featured Visual Explainers

**Files:**

- Create: `tests/test_readme_learner_first.py`
- Modify: `README.md`
- Test: `tests/test_readme_learner_first.py`
- Test: `tests/test_erdos_1038_readme.py`

**Interfaces:**

- Consumes: Existing assets in `docs/showcase/assets/`
- Produces: A top section whose first six local GIF references are the six
  approved explainers in the approved order

- [ ] **Step 1: Write the failing featured explainer test**

Create `tests/test_readme_learner_first.py` with:

```python
import re
from pathlib import Path


README = Path("README.md")

FEATURED_EXPLAINERS = [
    "docs/showcase/assets/erdos-1038-potential-landscape.gif",
    "docs/showcase/assets/jacobian-conjecture-3d.gif",
    "docs/showcase/assets/traitor-axis.gif",
    "docs/showcase/assets/vortex-leapfrog.gif",
    "docs/showcase/assets/the-valley.gif",
    "docs/showcase/assets/exceptional-point-monodromy.gif",
]


def readme_text() -> str:
    return README.read_text(encoding="utf-8")


def local_gif_references(text: str) -> list[str]:
    return re.findall(r'docs/showcase/assets/[^"\']+\.gif', text)


def test_featured_explainers_are_first_and_in_order():
    text = readme_text()
    references = local_gif_references(text)

    assert references[:6] == FEATURED_EXPLAINERS
    assert "api.star-history.com/chart" in text
    assert "Ask a question. Get a visual explainer." in text
    assert "docs/showcase/README.md" in text


def test_every_featured_explainer_asset_exists():
    for asset in FEATURED_EXPLAINERS:
        assert Path(asset).is_file()
```

- [ ] **Step 2: Run the focused test and verify the old order fails**

Run:

```bash
python -m pytest tests/test_readme_learner_first.py -q
```

Expected: `test_featured_explainers_are_first_and_in_order` fails because The
Last Day currently appears before Vortex Leapfrog.

- [ ] **Step 3: Replace the opening showcase with the curated premiere**

In `README.md`, preserve the star chart, title, badges, and opening navigation.
Change the tagline to:

```markdown
### Ask a question. Get a visual explainer.
```

Replace the animation sequence between the opening quote and the closing
centered container with six entries in the exact test order.

Keep the existing Erdős preview, proof explanation, complete MP4 link, and
production prompt link. Change its final link text to:

```html
<p align="center"><em><a href="docs/showcase/assets/erdos-1038-potential-landscape.mp4">Watch the complete 79 second visual explainer</a> · <a href="docs/prompts/erdos-1038-off-white-3d.md">Read the complete Sol production prompt</a></em></p>
```

Keep the current Jacobian and Traitor Axis visual blocks, but shorten their
captions so each one states the idea, the visual, and the learning value.

Add these three exact visual blocks after Traitor Axis:

```html
<p align="center">
  <img src="docs/showcase/assets/vortex-leapfrog.gif" alt="Two glowing vortex rings pass through each other while tracer particles reveal the surrounding flow" width="85%" />
</p>

<p align="center"><em><strong>VORTEX LEAPFROG.</strong> This explainer teaches how one vortex ring can pass through another. The rings contract, accelerate, pass, and expand under a computed velocity field while tracer particles make the invisible flow visible.</em></p>

<br />

<p align="center">
  <img src="docs/showcase/assets/the-valley.gif" alt="The valley of nuclear stability appears as a three dimensional energy landscape" width="85%" />
</p>

<p align="center"><em><strong>THE VALLEY OF STABILITY.</strong> This explainer turns nuclear binding energy into terrain. Fusion and fission begin on opposite sides, then both move toward the same stable basin near iron, making two difficult processes feel like one geometric idea.</em></p>

<br />

<p align="center">
  <img src="docs/showcase/assets/exceptional-point-monodromy.gif" alt="A loop around an exceptional point moves between two sheets of a square root surface" width="85%" />
</p>

<p align="center"><em><strong>EXCEPTIONAL POINT MONODROMY.</strong> This explainer shows why one loop around a branch point swaps two eigenvalues. The path lifts onto a two sheeted square root surface, so the learner can watch one branch become the other.</em></p>
```

End the section with:

```markdown
<p align="center"><strong><a href="docs/showcase/README.md">Explore every visual explainer in the motion showcase</a></strong></p>
```

Remove The Last Day, Associate Family, Holonomy, paired process previews, and
all thumbnail rows from this opening showcase.

- [ ] **Step 4: Run the focused README tests**

Run:

```bash
python -m pytest tests/test_readme_learner_first.py tests/test_erdos_1038_readme.py -q
```

Expected: All focused tests pass except the existing Erdős phrase check if the
old word film has already been replaced.

- [ ] **Step 5: Update the Erdős wording regression**

In `tests/test_erdos_1038_readme.py`, replace:

```python
assert "Watch the complete 79-second film" in text
```

with:

```python
assert "Watch the complete 79 second visual explainer" in text
```

- [ ] **Step 6: Run the focused README tests again**

Run:

```bash
python -m pytest tests/test_readme_learner_first.py tests/test_erdos_1038_readme.py -q
```

Expected: All tests pass.

- [ ] **Step 7: Commit the curated premiere**

```bash
git add README.md tests/test_erdos_1038_readme.py tests/test_readme_learner_first.py
git commit -m "docs: curate featured visual explainers"
```

### Task 2: Add The Learner Guide And Reasoning Story

**Files:**

- Modify: `tests/test_readme_learner_first.py`
- Modify: `README.md`
- Test: `tests/test_readme_learner_first.py`

**Interfaces:**

- Consumes: The curated explainer section from Task 1
- Produces: A learner guide with a product definition, Manim credit, prompt
  examples, prompt recipe, and provider neutral reasoning flow

- [ ] **Step 1: Write the failing learner guide tests**

Append:

```python
def test_product_definition_and_manim_credit_are_present():
    text = readme_text()

    assert "## What Is Math To Manim" in text
    assert "carefully reasoned visual explanation" in text
    assert "originally created by Grant Sanderson for 3Blue1Brown" in text
    assert "https://docs.manim.community/en/stable/" in text


def test_prompt_examples_cover_beginner_through_research_levels():
    text = readme_text()

    required_phrases = [
        "eighth grade student",
        "Pythagorean theorem",
        "Teach slope using three ramps",
        "conservation of momentum",
        "Fourier series as rotating vectors",
        "exceptional point swaps the eigenvalue branches",
        "Assume they already know",
        "End with",
    ]
    for phrase in required_phrases:
        assert phrase in text


def test_reasoning_flow_uses_learning_order():
    text = readme_text()
    stages = [
        "Understand the learner",
        "Find the missing prerequisites",
        "Build the teaching sequence",
        "Choose the mathematics",
        "Plan the visuals",
        "Compose the Manim scene",
        "Validate the result",
        "Render, inspect, and repair",
    ]

    positions = [text.index(stage) for stage in stages]
    assert positions == sorted(positions)
```

- [ ] **Step 2: Run the learner guide tests and verify they fail**

Run:

```bash
python -m pytest tests/test_readme_learner_first.py -q
```

Expected: Three new tests fail because the learner guide does not exist.

- [ ] **Step 3: Add the product definition**

After the featured explainers, add:

```markdown
## What Is Math To Manim

Math To Manim turns a math or physics question into a carefully reasoned
visual explanation. It works backward to identify what the learner needs to
know, rebuilds those ideas in teaching order, checks the mathematics, and
animates the explanation in Manim.

[Manim](https://docs.manim.community/en/stable/) is the open source animation
engine originally created by Grant Sanderson for 3Blue1Brown. It powers many
of the most recognizable math and physics animations online. This project
uses the edition maintained by the Manim community.

The reasoning process is the product. Math To Manim does not jump directly
from a sentence to Python. It first decides what must be understood, what must
be shown, and in what order each idea should appear.
```

- [ ] **Step 4: Add the prompt examples and reusable recipe**

Add `## What Can I Ask` with the six exact prompt examples from the approved
design. Present them as short quoted prompts with a plain language level label.
Then add:

```markdown
### A Useful Prompt Recipe

> Explain [topic] to [learner]. Assume they already know [starting point].
> Use [visual metaphor or physical model]. Work through [specific example].
> End with [summary or check question].

You can name the learner's age, prior knowledge, pace, preferred visual model,
worked example, notation level, and final comprehension check. A simple
homework question is enough. The pipeline expands it into a teaching plan.
```

- [ ] **Step 5: Add the provider neutral reasoning flow**

Add:

```markdown
## How The Reasoning Pipeline Works

1. **Understand the learner.** Identify the real question, the audience, and
   the intended depth.
2. **Find the missing prerequisites.** Work backward until every branch reaches
   ideas the learner already knows.
3. **Build the teaching sequence.** Walk those ideas forward in the order that
   makes the final concept feel earned.
4. **Choose the mathematics.** Select the definitions, equations, examples,
   and checks that carry the explanation.
5. **Plan the visuals.** Decide what appears on screen, what changes, and where
   the camera guides attention.
6. **Compose the Manim scene.** Turn the teaching plan into complete,
   addressable visual objects and timing.
7. **Validate the result.** Check code structure, mathematical presentation,
   readability, and camera rules.
8. **Render, inspect, and repair.** Produce the explainer, review the evidence,
   and correct visible defects.
```

- [ ] **Step 6: Run the learner guide tests**

Run:

```bash
python -m pytest tests/test_readme_learner_first.py -q
```

Expected: All tests pass.

- [ ] **Step 7: Commit the learner guide**

```bash
git add README.md tests/test_readme_learner_first.py
git commit -m "docs: explain the learner journey"
```

### Task 3: Add MCP First Onboarding And Architecture Choices

**Files:**

- Modify: `tests/test_readme_learner_first.py`
- Modify: `README.md`
- Test: `tests/test_readme_learner_first.py`

**Interfaces:**

- Consumes: Existing `math-to-manim`, `math-to-manim-sol`, API, and MCP command
  surfaces
- Produces: A beginner path for MCP, explicit Mythos and Sol commands, and a
  related Kimi repository note

- [ ] **Step 1: Write the failing onboarding tests**

Append:

```python
def test_mcp_onboarding_includes_setup_and_conversation():
    text = readme_text()

    assert "## Make Your First Explainer" in text
    assert 'pip install -e ".[mcp]"' in text
    assert '"args": ["serve-mcp"]' in text
    assert "Use Math To Manim to create a visual explainer" in text
    assert "The assistant starts the explainer" in text
    assert "The assistant reports progress" in text
    assert "The assistant can inspect every reasoning artifact" in text


def test_native_pipelines_and_related_kimi_repo_are_clear():
    text = readme_text()

    assert "## Choose A Native Pipeline" in text
    assert "math-to-manim run" in text
    assert "math-to-manim-sol run" in text
    assert "Neither pipeline routes through the other" in text
    assert "https://github.com/HarleyCoops/KimiK3Manim" in text
    assert "different enough to warrant its own repository" in text
```

- [ ] **Step 2: Run the onboarding tests and verify they fail**

Run:

```bash
python -m pytest tests/test_readme_learner_first.py -q
```

Expected: Two new tests fail because the new onboarding sections do not exist.

- [ ] **Step 3: Add the MCP first path**

Add `## Make Your First Explainer`, then add the existing MCP install command
and client configuration. Follow them with this exact conversation example:

```markdown
Once the server is connected, type this in your assistant:

> Use Math To Manim to create a visual explainer for my eighth grade student.
> Explain why solving an equation means doing the same thing to both sides.
> Use a balance scale, solve 3x + 5 = 20, and end with one practice question.

You do not need to memorize tool names. The assistant starts the explainer,
reports progress, can inspect every reasoning artifact, and returns the final
scene and render from the local run directory.
```

Keep the detailed MCP tool table in the later technical reference.

- [ ] **Step 4: Add the native pipeline choices**

Add:

````markdown
## Choose A Native Pipeline

Math To Manim contains two complete and independent ways to create a visual
explainer. Choose the command line account you already use. Neither pipeline
routes through the other.

### Mythos

Mythos uses the Claude CLI and a six agent charter chain. It reasons through
learner intent, prerequisite mapping, curriculum, mathematics, camera
direction, and scene composition.

```bash
math-to-manim doctor --ping
math-to-manim run "Explain fractions with a folding paper model for a sixth grade learner." --render -q m
```

### Sol

Sol uses the logged in Codex CLI and durable specialist stages. Each role saves
its artifact and session so the run can be inspected, resumed, and repaired by
the responsible specialist.

```bash
math-to-manim-sol doctor
math-to-manim-sol run "Explain fractions with a folding paper model for a sixth grade learner."
```

Read the [complete Sol contract](docs/SOL_5_6_SILO.md).

### Kimi

Kimi uses an agent architecture that is different enough to warrant its own
repository. Explore [Kimi K3 Manim](https://github.com/HarleyCoops/KimiK3Manim).
````

- [ ] **Step 5: Run the onboarding tests**

Run:

```bash
python -m pytest tests/test_readme_learner_first.py -q
```

Expected: All tests pass.

- [ ] **Step 6: Commit onboarding**

```bash
git add README.md tests/test_readme_learner_first.py
git commit -m "docs: add learner onboarding"
```

### Task 4: Replace Stale Narrative With Concise Technical Reference

**Files:**

- Modify: `tests/test_readme_learner_first.py`
- Modify: `README.md`
- Test: `tests/test_readme_learner_first.py`
- Test: `tests/test_erdos_1038_readme.py`

**Interfaces:**

- Consumes: The new learner journey from Tasks 1 through 3 and the existing
  CLI, MCP, API, artifact, and repository documentation
- Produces: One concise technical reference with no stale provider claims,
  duplicate gallery, release announcement, or extended origin story

- [ ] **Step 1: Write the failing cleanup tests**

Append:

```python
def prose_without_code_or_links(text: str) -> str:
    alt_text = " ".join(re.findall(r'alt="([^"]*)"', text))
    prose = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    prose = re.sub(r"`[^`]*`", "", prose)
    prose = re.sub(r"<[^>]+>", "", prose)
    prose = re.sub(r"\]\([^)]+\)", "]", prose)
    return f"{prose}\n{alt_text}"


def test_legacy_root_material_is_removed():
    text = readme_text()
    forbidden = [
        "docs/showcase/assets/the-last-day.gif",
        "docs/showcase/assets/associate-family-riso.gif",
        "docs/showcase/assets/blueprint-holonomy.gif",
        "docs/showcase/assets/reverse-reasoning-tree.gif",
        "docs/showcase/assets/mythos-grammar-reel.gif",
        "## What's new in v1.1",
        "## The morning it started",
        "## Motion showcase",
    ]
    for item in forbidden:
        assert item not in text


def test_technical_reference_remains_complete():
    text = readme_text()
    required = [
        "## Installation",
        "## Run Artifacts",
        "## MCP Reference",
        "## REST API",
        "## Configuration",
        "## Testing",
        "## Repository Layout",
        "## License",
    ]
    for heading in required:
        assert heading in text


def test_written_prose_contains_no_dash_punctuation():
    prose = prose_without_code_or_links(readme_text())

    assert "—" not in prose
    assert "–" not in prose
    assert re.search(r"(?<=[A-Za-z])-(?=[A-Za-z])", prose) is None
```

- [ ] **Step 2: Run the cleanup tests and verify they fail**

Run:

```bash
python -m pytest tests/test_readme_learner_first.py -q
```

Expected: The legacy and technical heading tests fail. The prose test reports
existing compound words and dash punctuation.

- [ ] **Step 3: Remove stale and duplicate sections**

Delete the old root sections for:

1. The v1.1 release announcement
2. The hardening update
3. The extended origin story
4. The old reverse reasoning tree explanation
5. One engine, every altitude
6. The old Mythos only architecture narrative
7. The duplicated Quickstart
8. The duplicated API and MCP introductions
9. The Prime Intellect feature block
10. The duplicate motion showcase

Preserve links to release history, Prime Intellect work, and the full gallery
in one compact `## More From The Project` section.

- [ ] **Step 4: Build the concise technical reference**

After the native pipeline section, add these sections in order:

````markdown
## Installation

```bash
git clone https://github.com/HarleyCoops/Math-To-Manim.git
cd Math-To-Manim
python -m venv .venv
pip install -e ".[dev,render,mcp,api]"
python -m pytest -q
```

Use `math-to-manim doctor --ping` for Mythos or
`math-to-manim-sol doctor` for Sol before a live run.

## Run Artifacts

Every run keeps its reasoning, scene source, validation evidence, and manifest
inside the repository. Mythos writes to `runs/mythos/`. Sol writes to
`runs/sol/`. Open the intermediate JSON when you want to understand or revise
how the explainer was built.

## MCP Reference

Retain the existing seven tool table. Introduce it as reference for assistants
and integrations rather than required knowledge for learners.

## REST API

Retain the existing start command, route table, and curl example. Explain that
the API exposes Mythos for applications and background jobs.

## Configuration

Retain the accurate Mythos environment table. Link to
`docs/SOL_5_6_SILO.md` for the Sol environment and CLI contract.

## Testing

```bash
python -m pytest -q
math-to-manim run "the heat equation" --offline
math-to-manim-sol run "the heat equation" --offline
```

Offline runs validate the complete artifact shape without model calls or an
expensive render.

## More From The Project

Link to `docs/showcase/README.md`, `docs/PRIME_INTELLECT_RL.md`,
`docs/ROADMAP.md`, and the repository history through Git.

## Repository Layout

Retain and update the existing layout so both `mythos/` and `sol/` appear.

## License

MIT.
````

When inserting fenced blocks inside the README, use valid Markdown fence
boundaries. The nested fences above communicate content and are not meant to
be pasted as one outer fenced block.

- [ ] **Step 5: Remove dash punctuation from all remaining prose**

Search written prose:

```bash
python -m pytest tests/test_readme_learner_first.py::test_written_prose_contains_no_dash_punctuation -q
```

Replace dash punctuation with sentences, commas, colons, parentheses, or
separate words. Do not alter filenames, commands, URLs, identifiers, code, or
markup syntax.

- [ ] **Step 6: Run all focused README tests**

Run:

```bash
python -m pytest tests/test_readme_learner_first.py tests/test_erdos_1038_readme.py -q
```

Expected: All tests pass.

- [ ] **Step 7: Commit the technical cleanup**

```bash
git add README.md tests/test_readme_learner_first.py
git commit -m "docs: simplify the technical reference"
```

### Task 5: Validate The Complete README

**Files:**

- Verify: `README.md`
- Verify: `tests/test_readme_learner_first.py`
- Verify: `tests/test_erdos_1038_readme.py`

**Interfaces:**

- Consumes: All prior tasks
- Produces: Fresh evidence that the complete repository and README contract
  pass before publication

- [ ] **Step 1: Run the complete test suite**

Run:

```bash
python -m pytest -q
```

Expected: Every test passes. Existing dependency warnings may remain, but no
test may fail.

- [ ] **Step 2: Check whitespace and local links**

Run:

```bash
git diff --check
python -c "from pathlib import Path; import re; text=Path('README.md').read_text(encoding='utf-8'); links=re.findall(r'(?<!https:)(?<!http:)\\]\\(([^)#]+)', text); missing=[p for p in links if not Path(p).exists()]; assert not missing, missing"
```

Expected: No whitespace errors and no missing local link targets.

- [ ] **Step 3: Confirm repository scope**

Run:

```bash
git status --short
git diff --stat HEAD~4..HEAD
```

Expected: Only README documentation, the two README test files, the approved
specification, and this plan appear in the implementation history. Existing
untracked helper scripts and `tmp/` remain untouched.

- [ ] **Step 4: Review the rendered README on GitHub after publication**

Confirm:

1. The star chart renders.
2. Erdős is the first animation.
3. All six selected GIFs animate.
4. The page reads in the designed order.
5. Code fences and MCP JSON render correctly.
6. The complete Erdős MP4 link opens.
7. The showcase, Manim, Sol, Kimi, Prime Intellect, and roadmap links open.

- [ ] **Step 5: Commit any evidence based correction**

If visual review finds a real defect, change only the affected README or test
line, rerun the focused tests and full suite, then commit:

```bash
git add README.md tests/test_erdos_1038_readme.py tests/test_readme_learner_first.py
git commit -m "docs: correct README presentation"
```

If visual review finds no defect, do not create an empty commit.
