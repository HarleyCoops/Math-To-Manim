# ENTIRE Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a verified ENTIRE foundation for Math-To-Manim with private
checkpoint storage, Codex and Claude session capture, reconciled historical
sessions, and a US-East repository mirror.

**Architecture:** Keep public code and releases on GitHub, route permanent
ENTIRE checkpoint data to a private sibling GitHub repository, and add the
US-East EntireDB mirror as a second Git remote. Install built-in agent hooks
without replacing existing Git LFS hooks or Claude permissions, then prove the
topology with historical import, mirror, LFS, push-through, and live-session
checks.

**Tech Stack:** ENTIRE CLI v0.9.0, Git/Git LFS, GitHub CLI, PowerShell 7,
Python 3.10+, pytest, Codex CLI, Claude Code.

**Design:**
`docs/superpowers/specs/2026-07-31-entire-platform-integration-design.md`

## Global Constraints

- Work on `codex/prime-visual-improvement-rl`; do not create or switch the
  implementation branch unless the user requests it.
- Preserve the current unrelated modifications and untracked files under
  `environments/m2m2_visual_improvement/`, `scripts/make_gifs.ps1`,
  `scripts/make_traitor_gif.ps1`, and `tmp/`.
- Stage every foundation commit by exact path; never use `git add .`.
- Keep `origin` pointed at `https://github.com/HarleyCoops/Math-To-Manim.git`.
- Store permanent checkpoints only in private
  `HarleyCoops/math-to-manim-checkpoints`.
- Use ENTIRE's US-East cluster `aws-us-east-2.entire.io`.
- Keep Git LFS object transfers on GitHub; ENTIRE mirrors do not serve LFS.
- Do not push an `entire/checkpoints/v1` ref to the public source repository.
- Do not print or commit tokens, credentials, `.env`, transcript bodies,
  personal settings, or device-auth state.
- Disable ENTIRE anonymous telemetry and enable PII email/phone redaction.
- Treat ENTIRE as fail-open observational infrastructure.
- Use the stable Windows ARM64 release archive with SHA-256
  `ddaf1ba890388ed1889870b4b30b771eb5f3a95488d4e897b1e4820707a9602d`.
- Do not install Scoop or Go solely to install the ENTIRE CLI.

---

### Task 1: Install and Verify ENTIRE v0.9.0

**Files:**

- Create locally:
  `C:\Users\chris\AppData\Local\Programs\Entire\entire.exe`
- Do not modify repository files.

**Interfaces:**

- Consumes: official v0.9.0 GitHub release archive and checksum.
- Produces: `entire` available on the current and user `PATH`, reporting
  version `0.9.0`.

- [ ] **Step 1: Confirm architecture, target, and absence of another binary**

```powershell
[System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture
Get-Command entire -ErrorAction SilentlyContinue
[Environment]::GetEnvironmentVariable("Path", "User")
```

Expected: architecture is `Arm64`; the initial command lookup is empty; no
existing ENTIRE installation is overwritten without inspection.

- [ ] **Step 2: Download into a unique temporary directory**

```powershell
$entireTemp = Join-Path $env:TEMP ("m2m-entire-v0.9.0-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $entireTemp | Out-Null
$archive = Join-Path $entireTemp "entire_windows_arm64.zip"
Invoke-WebRequest -UseBasicParsing `
  -Uri "https://github.com/entireio/cli/releases/download/v0.9.0/entire_windows_arm64.zip" `
  -OutFile $archive
```

Expected: `$archive` exists and is approximately 20 MB.

- [ ] **Step 3: Verify the pinned SHA-256 before extraction**

```powershell
$expected = "ddaf1ba890388ed1889870b4b30b771eb5f3a95488d4e897b1e4820707a9602d"
$actual = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) {
  throw "ENTIRE archive checksum mismatch: $actual"
}
```

Expected: no exception.

- [ ] **Step 4: Install to the user-local program directory**

