# Math-To-Manim Codex 5.5 / OpenAI Agents SDK Refactor Proposal

Yes. I inspected the repo intent, current architecture docs, README, core agents, pyproject, and the current Python layout. Here’s the strategic proposal before we touch code.

Short version: this repo should become a clean OpenAI Agents SDK pipeline that turns:

simple prompt
→ concept intent
→ prerequisite graph
→ mathematical plan
→ visual storyboard
→ Manim implementation
→ render
→ automated visual/code review
→ repair loop
→ final MP4/GIF/README artifact

…and Codex 5.5 should be used not just as a code generator, but as the reasoning/runtime brain behind each agent.

Current state I see:
- Strong product intent.
- Good core idea: reverse knowledge tree.
- Chaotic implementation layering:
  - `src/agents/` has the current main pipeline.
  - `KimiK2.5Swarm/` duplicates/enriches the same concepts in a separate architecture.
  - `Gemini3/` has more separate experiments.
  - `scripts/` has ad hoc runners.
  - `examples/` has many valuable generated outputs but is mixed with showcase/prototype code.
  - Current core agents are mostly “classes that call an LLM,” not true tool-using agents.
- The big missing piece: no unified agent runtime, no strict artifacts/contracts, no robust render-review-repair loop, no capability registry, no persistent eval system.

I would refactor toward this:

```text
math_to_manim/
  agents/
  tools/
  schemas/
  pipeline/
  rendering/
  review/
  examples/
  datasets/
  app/
  cli/
```

with every pipeline step producing typed structured artifacts.

---

## 1. Repo intent

The real intent is not “generate Manim code.”

The real intent is:

Build an agentic educational animation studio for mathematical/scientific concepts.

The repo should accept a small human prompt like:

“explain why derivatives are slopes”

and produce:

1. Pedagogically sound concept decomposition.
2. A foundation-to-target learning path.
3. Mathematically valid equations and definitions.
4. A coherent visual storyboard.
5. Renderable Manim CE code.
6. A rendered video/GIF.
7. A review report.
8. Repairs until it passes syntax/render/visual criteria.
9. Optional article/README/social/demo artifacts.

The core innovation remains the reverse knowledge tree:

“What must someone understand BEFORE this?”

That should stay central. But we should stop treating the tree as a loosely mutated dataclass and instead treat it as a canonical graph artifact with versioned schemas, cache keys, validation, and eval traces.

---

## 2. What Codex 5.5 / Hermes capabilities we should turn on or use

I’ll separate this into practical Hermes harness capabilities and “sky is the limit” Codex/OpenAI capabilities.

### A. Hermes harness capabilities we are not fully exploiting

#### 1. Codex CLI as implementation worker

Use Codex 5.5 through `codex exec` for actual refactor/codegen tasks.

Pattern:
- Hermes orchestrates.
- Codex workers implement one isolated task.
- Each task runs in a git worktree.
- Hermes reviews and merges.

Use for:
- Large refactors.
- Schema migrations.
- Test creation.
- API cleanup.
- Converting old Kimi/Gemini code into unified adapters.

#### 2. Parallel Codex worktrees

This repo is perfect for parallelization.

Example workers:
- Worker A: schemas and typed artifacts.
- Worker B: OpenAI Agents SDK runtime.
- Worker C: Manim render/review tools.
- Worker D: CLI and app integration.
- Worker E: tests and fixtures.
- Worker F: migration of examples/docs.

#### 3. Hermes `delegate_task`

Use lightweight subagents for reasoning/design audits before coding:
- architecture critique
- migration risk list
- test plan generation
- prompt contract review
- Manim failure taxonomy
- README/docs rewrite

#### 4. Hermes `cronjob`

Useful later for:
- nightly render smoke tests
- weekly example gallery refresh
- dead-link/GIF validation
- “try 10 prompts and score pass rate”
- GitHub README asset validation

#### 5. Hermes `vision` and browser tools

