# Render sandbox and residual risk

This note is the WAR-1533 audit of how generated Manim is executed. There
is no `renderer.py` in the current tree. The live render wrappers are:

- `mythos/render.py` for Mythos
- `sol/rendering.py` for Sol

## What was wrong

Mythos previously invoked Manim with `cwd` set to the repository root and
without `--media_dir`. Manim then wrote `media/` next to the checkout.
Sol already pinned `--media_dir` and `cwd` to the run directory.

## What the wrappers now enforce

- Argument vector only. No `shell=True`, no string-concatenated commands.
- `cwd` is the run directory.
- `--media_dir` is `<run_dir>/media`.
- Scene file and media paths are resolved and rejected if they escape
  `run_dir`.
- `scene_name` must be a Python identifier.
- Quality must be one of `l m h p k`.
- A wall-clock timeout is always set.
- On Linux the child gets best-effort `RLIMIT_CPU` and `RLIMIT_AS` caps.

## Threat model

`mythos_scene.py` / `sol_scene.py` is trusted-with-caveats agent output.
Manim imports and executes that file. The wrapper can pin where media
lands. It cannot make arbitrary Python safe.

Assumptions:

- The operator intended to render this run.
- The scene should not need network access. The static verifier blocks
  common network and process imports. That is not a sandbox.
- Render outputs stay inside `run_dir`.

## Residual risk

- Windows has no `resource.setrlimit`.
- Address-space limits are best-effort and can fail inside constrained
  CI containers.
- Manim itself may shell out to LaTeX, FFmpeg, and dvisvgm. Those tools
  inherit the child environment.
- A scene that avoids the blocked-import list can still do work the
  verifier does not see, including `pathlib.Path.write_text` and
  `__import__` via getattr tricks.
- There is no user-namespace jail, seccomp filter, or network namespace.

A follow-up that is too involved for this pass: run Manim under
bubblewrap or a similar OS sandbox with no network and a writable
bind-mount of `run_dir` only.
