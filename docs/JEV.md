# TypeSafe Jev decision contract

Jev is TypeSafe's separate System One model, **jev-1.13.0**, accessed with
**typesafe-sdk 0.7.1** and `TYPESAFE_API_KEY`. It is not an Astra persona.
Earlier Sol reviewer code used the name “jev” incorrectly; it is now named
`sol/astra_reviewer.py`, with the explicit `--evaluator astra_review` option.
Historical review artifacts retain their original records; they are not
TypeSafe evaluations. The primary `astra/jev.py` implementation is authoritative.

At every brief, mathematics, storyboard, scene and render checkpoint:

1. Astra audits the exact candidate and relevant upstream artifacts in a fresh
   Codex SDK session. The render auditor also receives sampled frame images.
2. The harness validates exact evidence citations and checks SHA-256 hashes.
3. Jev receives text artifacts, the Astra audit, checkpoint and original request.
   Images are represented only by explicitly attributed Astra observations.
4. Two atomic Score questions evaluate checkpoint-specific evidence. Each must
   score at least 3.2 on a 0–4 rubric, with confidence at least 0.65.
5. Noul evidence sufficiency must be at least 0.8; Noul blocking defect
   probability must be at most 0.2. An unresolved Astra blocker also rejects.
6. Choice selects the repair role. Confidence below 0.65 routes to the current
   stage for more evidence. Routing never skips an unapproved earlier stage.

The thresholds are provisional engineering policy, not calibrated accuracy.
Jev confidence reflects answer distributions, not a proof of correctness.
Human calibration should label held-out accepted and rejected artifacts,
measure false accept/reject rates by stage, then version any policy changes.
Sampled frames cannot verify every instant of motion. Jev cannot see pixels.

## Authentication and failure

Save `TYPESAFE_API_KEY=your-key` in the repository's git-ignored `.env.local`
or provide the process environment variable. The local file is read directly
into the TypeSafe client, never exported to Astra or the renderer. Codex uses
cached ChatGPT login separately. Credentials are never written to run artifacts.
Missing keys, API failures, malformed responses and exhausted repair budgets
stop the run. There is no simulated or Astra fallback for a live Jev gate.

## Audit trail

Each attempt stores the Astra audit, exact input hashes, TypeSafe request state,
raw typed response and deterministic gate decision. Feedback derived from the
Astra audit is explicitly labeled; Jev does not generate that prose. Approved
stages bind the original request and all upstream artifact hashes. A changed
artifact or evaluation policy invalidates cached approvals. Resume rerenders and
rechecks the film. Offline tests use explicit fakes and are never live evidence.

[TypeSafe introduction](https://docs.typesafe.ai/introduction) ·
[Python SDK](https://docs.typesafe.ai/sdk/python) ·
[Confidence](https://docs.typesafe.ai/confidence)

## Jev-selected investigations

Jev does not execute tools or generate recommendations in prose. The CLI offers
an allowlisted action menu as a Choice question. The host executes a selected
action through a focused Astra session; that session uses tools and writes
specific evidence-backed recommendations. Its text is labeled as Astra's.

| Action | Investigation |
|---|---|
| `check_math` | Calculate formulas, check domains and topology, inspect primary references |
| `clarify_definitions` | Locate first use, propose definitions and exact teaching order |
| `inspect_scene` | Check source and installed Manim APIs; recommend specific corrections |
| `inspect_frames` | Inspect actual frames and identify visible problems by filename |
| `replan_camera` | Recommend camera targets, zoom, labels, colors and holds |
| `no_action` | No additional investigation |

Actions are filtered by checkpoint. Confidence below 0.65 does not dispatch a
tool. Rejected gates can request one investigation before the ordinary bounded
repair loop continues. Investigation never overrides a rejected gate and never
edits a candidate. A repaired candidate must pass a new audit and Jev gate.

```bash
math-to-manim recommend runs/astra/<run-id> --stage storyboard --attempt 3
math-to-manim recommend runs/astra/<run-id> --stage storyboard --attempt 3 --execute
```

The first command records Jev's selection; `--execute` runs it when confident.
Standalone reports remain advisory and do not change the active run's approvals.
Requests, responses, action probabilities, evidence hashes and investigation
reports are retained under `recommendations/` (or `attempts/` for gate-triggered
actions). This is host-dispatched tool routing, not native Jev function calling.

[TypeSafe: Jev with coding agents](https://docs.typesafe.ai/introduction/coding-agents)

See the [verbose artistic decision map](JEV_DESIGN_MAP.md) for all 16 rubrics,
evidence requirements, repair actions and verification criteria.