Critical for this repo.

Current system does syntax validation and sometimes video tooling, but the product needs visual QA:
- extract frames
- inspect layout
- detect off-screen text
- detect unreadable equations
- detect empty/black frames
- detect scene clutter
- detect whether animation actually depicts the target concept

Hermes vision can help during repo development, but we should also build this into the app pipeline using OpenAI vision models.

#### 6. Hermes memory/skills

Useful for:
- recurring Manim pitfalls
- known render failures
- model-specific API quirks
- successful repair strategies
- style presets

But in the repo itself, this should become a local “knowledge base” and “failure memory,” not just Hermes memory.

#### 7. Hermes MCP

We can add MCP servers for repo-specific tools:
- Manim render MCP
- FFmpeg/video review MCP
- Math validation MCP
- example-search MCP
- artifact database MCP
- OpenAI evals MCP
- Nomic/embedding search MCP

#### 8. Hermes background processes

Use for long Codex refactor agents, render workers, or test suites.

#### 9. Hermes checkpoints / worktree mode

For a refactor this large, use checkpoints/worktrees aggressively.

---

### B. Codex / OpenAI capabilities to consider turning on

Some of these depend on what’s available in your account/environment, so I’d frame them as “turn on if available.”

#### 1. OpenAI Agents SDK

This is the big one.

Replace homemade `LLMClient` + direct Anthropic calls with OpenAI Agents SDK agents:

- `ConceptIntentAgent`
- `PrerequisiteGraphAgent`
- `MathEnrichmentAgent`
- `StoryboardAgent`
- `ManimCodeAgent`
- `RenderAgent`
- `VideoReviewAgent`
- `RepairAgent`
- `ArtifactPublisherAgent`

Each agent should have:
- instructions
- model config
- tool access
- typed output schema
- handoff rules
- trace metadata

#### 2. Structured outputs / strict JSON schema

Every intermediate artifact should be schema-validated.

Current problem:
- agents return free-form JSON-ish text
- code manually parses with regex/code fences
- `KnowledgeNode` mutates across phases

Refactor to:
- Pydantic schemas
- strict JSON schema outputs
- explicit artifact versioning

Example artifacts:
- `ConceptIntent`
- `KnowledgeGraph`
- `MathEnrichment`
- `VisualStoryboard`
- `ManimSceneSpec`
- `GeneratedCode`
- `RenderResult`
- `ReviewReport`
- `RepairPatch`

#### 3. Built-in function/tool calling

Do not ask Codex to hallucinate Manim facts when it can call tools.

Tools to expose:
- `search_examples(query)`
- `inspect_manim_docs(symbol)`
- `validate_latex(equation)`
- `validate_python_ast(code)`
- `run_ruff(file)`
- `render_manim(file, scene, quality)`
- `extract_video_frames(video)`
- `score_video_frames(frames)`
- `repair_code_with_error(code, traceback)`
- `lookup_known_failure(signature)`

#### 4. Tracing

Use OpenAI tracing or equivalent to log:
- each agent call
- prompts
- tool calls
- outputs
- schema validation
- render result
- repair attempts
- total cost/time/tokens
- final pass/fail score

This repo needs observability because animation generation is inherently multi-step and failure-prone.

#### 5. File search / vector stores

The examples folder is a goldmine. Use it.

Build an example/style retrieval layer:
- index successful Manim examples
- index scene classes
- index failure/repair reports
- index README showcase artifacts
- index docs/manim snippets

Then the code generator can retrieve relevant known-good patterns:
- “Lorenz attractor”
- “Hopf fibration”
- “derivative slope animation”
- “3D camera scene”
- “equation transform sequence”

#### 6. Code interpreter / sandboxed execution

Use for:
- symbolic checks
- quick matplotlib previews
- validating equations
- geometry calculations
- generating helper data arrays
- checking scene duration estimates
- AST inspection

#### 7. Computer/browser control

