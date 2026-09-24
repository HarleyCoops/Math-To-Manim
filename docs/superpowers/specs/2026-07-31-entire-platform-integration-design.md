# ENTIRE Platform Integration Design

**Date:** 2026-07-31

**Status:** Approved for implementation planning

**Repository:** `HarleyCoops/Math-To-Manim`

**ENTIRE region:** US East

**Checkpoint repository:** private `HarleyCoops/math-to-manim-checkpoints`

## Summary

Math-To-Manim will adopt ENTIRE in two ordered milestones.

Milestone one establishes ENTIRE as the agent-development system of record and
as a high-throughput Git read path. The public GitHub repository remains the
source of truth for code and releases. Full Codex and Claude Code transcripts
are stored in a separate private checkpoint repository. A US-East ENTIRE mirror
serves clone and fetch traffic for North American agents and RL workers.

Milestone two adds a provider-neutral `entire-agent-m2m` integration. It turns
Mythos films, Sol films, visual-improvement RL experiments, and model-harness
rollouts into native ENTIRE sessions without placing ENTIRE in any provider's
orchestration or rendering control path. The captured corpus is suitable for
later model-harness training because it preserves prompts, outputs, stage
decisions, code revision, artifacts, timing, tokens, render evidence, and
rewards with stable identifiers.

## Goals

1. Capture future Codex and Claude Code development sessions with prompts,
   responses, tool activity, file changes, timing, token usage, checkpoints,
   and attribution when the underlying agent exposes them.
2. Import every locally discoverable repository-scoped historical Codex and
   Claude Code session after a dry-run and privacy review, including sessions
   older than ENTIRE's default one-month scan window.
3. Keep all permanent checkpoint and transcript data out of the public source
   repository.
4. Create a US-East ENTIRE mirror that agents and RL workers can use for Git
   clone and fetch traffic while GitHub remains the durable upstream.
5. Preserve the existing Git LFS behavior and route LFS object transfers to
   GitHub because ENTIRE mirrors do not currently serve Git LFS.
6. Capture Mythos, Sol, and RL executions as coherent, queryable M2M sessions.
7. Preserve enough normalized session context to build supervised examples,
   preference pairs, failure corpora, reward-analysis datasets, and harness
   replay inputs later.
8. Keep `mythos/` and `sol/` provider-native and independently operable.
9. Make all ENTIRE capture fail open: generation, rendering, evaluation, and
   training must continue when ENTIRE is absent or unhealthy.

## Non-goals

- ENTIRE will not replace GitHub issues, pull requests, Actions, releases, or
  the public project homepage.
- ENTIRE will not become an application runtime for Mythos, Sol, Manim, Prime
  Hosted Training, or the visual-improvement environment.
- The integration will not route Sol through Mythos, route Mythos through Sol,
  or introduce a shared provider client.
- Binary videos, frame archives, model weights, caches, virtual environments,
  and render media will not be copied into checkpoint transcripts.
- Milestone two will not redesign the reward function or training algorithm.
- ENTIRE-native unmirrored branches will not hold irreplaceable work because
  ENTIRE does not currently back them up.

## Current-state constraints

- The checkout is on `codex/prime-visual-improvement-rl` and contains unrelated
  uncommitted renderer and RL-test work. ENTIRE changes must be staged by exact
  path and must not amend, reset, clean, or otherwise absorb that work.
- GitHub CLI is authenticated as `HarleyCoops` with repository access.
- The stable ENTIRE release inspected for this design is `v0.9.0`, published
  2026-07-27, with a native Windows ARM64 archive and published checksums.
- Scoop and Go are not installed. Installation will therefore use the official
  Windows ARM64 release archive and verify its checksum.
- Four existing Git hooks (`post-checkout`, `post-commit`, `post-merge`, and
  `pre-push`) invoke Git LFS. ENTIRE must preserve or chain these hooks.
- The project has Claude Code local settings and no project-level Codex hook
  files. ENTIRE must merge settings rather than replace unrelated keys.
- Historical LFS objects exist under retired material. A mirror checkout must
  still configure `lfs.url` to GitHub before downloading LFS objects.