```powershell
$expanded = Join-Path $entireTemp "expanded"
Expand-Archive -LiteralPath $archive -DestinationPath $expanded
$sourceBinary = Get-ChildItem -File -Recurse $expanded -Filter "entire.exe" |
  Select-Object -First 1
if (-not $sourceBinary) {
  throw "entire.exe was not present in the verified archive"
}
$installDir = Join-Path $env:LOCALAPPDATA "Programs\Entire"
New-Item -ItemType Directory -Path $installDir -Force | Out-Null
Copy-Item -LiteralPath $sourceBinary.FullName `
  -Destination (Join-Path $installDir "entire.exe")
```

Expected: the installed file exists at the declared local path.

- [ ] **Step 5: Add the exact directory to the user and current PATH**

```powershell
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$pathEntries = @($userPath -split ";" | Where-Object { $_ })
if ($installDir -notin $pathEntries) {
  $newUserPath = (($pathEntries + $installDir) -join ";")
  [Environment]::SetEnvironmentVariable("Path", $newUserPath, "User")
}
if ($installDir -notin ($env:Path -split ";")) {
  $env:Path = "$installDir;$env:Path"
}
```

- [ ] **Step 6: Verify the installed executable**

```powershell
Get-Command entire
entire version
```

Expected: command source is the user-local binary and output contains
`0.9.0`.

- [ ] **Step 7: Preserve installation evidence without committing it**

```powershell
$evidenceDir = Join-Path (Get-Location) ".tmp-runs\entire-foundation"
New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
Get-FileHash (Join-Path $installDir "entire.exe") -Algorithm SHA256 |
  Format-List | Out-File (Join-Path $evidenceDir "install-hash.txt")
entire version | Out-File (Join-Path $evidenceDir "version.txt")
git check-ignore ".tmp-runs/entire-foundation/version.txt"
```

Expected: evidence is ignored by Git.

### Task 2: Create Private Checkpoint Storage and Authenticate ENTIRE

**Files:**

- Create externally: private GitHub repository
  `HarleyCoops/math-to-manim-checkpoints`.
- Create local ENTIRE device-auth state outside the repository.
- Do not modify tracked repository files.

**Interfaces:**

- Consumes: authenticated GitHub CLI account `HarleyCoops` and installed
  ENTIRE CLI.
- Produces: verified private checkpoint repository and authenticated ENTIRE
  account with GitHub identity linked.

- [ ] **Step 1: Reconfirm GitHub identity and source access**

```powershell
gh auth status
gh repo view HarleyCoops/Math-To-Manim `
  --json nameWithOwner,visibility,url,viewerPermission
```

Expected: active account is `HarleyCoops`, source visibility is `PUBLIC`, and
viewer permission permits administration of the mirror/App connection.

- [ ] **Step 2: Create the private empty repository idempotently**

```powershell
$checkpointRepo = "HarleyCoops/math-to-manim-checkpoints"
gh repo view $checkpointRepo --json nameWithOwner,visibility,url 2>$null
if ($LASTEXITCODE -ne 0) {
  gh repo create $checkpointRepo `
    --private `
    --description "Private ENTIRE checkpoints for Math-To-Manim" `
    --disable-issues `
    --disable-wiki
}
```

- [ ] **Step 3: Prove the repository is private and empty**

```powershell
gh repo view HarleyCoops/math-to-manim-checkpoints `
  --json nameWithOwner,visibility,isEmpty,url
```

Expected: `visibility` is `PRIVATE` and `isEmpty` is `true` before ENTIRE's
first checkpoint push.

- [ ] **Step 4: Complete ENTIRE device authentication**

```powershell
entire login
entire auth status
```

Expected: the device flow completes in the user's browser and auth status is
authenticated. Do not capture the device code or tokens in repository files.

- [ ] **Step 5: Authorize the ENTIRE GitHub App narrowly**

Use the ENTIRE web authorization flow to grant the GitHub App access to:

```text
HarleyCoops/Math-To-Manim
HarleyCoops/math-to-manim-checkpoints
```

Do not select all repositories. Re-run:

```powershell
entire auth status
entire repo mirror create github.com/HarleyCoops/Math-To-Manim `
  aws-us-east-2.entire.io --no-wait
```

Expected: authentication succeeds and mirror registration is accepted. The
`--no-wait` registration is idempotent; full readiness is verified in Task 5.