Potentially useful for:
- previewing generated HTML/Three.js
- checking GitHub README rendering
- visual QA of local web UI
- capturing screenshots

#### 8. Codex app servers

This is probably the most “sky is the limit” thing.

Create app servers / MCP-like servers for domain capabilities:

- Manim Server:
  - render scene
  - inspect scene classes
  - list output media
  - cache renders
  - return traceback and frame samples

- Math Server:
  - validate LaTeX
  - sympy checks
  - dimensional analysis
  - equation simplification

- Example Corpus Server:
  - semantic search across examples
  - retrieve snippets
  - retrieve style presets
  - retrieve successful scene patterns

- Video QA Server:
  - ffprobe
  - frame extraction
  - black-frame detection
  - OCR text readability
  - visual model scoring

- Asset Server:
  - GIF conversion
  - thumbnail generation
  - README asset validation
  - public/showcase management

- Evaluation Server:
  - run prompt suite
  - compare pass rates
  - score narrative quality
  - log regressions

#### 9. Eval harness

This repo needs evals more than almost anything.

Create a prompt suite:
- derivatives as slopes
- Pythagorean theorem
- Fourier epicycles
- Lorenz attractor
- gradient descent
- Brownian motion
- Hopf fibration
- black hole spacetime
- QED interaction
- radius of convergence

Each eval checks:
- schema validity
- Python syntax
- Manim import validity
- render success
- no empty video
- minimum duration
- readable frame samples
- title/equation present
- concept-specific visual markers
- final artifact exists

#### 10. Prompt caching / response caching

Prerequisite trees and enrichment are cacheable.

Cache keys:
- concept
- level
- audience
- max depth
- model version
- prompt template version

#### 11. Batch/parallel agent execution

The tree naturally parallelizes:
- explore prerequisites in parallel
- enrich nodes in parallel
- produce visual specs in parallel
- review generated code in parallel
- run independent repair candidates in parallel and choose best

#### 12. Model roles / model routing

Even if “only Codex 5.5” is the main premise, internally we can still route tasks by capability if allowed later.

If strictly Codex 5.5 only:
- same model, different agents/instructions/tools.

If not strict:
- cheaper model for classification
- stronger model for code
- vision model for video review
- embedding model for example retrieval
- TTS/music/image later

---

## 3. Reimagined pipeline using Codex 5.5 + OpenAI Agents SDK

Here’s the clean version I’d build.

### A. Top-level pipeline

Input:
`UserPrompt`

Output:
`AnimationPackage`

Pipeline:

1. Intent pass
2. Concept graph pass
3. Curriculum pass
4. Math enrichment pass
5. Visual storyboard pass
6. Scene spec pass
7. Manim code pass
8. Static validation pass
9. Render pass
10. Visual review pass
11. Repair loop
12. Package/publish pass

---

### B. Canonical artifacts

#### 1. `UserRequest`

Fields:
- prompt
- audience_level
- desired_duration
- style
- output_formats
- constraints
- target_platform
- requested_model
- seed/examples if supplied

#### 2. `ConceptIntent`

Fields:
- core_concept
- domain
- audience_level
- learning_goal
- aha_moment
- visual_potential
- forbidden_complexity
- success_criteria

#### 3. `KnowledgeGraph`

Replace `KnowledgeNode` tree with a graph.

Fields:
- nodes
- edges
- root_node_id
- foundation_nodes
- depth
- rationale
- confidence
- source_agent
- version

Why graph, not tree?
Because prerequisites repeat. A concept like “function” may support multiple branches. A DAG is better than recursive duplicate trees.

#### 4. `CurriculumPlan`

Fields:
- ordered_concepts
- scene_count
- teaching_arc
- misconception_warnings
- prerequisite_compression_strategy
- target_aha_moment

#### 5. `MathPacket`

Per concept:
- definitions
- equations
- variables
- assumptions
- examples
- latex_strings
- math_validity_notes
- rendering_risk

#### 6. `VisualStoryboard`

