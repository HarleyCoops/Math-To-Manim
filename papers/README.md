# OpenAI mathematics in 3D

A public film series built from the [OpenAI manuscript map](https://github.com/HarleyCoops/math).
Each episode turns one paper into a spatial explanation: actual 3D geometry,
camera motion and zooms, readable LaTeX, numerical examples, and an attributed
outline of the paper's argument.

Production uses the existing **Codex SDK / GPT-6 Astra chain**. Real TypeSafe
Jev remains available through its separate API. This pilot explicitly disables
Jev and retains independent Astra evidence audits. Published films will link their source,
production records and actual render evidence; a source file or proposed
storyboard is not a finished episode.

| Episode | Paper | Status |
| --- | --- | --- |
| 01 · The Shape and Its Shadow | [Symmetric Mahler and its equality cases](mahler/README.md), family 087 | Complete 179.8-second 720p/30 fps cloud film; Astra source and 23 rendered frames reviewed; Jev off |

The pilot begins with a cube and its polar octahedron, computes the exact
volume product, follows inverse-transpose duality, and reveals the manuscript's
analytic lens and integrated simplex-volume argument. Its all-dimensional
result is attributed to the manuscript. The film does not certify the Lean
formalization or independently prove the analytic input.

## Run the pilot

Install the project and pinned SDK following the root README. The existing
Codex ChatGPT login supplies Astra access. Jev-off mode needs no TypeSafe key.
To enable advisory or gated Jev reviews later, save `TYPESAFE_API_KEY=...` in
the git-ignored `.env.local`. Never commit that file.

```bash
python scripts/drive_astra_mcp.py papers/mahler --quality m --review-mode off --no-render
python scripts/drive_astra_mcp.py papers/mahler --inspect <run-id>
```

This client uses the real MCP protocol. The new Astra MCP front door invokes
`astra.pipeline.Pipeline` without replacing its orchestration. The client keeps
the connection open while the worker records progress and SDK evidence under
`runs/astra/<run-id>/`. With `--no-render`, this phase produces scene code.
Its `astra_only` label describes Astra audits, never Jev approval.

The `Render a paper film` GitHub Actions workflow renders the retained
`papers/mahler/candidate.json`, with no model calls or API keys. It installs
FFmpeg alongside the pinned Manim image and saves the MP4, sampled frames,
contact sheet, source and logs as a 30-day artifact. That separate render is
`not_reviewed` until actual rendered evidence is inspected. The Mahler pilot's
MP4, preview and review records are now public in its episode folder. Its rendered
frame review does not certify every transition or the manuscript proof.