### Task 3: Enable Shared Foundation Configuration and Preserve Existing Hooks

**Files:**

- Create: `.entire/settings.json`
- Create: `.entire/.gitignore`
- Create: `.codex/hooks.json`
- Create: `.codex/config.toml`
- Create or modify: `.claude/settings.json`
- Create: `tests/test_entire_foundation.py`
- Preserve locally: `.claude/settings.local.json`
- Preserve locally: `.git/hooks/post-checkout`, `.git/hooks/post-commit`,
  `.git/hooks/post-merge`, `.git/hooks/pre-push`

**Interfaces:**

- Consumes: authenticated ENTIRE CLI and private checkpoint repository.
- Produces: shared settings with Codex/Claude capture, external-agent discovery,
  private checkpoint routing, privacy settings, and passing static contract
  tests.

- [ ] **Step 1: Write the failing shared-settings contract test**

Create `tests/test_entire_foundation.py`:

```python
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_entire_routes_checkpoints_privately() -> None:
    settings = json.loads((ROOT / ".entire" / "settings.json").read_text())
    assert settings["enabled"] is True
    assert settings["external_agents"] is True
    assert settings["telemetry"] is False
    assert settings["strategy_options"]["checkpoint_remote"] == {
        "provider": "github",
        "repo": "HarleyCoops/math-to-manim-checkpoints",
    }
    assert settings["redaction"]["pii"] == {
        "enabled": True,
        "email": True,
        "phone": True,
        "address": False,
    }


def test_agent_hooks_are_project_scoped() -> None:
    codex_hooks = (ROOT / ".codex" / "hooks.json").read_text()
    codex_config = (ROOT / ".codex" / "config.toml").read_text()
    claude_settings = (ROOT / ".claude" / "settings.json").read_text()
    assert "entire" in codex_hooks.lower()
    assert "codex_hooks = true" in codex_config.lower()
    assert "entire" in claude_settings.lower()


def test_entire_local_state_is_ignored() -> None:
    patterns = (ROOT / ".entire" / ".gitignore").read_text().splitlines()
    assert "settings.local.json" in patterns
    assert "logs/" in patterns
    assert "m2m-sessions/" in patterns
    assert "tmp/" in patterns
```

- [ ] **Step 2: Run the test to prove configuration is absent**

```powershell
python -m pytest tests/test_entire_foundation.py -q
```

Expected: failure because `.entire/settings.json` and agent hook files do not
exist.

- [ ] **Step 3: Snapshot the existing local hook and Claude state**

```powershell
$evidenceDir = ".tmp-runs\entire-foundation"
New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
Get-ChildItem -File ".git\hooks" |
  Where-Object { $_.Name -in @("post-checkout", "post-commit", "post-merge", "pre-push") } |
  Get-FileHash -Algorithm SHA256 |
  ConvertTo-Json |
  Out-File "$evidenceDir\hooks-before.json"
$claudeLocal = Get-Content -Raw ".claude\settings.local.json" |
  ConvertFrom-Json
$claudeLocal.PSObject.Properties.Name |
  Out-File "$evidenceDir\claude-local-keys-before.txt"
```

- [ ] **Step 4: Enable Codex and add Claude Code through ENTIRE**

```powershell
entire enable -y `
  --agent codex `
  --telemetry=false `
  --checkpoint-remote github:HarleyCoops/math-to-manim-checkpoints
entire agent add claude-code
entire status
```

Expected: ENTIRE reports enabled; both agents are listed.

- [ ] **Step 5: Complete the shared settings with an exact patch**

Use `apply_patch` to preserve CLI-generated fields and ensure the effective
`.entire/settings.json` contains these values:

```json
{
  "enabled": true,
  "external_agents": true,
  "strategy_options": {
    "checkpoint_remote": {
      "provider": "github",
      "repo": "HarleyCoops/math-to-manim-checkpoints"
    }
  },
  "telemetry": false,
  "redaction": {
    "pii": {
      "enabled": true,
      "email": true,
      "phone": true,
      "address": false
    }
  }
}
```

Do not remove additional fields written by ENTIRE v0.9.0.

- [ ] **Step 6: Verify hooks were merged rather than replaced**

```powershell
entire agent list
entire status
entire doctor
Select-String -Path ".git\hooks\pre-push" -Pattern "git lfs|entire"
Get-Content -Raw ".claude\settings.local.json" | ConvertFrom-Json |
  Select-Object -ExpandProperty permissions