Per scene:
- title
- purpose
- visual metaphor
- objects
- color roles
- animation beats
- camera plan
- timing
- text/equation overlays
- transition in/out
- known Manim primitives

#### 7. `ManimSceneSpec`

More implementation-level than storyboard.

Fields:
- scene_class_name
- imports
- helper_functions
- mobjects
- timeline
- constants
- assets
- quality target
- render command
- expected output path

#### 8. `GeneratedCode`

Fields:
- file_path
- scene_class
- code
- imports
- dependencies
- estimated_runtime
- risk_notes

#### 9. `ValidationReport`

Fields:
- ast_valid
- imports_valid
- ruff_pass
- latex_pass
- manim_dry_run_pass
- render_pass
- traceback
- repair_hints

#### 10. `RenderResult`

Fields:
- video_path
- duration
- resolution
- fps
- frame_count
- stdout/stderr
- media_dir
- render_time_seconds

#### 11. `VideoReviewReport`

Fields:
- black_frame_score
- text_readability_score
- equation_readability_score
- visual_relevance_score
- pacing_score
- clutter_score
- sampled_frames
- visual_failures
- suggested_repairs

#### 12. `AnimationPackage`

Fields:
- prompt
- final_code_path
- final_video_path
- gif_path
- thumbnail_path
- reports
- README snippet
- run trace
- reproducibility manifest

---

### C. Proposed OpenAI Agents

#### 1. `IntentAgent`

Purpose:
Understand what the user wants educationally, not just keywords.

Tools:
- none initially
- maybe `classify_domain`

Output:
`ConceptIntent`

Why:
Keeps prompt understanding clean and testable.

#### 2. `PrerequisiteGraphAgent`

Purpose:
Build reverse prerequisite graph.

Tools:
- `search_existing_graph_cache`
- `save_graph_cache`
- `deduplicate_concepts`
- `detect_cycles`
- `normalize_concept_name`

Output:
`KnowledgeGraph`

Important:
This should do parallel expansion with cycle/dedup protection.

#### 3. `CurriculumAgent`

Purpose:
Convert graph into teachable sequence.

Tools:
- `toposort_graph`
- `estimate_scene_budget`
- `compress_foundations`

Output:
`CurriculumPlan`

This agent decides what to explain and what to skip.

#### 4. `MathAgent`

Purpose:
Generate equations and definitions safely.

Tools:
- `validate_latex`
- `sympy_check`
- `manim_mathtex_check`
- `unit_check`
- `search_math_examples`

Output:
`MathPacket`

#### 5. `VisualStoryboardAgent`

Purpose:
Design the video before code.

Tools:
- `search_examples`
- `retrieve_style_preset`
- `check_visual_feasibility`
- `estimate_manim_complexity`

Output:
`VisualStoryboard`

This is where “cinematic” quality should live.

#### 6. `SceneSpecAgent`

Purpose:
Translate storyboard into a concrete implementable Manim plan.

Tools:
- `inspect_manim_api`
- `retrieve_manim_snippet`
- `validate_scene_spec`

Output:
`ManimSceneSpec`

This layer prevents the code generator from improvising too much.

#### 7. `ManimCodeAgent`

Purpose:
Generate code.

Tools:
- `search_examples`
- `validate_python_ast`
- `validate_manim_imports`
- `write_file`

Output:
`GeneratedCode`

#### 8. `StaticReviewAgent`

Purpose:
Review before rendering.

Tools:
- `python_ast_parse`
- `ruff`
- `import_check`
- `latex_check`
- `scene_class_discovery`

Output:
`ValidationReport`

#### 9. `RenderAgent`

Purpose:
Run Manim.

Tools:
- `render_manim`
- `ffprobe`
- `collect_artifacts`

Output:
`RenderResult`

#### 10. `VideoCriticAgent`

Purpose:
Look at the video like a human reviewer.

