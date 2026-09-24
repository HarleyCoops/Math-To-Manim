# Prime Visual-Improvement RL Experiment Implementation Plan

> **For Chris:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to
> implement this plan task by task.

**Goal:** Build, verify, and publish a render-grounded Prime Intellect
reinforcement-learning experiment that trains a multimodal policy to improve
valid Math-To-Manim visuals by revising generated code alone or the scene spec
and code together.

**Architecture:** Add a standalone `m2m2_visual_improvement` Verifiers package
that reads immutable task bundles, validates one typed `VisualRevision`,
renders the candidate in a pinned sandbox, extracts visual telemetry, and
scores candidate-versus-baseline improvement. Keep Mythos and Sol isolated by
using filesystem-only adapters. Drive preparation, evaluation, hosted
training, collection, and comparison through one repository-owned launcher
and immutable experiment ledgers.

**Tech Stack:** Python 3.12, Pydantic 2, current pinned `verifiers`, Hugging
Face Datasets, Manim Community 0.19, OpenCV, Pillow, Tesseract/pytesseract,
FFmpeg/ffprobe, Docker/Prime Images, Prime CLI, pytest.

**Design:** `docs/superpowers/specs/2026-07-24-prime-visual-improvement-rl-design.md`

---

## Execution Rules

- Work on `codex/prime-visual-improvement-rl`.
- Never import from `archive/`, `legacy/`, or the divergent checkout.
- Treat `C:\Users\chris\Math-To-Manim-prime-rl` as audit evidence only.
- Do not modify or stage `scripts/make_gifs.ps1`,
  `scripts/make_traitor_gif.ps1`, or `tmp/`.
- Run the root suite after every task that touches root-level files.
- Use low-resolution deterministic fixtures for tests; do not put generated
  videos or credentials in Git.
- Never print credential values. Authentication probes may report only
  present/missing and authorized/unauthorized.
- Stop before a paid full training run if smoke-run cost, model support, or
  training authorization differs materially from this plan.
- Commit after each green task using the commit message shown.

## Task 1: Pin the Standalone Package and Platform Capability Contract

**Files:**

- Create: `environments/m2m2_visual_improvement/pyproject.toml`
- Create: `environments/m2m2_visual_improvement/README.md`
- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/__init__.py`
- Create: `environments/m2m2_visual_improvement/tests/test_package.py`
- Create: `environments/m2m2_visual_improvement/uv.lock`
- Create: `experiments/prime_rl/README.md`
- Modify: `.gitignore`

**Step 1: Write the failing package-contract test**

```python
from importlib.metadata import version

from m2m2_visual_improvement import ENVIRONMENT_ID, SCHEMA_VERSION


def test_package_contract_is_versioned() -> None:
    assert ENVIRONMENT_ID == "harleycooper/math-to-manim-visual-improvement"
    assert SCHEMA_VERSION == "m2m2.visual_revision.v1"
    assert version("m2m2-visual-improvement") == "0.1.0"
```

**Step 2: Verify the test fails**

Run:

```bash
uv run --project environments/m2m2_visual_improvement pytest \
  environments/m2m2_visual_improvement/tests/test_package.py -q
```

Expected: import or project-not-found failure.

**Step 3: Create the minimal standalone package**

Pin exact versions in `pyproject.toml`; the package must not be added to the
root `tool.setuptools.packages.find`. Export:

```python
ENVIRONMENT_ID = "harleycooper/math-to-manim-visual-improvement"
SCHEMA_VERSION = "m2m2.visual_revision.v1"
```

Use `uv lock --project environments/m2m2_visual_improvement` to generate the
lockfile rather than editing it by hand. Add the narrow exception
`!environments/m2m2_visual_improvement/uv.lock` to `.gitignore`; do not
unignore lockfiles globally.

**Step 4: Verify platform capabilities without exposing credentials**

Run in WSL:

```bash
prime --version
prime train models
prime images list
```

Record only the CLI version, current `verifiers` pin, whether
`Qwen/Qwen3-VL-4B-Instruct` is trainable, and whether image/environment and
hosted-training permissions are authorized. If the model is unavailable,
select no replacement silently: amend the design with an evidence-backed
multimodal model choice and obtain approval first.

**Step 5: Run tests**

Run:

```bash
uv sync --project environments/m2m2_visual_improvement
uv run --project environments/m2m2_visual_improvement pytest -q
pytest -q
```

Expected: package test and root suite pass.

**Step 6: Commit**

```bash
git add environments/m2m2_visual_improvement/pyproject.toml \
  environments/m2m2_visual_improvement/uv.lock \
  environments/m2m2_visual_improvement/README.md \
  environments/m2m2_visual_improvement/m2m2_visual_improvement/__init__.py \
  environments/m2m2_visual_improvement/tests/test_package.py \
  experiments/prime_rl/README.md .gitignore