```

Expected: the effective pre-push path reaches both LFS and ENTIRE, the other
LFS lifecycle hooks remain functional, and local Claude permissions still
deserialize.

- [ ] **Step 7: Run the static test and repository tests**

```powershell
python -m pytest tests/test_entire_foundation.py -q
python -m pytest -q
```

Expected: both commands pass.

- [ ] **Step 8: Review the exact staged set**

```powershell
git add -- `
  .entire/settings.json `
  .entire/.gitignore `
  .codex/hooks.json `
  .codex/config.toml `
  .claude/settings.json `
  tests/test_entire_foundation.py
git diff --cached --check
git diff --cached --name-status
```

Expected: only the six declared paths are staged; none of the existing RL or
render files appears.

- [ ] **Step 9: Commit the shared foundation configuration**

```powershell
git commit -m "chore: enable private Entire checkpoints"
```

### Task 4: Reconcile and Import All Historical Development Sessions

**Files:**

- Create: `scripts/entire/session_inventory.py`
- Create: `tests/test_entire_session_inventory.py`
- Create locally and ignore:
  `.entire/tmp/session-import-inventory.json`

**Interfaces:**

- Consumes: Codex JSONL roots, Claude project transcript roots, repository root,
  and GitHub remote URL.
- Produces: deterministic candidate inventory with `agent`, `session_id`,
  `source_path`, `started_at`, `repo_match`, `sha256`, `import_status`, and
  `checkpoint_id` fields.

- [ ] **Step 1: Write failing inventory tests with sanitized fixtures**

Create `tests/test_entire_session_inventory.py`:

```python
import json
from pathlib import Path

from scripts.entire.session_inventory import discover_claude, discover_codex


def test_codex_inventory_matches_repo_cwd_and_remote(tmp_path: Path) -> None:
    root = tmp_path / "codex"
    root.mkdir()
    matching = root / "rollout-2026-07-01T00-00-00-session-a.jsonl"
    matching.write_text(json.dumps({
        "timestamp": "2026-07-01T00:00:00Z",
        "type": "session_meta",
        "payload": {
            "session_id": "session-a",
            "cwd": "C:/work/Math-To-Manim",
            "git": {"repository_url": "https://github.com/HarleyCoops/Math-To-Manim.git"},
        },
    }) + "\n", encoding="utf-8")
    candidates = discover_codex(
        root,
        Path("C:/work/Math-To-Manim"),
        {"https://github.com/HarleyCoops/Math-To-Manim.git"},
    )
    assert [item.session_id for item in candidates] == ["session-a"]
    assert len(candidates[0].sha256) == 64


def test_claude_inventory_uses_repo_scoped_project_dirs(tmp_path: Path) -> None:
    project = tmp_path / "C--work-Math-To-Manim"
    project.mkdir()
    transcript = project / "session-b.jsonl"
    transcript.write_text(
        json.dumps({"type": "ai-title", "sessionId": "session-b"}) + "\n",
        encoding="utf-8",
    )
    candidates = discover_claude([project])
    assert [item.session_id for item in candidates] == ["session-b"]
    assert candidates[0].agent == "claude-code"
```

- [ ] **Step 2: Prove the tests fail**

```powershell
python -m pytest tests/test_entire_session_inventory.py -q
```

Expected: import failure because the inventory module does not exist.

- [ ] **Step 3: Implement bounded transcript discovery**

Create `scripts/entire/session_inventory.py` with this public interface:

```python
@dataclass(frozen=True)
class SessionCandidate:
    agent: str
    session_id: str
    source_path: str
    started_at: str | None
    repo_match: str
    sha256: str
    import_status: str = "pending"
    checkpoint_id: str | None = None
