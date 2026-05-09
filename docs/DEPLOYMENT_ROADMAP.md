# Deployment Roadmap for a Manim Animation Engine

This roadmap is for teams that want to deploy a Math-To-Manim-like service:
users submit educational prompts, the system plans an explanation, generates
Manim code, renders video in an isolated worker, and returns an inspectable run
bundle. It is a reusable implementation guide, not a hosted support offer.

## Target Shape

Start with a boring, inspectable architecture:

```text
browser or API client
  -> API service
  -> database row for the job
  -> queue
  -> render worker sandbox
  -> object storage
  -> status/result API
```

Keep planning, code generation, validation, rendering, and publishing as
separate stages even if they run in one worker process at first. The main
product contract should be artifacts, not side effects: prompt, plan, generated
scene, validation report, render result, review notes, final video, and manifest.

## Architecture Choices

- API service: FastAPI, Django, Rails, or Node can all work. Choose the stack
  your team already operates well.
- Queue: use managed queues first, such as SQS, Cloud Tasks, Pub/Sub, or a
  hosted Redis queue. Rendering must not run in the request/response path.
- Workers: package Manim, Python dependencies, FFmpeg, LaTeX, fonts, and your
  engine code into a pinned container image.
- Database: store job state, ownership, prompt metadata, artifact keys, retry
  counts, timestamps, and billing or quota metadata if needed.
- Object storage: store run bundles and videos in S3, GCS, Azure Blob, R2, or
  similar storage. Do not store large videos in the database.
- UI: poll or subscribe to job state, show stage progress, expose logs safely,
  and link to downloadable outputs when publishing completes.

For a first production version, one API service, one queue, one worker image, one
database, and one storage bucket are enough.

## Job Lifecycle

Use explicit states so failures are supportable:

1. `queued`: request accepted, basic limits checked, job persisted.
2. `planning`: prompt becomes intent, graph, curriculum, storyboard, and scene
   spec artifacts.
3. `codegen`: scene spec becomes `generated_scene.py`.
4. `validating`: AST/import/scene discovery checks run before Manim.
5. `rendering`: a sandboxed worker invokes Manim and captures stdout/stderr.
6. `reviewing`: optional video probes, frame checks, or model review run.
7. `published`: manifest, video, thumbnails, and reports are stored.
8. `failed`: error summary, stage, command, and relevant artifact paths are
   stored for debugging.

Retries should be stage-aware. A render retry should reuse the frozen upstream
scene spec and captured render error rather than rerunning all planning.

## Sandboxing and Security

Generated Manim code is untrusted code. Treat the render worker as a containment
boundary:

- Run each job in a fresh container, Firecracker microVM, gVisor sandbox, or
  similarly isolated environment.
- Disable outbound network access from render jobs unless a reviewed feature
  requires it.
- Mount a job-specific working directory and write outputs only inside that
  directory.
- Use a non-root user, read-only base image layers, CPU and memory limits,
  process limits, timeout limits, and disk quotas.
- Pass secrets only to the API or model-call stages that need them. Render
  sandboxes should not receive provider keys by default.
- Validate generated code before rendering. Block obvious unsafe imports,
  filesystem writes outside the job directory, subprocess calls, network calls,
  and dynamic execution patterns.
- Store logs with secret redaction. Never expose raw environment variables or
  provider credentials in UI logs.

For high-risk public upload or arbitrary-code scenarios, prefer VM-level
isolation over plain Docker.

## Rendering Dependencies

Manim rendering is more than a Python package. The worker image usually needs:

- Python and the project package installed with render extras.
- Manim Community Edition pinned to a known version.
- FFmpeg for video output and post-processing.
- LaTeX plus `dvisvgm` for `MathTex` and equation-heavy scenes.
- Cairo, Pango, fontconfig, and system fonts.
- Optional GPU libraries only if your scenes or post-processing actually use
  them.

Build the image once, run a small deterministic scene during image validation,
and publish the image by digest. Avoid installing system render dependencies at
job runtime.

## API and UI Surface

Minimum API:

- `POST /jobs`: create a job from prompt, style, quality, and render options.
- `GET /jobs/{id}`: return state, current stage, timestamps, and safe errors.
- `GET /jobs/{id}/artifacts`: list manifest entries the user may access.
- `GET /jobs/{id}/download`: return signed URLs for video and selected reports.
- `POST /jobs/{id}/cancel`: request cancellation before or during rendering.

Minimum UI:

- Prompt form with clear quality and render-time tradeoffs.
- Job status page with stage progress.
- Final video playback, download links, and artifact/report links.
- Failure page that explains the failed stage without leaking internals or
  secrets.

If you expose generated code, label it as generated and run it only in the
sandboxed worker path.

## Observability

Capture enough detail to answer "what happened?" without shelling into workers:

- Job id, user id or tenant id, stage, status, timestamps, duration, attempt.
- Queue wait time, render time, total wall-clock time, CPU and memory usage.
- Container image digest and project version.
- Manim command, exit code, stderr summary, and artifact paths.
- Model provider, model name, token counts, and cost metadata when applicable.
- Structured events for every stage transition.

Dashboards should track queue depth, worker saturation, failure rate by stage,
timeout rate, median and p95 render time, storage growth, and cost per completed
video.

## Cost and Scaling Notes

Rendering is bursty and CPU-heavy. Plan for backpressure before scaling:

- Start with fixed-size workers and strict per-job timeouts.
- Add autoscaling from queue depth and oldest-message age.
- Cap quality presets. Low-quality preview renders are much cheaper than final
  high-quality renders.
- Cache base images and reusable assets, but do not cache untrusted job
  workspaces across users.
- Use lifecycle policies to expire temporary artifacts, logs, and preview media.
- Separate preview and final queues if final renders can block quick feedback.
- Put quotas around prompts, concurrent jobs, render minutes, storage, and
  retries.

Most teams should scale workers horizontally before considering GPUs or custom
render orchestration.

## Practical Rollout Plan

1. Local engine: deterministic no-render jobs create typed artifacts and a
   manifest.
2. Local render: one trusted scene renders through the same worker command used
   in production.
3. Container image: render dependencies are pinned and validated in CI.
4. Private queue: API creates jobs, one worker consumes jobs, object storage
   receives bundles.
5. Sandbox hardening: network, filesystem, process, memory, CPU, and timeout
   limits are enforced.
6. Public beta: quotas, cancellation, safe error messages, and artifact expiry
   are enabled.
7. Production hardening: autoscaling, dashboards, alerting, abuse controls,
   cost reporting, and incident runbooks are in place.

## Production Readiness Checklist

- Jobs never render synchronously inside API requests.
- Generated code is validated before render and executed only in a sandbox.
- Workers have no default access to model provider secrets.
- Every job writes a manifest and a stage-specific failure record when needed.
- Render dependencies are installed in the image, not during the job.
- Videos and run bundles live in object storage behind signed URLs.
- Queue depth, failures, render duration, and costs are observable.
- Timeouts, quotas, cancellation, retries, and artifact retention are explicit.
- A small deterministic render smoke test runs for every worker image release.