Tools:
- `extract_frames`
- `vision_analyze_frames`
- `ocr_text`
- `detect_blank_frames`

Output:
`VideoReviewReport`

This should be mandatory, not optional. The user already expects actual media validation for download/archive tasks; same principle applies here.

#### 11. `RepairAgent`

Purpose:
Given validation/review failures, patch only what is broken.

Tools:
- `read_file`
- `patch_file`
- `render_manim`
- `search_failure_memory`
- `save_failure_memory`

Output:
`RepairPatch`

Repair loop:
- max 3 static repairs
- max 3 render repairs
- max 2 visual repairs
- if still failing, package failure report with artifacts

#### 12. `PublisherAgent`

Purpose:
Create final user-facing artifacts.

Tools:
- `ffmpeg_gif`
- `make_thumbnail`
- `write_readme_snippet`
- `save_manifest`

Output:
`AnimationPackage`

---

## 4. Functions/tools we should add inside the repo

These are repo-level Python tools, not just Hermes tools.

### A. Core graph tools

1. `normalize_concept_name(concept: str) -> str`
2. `concept_id(concept: str) -> str`
3. `merge_duplicate_nodes(graph) -> KnowledgeGraph`
4. `detect_cycles(graph) -> list[Cycle]`
5. `topological_curriculum_order(graph) -> list[ConceptId]`
6. `prune_graph_for_duration(graph, seconds) -> KnowledgeGraph`
7. `graph_to_mermaid(graph) -> str`
8. `graph_to_curriculum_outline(graph) -> CurriculumPlan`

### B. LLM/runtime tools

1. `run_agent(agent_name, input_artifact) -> output_artifact`
2. `validate_artifact(schema, value)`
3. `cache_get(key)`
4. `cache_put(key, artifact)`
5. `trace_event(stage, input, output, metadata)`
6. `retry_with_schema_repair(agent, invalid_output, error)`

### C. Math tools

1. `validate_latex_mathtex(latex: str) -> LatexValidation`
2. `render_equation_preview(latex: str) -> image`
3. `sympy_parse_equation(equation: str)`
4. `check_variable_definitions(equations, definitions)`
5. `detect_undefined_symbols(equations, definitions)`
6. `latex_to_manim_safe_string(latex: str) -> str`

### D. Manim tools

1. `discover_scene_classes(file_path) -> list[str]`
2. `validate_manim_imports(code) -> ImportReport`
3. `run_manim_dry_import(file_path) -> ValidationReport`
4. `render_manim_scene(file_path, scene, quality) -> RenderResult`
5. `extract_manim_traceback(stderr) -> ErrorSignature`
6. `classify_manim_error(traceback) -> ErrorKind`
7. `suggest_manim_repair(error_kind) -> RepairHint`

### E. Video tools

1. `ffprobe_video(video_path) -> VideoMetadata`
2. `extract_keyframes(video_path) -> list[FramePath]`
3. `detect_black_or_static_video(frames) -> Score`
4. `detect_offscreen_text(frames) -> Score`
5. `ocr_frame_text(frames) -> OCRReport`
6. `sample_representative_frames(video_path) -> frames`
7. `make_readme_gif(video_path, start, duration) -> gif_path`
8. `make_thumbnail(video_path) -> png_path`

### F. Example retrieval tools

1. `index_examples()`
2. `search_examples_by_concept(query)`
3. `search_examples_by_manim_primitive(primitive)`
4. `retrieve_scene_snippet(scene_id)`
5. `retrieve_style_preset(name)`
6. `score_example_relevance(prompt, example)`

### G. Eval tools

1. `run_prompt_eval_suite()`
2. `score_pipeline_run(run_dir)`
3. `compare_eval_runs(old, new)`
4. `generate_eval_report()`
5. `track_pass_rate_by_domain()`

### H. Artifact tools

1. `create_run_directory(prompt) -> RunDir`
2. `save_artifact(stage, artifact)`
3. `load_artifact(run_id, stage)`
4. `package_animation(run_id)`
5. `generate_repro_manifest(run_id)`