```

Define `discover_codex(root: Path, repo_root: Path, repo_urls: set[str]) ->
list[SessionCandidate]` and `discover_claude(project_dirs: list[Path]) ->
list[SessionCandidate]`. Implement them so they:

- stream files rather than loading full transcripts;
- inspect at most the first 128 JSONL records for Codex session metadata;
- support current `session_meta.payload` and legacy top-level `id`, `cwd`, and
  `git` shapes;
- compare paths case-insensitively on Windows;
- match either repository root or exact known GitHub remote;
- derive Claude IDs from `sessionId` or the filename stem;
- hash each complete transcript with streaming SHA-256;
- sort by `(agent, started_at or "", session_id)`;
- serialize only metadata, never transcript bodies.

Add a `main()` that accepts repeated `--claude-project-dir`, `--codex-root`,
`--repo-root`, `--repo-url`, and `--output` arguments.

- [ ] **Step 4: Run the focused and root tests**

```powershell
python -m pytest tests/test_entire_session_inventory.py -q
python -m pytest -q
```

Expected: both pass.

- [ ] **Step 5: Build the real ignored reconciliation inventory**

```powershell
python scripts/entire/session_inventory.py `
  --repo-root "C:\Users\chris\Math-To-Manim" `
  --repo-url "https://github.com/HarleyCoops/Math-To-Manim.git" `
  --repo-url "https://github.com/unitseeker/math-to-manim" `
  --codex-root "C:\Users\chris\.codex\sessions" `
  --claude-project-dir "C:\Users\chris\.claude\projects\C--Users-chris-Math-To-Manim" `
  --claude-project-dir "C:\Users\chris\.claude\projects\C--Users-chris-OneDrive-Documents-Math-To-Manim" `
  --output ".entire\tmp\session-import-inventory.json"
git check-ignore ".entire/tmp/session-import-inventory.json"
```

Expected: output is valid JSON, contains no transcript text, and is ignored.

- [ ] **Step 6: Run broad dry-run imports**

```powershell
entire import codex --dry-run
entire import claude-code --dry-run
```

Expected: ENTIRE reports repository-scoped candidates and writes no checkpoint.

- [ ] **Step 7: Dry-run every inventoried session explicitly**

```powershell
$inventoryPath = ".entire\tmp\session-import-inventory.json"
$inventory = Get-Content -Raw $inventoryPath | ConvertFrom-Json
foreach ($session in $inventory.sessions) {
  entire import $session.agent --session $session.session_id --dry-run
}
```

Record only success/error disposition and checkpoint IDs back into the ignored
inventory. Do not add transcript output to the inventory.

- [ ] **Step 8: Import every accepted session**

```powershell
foreach ($session in $inventory.sessions) {
  entire import $session.agent --session $session.session_id
}
```

Expected: accepted sessions become read-only checkpoints. Parser failures are
kept with their source path, hash, and exact error for milestone-two backfill.

- [ ] **Step 9: Prove idempotency and inspect private data before push**

```powershell
entire import codex --dry-run
entire import claude-code --dry-run
entire checkpoint list
git log --oneline --decorate entire/checkpoints/v1 -10
git show --stat entire/checkpoints/v1
```

Expected: repeat import identifies prior turns; private branch inspection shows
redacted metadata and no source snapshots, `.env`, or credentials.

- [ ] **Step 10: Push only to the checkpoint remote and verify visibility**

Trigger the ENTIRE checkpoint sync using its documented push path, then run:

```powershell
git ls-remote "https://github.com/HarleyCoops/math-to-manim-checkpoints.git" `
  "refs/heads/entire/checkpoints/v1"
git ls-remote "https://github.com/HarleyCoops/Math-To-Manim.git" `
  "refs/heads/entire/checkpoints/v1"
```

Expected: the private repository prints one checkpoint ref; the public
repository prints none.

- [ ] **Step 11: Commit only inventory tooling and tests**

```powershell
git add -- `
  scripts/entire/session_inventory.py `
  tests/test_entire_session_inventory.py
git diff --cached --check
git commit -m "feat: inventory historical agent sessions"
```

### Task 5: Create and Verify the US-East ENTIRE Mirror

