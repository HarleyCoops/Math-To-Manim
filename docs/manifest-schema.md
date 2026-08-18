# Run manifest schema

Both Mythos and Sol write `manifest.json` at the root of a run directory.
The file now carries `schema_version` so readers can detect and migrate
contract changes instead of silently desyncing from new pipeline code.

## Current version

`schema_version` is `2`.

New manifests also include:

- `artifacts.validation` → `validation.json`
- a validation gate flag (`status.validation` on Mythos, `status_detail.validation` on Sol)

Sol already used the top-level `status` field for the run lifecycle
(`running` / `completed` / `failed`). That string is left alone. The
validation gate lives under `status_detail` so the two meanings do not
collide.

## `validation.json`

Every run workspace is seeded with:

```json
{
  "latex": null,
  "manim_code": null,
  "complexity": null,
  "ran_at": null
}
```

After static checks, the same file is rewritten with the structured
LaTeX report, the Manim AST report, a small complexity summary, and
`ran_at`.

## Migrations

Loaders run `migrate_manifest()` before trusting a file.

| From | To | Change |
|---|---|---|
| missing / `0` | `1` | Insert `schema_version` and the `artifacts` map |
| `1` | `2` | Add `validation.json` to `artifacts` and the validation gate flag |

A future bump must add `migrations[from_version]` and a unit test that
round-trips a fixture from the previous version to the new one.

## Historic Linear note

WAR-1532 named `src/hermes_learns_manim/prompts.py::manifest_template`.
That package is not in this repository. The live writers are
`mythos/manifest_schema.py` and `sol/manifest_schema.py`.