git commit -m "build: scaffold visual improvement environment"
```

## Task 2: Define the Immutable Task, Action, Evidence, and Ledger Schemas

**Files:**

- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/schemas.py`
- Create: `environments/m2m2_visual_improvement/tests/test_schemas.py`

**Step 1: Write failing schema tests**

Cover:

```python
def test_code_only_rejects_scene_spec_patch() -> None: ...
def test_hierarchical_requires_scene_spec_patch() -> None: ...
def test_no_change_requires_baseline_code_and_diagnosis() -> None: ...
def test_contract_rejects_empty_required_concepts() -> None: ...
def test_evidence_hashes_are_sha256() -> None: ...
def test_reward_ledger_requires_every_component_and_digest() -> None: ...
def test_secrets_cannot_serialize_into_ledger() -> None: ...
```

Use fixtures that instantiate:

- `EducationalContract`
- `EditableBaseline`
- `VisualRevision`
- `VisualEvidence`
- `MetricScore`
- `RewardLedger`
- `InfrastructureExclusion`

**Step 2: Verify failures**

Run:

```bash
uv run --project environments/m2m2_visual_improvement pytest \
  environments/m2m2_visual_improvement/tests/test_schemas.py -q
```

Expected: module-not-found failure.

**Step 3: Implement strict Pydantic models**

Use `ConfigDict(extra="forbid", frozen=True)` for immutable inputs and ledger
records. Validate scope with a model validator:

```python
if self.scope == RevisionScope.CODE_ONLY and self.scene_spec_patch is not None:
    raise ValueError("code_only cannot include scene_spec_patch")
if self.scope == RevisionScope.SPEC_AND_CODE and self.scene_spec_patch is None:
    raise ValueError("spec_and_code requires scene_spec_patch")
```

Require SHA-256 values as 64 lowercase hexadecimal characters. Keep
credentials out of every model field. Store judge endpoint/model identity, not
headers, tokens, or environment-variable values.

**Step 4: Run tests**

Run the schema file, then the entire environment suite.

**Step 5: Commit**

```bash
git add environments/m2m2_visual_improvement
git commit -m "feat: define visual revision contracts"
```

## Task 3: Parse Tagged Model Output and Apply RFC 7396 Merge Patches

**Files:**

- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/merge_patch.py`
- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/parsing.py`
- Create: `environments/m2m2_visual_improvement/tests/test_merge_patch.py`
- Create: `environments/m2m2_visual_improvement/tests/test_parsing.py`

**Step 1: Write failing tests**

Test scalar replacement, nested merge, array replacement, and `null` deletion.
Test exactly one tagged action:

```text
<visual_revision>{"schema_version":"m2m2.visual_revision.v1", ...}</visual_revision>
```

Reject missing tags, duplicate tags, surrounding action tags, invalid JSON,
unknown fields, and output larger than the configured limit.

**Step 2: Verify failures**

```bash
uv run --project environments/m2m2_visual_improvement pytest \
  environments/m2m2_visual_improvement/tests/test_merge_patch.py \
  environments/m2m2_visual_improvement/tests/test_parsing.py -q
```

**Step 3: Implement the minimal pure functions**

```python
def apply_merge_patch(target: JsonValue, patch: JsonValue) -> JsonValue:
    if not isinstance(patch, dict):
        return deepcopy(patch)
    result = deepcopy(target) if isinstance(target, dict) else {}
    for key, value in patch.items():
        if value is None:
            result.pop(key, None)
        else:
            result[key] = apply_merge_patch(result.get(key), value)
    return result
```

Parse to `VisualRevision` only after extracting one exact tag pair.

**Step 4: Run tests and commit**

```bash
git add environments/m2m2_visual_improvement
git commit -m "feat: validate hierarchical visual revisions"
```

## Task 4: Build Filesystem-Only Mythos and Sol Adapters

**Files:**

- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/adapters/__init__.py`
- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/adapters/common.py`
- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/adapters/mythos.py`
- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/adapters/sol.py`
- Create: `environments/m2m2_visual_improvement/tests/test_adapters.py`
- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/fixtures/provider_holdout/mythos/`
- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/fixtures/provider_holdout/sol/`

**Step 1: Create minimal text-only fixtures**

