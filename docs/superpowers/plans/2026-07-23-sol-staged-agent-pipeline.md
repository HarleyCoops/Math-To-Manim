# Sol Staged Agent Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a resumable six-role GPT-5.6 Sol pipeline with streamed JSONL observability, validated artifact handoffs, narrow repair routing, and a live Erdős 1038 production run.

**Architecture:** Keep the existing Sol artifact contract but replace the single long-horizon call with role-specific Codex sessions governed by a dependency graph. Stream every Codex JSONL event to per-stage traces and metadata, store thread IDs for `codex exec resume`, and let the Python wrapper own validation and rendering.

**Tech Stack:** Python 3.10+, Pydantic 2, Codex CLI 0.144+, GPT-5.6 Sol, pytest, Manim CE, FFmpeg.

## Global Constraints

- Sol remains Codex CLI-only with cached ChatGPT authentication.
- Never import Mythos prompts, agents, backends, or orchestration.
- Remove `OPENAI_API_KEY` from every Codex child process.
- Preserve all existing root artifact filenames.
- JSONL streams feed observability only; handoffs use completed, validated JSON.
- Live agents use separate durable Codex thread IDs.
- Work on `main` is explicitly authorized by the user.
- Preserve unrelated untracked `scripts/*.ps1` and `tmp/`.

---

### Task 1: Stream Codex JSONL and Support Session Resume

**Files:**
- Modify: `sol/client.py`
- Modify: `sol/models.py`
- Test: `tests/test_sol_staged_pipeline.py`

**Interfaces:**
- Consumes: `CodexCli.run(..., event_sink=None, session_id=None)`.
- Produces: immediate JSONL trace writes, parsed event callbacks, and `codex exec resume`.

- [ ] Write tests proving `build_command(..., session_id=...)` emits the resume form and a fake process delivers `thread.started` before returning.
- [ ] Run the focused tests and confirm failures are caused by the missing parameters and streaming implementation.
- [ ] Replace buffered `subprocess.run` with a bounded `subprocess.Popen` implementation that drains stdout/stderr concurrently, flushes JSONL lines, and invokes the optional sink.
- [ ] Run the focused tests and existing Sol client tests.
- [ ] Commit the streaming client.

### Task 2: Define the Six Sol-Native Agent Contracts

**Files:**
- Create: `sol/agents.py`
- Modify: `sol/models.py`
- Test: `tests/test_sol_staged_pipeline.py`

**Interfaces:**
- Produces: `AgentStage`, `AGENT_STAGES`, `StageRunResult`, `StageRecord`, and `build_stage_prompt`.
- Consumes: original request plus declared upstream root artifacts.

- [ ] Write tests for exact role order, dependency edges, disjoint parallel writes, prompt boundaries, and absence of Mythos references.
- [ ] Run the tests and observe missing-contract failures.
- [ ] Add the six concise Sol-native charters and strict structured-result models.
- [ ] Run the focused tests.
- [ ] Commit the role contracts.

### Task 3: Add Staged Orchestration, Cache, and Resume

**Files:**
- Create: `sol/staged.py`
- Modify: `sol/harness.py`
- Modify: `sol/service.py`
- Modify: `sol/cli.py`
- Modify: `sol/offline.py`
- Test: `tests/test_sol_staged_pipeline.py`
- Test: `tests/test_sol_silo.py`

**Interfaces:**
- Produces: `StagedPipeline.run(run_dir, request)`, `SolHarness.resume(run_id, from_stage=None)`, and CLI `resume`/`status`.
- Consumes: `AgentStage`, `CodexCli`, existing validation, request, and root artifacts.

- [ ] Write failing tests for six offline stage records, cache hits, invalidation from a named stage, thread capture, and CLI parsing.
- [ ] Run focused tests and confirm expected failures.
- [ ] Implement stage hashing, atomic stage records, the dependency graph, two-branch execution, artifact validation, and resume.
- [ ] Adapt offline rehearsal to emit the same stage ledger.
- [ ] Run focused and existing Sol tests.
- [ ] Commit staged orchestration.

### Task 4: Move Rendering and Review Routing into the Wrapper

**Files:**
- Create: `sol/rendering.py`
- Modify: `sol/staged.py`
- Modify: `sol/validation.py`
- Test: `tests/test_sol_staged_pipeline.py`

**Interfaces:**
- Produces: render preflight, `python -m manim` command construction, contact-sheet extraction, deterministic review evidence, and scene-composer resume on render defects.

- [ ] Write failing tests for use of `sys.executable -m manim`, run-local MiKTeX paths, final-MP4 selection over partial fragments, and targeted scene-composer repair.
- [ ] Run tests and confirm missing behavior.
- [ ] Implement wrapper-owned render and representative-frame evidence.
- [ ] Route code/render failures to the saved scene-composer session; route visual review to the cinematographer session.
- [ ] Run focused and full offline tests.
- [ ] Commit rendering and repair routing.

### Task 5: Document, Run Erdős 1038, and Package the Showcase

**Files:**
- Modify: `docs/SOL_5_6_SILO.md`
- Modify: `README.md`
- Create: `docs/showcase/assets/erdos-1038-potential-landscape.gif`
- Generate only: `runs/sol/<staged-erdos-run>/`

**Interfaces:**
- Consumes: `docs/prompts/erdos-1038-off-white-3d.md`.
- Produces: a staged manifest, six role ledgers, validated Manim scene, MP4, contact sheet, curated GIF, and README feature.

- [ ] Update architecture and CLI documentation after tests define the final surface.
- [ ] Run the exact prompt offline and verify six stage records.
- [ ] Run `doctor` and the staged live render with the repository-pinned Codex CLI.
- [ ] Inspect the manifest, role thread IDs, scene source, MP4 metadata, representative frames, and contact sheet.
- [ ] Repair only evidence-backed defects through the responsible saved session.
- [ ] Produce and inspect the curated GIF, then add the README feature without disturbing the star chart or existing showcase.
- [ ] Run the entire pytest suite, `git diff --check`, media probes, and repository status review.
- [ ] Commit only source, tests, docs, curated media, and README changes.
