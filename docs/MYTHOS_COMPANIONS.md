# Mythos companions: the paper and the Lean file

A Mythos run makes a film. A run can now also make two companions that state
and prove the same mathematics:

| Companion | File in the run directory | Charter | Build |
|---|---|---|---|
| `paper` | `paper.tex`, `paper.pdf` | `src/mythos/agents/mythos-paper-author.md` | `pdflatex`, two passes, no shell escape |
| `lean` | `Companion.lean` | `src/mythos/agents/mythos-lean-author.md` | `lake env lean` in the project named by `M2M_LEAN_PROJECT` |

The code is in `src/mythos/companions.py`. The tests are in
`tests/test_companions.py`.

## Run it

With the model backend:

```bash
math-to-manim-mythos run "Why does a top precess?" --render -q m --companions paper,lean
```

With an operator as the model (a Claude session answers each stage):

```bash
python scripts/operate_mythos_chain.py path/to/stages --render -q m --companions paper,lean
```

The operator script asks for `paper.tex` and then for `Companion.lean`, in the
same way that it asks for the six stage replies and the scene.

## What happens to a companion

1. **Write.** The stage receives its charter, the user prompt and the full
   dossier of the run (the six stage artifacts). It returns one fenced block.
2. **Static check.** No tool is needed.
   - Paper: one `\documentclass`, one `document` environment, balanced
     environments, at least one theorem-like statement and one proof, no
     `\input`, `\include`, `\includegraphics` or `\bibliography`, no
     placeholder text.
   - Lean: only Mathlib imports; no `sorry`, `admit`, `native_decide` or
     `axiom` (comments do not count); at least one theorem; a
     `#print axioms` audit.
3. **Build.** The paper is compiled if `pdflatex` is on PATH. The Lean file is
   checked if `M2M_LEAN_PROJECT` names a Lake project that requires Mathlib and
   `lake` is on PATH. A missing tool gives the status `skipped`, not a failure.
4. **One repair.** In a model run, a companion that fails step 2 or step 3
   goes back to the model once, with the list of problems or the build log.
5. **Record.** The result is written to the manifest:

```json
"companions": {
  "paper": {"artifact": "paper.tex",
            "static": {"passed": true, "errors": []},
            "build": {"status": "built", "tool": "pdflatex", "pdf": "paper.pdf", "pages": 11}},
  "lean":  {"artifact": "Companion.lean",
            "static": {"passed": true, "errors": []},
            "build": {"status": "built", "tool": "lake env lean",
                      "toolchain": "leanprover/lean4:v4.33.1", "warnings": 0,
                      "axioms": ["propext, Classical.choice, Quot.sound"]}}
}
```

A companion that fails does not change `status.outcome`: the outcome still
says if a film exists. Read `companions.<name>.build.status` to know if the
paper or the Lean file was built.

## The Lean project

`M2M_LEAN_PROJECT` is a directory with a `lean-toolchain` file and a Lake
configuration that requires Mathlib, with the Mathlib cache downloaded
(`lake exe cache get`). The companion is checked in place; it is not copied
into the project. One project serves all runs.

```bash
mkdir lean-check && cd lean-check
echo "leanprover/lean4:v4.33.1" > lean-toolchain
cat > lakefile.toml <<'EOF'
name = "leancheck"
[[require]]
name = "mathlib"
git = "https://github.com/leanprover-community/mathlib4"
rev = "0df444a360eaa60ab8c11dca51a86af692955474"
EOF
lake update && lake exe cache get
export M2M_LEAN_PROJECT="$PWD"
```

## Settings

| Variable | Meaning | Default |
|---|---|---|
| `M2M_LEAN_PROJECT` | Lake project that checks `Companion.lean` | not set: the Lean build is `skipped` |
| `M2M_COMPANION_TIMEOUT` | seconds for one companion build | 900 |

## Other changes made with this feature

- **Cinematic Charter, rules 8 to 11** (`src/mythos/charter.py`): SPACE (one
  continuous 3D world with stations, at least two 3D set pieces), GEOMETRY IS
  COMPUTED (coordinates and on-screen numbers come from the formulas in the
  scene file), FORMULA ON A CARD (a fixed card for formulas over a 3D set
  piece), HONEST PICTURES. Rule 1 now allows a resting tilt of at most 25
  degrees between formula zooms. Rule 4 limits a caption to 14 words.
- **Render CPU limit** (`src/mythos/render.py`): the limit was a fixed 600 s
  of CPU on Linux, so a long film could not finish even when
  `M2M_RENDER_TIMEOUT` was larger. The CPU limit is now equal to the
  wall-clock budget, with a minimum of 600 s.

## Limits

- The static checks do not judge the mathematics. Only the Lean build does
  that, and only for the statements that the Lean file contains.
- The paper build shows that the file compiles. It does not show that the
  proofs are correct or that the references exist. Read the paper before you
  submit it.
- The REST API and the MCP server do not have a `companions` option yet.
