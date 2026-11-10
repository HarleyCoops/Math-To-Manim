<!--
DRAFT. Proposed README section. Not yet in README.md.
Image paths are relative to the repo root, so they work when this section is
pasted into README.md. They do not resolve when this file is viewed in docs/.
Images and the scripts that make them: docs/assets/fable-5-2/
-->

## Fable 5.2 Learns Manim

![Title image "Fable 5.2 Learns Manim". On the right, a 3D drawing of the Hopf fibration: linked circles in coral, blue and gold wrap a coral torus, with a vertical axis through the middle. Below the title, the formula h(z1, z2) = (2 z1 conj(z2), |z1|^2 - |z2|^2), h: S^3 -> S^2.](docs/assets/fable-5-2/hero.png)

Claude Fable 5.2 wrote this week's changes to the Mythos chain, and the images in this section.
The title image is a still from a Manim `ThreeDScene` that the model wrote: [`docs/assets/fable-5-2/src/hero.py`](docs/assets/fable-5-2/src/hero.py).
The chain itself calls the model set in `M2M_MODEL` (default `claude-fable-5-2`).

### What changed in the chain

Two commits changed how a run reports its state.

**`a49352e`: explicit job and run lifecycles.**
A job's status now moves only through a transition table: `queued` to `running`, then `completed` or `failed`.
The run manifest records three fields under `status`:

- `run`: `running`, `completed` or `failed`.
- `stage`: the step that is running now. On a failed run, the step that failed.
- `outcome`: how a finished run ended. One of `film_ready`, `scene_ready`, `validation_failed`, `render_failed`, `render_timed_out`, `render_blocked`, `chain_failed`.

Before this commit, a crashed run looked the same on disk as a run in progress.
Now it is recorded as failed, with the step that failed.

![Diagram of the lifecycles in src/mythos/lifecycle.py. Job status: queued to running, running to completed or failed, queued to failed. Run stage: the ten step names from intent to repair. Run outcome: the seven values and what each means. Before and after: a crashed run's manifest.json, first without and then with the fields run, stage, outcome, error and failed_utc.](docs/assets/fable-5-2/lifecycle.png)

**`9e154fd`: `serve-mcp` runs the Mythos chain and returns the Mythos job.**
`src/mythos/mcp_server.py` is now an MCP server over the Mythos service.
It has seven tools: `m2m_create_animation`, `m2m_get_job`, `m2m_list_runs`, `m2m_get_run`, `m2m_get_artifact`, `m2m_get_scene_code`, `m2m_cinematic_charter`.
An agent that polls a job gets `status`, `stage` and `outcome` in the job record.
A `completed` job can still have the outcome `render_failed`, so read `outcome` to know if a film exists.
The Grok chain has its own server: `math-to-manim-grok serve-mcp`.
No silo imports another silo (`tests/test_silo_boundaries.py`).

![Diagram of the Mythos MCP server. Left: the seven tool names, each with one line on what it does. Right: the order of calls (m2m_create_animation, then m2m_get_job until done, then m2m_get_scene_code), one real job record with status "running", stage "math-director" and outcome null, and a table of status, stage and outcome for a running job, a finished offline run and a failed run.](docs/assets/fable-5-2/mcp.png)

The job records in both diagrams are real output.
[`capture_job_records.py`](docs/assets/fable-5-2/src/capture_job_records.py) calls the MCP tool functions with a stub model backend that stops at the fourth stage.

### How it works now

The chain has six reasoning stages. Each stage writes one JSON file into the run directory.
Then `codegen` writes the Manim scene, `verify` checks it, and `render` runs Manim.
If a check or a render fails, `repair` asks the model to rewrite the scene file. The default limit is 3 repairs.

![Diagram of the Mythos chain. Left: the six reasoning stages and the file each writes: intent (01_intent.json), cartographer (02_knowledge_map.json), curriculum (03_curriculum.json), math-director (04_math_dossier.json), cinematographer (05_shot_list.json), scene-composer (06_scene_spec.json). Right: codegen writes mythos_scene.py, verify writes validation.json, render writes a log; a failed check or render goes to repair, which sends a new file back to verify, at most 3 rounds by default; the run ends and manifest.json records status.run and status.outcome.](docs/assets/fable-5-2/chain.png)

Run the chain without a model, to test the setup:

```bash
math-to-manim-mythos run "Why does a top precess?" --offline
```

Run the chain with the model and render the film:

```bash
math-to-manim-mythos run "Why does a top precess?" --render -q m
```

Serve the chain to agents over MCP (needs the `mcp` extra: `pip install -e ".[mcp]"`):

```bash
math-to-manim-mythos serve-mcp
math-to-manim-mythos serve-mcp --transport streamable-http --port 8643
```

Runs are written to `runs/mythos/<timestamp>-<slug>/`. The stage table is in `src/mythos/stages.py` and the runner is in `src/mythos/harness.py`.

### What comes next (planned)

Studio is a planned redesign. The design is approved in outline. It is not built: no code named Studio is in `src/` yet.

The plan:

- One run produces an MP4 film (Manim and Blender shots) and an interactive three.js page.
- One typed scene description, `SceneSpec`, drives Manim, Blender and three.js.
- The run is a state machine in code, with one state per shot.
- Nine agents each write one typed file: Story Scout, Physics Verifier, Director, Spec Author, Manim Builder, Blender Builder, Web Builder, Visual Critic, Fact Checker.
- Each shot is rendered, measured by code, then reviewed by a critic that looks at a contact sheet. A shot gets at most 3 repair rounds.
- The agents run on Claude Managed Agents. Blender EEVEE runs on the user's PC.
- A viewer shows a run while it runs.

![Diagram marked "Planned, not built", drawn with dashed outlines. Nine agents each write one typed file. One SceneSpec feeds three engines: Manim, Blender and three.js. Manim and Blender shots become an MP4 film; three.js becomes an interactive web page. For each shot: build, measure, review, then shot done, with a repair path from review back to build of at most 3 rounds.](docs/assets/fable-5-2/studio-planned.png)
