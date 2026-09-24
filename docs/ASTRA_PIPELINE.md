# Astra-native animation pipeline

The primary CLI runs `astra.pipeline.Pipeline`: brief → mathematics → storyboard
→ scene → local render. Every checkpoint requires a fresh Astra evidence audit
and a real TypeSafe Jev decision. See [the gate contract](JEV.md).

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