For each provider, include the six numbered JSON artifacts, provider scene
source, and a sanitized manifest. Derive them from completed local runs but
remove absolute paths, model sessions, videos, timestamps that identify local
machines, and all credentials.

**Step 2: Write failing adapter tests**

Prove both adapters:

- detect their provider from required filenames;
- preserve `06_scene_spec.json` as opaque JSON;
- normalize path separators;
- hash every source artifact;
- reject a missing numbered stage;
- reject a failed/incomplete manifest;
- never import `mythos` or `sol`.

The isolation assertion must run the adapter in a subprocess with an import
guard that raises on module names beginning with `mythos` or `sol`.

**Step 3: Implement shared normalization**

Return one `TaskBundle` model. Read with UTF-8 and explicit size limits. Use
`Path.resolve()` plus `is_relative_to(run_dir.resolve())` before opening any
manifest-referenced file.

**Step 4: Verify**

```bash
uv run --project environments/m2m2_visual_improvement pytest \
  environments/m2m2_visual_improvement/tests/test_adapters.py -q
pytest tests/test_sol_silo.py tests/test_harness_offline.py -q
```

**Step 5: Commit**

```bash
git add environments/m2m2_visual_improvement
git commit -m "feat: adapt Mythos and Sol run artifacts"
```

## Task 5: Generate the Deterministic 144-Task Laboratory Dataset

**Files:**

- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/dataset.py`
- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/micro_scenes.py`
- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/fixtures/micro_scenes/`
- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/data/tasks.jsonl`
- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/data/manifest.json`
- Create: `environments/m2m2_visual_improvement/tests/test_dataset.py`

**Step 1: Write the dataset invariants as failing tests**

```python
def test_manifest_has_144_tasks() -> None: ...
def test_grouped_splits_are_96_24_24() -> None: ...
def test_base_scene_never_crosses_splits() -> None: ...
def test_all_six_defect_families_are_represented() -> None: ...
def test_each_base_scene_has_eight_mutations() -> None: ...
def test_generation_is_byte_deterministic() -> None: ...
def test_task_ids_and_hashes_match_payloads() -> None: ...
```

**Step 2: Verify failures**

Run only `test_dataset.py`.

**Step 3: Implement 18 clean micro-scenes**

Each scene is 6–12 seconds and uses a common metadata block declaring required
visible text, object IDs, safe regions, and focus beats. Implement eight
seeded mutations per scene across the six approved families. Mutations must
alter actual scene parameters or code, not merely label a task.

Use fixed split assignments:

```python
TRAIN_BASES = tuple(f"scene_{i:02d}" for i in range(1, 13))
VALIDATION_BASES = tuple(f"scene_{i:02d}" for i in range(13, 16))
TEST_BASES = tuple(f"scene_{i:02d}" for i in range(16, 19))
```

**Step 4: Generate committed text artifacts twice**

Generate into two temporary directories, compare SHA-256 hashes, then replace
the tracked JSONL/manifest only if byte-identical. Do not commit rendered
media.

**Step 5: Verify and commit**

```bash
uv run --project environments/m2m2_visual_improvement pytest \
  environments/m2m2_visual_improvement/tests/test_dataset.py -q
git add environments/m2m2_visual_improvement
git commit -m "feat: add deterministic visual defect dataset"
```

## Task 6: Implement Safe Candidate Validation

**Files:**

- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/safety.py`
- Create: `environments/m2m2_visual_improvement/tests/test_safety.py`

**Step 1: Write failing tests**

Reject:

- non-Python or syntax errors;
- imports outside an allowlist;
- filesystem access beyond the candidate directory;
- networking, subprocesses, dynamic imports, `eval`, `exec`, and pickling;
- a missing `Scene`/`ThreeDScene` subclass and `construct`;
- `self.camera.animate` in `ThreeDScene`;
- code exceeding byte or AST-node limits.

Accept the committed micro-scenes and normal Manim constructs.

**Step 2: Implement AST validation**

Return typed violations; do not execute code during validation. Keep runtime
containment as a second boundary rather than claiming AST checks are a
sandbox.

**Step 3: Verify and commit**

```bash
uv run --project environments/m2m2_visual_improvement pytest \
  environments/m2m2_visual_improvement/tests/test_safety.py -q
git add environments/m2m2_visual_improvement
git commit -m "feat: validate candidate Manim source"
```

## Task 7: Render Baselines and Candidates into Reproducible Evidence

**Files:**

- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/renderer.py`
- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/telemetry.py`
- Create: `environments/m2m2_visual_improvement/tests/test_renderer.py`
- Create: `environments/m2m2_visual_improvement/tests/test_render_integration.py`
- Modify: `environments/m2m2_visual_improvement/m2m2_visual_improvement/schemas.py`

**Step 1: Write failing renderer unit tests with a fake process runner**

Assert:

- exact Manim command construction;
- 854x480, fixed FPS, quality, media directory, and timeout;
- candidate and baseline output separation;
- typed candidate failure versus infrastructure exclusion;
- ffprobe duration parsing;
- atomic evidence manifest writes;
- stdout/stderr truncation and secret redaction.

**Step 2: Implement injectable subprocess rendering**

```python
class Renderer:
    def __init__(self, runner: ProcessRunner, settings: RenderSettings): ...
    def render(self, request: RenderRequest) -> RenderOutcome: ...
```

Classify invalid candidate source, candidate timeout, and candidate render
exception as model-attributable zero-reward outcomes. Classify missing Manim,
broken runtime image, storage failure, and unavailable renderer as
infrastructure exclusions.

**Step 3: Implement evidence extraction**

- sample committed timestamps with FFmpeg;
- create a contact sheet with Pillow;
- OCR via pytesseract;
- detect frame bounds and safe-margin violations;
- record annotated object/focus metadata emitted by the fixture scene;
- hash every frame, contact sheet, and manifest.

Do not infer arbitrary Manim object identity from pixels. Laboratory scenes
emit explicit metadata; provider holdout uses OCR and annotated focus regions.

**Step 4: Add an opt-in render integration test**

Mark it `@pytest.mark.render` and skip with an actionable reason when Manim,
FFmpeg, or Tesseract is absent. Render one known-bad and one known-good fixture
and assert evidence files and directionally improved measurements.

**Step 5: Verify and commit**

```bash
uv run --project environments/m2m2_visual_improvement pytest -q
uv run --project environments/m2m2_visual_improvement pytest -m render -q
git add environments/m2m2_visual_improvement
git commit -m "feat: render visual evidence for RL scoring"
```

## Task 8: Implement Deterministic Relative Visual Scoring

**Files:**

- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/scoring.py`
- Create: `environments/m2m2_visual_improvement/tests/test_scoring.py`

**Step 1: Write failing arithmetic and metric tests**

Test:

```python
assert relative_score(0.8, 0.8) == 0.5
assert relative_score(1.0, 0.0) == 1.0
assert relative_score(0.0, 1.0) == 0.0
```

Then prove framing penalizes clipping/overlap/density, legibility penalizes
small or transient OCR text, and focus penalizes off-frame/wrong-scale target
regions. Assert final weights are exactly 0.25, 0.25, 0.20, and 0.30.

**Step 2: Implement pure metric functions**

All functions consume `VisualEvidence`, return `[0, 1]`, and expose raw
submetrics. Round only when serializing reports, never during reward
calculation.

**Step 3: Preserve visible educational content**

Compute required-token coverage from OCR text and formula-region annotations,
never from candidate source. Return an ineligible content-preservation outcome
when required concepts or narrative beats disappear.

**Step 4: Verify and commit**

```bash
uv run --project environments/m2m2_visual_improvement pytest \
  environments/m2m2_visual_improvement/tests/test_scoring.py -q
git add environments/m2m2_visual_improvement
git commit -m "feat: score relative visual quality"
```

## Task 9: Add the Blinded Pairwise Vision Judge

**Files:**

- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/judge.py`
- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/data/preference_calibration.jsonl`
- Create: `environments/m2m2_visual_improvement/tests/test_judge.py`
- Create: `environments/m2m2_visual_improvement/tests/test_judge_calibration.py`

**Step 1: Write failing tests using a fake multimodal client**

Prove:

- contact sheets are blinded as `A` and `B`;
- A/B and B/A are both requested at temperature zero;
- consistent votes map to loss/tie/win;
- disagreement maps to `0.5` and logs inconsistency;
- malformed output is an infrastructure exclusion, not candidate reward zero;
- prompts never expose which image is the baseline;
- no API key is serialized.

**Step 2: Implement a narrow judge protocol**

Use an injected client with one method:

```python
class PairwiseJudgeClient(Protocol):
    def compare(self, request: JudgeRequest) -> JudgeVote: ...
```

Keep Verifiers/endpoint adaptation outside the comparison logic.

**Step 3: Add calibration**

Build obvious clean/corrupted pairs from the held-out bases. The calibration
command exits nonzero unless order consistency is at least 90% and expected
clean-scene preference is above the predeclared threshold.

**Step 4: Verify and commit**

```bash
uv run --project environments/m2m2_visual_improvement pytest \
  environments/m2m2_visual_improvement/tests/test_judge.py \
  environments/m2m2_visual_improvement/tests/test_judge_calibration.py -q