**Files:**

- Modify locally: `.git/config` to add remote `entire` and GitHub LFS URL.
- Create temporary ignored clone under `.tmp-runs/entire-mirror-smoke-*`.
- Do not modify tracked files.

**Interfaces:**

- Consumes: authorized GitHub App, authenticated ENTIRE account, public source
  repository.
- Produces: ready US-East mirror URL and verified Git/LFS/push-through behavior.

- [ ] **Step 1: Create or join the US-East mirror and wait for readiness**

```powershell
entire repo mirror create `
  github.com/HarleyCoops/Math-To-Manim `
  aws-us-east-2.entire.io
```

Expected URL:

```text
entire://aws-us-east-2.entire.io/gh/HarleyCoops/Math-To-Manim
```

- [ ] **Step 2: Add the mirror as a second remote idempotently**

```powershell
$mirrorUrl = "entire://aws-us-east-2.entire.io/gh/HarleyCoops/Math-To-Manim"
$existing = git remote get-url entire 2>$null
if ($LASTEXITCODE -eq 0) {
  git remote set-url entire $mirrorUrl
} else {
  git remote add entire $mirrorUrl
}
git remote -v
```

Expected: `origin` still targets GitHub and `entire` targets US East.

- [ ] **Step 3: Fetch and compare source refs**

```powershell
git fetch origin
git fetch entire
$originMain = git rev-parse "refs/remotes/origin/main"
$entireMain = git rev-parse "refs/remotes/entire/main"
if ($originMain -ne $entireMain) {
  throw "ENTIRE mirror main ref does not match GitHub"
}
```

- [ ] **Step 4: Make a disposable mirror clone with LFS directed to GitHub**

```powershell
$cloneRoot = Join-Path (Get-Location) `
  (".tmp-runs\entire-mirror-smoke-" + [guid]::NewGuid())
$env:GIT_LFS_SKIP_SMUDGE = "1"
git clone $mirrorUrl $cloneRoot
Remove-Item Env:GIT_LFS_SKIP_SMUDGE
git -C $cloneRoot config lfs.url `
  "https://github.com/HarleyCoops/Math-To-Manim.git/info/lfs"
git -C $cloneRoot lfs pull
```

Expected: ordinary Git data comes from ENTIRE and LFS objects come from GitHub.

- [ ] **Step 5: Verify a push-through branch reaches GitHub**

```powershell
$smokeBranch = "codex/entire-mirror-smoke-20260731"
git -C $cloneRoot switch -c $smokeBranch
git -C $cloneRoot commit --allow-empty -m "test: verify Entire mirror push"
git -C $cloneRoot push -u origin $smokeBranch
gh api "repos/HarleyCoops/Math-To-Manim/branches/$smokeBranch" `
  --jq '.name'
```

Expected: GitHub reports the exact smoke branch, proving push-through.

- [ ] **Step 6: Remove the disposable remote branch and local clone safely**

```powershell
git -C $cloneRoot push origin --delete $smokeBranch
$resolvedClone = (Resolve-Path -LiteralPath $cloneRoot).Path
$resolvedTmp = (Resolve-Path -LiteralPath ".tmp-runs").Path
if (-not $resolvedClone.StartsWith($resolvedTmp, [StringComparison]::OrdinalIgnoreCase)) {
  throw "Refusing to remove clone outside .tmp-runs"
}
Remove-Item -LiteralPath $resolvedClone -Recurse -Force
```

Expected: GitHub no longer lists the branch; only the verified ignored clone is
removed.

- [ ] **Step 7: Re-run negative checkpoint-ref verification**

```powershell
git ls-remote origin "refs/heads/entire/checkpoints/v1"
```

Expected: no output.

### Task 6: Prove Live Session Capture and Document the Foundation

**Files:**

- Create: `docs/ENTIRE_PLATFORM.md`
- Create temporarily: ignored smoke worktree and smoke branch.
- Modify only failures found in foundation-owned files.

**Interfaces:**

- Consumes: enabled agent hooks, private checkpoint remote, ready mirror.
- Produces: one real private smoke checkpoint, operator documentation, and a
  requirement-by-requirement milestone-one audit.

- [ ] **Step 1: Create a dedicated ignored smoke worktree**

Use the `superpowers:using-git-worktrees` skill before this step. Then create a
worktree under `.tmp-runs` from the current committed foundation head:

```powershell
$smokeWorktree = Join-Path (Get-Location) ".tmp-runs\entire-session-smoke"
git worktree add -b codex/entire-session-smoke $smokeWorktree HEAD
```

- [ ] **Step 2: Run one bounded Codex smoke session**

```powershell
codex exec --sandbox workspace-write `
  --cd $smokeWorktree `
  "Create docs/entire-smoke.md containing only: ENTIRE session capture smoke test."
