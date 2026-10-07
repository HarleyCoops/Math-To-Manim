# Astra-native animation pipeline

The [Astra bundle pathway](ASTRA_BUNDLE.md) distributes the wheel, source
package, locked Codex runtime manifests and a completed film with its evidence.
`math-to-manim setup` installs the pinned runtime in a user-writable cache;
`math-to-manim login` opens Codex ChatGPT authentication. Installed packages
write `runs/astra/` in the working directory and work outside a source checkout.
An existing source install continues to use its matching `node_modules` runtime.

The primary CLI runs `astra.pipeline.Pipeline`: brief → mathematics → storyboard
→ scene → local render. Default reviews are advisory: each checkpoint receives
an Astra audit and one Jev evaluation, without Jev-triggered retries or extra
investigations. `--review-mode gated` enables the strict [gate contract](JEV.md).

`--review-mode off` explicitly disables Jev, including credential loading and
all TypeSafe calls. Independent Astra evidence audits still run. The manifest
records `review_status: astra_only`; it does not claim Jev approval.

The same pipeline is exposed through `math-to-manim serve-mcp` (stdio by
default, or loopback streamable HTTP on port 8644). Its tools create an operator
Astra/Jev worker, inspect a durable manifest, list runs, and retrieve scene
source. Worker diagnostics go to `worker.log`, keeping MCP stdout clean.
Keep the MCP server alive until completion. The reference client waits for a
terminal manifest; Windows MCP clients terminate server descendants on shutdown.
The existing explicit Mythos/Grok MCP entry points keep their provider routing.
See [the paper-film pilot](../papers/README.md) and
`scripts/drive_astra_mcp.py` for a real MCP client example.

`render-existing RUN --candidate FILE -q m` finishes retained scene code with
zero model/API calls. Manim joins its animation segments into one MP4. This
path records `review_status: not_reviewed` and preserves earlier verdicts.

`astra/bridge.mjs` uses the official pinned Codex SDK and CLI 0.156.1, with
`gpt-6-astra`, structured outputs and cached ChatGPT login. Specialist sessions
can inspect files and execute permitted read-only tools; mathematical sessions
also have web search. Tool events, model output and session IDs are recorded.
The harness writes validated artifacts and manages bounded backward repairs.

Astra authors mathematical content and code. Astra auditors inspect evidence,
including images at the render checkpoint. TypeSafe's text-only Jev evaluates
narrow questions over that evidence and returns typed decisions. These are
separate models, services and authentication paths.

The local renderer uses Manim's Cairo backend, actual MathTex, FFmpeg metadata
and sampled frames. AST screening rejects unsupported imports and dangerous
operations, but is not a security sandbox. Local code execution is authorized
for this workflow; do not treat it as safe execution of arbitrary hostile code.

A successful manifest binds the MP4 hash and review history. A source file,
mock test, API smoke test or an interrupted run is not a completed animation.

Before a requested full movie render, the harness executes each scene candidate
to a final still with Manim. The scene audit receives that actual image and an
execution record bound to the source hash. This supplies runtime and LaTeX
evidence without claiming a movie exists. The later render gate still requires
the full MP4 and sampled frames. `--no-render` does not execute this probe.

Full local renders have a two-hour execution limit; final-still probes have a
ten-minute limit. Detailed 1080p/60 fps Cairo surfaces can take longer than the
movie's playback duration by a substantial factor. These limits do not change
the Jev acceptance criteria.

Delivery quality is enforced after loading the generated scene, so hard-coded
scene defaults cannot override the user's choice. `-q m` means 1280×720 at
30 fps; `-q h` means 1920×1080 at 60 fps, and `-q l` means 854×480 at 15 fps.
Use `math-to-manim resume runs/astra/<run-id> -q m` to change an existing run.
The override is recorded in `delivery.json`; mathematical planning remains
cached, while the scene and final render receive fresh reviews at that quality.