git add environments/m2m2_visual_improvement
git commit -m "feat: add blinded visual preference judge"
```

## Task 10: Assemble the One-Action Verifiers Environment

**Files:**

- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/environment.py`
- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/verifiers_compat.py`
- Create: `environments/m2m2_visual_improvement/tests/test_environment.py`
- Modify: `environments/m2m2_visual_improvement/m2m2_visual_improvement/__init__.py`

**Step 1: Write failing environment tests**

Assert `load_environment()`:

- returns the current pinned `vf.Environment`;
- exposes train/validation/test splits without leakage;
- formats text plus baseline contact-sheet multimodal input;
- accepts `scope="code_only"` or `scope="spec_and_code"`;
- performs exactly one policy action and one reward transition;
- emits component rewards and a complete ledger;
- returns zero for candidate-attributable invalid output;
- raises/retries a typed infrastructure exclusion;
- never sends stderr back for a second model attempt.

**Step 2: Implement the compatibility boundary**

Only `verifiers_compat.py` may depend on version-sensitive Verifiers base
classes, dataset columns, state layout, or rubric callback signatures. Pin the
verified package version in `pyproject.toml` and expose a stable internal
adapter to `environment.py`.

The public entry point is:

```python
def load_environment(
    split: str = "train",
    scope: str = "spec_and_code",
    judge_model: str | None = None,
    render_backend: str = "sandbox",
) -> vf.Environment:
    ...
```

**Step 3: Compose the reward**

The environment must:

1. parse and validate the action;
2. apply the permitted scene-spec patch;
3. validate candidate safety and educational preservation;
4. render the candidate;
5. extract evidence;
6. run deterministic metrics and both judge orders;
7. serialize `RewardLedger`;
8. return the weighted reward.

**Step 4: Verify locally with Verifiers**

```bash
uv run --project environments/m2m2_visual_improvement python -c \
  "from m2m2_visual_improvement import load_environment; print(load_environment(split='validation'))"
uv run --project environments/m2m2_visual_improvement vf-eval \
  m2m2-visual-improvement -n 2
```

Use a fake/local judge for the offline test. Run a real endpoint only after
credential redaction tests pass.

**Step 5: Commit**

```bash
git add environments/m2m2_visual_improvement
git commit -m "feat: assemble render-grounded RL environment"
```

## Task 11: Prove the Old Reward Hacks No Longer Work

**Files:**

- Create: `environments/m2m2_visual_improvement/tests/test_reward_hacking.py`
- Create: `environments/m2m2_visual_improvement/m2m2_visual_improvement/fixtures/adversarial/`

**Step 1: Encode the observed exploit as a regression test**

The valid blank Manim scene with all required terms only in a Python comment
must be ineligible for visible-content preservation and receive total reward
`0.0`.

**Step 2: Add the remaining adversarial cases**

- delete all instructional text;
- replace the lesson with one oversized title;
- return unchanged baseline;
- delete difficult objects through the spec patch;
- move a required target off-screen and add whitespace;
- include a patch in `code_only`;
- patch spec and return code that contradicts it;
- exploit judge-order labels.

Expected: hacks receive zero or neutral exactly as specified; unchanged
baseline receives `0.5`, never `1.0`.

**Step 3: Run the complete environment suite**

```bash
uv run --project environments/m2m2_visual_improvement pytest -q
```

**Step 4: Commit**

```bash
git add environments/m2m2_visual_improvement
git commit -m "test: block visual reward exploits"
```

## Task 12: Build and Verify the Pinned Prime Runtime Image

**Files:**

- Create: `environments/m2m2_visual_improvement/runtime/Dockerfile`
- Create: `environments/m2m2_visual_improvement/runtime/.dockerignore`
- Create: `environments/m2m2_visual_improvement/runtime/requirements.lock`
- Create: `environments/m2m2_visual_improvement/runtime/smoke.py`
- Create: `environments/m2m2_visual_improvement/tests/test_runtime_contract.py`
- Modify: `environments/m2m2_visual_improvement/README.md`

**Step 1: Write a failing static runtime-contract test**

Assert exact base-image digest, non-root user, Python 3.12, Manim 0.19,
FFmpeg, TeX packages, Tesseract English data, locked dependencies, health
check, a dedicated build context, and a deny-by-default `.dockerignore`.

**Step 2: Implement the image**

Use an OCI image with:

- a digest-pinned base;
- `apt-get` packages in one deterministic layer;
- hashed Python requirements;
- a non-root `renderer` user;
- `/workspace/input` read-only by convention and separate writable output;
- `smoke.py` that renders a formula, runs OCR, and probes FFmpeg.

The build context is only
`environments/m2m2_visual_improvement/runtime/`. Its `.dockerignore` ignores
everything and then explicitly permits only `Dockerfile`,
`requirements.lock`, and `smoke.py`. The image must never upload the repository
root, `.git`, `.env`, run bundles, or user-owned untracked files.

**Step 3: Build locally if Docker is available**

```bash
docker build -t m2m2-visual-runtime:0.1.0 \
  -f environments/m2m2_visual_improvement/runtime/Dockerfile .