- `runs/`, media, output, logs, environments, and local secrets have different
  retention rules. Only normalized session metadata and textual transcript
  records belong in ENTIRE.

## Architecture

```text
                                  +-------------------------------+
                                  | private GitHub checkpoint repo |
                                  | entire/checkpoints/v1          |
                                  +---------------^---------------+
                                                  |
                  built-in Codex/Claude capture --+-- M2M plugin capture
                                                  |
+---------------------------+       +-------------+--------------+
| public GitHub source repo |<----->| US-East ENTIRE mirror      |
| code, PRs, releases       |       | regional clone/fetch path  |
+-------------^-------------+       +-------------^--------------+
              |                                   |
              +--------- humans and agents -------+
                                                  |
                                  +---------------+----------------+
                                  | North American RL/harness fleet |
                                  +--------------------------------+
```

The local checkout keeps `origin` pointed at GitHub during initial validation.
The mirror is added as a separate remote named `entire`. After the mirror has
passed clone, fetch, comparison, LFS, and push-through checks, automated agents
may use the `entire://` URL as their read remote. Human development may retain
GitHub as `origin`; no hard cutover is required.

## Milestone one: foundation

### 1. Install and authenticate

The official `entire_windows_arm64.zip` for the pinned stable release is
downloaded to a temporary directory, verified against `checksums.txt`, and
installed to a user-local executable directory already on `PATH` or added to
the user `PATH`. Installation must not introduce Scoop or Go solely for this
binary. `entire version` must report the expected release before setup proceeds.

`entire login` performs device authentication. Authentication state is checked
with `entire auth status`. The ENTIRE GitHub App is authorized only for the
public Math-To-Manim source repository and the private checkpoint repository
unless the user explicitly broadens access later.

### 2. Private checkpoint repository

Create `HarleyCoops/math-to-manim-checkpoints` as a private, empty GitHub
repository. The source and checkpoint repositories share the same GitHub owner,
which ENTIRE requires for checkpoint pushes from this source repository.

The project-level ENTIRE configuration points checkpoint storage to:

```text
github:HarleyCoops/math-to-manim-checkpoints
```

The shared settings also enable external-agent discovery for milestone two,
enable PII redaction for email and phone values, and disable anonymous CLI
telemetry. The settings may name the private repository because the name is not
treated as a secret. Credentials and tokens never enter project settings.

### 3. Built-in agent hooks

Enable ENTIRE for Codex, then add Claude Code through ENTIRE's agent command.
The generated project hook files are committed when they are designed to be
shared. Local authentication, logs, temporary markers, and personal overrides
remain ignored.

Before and after hook installation, record the content or hashes of:

- the four active Git LFS hooks;
- `.claude/settings.local.json` keys;
- any newly created `.codex/hooks.json` and `.codex/config.toml`;
- `.entire/settings.json` and `.entire/.gitignore`.

Setup passes only if the existing LFS hook behavior remains reachable and the
Claude permission settings remain present.

### 4. Historical development sessions

Run dry-run imports for every locally supported repository-scoped Codex and
Claude Code transcript store. ENTIRE's default import scans the past month, so
also enumerate older repository-scoped transcript IDs from the local stores and
submit them through repeated explicit `--session` imports. Save a local, ignored
reconciliation inventory containing agent name, session ID, turn count, date,
source path, import disposition, and checkpoint ID. Do not copy transcript
bodies into the public working tree.

Review the resulting private checkpoint branch locally before its first push.
After the review, run the real imports. Imports are expected to be idempotent,
searchable, explainable, read-only, unlinked to source commits, and not
rewindable. Re-running each import must report no duplicate turns. Reconcile
the inventory against ENTIRE after import. Any transcript the installed CLI
cannot parse remains in the inventory with a concrete error and is handled by
the historical adapter in milestone two; it is never silently omitted.

### 5. US-East mirror

Create the mirror for `github.com/HarleyCoops/Math-To-Manim` in ENTIRE's
US-East cluster and add the returned `entire://` URL as a local remote named
`entire`. Do not replace or delete `origin` during initial setup.

Verification uses a fresh disposable clone and covers:

- default-branch and current-branch refs match GitHub;
- ordinary Git object fetches succeed through ENTIRE;
- LFS is explicitly directed to GitHub and required LFS objects can be pulled;
- a disposable mirrored branch can be pushed through ENTIRE to GitHub and then
  deleted through normal GitHub workflow;
- a checkpoint push reaches only the private checkpoint repository;
- no `entire/checkpoints/v1` ref appears in the public source repository.

### 6. Foundation smoke checkpoint

Start a new controlled agent session after hooks are installed, make a harmless
documentation-only change on a dedicated branch, commit it, and inspect the
linked checkpoint. The smoke checkpoint must show the session, prompt,
transcript, tool/file activity, token metadata when exposed, and commit trailer.
The smoke branch is not merged as part of setup; the foundation configuration
is committed separately by exact path.

## Milestone two: native Math-To-Manim integration

### Components

#### Provider-neutral session recorder

A top-level `m2m_entire/` package outside `mythos/` and `sol/` owns the
normalized M2M session schema and lifecycle emitter. Mythos and Sol may each
call this neutral interface, but neither imports the other provider's
implementation. Packaging exposes `entire-agent-m2m` for ENTIRE protocol calls
and `m2m-entire` for capture diagnostics, backfill, and session-aware resume.
The recorder never invokes a model, selects a provider, changes prompts, or
controls pipeline scheduling.

The recorder writes `entire_session.jsonl` into the existing run directory. It
then best-effort invokes `entire hooks m2m HOOK_NAME` with a normalized JSON
payload on standard input. A local transcript is always written first so an
ENTIRE failure cannot lose the run history. When capture is disabled or ENTIRE
is missing, the same code path becomes a bounded no-op after the local write.

#### `entire-agent-m2m`

The executable implements ENTIRE external-agent protocol version 1. It is
discoverable on `PATH` while the Math-To-Manim environment is active and
declares these capabilities:

- hooks;
- transcript analysis;
- token calculation;
- compact transcript support;
- subagent-aware extraction only after nested-run conformance tests pass.

It implements the required discovery, detection, session, transcript chunking,
reassembly, and resume-format commands plus the declared optional commands. Its
hook installer writes only an M2M-owned `.entire/m2m-agent.json` enablement
marker and can cleanly uninstall it. `format-resume-command` returns
`m2m-entire resume SESSION_ID`; that command delegates to the existing Sol or
RL resume path when one exists and reports Mythos historical sessions as
replay-only rather than inventing unsupported continuation behavior.

#### Historical M2M importer

An importer scans `runs/mythos/`, `runs/sol/`, and supported RL result ledgers,
normalizes completed and failed runs into the same canonical JSONL schema, and
submits them as read-only ENTIRE history. It uses deterministic source IDs and
content hashes so repeated imports are idempotent.

### Session boundaries

- A Mythos film request is one parent M2M session. Intent, cartography,
  curriculum, math direction, cinematography, scene composition, codegen,
  validation, rendering, and repair are turns or nested records.
- A Sol film request is one parent M2M session. Each durable specialist stage,
  validation pass, render, review, and repair is a turn or nested record.
- An RL experiment is one parent session. Each task rollout is a child session
  or linked session record, and each render/reward pass is a turn.
- A resumed run retains its stable M2M run ID and starts a new segment linked to
  the prior segment rather than overwriting prior transcript bytes.

### Canonical session record

Every record has a schema version and an event ID. Applicable events include:

- stable run/session ID and parent/segment linkage;
- session kind: Mythos film, Sol film, RL experiment, RL rollout, evaluation,
  or historical import;
- repository URL, source commit, branch, and a dirty-state fingerprint;
- provider, agent role, model, reasoning effort, and configuration fingerprint;
- original user prompt and immutable educational contract;
- stage or rollout input, output, status, and retry/repair relationship;
- tool and subprocess activity with bounded, redacted output;
- input, cached-input, output, reasoning, and aggregate token counts when known;
- start/end timestamps, monotonic duration, and timeout classification;
- textual artifact paths, media references, and SHA-256 hashes;
- validation findings, render settings, render outcome, review evidence, and
  repair decision;
