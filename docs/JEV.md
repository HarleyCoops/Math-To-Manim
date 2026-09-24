# jev: independent mathematics and render evaluation

Jev scores rendered candidates and returns revision feedback. It lives in
`sol/`, uses the Codex CLI with cached ChatGPT login, and has no API-key or HTTP
fallback. It does not call Mythos or update model weights.

## Run

```bash
math-to-manim-sol run "Explain Fourier modes" --render --evaluator jev --max-repairs 2
math-to-manim-sol resume <run-id>
```

The default reviewer remains the saved cinematographer. Jev runs only for live
rendered requests. `--offline` produces no jev assessment; omitting `--render`
also skips evaluation. Resume uses the saved evaluator choice and performs
fresh rendering and review. Each invocation permits at most `max_repairs`
review/render repairs; manual resume starts a new bounded budget.

## Model and isolation

Jev explicitly selects `gpt-6-astra` with `model_reasoning_effort="high"`,
independently of the writer's settings. This is a starting configuration, not a
measured optimum. On September 24, 2026, the
[official Astra model page](https://developers.openai.com/api/docs/models/gpt-6-astra)
and the local Codex catalog both supported `high`. The
[Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
documents the reasoning setting. Local verification used CLI 0.146.0; its
`exec --help` lists `--model`, `--sandbox read-only`, `--image`, and
`--output-schema`. The local catalog also listed `ultra`; jev uses the shared
documented `high` setting. Account access still requires a live run.

Every assessment starts a fresh session without a writer session ID. The client
requests a read-only sandbox, attaches rendered images, and tells the reviewer
to treat candidate files as evidence rather than instructions. The CLI writes
its final response through `--output-last-message`; the reviewer need not write
files. The Python wrapper writes audit records.

Independence means a separate session, role, and permissions. It does not mean
statistically independent errors or a formal security boundary against all
locally configured tools. Hash checks detect changes to supplied evidence
during review and fail the run if it changes.

## Assessment and acceptance

The typed assessment has `mathematics` and `presentation` criteria. Each has a
finite score in [0, 1], a boolean `verified`, a rationale, and exact relative
evidence paths. Lists record defects, observations, and limitations. Rubric
anchors are 0 (unusable), 0.5 (major repair), 0.8 (acceptable on inspected
evidence), and 1 (no issue found on inspected evidence).

The wrapper approves only when both criteria are verified, both scores are at
least 0.8, and there are no defects. The threshold is provisional. Missing
frames, invalid JSON/scores/citations, reviewer errors, and evidence mutations
fail the run. Low scores or unverified criteria generate repair feedback even
when no explicit defects were returned.

Mathematical rejection restarts the math director and downstream visual planning
and composition. Presentation-only low scores restart scene composition.
Explicit free-text defects conservatively restart the math director too,
because a defect can contradict a high score. The full assessment accompanies
feedback. Revised candidates are statically validated, rendered, and assessed
again. Exhausting the repair budget fails the run.

## Evidence and audit trail

Each `runs/sol/<run-id>/jev/NNN/` contains:

- `inputs/`: copies of the dossier, scene specification, source, and frames;
- `record.json`: request, reviewer settings, timestamps, SHA-256 input hashes,
  status/error, and the `uncalibrated_model_judgment` score label;
- `assessment.schema.json`, `assessment.json`, and `trace.jsonl`: schema and
  CLI response/trace (availability depends on where a failed call stops);
- `review.json`: the acceptance decision and feedback after a valid assessment.

Root `review.json` is cleared when a new jev review starts, so failure cannot
leave an earlier approval as current. Attempt directories are never reused.
Manifests preserve repair feedback; resume never trusts an old approval.
Rendering rejects unchanged old video output and removes old target frames
before extracting replacements.

Sampled stills cannot establish continuous motion quality, timing, narration
synchronization, or every transient layout defect. Mathematical review is a
model judgment, not a proof certificate. Copied inputs support later human
audits; the local filesystem is not an immutable evidence store.

## Human calibration before reward use

1. Build held-out cases with known mathematical errors, notation/clipping
   defects, correct controls, and failures between sampled frames. Keep these
   separate from repair training data.
2. Have two human reviewers score candidates without jev's verdict. Adjudicate
   disagreements and preserve reference explanations.
3. Repeat jev assessments on unchanged bundles. Measure false approvals and
   rejections separately for math and presentation, human agreement, score
   variation, and paired before/after repair outcomes.
4. Tune rubric, frame sampling, and thresholds on a development split. Report
   results on untouched held-out cases. Version any reward mapping separately
   and audit reward gaming during actual RL training.

No calibration results or training gains are claimed by this implementation.

## Offline verification

```bash
python -m pytest tests/test_jev.py tests/test_sol_silo.py tests/test_sol_staged_pipeline.py
python -m pytest
```

Fake CLI responses and renders test isolation, score validation, citations,
mutations, snapshots, rejection feedback, math repair routing, bounded retries,
and resume review. They do not establish live model or rendering quality.