---

## 5. MCP servers we could add

### A. `manim-mcp`

Tools:
- render scene
- list scene classes
- validate imports
- return render output
- return traceback
- return video path

### B. `ffmpeg-video-mcp`

Tools:
- probe video
- extract frames
- make GIF
- make thumbnail
- detect black frames
- crop/resize/compress

### C. `math-validation-mcp`

Tools:
- validate LaTeX
- render MathTex preview
- parse symbols
- run SymPy checks
- dimensional sanity checks

### D. `example-corpus-mcp`

Tools:
- semantic search examples
- retrieve snippets
- retrieve matching animation styles
- retrieve known good Manim idioms

### E. `artifact-store-mcp`

Tools:
- save/load run artifacts
- list runs
- diff runs
- attach metadata
- search prior failures

### F. `github-showcase-mcp`

Tools:
- validate README image links
- verify GIF assets are real images not LFS pointers
- generate showcase table
- update README snippets

### G. `openai-evals-mcp`

Tools:
- run eval suite
- log model/prompt versions
- compare pass rates

### H. `browser-preview-mcp`

Tools:
- open local Gradio app
- screenshot output
- inspect generated Three.js
- verify README rendering

---

## 6. Subagents I would use during the actual refactor

### A. Hermes/Codex development subagents

#### 1. Architecture Planner

Produces migration plan and folder structure.

#### 2. Schema Engineer

Creates Pydantic models and artifact contracts.

#### 3. Agent Runtime Engineer

Builds OpenAI Agents SDK pipeline.

#### 4. Manim Tooling Engineer

Builds render/validation wrappers.

#### 5. Video QA Engineer

Builds frame extraction and visual review pipeline.

#### 6. Example Corpus Engineer

Indexes examples and retrieval.

#### 7. CLI/App Engineer

Creates clean CLI and Gradio/FastAPI interface.

#### 8. Test/Eval Engineer

Builds unit, integration, render smoke, and eval suites.

#### 9. Migration Engineer

Moves Claude/Kimi/Gemini experimental code into archive/adapters.

#### 10. Documentation Engineer

Rewrites architecture docs around Codex 5.5/OpenAI Agents SDK.

### B. Runtime product subagents inside the app

1. Intent agent
2. Prerequisite graph agent
3. Curriculum agent
4. Math agent
5. Visual/storyboard agent
6. Manim code agent
7. Static reviewer
8. Renderer
9. Video reviewer
10. Repair agent
11. Publisher/export agent

---

## 7. Proposed new repo structure

I would aim for:

```text
Math-To-Manim/
├── math_to_manim/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── schemas/
│   │   ├── request.py
│   │   ├── concept.py
│   │   ├── graph.py
│   │   ├── curriculum.py
│   │   ├── math.py
│   │   ├── storyboard.py
│   │   ├── manim.py
│   │   ├── render.py
│   │   ├── review.py
│   │   └── package.py
│   ├── agents/
│   │   ├── base.py
│   │   ├── intent.py
│   │   ├── prerequisite_graph.py
│   │   ├── curriculum.py
│   │   ├── math_enrichment.py
│   │   ├── storyboard.py
│   │   ├── scene_spec.py
│   │   ├── codegen.py
│   │   ├── static_review.py
│   │   ├── render.py
│   │   ├── video_review.py
│   │   ├── repair.py
│   │   └── publisher.py
│   ├── tools/
│   │   ├── graph_tools.py
│   │   ├── latex_tools.py
│   │   ├── manim_tools.py
│   │   ├── video_tools.py
│   │   ├── example_search.py
│   │   ├── artifact_store.py
│   │   └── eval_tools.py
│   ├── pipeline/
│   │   ├── runner.py
│   │   ├── state.py
│   │   ├── repair_loop.py
│   │   └── tracing.py
│   ├── rendering/
│   │   ├── manim_renderer.py
│   │   └── ffmpeg.py
│   ├── review/
│   │   ├── static.py
│   │   ├── visual.py
│   │   └── scoring.py
│   ├── retrieval/
│   │   ├── index_examples.py
│   │   ├── corpus.py
│   │   └── style_presets.py
│   └── app/
│       ├── gradio_app.py
│       └── api.py
├── examples/
│   ├── showcase/
│   ├── generated/
│   └── reference/
├── evals/
│   ├── prompts.yaml
│   ├── expected_markers.yaml
│   └── run_eval.py
├── scripts/
│   ├── migrate_legacy.py
│   └── build_readme_showcase.py
├── legacy/
│   ├── claude_pipeline/
│   ├── gemini3/
│   └── kimi_k2_5_swarm/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── OPENAI_AGENTS_PIPELINE.md
│   ├── ARTIFACT_SCHEMAS.md
│   └── EVALS.md
└── tests/
    ├── unit/
    ├── integration/
    ├── render/
    └── evals/
```