docker run --rm --network none m2m2-visual-runtime:0.1.0
```

If local Docker is absent, run the static test and use the Prime cloud build
in Step 4.

**Step 4: Push and record the immutable Prime image**

```bash
prime images push m2m2-visual-runtime:0.1.0 \
  --dockerfile Dockerfile \
  --context environments/m2m2_visual_improvement/runtime --public
prime images list
```

Wait for `Ready`, smoke-test it with `prime sandbox create`, then record the
exact `prime/...` reference and resolved digest. Never proceed with only the
mutable tag.

**Step 5: Verify and commit**

```bash
uv run --project environments/m2m2_visual_improvement pytest \
  environments/m2m2_visual_improvement/tests/test_runtime_contract.py -q
git add environments/m2m2_visual_improvement
git commit -m "build: pin Manim visual reward runtime"
```

## Task 13: Add Reproducible Experiment Configs and Ledger Management

**Files:**

- Create: `configs/eval/m2m2-visual-code-only.toml`
- Create: `configs/eval/m2m2-visual-hierarchical.toml`
- Create: `configs/rl/m2m2-visual-code-only-smoke.toml`
- Create: `configs/rl/m2m2-visual-hierarchical-smoke.toml`
- Create: `configs/rl/m2m2-visual-code-only.toml`
- Create: `configs/rl/m2m2-visual-hierarchical.toml`
- Create: `experiments/prime_rl/schema.json`
- Create: `experiments/prime_rl/ledger.py`
- Create: `experiments/prime_rl/tests/test_ledger.py`
- Modify: `.gitignore`

**Step 1: Write failing config/ledger tests**

Prove:

- all four arms share model, split, seeds, sampling, judge, and rollout budget
  except the intended scope/weight dimensions;
- smoke configs are 5 steps, batch 8, rollouts 2;
- full configs are 50 steps, batch 32, rollouts 4;
- no secret values or local secret-file paths appear;
- manifest schema requires every approved digest and run ID;
- a dirty run is marked non-publishable;
- atomic updates preserve a previous completed manifest.
- only `manifest.json` and `summary.md` are trackable beneath experiment run
  directories; downloaded rollouts, checkpoints, media, and logs remain
  ignored.

**Step 2: Implement configs using the current Prime schema**

Use:

```toml
model = "Qwen/Qwen3-VL-4B-Instruct"
max_steps = 5
batch_size = 8
rollouts_per_example = 2

[[env]]
id = "harleycooper/math-to-manim-visual-improvement"
args = { split = "train", scope = "code_only" }
```

Add exact sampling, eval interval, seed, image reference/digest, and W&B
project/name fields supported by the verified CLI. Do not invent unsupported
TOML keys; store extra reproducibility data in the repository ledger.

**Step 3: Implement ledger creation and redaction**

Hash files using streaming SHA-256. Capture Git SHA and porcelain status.
Allow `--allow-dirty` only for local development and force
`publishable=false`.

Add narrow `.gitignore` rules that re-include
`experiments/prime_rl/runs/**/manifest.json` and `summary.md` while retaining
the existing repository-wide `runs/`, media, image, log, and artifact ignores.

**Step 4: Verify and commit**

```bash
uv run --project environments/m2m2_visual_improvement pytest \
  experiments/prime_rl/tests/test_ledger.py -q
