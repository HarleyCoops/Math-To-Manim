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
