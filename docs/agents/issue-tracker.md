# Issue tracker: Linear

Issues and specs for this repo live in Linear, in the `Warreandvavasour` team (key `WAR`), project `Math-To-Manim Upgrade` (`P-WAR-1`). Use the Linear connector tools for all operations. Issue identifiers have the form `WAR-<number>`.

Other Warre & Vavasour repos also use the `WAR` team. Always filter list queries by the project, so that issues from other repos do not appear.

## Conventions

- **Create an issue**: `save_issue` with `team: "WAR"`, `project: "Math-To-Manim Upgrade"`, `state: "Backlog"`, `title`, and a Markdown `description`. Do not pass `id`.
- **Read an issue**: `get_issue` with `id: "WAR-<n>"` and `fields` that include `labels` and `status`, then `list_comments` with `issueId: "WAR-<n>"`.
- **List issues**: `list_issues` with `team: "WAR"` and `project: "Math-To-Manim Upgrade"`, plus `label` and `state` filters as necessary.
- **Comment on an issue**: `save_comment` with `issueId` and `body`.
- **Apply / remove labels**: `save_issue` with `id` and `addLabels` / `removeLabels`. Do not use `labels`, because it replaces all labels on the issue.
- **Close**: `save_comment` with the reason, then `save_issue` with `state: "Done"`. For a won't-fix issue, use `state: "Canceled"`. For a duplicate, use `duplicateOf: "WAR-<n>"`.

Team statuses: `Backlog`, `Todo`, `Snoozed`, `In Progress`, `In Review`, `Done`, `Canceled`, `Duplicate`. The team has no `Triage` status. The triage labels show the triage state.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature requests; `/triage` reads this flag.)_

Pull requests are on GitHub (`HarleyCoops/Math-To-Manim`), not in Linear. When this flag is `yes`, read external PRs with `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments` and keep only `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR`, or `NONE` authors. Record the triage decision as a comment on the PR (`gh pr comment`).

## When a skill says "publish to the issue tracker"

Create a Linear issue in team `WAR`, project `Math-To-Manim Upgrade`.

## When a skill says "fetch the relevant ticket"

Run `get_issue` with `id: "WAR-<n>"`, then `list_comments` with `issueId: "WAR-<n>"`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **child** issues as tickets.

- **Map**: one issue with the label `wayfinder:map`. Its description holds the Notes / Decisions-so-far / Fog sections.
- **Child ticket**: an issue created with `parentId: "<map id>"` and one label `wayfinder:<type>` (`research` / `prototype` / `grilling` / `task`).
- **Blocking**: Linear "blocked by" relations. Add one with `save_issue` and `blockedBy: ["WAR-<n>"]`. Read them with `get_issue` and `includeRelations: true`. A ticket is unblocked when every blocker has a status of type completed or canceled.
- **Frontier query**: `list_issues` with `parentId: "<map id>"`. Drop tickets with a completed or canceled status, an open blocker, or an assignee. Use the order of the ticket list in the map description. If the map has no list, use the lowest `WAR` number.
- **Claim**: `save_issue` with `id`, `assignee: "me"`, and `state: "In Progress"`. This is the first write of the session.
- **Resolve**: `save_comment` with the answer, then `save_issue` with `state: "Done"`, then add a pointer (summary and link) to the map's Decisions-so-far with `save_issue` and `patch`.