git add configs experiments/prime_rl .gitignore
git commit -m "feat: define Prime RL experiment matrix"
```

## Task 14: Implement the Single Experiment Launcher

**Files:**

- Create: `scripts/prime_visual_experiment.py`
- Create: `experiments/prime_rl/tests/test_launcher.py`
- Modify: `experiments/prime_rl/README.md`

**Step 1: Write failing CLI tests**

Use injected command runners. Cover:

- `prepare`
- `validate`
- `publish-image`
- `publish-environment`
- `baseline`
- `train`
- `collect`
- `compare`

Assert exact argument arrays rather than shell strings, Windows-to-WSL path
normalization, secret redaction, nonzero propagation, dirty-tree refusal,
opaque Prime ID capture, fixed retry budgets, and no command execution in
`--dry-run`.

**Step 2: Implement with `argparse` and argument arrays**

Never use `shell=True`. The launcher is orchestration only; it must call
`prime eval run`, `prime train run`, `prime env push`, and `prime images push`
rather than implementing an optimizer.

Use:

```python
COMMANDS = (
    "prepare",
    "validate",
    "publish-image",
    "publish-environment",
    "baseline",
    "train",
    "collect",
    "compare",
)
```

Every mutating command creates or atomically updates a run ledger.

**Step 3: Implement comparison**

Require all A/B/C/D result files and identical held-out task IDs. Report:

- D minus A win-rate percentage points;
- D versus B and C;
- content-preservation regression versus A;
- judge order consistency;
- eligibility and infrastructure exclusion rates;
- component deltas and bootstrap confidence intervals.

Exit zero for a valid negative result, but mark `success_criteria_met=false`.
Exit nonzero only for invalid or incomplete evidence.

**Step 4: Verify and commit**

```bash
uv run --project environments/m2m2_visual_improvement pytest \
  experiments/prime_rl/tests/test_launcher.py -q
python scripts/prime_visual_experiment.py validate --dry-run
git add scripts/prime_visual_experiment.py experiments/prime_rl
git commit -m "feat: orchestrate repeatable Prime experiments"
```

## Task 15: Replace Misleading RL Documentation and Preserve README Assets

**Files:**

- Modify: `README.md`
- Replace: `docs/PRIME_INTELLECT_RL.md`
- Modify: `environments/m2m2_visual_improvement/README.md`
- Modify: `experiments/prime_rl/README.md`
- Create: `tests/test_prime_rl_docs.py`

**Step 1: Write failing documentation assertions**

Assert:

- README showcase GIFs and star chart references remain unchanged;
- ordinary prompt retries are never called reinforcement learning;
- the old `harleycooper/math-to-manim` environment is labeled deprecated;
- the new environment ID is present;
- docs distinguish repository-owned environment/reward/data from Prime-hosted
  weight updates;
- docs describe rendered candidate-versus-baseline scoring and editable spec;
- docs include exact prepare/eval/train/collect/compare commands;
- no stray `-christian` signature exists;
- no secret-like assignments are committed.

**Step 2: Rewrite the Prime guide**

Document:

1. architecture and typed action;
2. dataset generation and provider export;
3. runtime image build/publish;
4. local validation;
5. public environment publish;
6. A/B baseline evaluation;
7. C/D hosted smoke and full training;
8. result collection/comparison;
9. limitations, cost, judge dependence, and negative-result reporting.

Link the design and implementation plan. State that Prime Hosted Training is
external and performs actual optimizer updates.

**Step 3: Update README minimally**

Keep the showcase and star chart byte-for-byte intact. Replace the stale RL
link context with a short, accurate “Visual-improvement RL experiment”
section.

**Step 4: Verify and commit**

```bash
pytest tests/test_prime_rl_docs.py tests/test_gifs.py \
  tests/test_erdos_1038_readme.py tests/test_readme_learner_first.py -q
pytest -q
git add README.md docs/PRIME_INTELLECT_RL.md \
  environments/m2m2_visual_improvement/README.md \
  experiments/prime_rl/README.md tests/test_prime_rl_docs.py
git commit -m "docs: describe the real visual RL experiment"
```

## Task 16: Run Full Local Verification

**Files:**

- Modify only files needed to fix failures revealed by this task.
- Create: `experiments/prime_rl/runs/local-verification/manifest.json`
- Create: `experiments/prime_rl/runs/local-verification/summary.md`

**Step 1: Run static and offline suites**

```bash
git diff --check
pytest -q
uv run --project environments/m2m2_visual_improvement pytest -q
```

**Step 2: Run root offline products**

Use a fresh repo-local temporary runs directory and preserve the resulting
manifests only in the local verification summary:

```bash
math-to-manim run "the heat equation" --offline
math-to-manim-sol run "why Fourier modes solve the heat equation" --offline
math-to-manim-sol doctor
```

**Step 3: Run rendering and reward-hack integration**

```bash
uv run --project environments/m2m2_visual_improvement pytest -m render -q
python scripts/prime_visual_experiment.py prepare \
  --run-id local-verification --allow-dirty