Important: move old `Gemini3/` and `KimiK2.5Swarm/` into `legacy/` or convert them into adapters. They should not remain as parallel first-class architectures.

---

## 8. Biggest design correction: split “creative planning” from “implementation”

Current code asks the LLM to generate a verbose prompt and then code. That makes codegen too magical.

Better:

Storyboard is creative.
SceneSpec is technical.
Codegen is mechanical.

This reduces failures dramatically.

Example:

`VisualStoryboardAgent` can say:
“Show secant line approaching tangent.”

`SceneSpecAgent` must say:
- use `Axes`
- plot `lambda x: x**2`
- create `Dot`s at x=1 and x=1+h
- create `Line` between graph points
- animate `h_tracker` from 1.5 to 0.05
- update line with `always_redraw`
- label slope formula with `MathTex`

Then `ManimCodeAgent` just implements.

---

## 9. Repair loop design

The app should assume first code generation will often fail.

Repair loop:

1. Generate code.
2. AST parse.
3. Import check.
4. Scene class discovery.
5. Low-quality Manim render.
6. If failure:
   - classify traceback
   - retrieve known repair strategy
   - patch code
   - rerun
7. If render success:
   - extract frames
   - visual review
8. If visual failure:
   - patch layout/timing/text sizes
   - rerender
9. Final high-quality render.
10. Make GIF/thumbnail.

Repair should be surgical. Not “rewrite everything” unless catastrophic.

Common repair categories:
- bad LaTeX
- missing import
- invalid Manim method
- wrong `ThreeDScene` camera call
- object offscreen
- text too large
- overlapping labels
- invalid color constant
- scene class name mismatch
- file path/output path mismatch
- render timeout
- memory-heavy 3D surface

---

## 10. Alternates you may have missed

### A. Don’t use only Manim

Keep Manim as primary, but support multiple render backends:

1. Manim CE
- educational videos
- math animations
- equations

2. Three.js
- interactive 3D web visuals
- topology, geometry, spatial demos

3. p5.js
- fast generative/interactive sketches

4. SVG/HTML explainers
- diagrams, static visual articles

5. Remotion
- web-native video generation

6. Blender Python
- advanced 3D cinematic scenes

A future pipeline could choose backend automatically:
- equations/calculus → Manim
- interactive topology → Three.js
- vector explainer → SVG/HTML
- physical 3D scene → Blender

### B. Build a “visual grammar” library

Instead of generating raw Manim every time, create reusable primitives:

- `ConceptTitle`
- `EquationReveal`
- `AxisScene`
- `SecantToTangent`
- `VectorFieldReveal`
- `Timeline`
- `ParticleSystem`
- `GraphTransform`
- `CameraOrbit`
- `LabelCallout`
- `AhaMoment`

Then agents assemble scenes from known components.

This is probably the single best way to improve reliability.

### C. Build a Manim component registry

The codegen agent should retrieve and use components instead of inventing from scratch.