- RL dataset version, task ID, split, seed, policy/checkpoint identity, reward
  components, infrastructure exclusions, aggregate reward, and terminal status;
- explicit missing-data reasons instead of fabricated zero values.

Transcript records may contain prompt and response text needed for future
training. Videos, images, weights, binary caches, and environment directories
are represented by metadata and hashes only.

### Lifecycle mapping

```text
M2M run starts                 -> SessionStart
stage or rollout starts        -> TurnStart
stage or rollout finishes      -> TurnEnd
parallel specialist/rollout    -> nested session where supported
context is compacted           -> Compaction
run completes or fails         -> SessionEnd
```

A failed stage still emits `TurnEnd` with structured failure information. A
failed run still emits `SessionEnd` from a `finally` path. Crash recovery scans
local transcripts with no terminal record, marks them interrupted, and allows
idempotent backfill.

## Privacy and security

- Permanent transcripts are pushed only to the private checkpoint repository.
- ENTIRE's mandatory secret redaction remains enabled; PII email and phone
  redaction is enabled in shared configuration.
- Existing application redaction and truncation remain in place before data
  reaches ENTIRE. ENTIRE is a second safety layer, not the first.
- `.env`, ignored files, credentials, cached login state, raw authorization
  headers, and token values are never added to normalized M2M records.
- Shadow branches remain local and are never pushed manually.
- The first permanent checkpoint branch is reviewed before it is pushed.
- The plugin treats repository and transcript paths as untrusted input,
  resolves them under approved roots, and never executes transcript content.
- Plugin subprocesses avoid a shell, use bounded timeouts, cap output, and
  surface structured errors.
- Model-harness exports apply a separate export-time privacy filter and include
  provenance pointing back to the private ENTIRE session, not credentials or
  machine-specific secrets.

## Failure handling

ENTIRE is observational infrastructure. It must not change the success result of
a Mythos, Sol, rendering, evaluation, or training operation.

- Local JSONL is written atomically before an ENTIRE hook is invoked.
- Hook calls have a short bounded timeout and failures are logged locally.
- A failed checkpoint push does not block the source-code push.
- A failed mirror fetch falls back to GitHub for workloads configured for
  fallback; source pushes continue to use GitHub until mirror validation ends.
- A failed or partial historical import can be safely re-run.
- Malformed historical runs are reported with path and reason and are skipped;
  they are never silently converted into successful sessions.
- If a record exceeds ENTIRE's command output limit, the plugin chunks it using
  the protocol rather than truncating training-relevant transcript text.
- When a token count is unavailable, the record carries an unavailable reason;
  it does not claim a count of zero.

## Testing strategy

### Foundation verification

- checksum and version verification for the installed ENTIRE binary;
- authentication and repository-access checks;
- private-repository visibility check through GitHub;
- hook merge test proving Git LFS and Claude permission behavior survive;
- ENTIRE status and doctor checks;
- historical import dry run, real import, and idempotency rerun;
- private checkpoint branch inspection;
- public repository negative check for checkpoint refs;
- mirror clone/fetch/ref comparison;
- GitHub-directed LFS pull from a mirror clone;
- push-through smoke branch;
- built-in Codex and Claude smoke sessions.

### Plugin unit and contract tests

- protocol `info` and capability declaration;
- detection and hook installation/uninstallation;
- parsing every lifecycle event;
- session ID stability and resume segmentation;
- canonical JSONL validation and deterministic hashing;
- transcript read/chunk/reassemble round trips;
- modified-file extraction;
- token aggregation with unavailable-data handling;
- secret filtering, path containment, timeout, and output bounds;
- failure and interrupted-session finalization;
- idempotent historical conversion for Mythos, Sol, and RL fixtures.

### End-to-end tests

- offline Mythos run produces a complete local M2M session without model calls;
- offline Sol run produces the same normalized lifecycle shape;
- a small deterministic RL fixture produces experiment, rollout, render, and
  reward records linked by stable IDs;