git -C $smokeWorktree add -- docs/entire-smoke.md
git -C $smokeWorktree commit -m "test: capture Entire Codex session"
```

Expected: the commit message gains an `Entire-Checkpoint` trailer and ENTIRE
lists the session/checkpoint.

- [ ] **Step 3: Inspect the smoke checkpoint and token metadata**

```powershell
entire checkpoint list
entire checkpoint explain HEAD
entire session current --json
entire session tokens --agent-brief
```

Expected: prompt, transcript, file activity, timestamps, and Codex token fields
are present without credential values.

- [ ] **Step 4: Push the smoke branch through ENTIRE and verify private sync**

```powershell
git -C $smokeWorktree remote add entire `
  "entire://aws-us-east-2.entire.io/gh/HarleyCoops/Math-To-Manim"
git -C $smokeWorktree push -u entire codex/entire-session-smoke
git ls-remote `
  "https://github.com/HarleyCoops/math-to-manim-checkpoints.git" `
  "refs/heads/entire/checkpoints/v1"
git ls-remote origin "refs/heads/entire/checkpoints/v1"
```

Expected: checkpoint ref exists privately and is absent publicly.

- [ ] **Step 5: Clean up only the disposable smoke branch/worktree**

```powershell
git -C $smokeWorktree push entire --delete codex/entire-session-smoke
git worktree remove $smokeWorktree
git branch -D codex/entire-session-smoke
```

Before the recursive worktree removal performed by Git, verify
`$smokeWorktree` resolves beneath `.tmp-runs`.

- [ ] **Step 6: Write operator documentation**

Create `docs/ENTIRE_PLATFORM.md` covering these exact commands and policies:

```text
entire status
entire doctor
entire checkpoint list
entire session current --json
entire session tokens --agent-brief
entire import codex --dry-run
entire import claude-code --dry-run
git fetch entire
```

Document private checkpoint storage, public negative checks, mirror URL, LFS
GitHub override, agent-hook locations, historical reconciliation inventory,
failure fallback to GitHub, and the milestone-two `entire-agent-m2m` boundary.

- [ ] **Step 7: Run the full milestone-one audit**

```powershell
entire version
entire auth status
entire status
entire doctor
gh repo view HarleyCoops/math-to-manim-checkpoints `
  --json nameWithOwner,visibility
git remote -v
git fetch entire
python -m pytest tests/test_entire_foundation.py `
  tests/test_entire_session_inventory.py -q
python -m pytest -q
git ls-remote origin "refs/heads/entire/checkpoints/v1"
git status --short
```

Expected: ENTIRE is healthy, private visibility is proven, mirror fetch works,
tests pass, public checkpoint lookup is empty, and the original unrelated RL
worktree changes remain present but unstaged.

- [ ] **Step 8: Commit documentation by exact path**

```powershell
git add -- docs/ENTIRE_PLATFORM.md
git diff --cached --check
git commit -m "docs: document Entire foundation operations"
```

- [ ] **Step 9: Record the milestone-one handoff**

Report:

- ENTIRE CLI version and installed path;
- private checkpoint repository URL and verified visibility;
- imported, skipped-as-duplicate, and parser-failure counts by agent;
- private checkpoint ref evidence and public negative evidence;
- US-East mirror URL and ref comparison;
- LFS pull and push-through results;
- smoke session/checkpoint ID;
- exact test counts and any limitations that remain for milestone two.