Example:
- `DerivativeSlopeComponent`
- `FourierEpicycleComponent`
- `LorenzAttractorComponent`
- `SpacetimeGridComponent`
- `BrownianMotionComponent`

### D. Build “style packs”

Examples:
- `3blue1brown`
- `dark_cinematic`
- `neon_scientific`
- `minimal_classroom`
- `paper_diagram`
- `space_documentary`
- `ml_explainer`

Each style pack:
- colors
- fonts
- background
- camera behavior
- equation placement
- transition conventions

### E. Use example mining as pseudo-training

No fine-tuning necessary at first. Mine your examples:
- extract scene classes
- summarize visual techniques
- tag concepts
- tag Manim primitives
- create retrieval index

This turns examples into live context.

### F. Later fine-tune or distill

Only after you have:
- successful prompt/spec/code/render traces
- failure/repair traces
- visual review scores

Fine-tune on:
- `Storyboard -> SceneSpec`
- `SceneSpec -> Manim code`
- `Traceback -> patch`

### G. Add human-in-the-loop checkpoints

For high quality:
- show concept graph before rendering
- show storyboard before code
- let user pick style/duration
- let user approve final repair direction

### H. Create “curriculum mode”

Instead of one animation:
- build a sequence of videos
- each concept becomes a lesson
- export playlist
- generate notes/quizzes

### I. Create “paper-to-animation mode”

Input:
- arXiv PDF
- LaTeX notes
- textbook page
- image/sketch

Pipeline:
- extract concepts
- choose visualizable theorem/idea
- generate animation

This repo already has hints of LaTeX pipeline scripts, but it should become first-class.

### J. Use PR/CI automation

CI should not render every video, but it should run:
- schema unit tests
- fast AST validation
- one tiny Manim smoke render
- example asset checks
- README link checks

Nightly cron can run heavier render evals.

---

## 11. My recommended implementation order

Phase 0: Freeze the current working state
- tag current main
- create `legacy/`
- write architecture decision doc

Phase 1: Schemas first
- Pydantic artifacts
- graph model
- validation tests

Phase 2: Tool layer
- Manim render tools
- LaTeX tools
- video tools
- artifact store

Phase 3: OpenAI Agents SDK runtime
- base agent
- typed outputs
- tracing
- model config

Phase 4: Core pipeline without render repair
- intent
- graph
- curriculum
- math
- storyboard
- scene spec
- codegen

Phase 5: Render and static validation
- AST/import checks
- Manim render
- error classification

Phase 6: Repair loop
- static repair
- render repair
- visual layout repair

Phase 7: Example retrieval
- index examples
- style presets
- retrieval-augmented codegen

Phase 8: Evals
- prompt suite
- run report
- compare pass rate

Phase 9: UI/CLI
- clean CLI
- Gradio/FastAPI app
- artifact browser

Phase 10: Docs and README update
- new architecture
- examples
- contribution guide

---

## 12. Strategic recommendation

If we are redesigning the entire repo using only Codex 5.5, I would not start by asking Codex to “refactor the repo.”

I would start by asking Codex to build the new spine beside the old code:

1. `math_to_manim/schemas`
2. `math_to_manim/tools`
3. `math_to_manim/pipeline`
4. One end-to-end thin vertical slice:
   “derivatives as slopes” → code → render → review

Once that works, migrate old code into it and delete/archive duplicates.

The success criterion for the refactor should be:

A single command:

```bash
math-to-manim generate "Explain why derivatives are slopes" --style cinematic --quality low
```

produces:

```text
runs/<run_id>/
  request.json
  intent.json
  knowledge_graph.json
  curriculum.json
  math_packet.json
  storyboard.json
  scene_spec.json
  generated_scene.py
  validation_report.json
  render_result.json
  review_report.json
  final.mp4
  preview.gif
  thumbnail.png
  manifest.json
```

That would turn this from a cool research prototype into an actual agentic animation engine.