- ENTIRE-enabled runs produce inspectable checkpoints in the private remote;
- ENTIRE-disabled runs behave identically except for remote capture;
- simulated hook timeout does not alter pipeline output or exit status;
- a backfill after simulated hook failure yields one session with no duplicate
  events;
- provider-boundary import checks confirm `sol/` imports no Mythos module and
  `mythos/` imports no Sol client.

The repository's standard offline test suite and both offline film commands
must continue to pass. Render-marked tests run only where Manim, FFmpeg, TeX,
and OCR prerequisites are available.

## Acceptance criteria

Milestone one is complete only when current external state proves all of the
following:

1. The ENTIRE CLI is installed, checksum-verified, authenticated, and healthy.
2. `HarleyCoops/math-to-manim-checkpoints` exists and is private.
3. Shared settings route checkpoints to that private repository.
4. Codex and Claude hooks are active without losing LFS hooks or local Claude
   permissions.
5. Every locally discoverable repository-scoped Codex and Claude session is
   reconciled to an ENTIRE checkpoint or a concrete parser failure queued for
   milestone-two backfill, and an idempotency rerun finds no new duplicates.
6. A live smoke checkpoint is visible through ENTIRE and exists in the private
   checkpoint repository.
7. The public source repository has no checkpoint branch.
8. A US-East ENTIRE mirror exists and passes clone, fetch, ref, LFS, and
   push-through verification.
9. Existing unrelated working-tree changes remain byte-for-byte outside the
   staged ENTIRE change set.

Milestone two is complete only when:

1. `entire-agent-m2m` passes protocol, unit, and lifecycle tests.
2. Mythos, Sol, and RL runs produce versioned canonical session transcripts.
3. Live ENTIRE capture and offline/local-only capture both pass end-to-end tests.
4. Historical M2M imports are idempotent and preserve failed as well as
   successful runs.
5. Every development-session parser failure left by milestone one is either
   backfilled through the historical adapter or proven unreadable or absent
   with its source path, hash, and error preserved in the reconciliation
   inventory.
6. Session records contain the provenance and reward fields required by the
   model-harness use case, with explicit missing-data semantics.
7. Capture failure cannot change pipeline, render, evaluation, or training
   outcomes.
8. Provider-silo boundaries and the repository's standard offline tests pass.

## Rollout order

1. Commit this design and its implementation plan without touching the current
   unrelated RL work.
2. Install and authenticate ENTIRE.
3. Create and configure the private checkpoint repository.
4. Enable built-in agents and verify hook coexistence.
5. Import historical development sessions.
6. Create and verify the US-East mirror.
7. Establish the foundation smoke checkpoint and audit milestone one.
8. Implement the canonical recorder and `entire-agent-m2m` protocol adapter.
9. Add Mythos, Sol, and RL lifecycle emissions plus historical conversion.
10. Run plugin compliance, offline, RL fixture, failure-injection, and live
    private-checkpoint verification.
11. Audit the complete two-milestone objective against the acceptance criteria.

## References

- ENTIRE installation: <https://docs.entire.io/installation>
- ENTIRE sessions: <https://docs.entire.io/guides/sessions/overview>
- Historical session import:
  <https://docs.entire.io/guides/sessions/import-past-agent-history>
- Separate checkpoint repository:
  <https://docs.entire.io/guides/checkpoints/store-checkpoints-in-another-repo>
- Codex integration: <https://docs.entire.io/agents/codex>
- Claude Code integration: <https://docs.entire.io/agents/claude-code>
- Repository mirrors: <https://docs.entire.io/guides/repositories/mirrors>
- Mirror CLI workflow:
  <https://docs.entire.io/guides/repositories/mirrors-in-cli>
- Mirror limitations:
  <https://docs.entire.io/guides/repositories/limitations>
- External-agent architecture:
  <https://docs.entire.io/agents/external-agent-plugins/architecture>
- External-agent lifecycle:
  <https://docs.entire.io/agents/external-agent-plugins/lifecycle>
- External-agent commands:
  <https://docs.entire.io/agents/external-agent-plugins/commands>
- External-agent data model:
  <https://docs.entire.io/agents/external-agent-plugins/data-model>
- ENTIRE security and privacy: <https://docs.entire.io/security>
