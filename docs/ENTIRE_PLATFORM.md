# ENTIRE Platform Operations

Math-To-Manim uses ENTIRE as an agent-session system of record and a regional
Git acceleration layer. GitHub remains the source of truth for code, pull
requests, Actions, releases, and public project history.

## What ENTIRE adds

GitHub records the resulting diff and the collaboration around it. ENTIRE
records the work that produced the diff: prompts, agent responses, tool
activity, file activity, timing, token usage when available, and checkpoints
linked to commits. That context makes an agent run explainable, searchable,
resumable, and suitable for later evaluation or training-data preparation.

ENTIRE also provides a regional Git mirror. North American workers can clone
and fetch ordinary Git objects from US East while pushes continue through to
GitHub. Git LFS remains on GitHub.

## Repository topology

| Purpose | Location | Visibility |
|---|---|---|
| Code, PRs, releases | `https://github.com/HarleyCoops/Math-To-Manim` | Public |
| Permanent checkpoints | `https://github.com/HarleyCoops/math-to-manim-checkpoints` | Private |
| Regional Git mirror | `entire://aws-us-east-2.entire.io/gh/harleycoops/math-to-manim` | ENTIRE-authenticated |
| Private checkpoint mirror | `entire://aws-us-east-2.entire.io/gh/harleycoops/math-to-manim-checkpoints` | ENTIRE-authenticated |

The permanent metadata ref is `refs/heads/entire/checkpoints/v1`. It must exist
in the private checkpoint repository and must never exist in the public source
repository.

## Windows ARM64 installation

The foundation is pinned to ENTIRE CLI v0.9.0. The official archive is:

```text
https://github.com/entireio/cli/releases/download/v0.9.0/entire_windows_arm64.zip
SHA-256: ddaf1ba890388ed1889870b4b30b771eb5f3a95488d4e897b1e4820707a9602d
```

Verify the archive before extracting it. Install both executables from the
archive, not only the main CLI:

```powershell
$archive = "$env:TEMP\entire_windows_arm64.zip"
$expected = "ddaf1ba890388ed1889870b4b30b771eb5f3a95488d4e897b1e4820707a9602d"
$actual = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw "ENTIRE checksum mismatch: $actual" }

$expanded = "$env:TEMP\entire_windows_arm64"
Expand-Archive -LiteralPath $archive -DestinationPath $expanded
$installDir = "$env:LOCALAPPDATA\Programs\Entire"
New-Item -ItemType Directory -Path $installDir -Force | Out-Null
Copy-Item "$expanded\entire.exe" "$installDir\entire.exe"
Copy-Item "$expanded\git-remote-entire.exe" "$installDir\git-remote-entire.exe"
```

Add `$installDir` to the user `PATH`, then start a new terminal. Existing app
processes retain their old environment; in one of those shells, prepend the
directory to `$env:Path` before using an `entire://` remote.

Verify both programs:

```powershell
entire version
git-remote-entire --version
entire auth status
```

## Daily diagnostics

Run these from the repository root:

```powershell
entire status
entire doctor
entire checkpoint list
entire session current --json
entire session tokens --agent-brief
```

`session current --json` is metadata-only. Do not use `--transcript` in logs or
CI because that flag streams the raw local transcript.

Codex project hooks require a one-time trust decision. If `entire doctor`
reports `Codex hook trust: REVIEW NEEDED`, open `/hooks` inside Codex for this
repository and approve the four hooks. Never fabricate `trusted_hash` entries.

## Agent hooks

Shared hook declarations live at:

- Codex: `.codex/hooks.json` and `.codex/config.toml`
- Claude Code: `.claude/settings.json`
- ENTIRE project policy: `.entire/settings.json`

Machine-local logs, metadata, reconciliation output, and personal settings are
ignored through `.entire/.gitignore`. ENTIRE's Git hooks chain the existing Git
LFS hooks; do not replace either side of that chain manually.

## Privacy policy

Permanent transcripts go only to the private checkpoint repository. Shared
settings disable anonymous telemetry, enable email and phone PII redaction,
and add generic redactors for short `sk-` and bearer-style credentials that
the entropy detector may otherwise miss.

Before and after a checkpoint push, prove the routing explicitly:

```powershell
git ls-remote `
  "https://github.com/HarleyCoops/math-to-manim-checkpoints.git" `
  "refs/heads/entire/checkpoints/v1"
git ls-remote origin "refs/heads/entire/checkpoints/v1"
```

The first command must print one ref. The second must print nothing. ENTIRE
redaction is a safety net, not permission to place credentials or private
files in agent context. Never push local `entire/*` shadow refs manually.

The private checkpoint repository is also mirrored in US East. ENTIRE v0.9.0
derives a structured checkpoint remote using the transport of the source push:
when code is pushed through an `entire://` source mirror, it tries the matching
`entire://` checkpoint URL. Both mirrors are therefore required for automatic
checkpoint sync on mirror pushes. If checkpoint sync ever warns while the code
push succeeds, retry explicitly through the GitHub transport context:

```powershell
entire hooks git pre-push origin
```

Then repeat both private-positive and public-negative ref checks above.

## Historical development sessions

The ignored reconciliation file is
`.entire/tmp/session-import-inventory.json`. Rebuild its metadata without
copying transcript bodies into the working tree:

```powershell
python scripts/entire/session_inventory.py `
  --repo-root (Get-Location) `
  --repo-url "https://github.com/HarleyCoops/Math-To-Manim.git" `
  --repo-url "https://github.com/unitseeker/math-to-manim" `
  --codex-root "$env:USERPROFILE\.codex\sessions" `
  --claude-project-dir "$env:USERPROFILE\.claude\projects\C--Users-chris-Math-To-Manim" `
  --claude-project-dir "$env:USERPROFILE\.claude\projects\C--Users-chris-OneDrive-Documents-Math-To-Manim" `
  --output ".entire\tmp\session-import-inventory.json"

entire import codex --dry-run
entire import claude-code --dry-run
```

ENTIRE v0.9.0 has a fixed 30-day file-modification lookback. Older Codex logs
can be imported from ignored temporary copies with current modification times;
do not alter originals. A Codex transcript whose recorded working directory is
outside the current repository cannot be attributed by the built-in v0.9.0
importer even when its Git remote matches. Preserve those records for the
`m2m-entire reconcile-development` backfill path.

## US-East mirror

The local remote named `entire` is the regional read path:

```powershell
git remote -v
git fetch entire
git rev-parse refs/remotes/origin/main
git rev-parse refs/remotes/entire/main
```

The two `main` hashes must match. For fresh high-throughput worker clones:

```powershell
$env:GIT_LFS_SKIP_SMUDGE = "1"
git clone `
  "entire://aws-us-east-2.entire.io/gh/harleycoops/math-to-manim" `
  Math-To-Manim
Remove-Item Env:GIT_LFS_SKIP_SMUDGE

git -C Math-To-Manim config lfs.url `
  "https://github.com/HarleyCoops/Math-To-Manim.git/info/lfs"
git -C Math-To-Manim lfs pull
git -C Math-To-Manim lfs fsck
```

If ENTIRE is unavailable, fetch or clone from GitHub. Do not make an
ENTIRE-native unmirrored branch the only copy of work. Source pushes may stay
on GitHub; validated mirror pushes pass through to GitHub.

## Native Math-To-Manim capture boundary

The milestone-two integration is provider-neutral and will live in
`m2m_entire/`. It exposes `entire-agent-m2m` for ENTIRE's external-agent
protocol and `m2m-entire` for diagnostics, backfill, RL wrappers, resume, and
training-example export.

This adapter is observational infrastructure:

- `mythos/` never imports Sol orchestration;
- `sol/` never imports Mythos prompts, backends, or orchestration;
- the standalone RL environment is read through ledger schemas, not imported;
- normalized JSONL is written locally before any ENTIRE subprocess call;
- hook calls use argument arrays, no shell, bounded output, and short timeouts;
- capture failures never change generation, rendering, evaluation, or training
  results.

Media, frame archives, weights, caches, and environment directories are stored
as paths and SHA-256 hashes, not copied into transcripts. Later model-harness
exports apply a separate privacy filter and retain private-session provenance.

## References

- [ENTIRE overview](https://docs.entire.io/overview)
- [Sessions](https://docs.entire.io/guides/sessions/overview)
- [Repository mirrors](https://docs.entire.io/guides/repositories/mirrors)
- [Security and privacy](https://docs.entire.io/security)
