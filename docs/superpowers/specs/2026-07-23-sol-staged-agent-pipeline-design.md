# Sol Staged Agent Pipeline Design

## Goal

Replace the Sol silo's opaque whole-film Codex call with a resumable,
Codex-native pipeline that preserves the six specialist roles, streams JSONL
events into a local ledger, and passes only validated JSON artifacts between
roles.

The six roles are:

1. intent
2. cartographer
3. curriculum
4. math-director
5. cinematographer
6. scene-composer

## Provider Boundary

Every reasoning stage uses the repository-pinned Codex CLI, cached ChatGPT
login, and `gpt-5.6-sol`. The staged pipeline must not import Mythos prompts,
charters, backends, or orchestration. It remains CLI-only and removes
`OPENAI_API_KEY` from every child process.

## Execution Graph

```text
preflight
    |
intent
    |
    +-- cartographer -> curriculum --+
    |                                |
    +-- math-director ---------------+
                                     |
                              cinematographer
                                     |
                              scene-composer
                                     |
                    static validation and render
                                     |
                       cinematographer review
                                     |
                         targeted repair routing
```

The cartographer/curriculum branch and math-director branch may run
concurrently because they write disjoint artifacts. All other dependencies
are explicit.

## Durable Agents

Each role starts one Codex session. The `thread.started` event supplies its
thread ID, which is stored in `stages/<stage>.json`. Follow-up work uses
`codex exec resume <thread-id>` so a render defect returns to the original
scene-composer and a visual-review turn returns to the original
cinematographer.

Each stage record contains:

- role and lifecycle status;
- input and output hashes;
- thread ID;
- start and completion timestamps;
- JSONL trace path;
- structured result path;
- event count and attempts.

## Streaming and Handoffs

Codex stdout is JSONL. The client writes each line to the trace immediately,
flushes it, parses valid events, and forwards them to an event sink. The
orchestrator uses these events for thread capture and progress metadata.

Partial stream events are never passed directly to another role. A role
handoff occurs only after:

1. the Codex command exits successfully;
2. its strict structured result validates;
3. every declared artifact exists;
4. JSON artifacts parse as non-empty objects;
5. the artifact hash is recorded.

This separates observability from the durable information contract.

## Artifact Compatibility

The existing root artifacts remain canonical:

- `01_intent.json`
- `02_knowledge_map.json`
- `03_curriculum.json`
- `04_math_dossier.json`
- `05_shot_list.json`
- `06_scene_spec.json`
- `sol_scene.py`
- `review.json`
- `manifest.json`

New metadata is additive under `stages/`. Existing validation and consumers
continue to work.

## Cache and Resume

A stage input hash covers:

- original user request;
- stage charter version and role;
- model and reasoning effort;
- hashes of declared upstream artifacts.

When the hash matches a completed stage record and its artifacts still match
their stored hashes, the stage is a cache hit. `resume <run-id> --from
<stage>` invalidates that stage and every downstream stage while retaining
unaffected work.

## Render Ownership and Repair Routing

The wrapper owns environment preflight, compilation, Manim execution,
FFmpeg frame extraction, and final validation. Agents do not rediscover the
runtime.

Failures route narrowly:

- runtime/toolchain failure: wrapper only;
- mathematical defect: resume math-director and invalidate downstream stages;
- story or framing defect: resume cinematographer, then scene-composer;
- Python, layout, or render defect: resume scene-composer only.

The wrapper produces representative frames and a contact sheet before asking
the cinematographer to review the rendered film.

## CLI

The default `run` command uses staged execution. Add:

```text
math-to-manim-sol resume <run-id> [--from <stage>]
math-to-manim-sol status <run-id>
```

`--offline` rehearses the same graph and stage ledger without model calls or
rendering.

## Acceptance

- All six roles have separate stage records and thread IDs in a live run.
- JSONL reaches trace files during execution rather than after process exit.
- Agent handoffs use validated final artifacts.
- Repairs use `codex exec resume` with the responsible role's thread.
- Offline tests cover graph order, cache invalidation, streamed events,
  session resumption, and provider isolation.
- A staged live run of the existing Erdős 1038 prompt produces a validated
  off-white true-3D film and review evidence.