python scripts/prime_visual_experiment.py validate \
  --run-id local-verification --allow-dirty
```

Confirm that:

- the known visual improvement beats its degraded baseline;
- the comment-only blank scene scores zero;
- unchanged baseline scores neutral;
- both adapters remain import-isolated;
- no secrets or absolute local paths appear in the ledger.

**Step 4: Record exact evidence**

Write counts, versions, digests, skipped tests, durations, and limitations.
Do not claim Prime smoke validation yet.

**Step 5: Commit**

```bash
git add experiments/prime_rl/runs/local-verification
git commit -m "test: record local visual RL verification"
```

## Task 17: Publish the Environment and Run Bounded Prime Smoke Experiments

**Files:**

- Create: `experiments/prime_rl/runs/{run-id}/manifest.json`
- Create: `experiments/prime_rl/runs/{run-id}/summary.md`
- Modify: `docs/PRIME_INTELLECT_RL.md`

**Step 1: Authenticate and verify scope**

Run `prime login` only if current credentials lack environment/image or hosted
training permission. Do not copy the key from `C:\Users\chris\Daily\.env`;
that file contains no Prime key. Use the Prime login flow and report only
authorization status.

Set one task-specific run identifier and reuse it throughout:

```bash
prime_smoke_run_id="$(date -u +%Y%m%dT%H%M%SZ)-prime-smoke"
```

**Step 2: Publish and verify the runtime**

Run the launcher’s `publish-image`, wait for `Ready`, create a sandbox, execute
the runtime smoke test, and store the resolved digest.

**Step 3: Publish the new environment**

```bash
python scripts/prime_visual_experiment.py publish-environment \
  --visibility PUBLIC --run-id "$prime_smoke_run_id"
```

Install the published version into a clean environment and evaluate two
validation tasks. Confirm Hub ID/version/archive digest match the ledger.

**Step 4: Capture untuned A/B baselines**

Run both held-out eval configs with identical task IDs and seeds. Save opaque
evaluation IDs and aggregate/component results.

**Step 5: Launch only the bounded C/D smoke configs**

```bash
python scripts/prime_visual_experiment.py train \
  --config configs/rl/m2m2-visual-code-only-smoke.toml \
  --run-id "$prime_smoke_run_id"
python scripts/prime_visual_experiment.py train \
  --config configs/rl/m2m2-visual-hierarchical-smoke.toml \
  --run-id "$prime_smoke_run_id"
```

Do not launch 50-step runs in this task. Verify weight updates, nonzero reward
variance, render evidence, judge calls, ledger capture, and cost/usage.

**Step 6: Evaluate C/D and compare all four arms**

Collect checkpoints/adapters, run the held-out suite, and execute `compare`.
Report the smoke result as plumbing evidence, not as a scientific conclusion.

**Step 7: Commit smoke evidence**

```bash
git add "experiments/prime_rl/runs/$prime_smoke_run_id" \
  docs/PRIME_INTELLECT_RL.md
git commit -m "test: record Prime visual RL smoke run"
```

## Task 18: Final Review, Push, and Pull Request

**Files:**

- Modify only issues found during final review.

**Step 1: Review the complete branch**

```bash
git status --short
git diff --check origin/main...HEAD
git diff --stat origin/main...HEAD
git log --oneline origin/main..HEAD
```

Verify user-owned untracked files are absent from every commit.

**Step 2: Run final tests from clean dependency state**

```bash
pytest -q
uv sync --project environments/m2m2_visual_improvement --locked
uv run --project environments/m2m2_visual_improvement pytest -q
```

Run render tests and the published-environment two-task eval once more.

**Step 3: Request code review**

Use `superpowers:requesting-code-review`. Resolve all critical findings and
rerun affected tests.

**Step 4: Push the feature branch**

```bash
git push -u origin codex/prime-visual-improvement-rl
```

**Step 5: Create a ready pull request**

The PR must summarize:

- why the old critique was valid;
- the one-action render-grounded environment;
- hierarchical spec+code actions;
- deterministic 144-task grouped dataset;
- anti-reward-hacking evidence;
- local and Prime smoke results;
- exact limitations and whether predeclared thresholds were evaluated.

Do not claim the full experiment succeeded unless the 50-step C/D runs were
separately authorized, completed, and met every predeclared criterion.

**Step 6: Hand off**

Provide the branch, PR, public environment/version, Prime image digest, smoke
run IDs, test counts, known limitations, and the exact command that would
launch the full experiment after explicit cost approval.
