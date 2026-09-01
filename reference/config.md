# JDI configuration

Every JDI command reads this configuration **first**, before doing anything else.

## Resolution order

1. `.jdi/config.yml` at the root of the repository being worked in. This is the source of truth.
2. If that file does not exist, fall back to defaults recorded in the repo's `AGENTS.md` or
   `CLAUDE.md` (a stated issue tracker, a stated plans folder, a stated docs folder).
3. If neither exists, use the built-in defaults in the table below and **ask the user** the one or
   two questions the current command actually depends on. Do not block the workflow over a missing
   config file — offer `/jdi:init` at the end instead.

A command must never invent a tracker, a project, or a plans location that the config does not
record and the user has not confirmed.

## Schema

```yaml
# .jdi/config.yml — JDI workflow configuration

tracker:
  # linear | jira | github | none
  # Any other value is treated as a custom tracker: JDI will use whatever MCP
  # integration is available for it, and degrade to "none" if there is none.
  name: none

  # Default project / board / repo used when creating a new issue.
  project: ""

  # Team, workspace, or organisation the project lives in.
  team: ""

  # Issue key prefix, e.g. "ENG" for ENG-1234. Used to build plan slugs and to
  # recognise whether the current git branch already names the issue.
  id_prefix: ""

  # First line of the comment JDI writes back to an issue when research lands.
  # Kept identical across runs so the write is idempotent (update, never duplicate).
  research_comment_heading: "## 🔬 Research findings (JDI)"

split:
  # commits | tasks | subtickets
  #   commits    — the split pieces stay task files in the plan folder, and each one
  #                becomes a commit when it is marked done. Nothing is written to the
  #                tracker. This is the default and the only mode that needs no tracker.
  #   tasks      — as `commits`, plus each piece is mirrored as a native task/checklist
  #                item on the issue, if the tracker has such a thing. Where it does not,
  #                JDI says so and falls back to `commits`.
  #   subtickets — as `commits`, plus each piece is mirrored as a child issue of the plan's
  #                issue (Linear sub-issue, Jira sub-task, GitHub sub-issue).
  #
  # The task files and the one-commit-per-task rhythm are the same in all three modes;
  # `tasks` and `subtickets` add a tracker mirror on top. See reference/tracker.md, T7/T8.
  pieces: commits

plans:
  # repo | external
  #   repo     — plans are files in this repository, committed with the code they describe.
  #   external — plans live in a note-taking or knowledge service (Obsidian, recuerd0,
  #              Notion, a wiki). Nothing plan-shaped is committed to the repo.
  mode: repo

  # repo mode: folder, relative to the repository root.
  path: plans

  # external mode: the service holding the plans, e.g. "obsidian", "recuerd0", "notion".
  service: ""

  # external mode: the vault / notebook / space / parent page plans are written into.
  location: ""

docs:
  # Where architecture and design documents live, relative to the repository root.
  # /jdi:research reads from here and writes new architecture docs here.
  path: doc

git:
  # Default branch to branch from and target PRs at. "auto" detects it from
  # `git symbolic-ref refs/remotes/origin/HEAD`.
  default_branch: auto

  # Optional prefix convention for feature branches, e.g. "feat/" or "".
  # Leave empty to follow whatever the repo's CLAUDE.md prescribes.
  branch_prefix: ""

# Optional. Maps JDI's three reasoning tiers onto concrete models for whichever
# harness and provider you are running. Leave a tier empty — or omit the whole
# block — to run that tier on whatever model the session is already using.
# See reference/delegation.md for what each tier is for.
models:
  deep: ""        # research, planning, implementation, review
  standard: ""    # splitting, condensing, PR writing
  fast: ""        # orchestration, status, commits

# Optional. Sibling repositories or client codebases that consume this repo's
# public interfaces (APIs, webhooks, tool surfaces, published packages). The
# Researcher sweeps these when a change alters an externally-consumed contract,
# so "does a client need updating?" is never left unanswered.
consumers: []
```

## Example tier mappings

None of these is a default — pick what your harness and account actually have. Any tier left empty
falls back to the session's own model, which is always a valid configuration.

```yaml
# Anthropic                # OpenAI                    # Local / mixed
models:                    models:                     models:
  deep: claude-opus-5        deep: gpt-5.1-codex-max      deep: claude-opus-5
  standard: claude-sonnet-5  standard: gpt-5.1            standard: qwen3-coder
  fast: claude-haiku-4-5     fast: gpt-5.1-mini           fast: qwen3-coder
```

## Defaults when nothing is configured

| Key | Default |
|---|---|
| `tracker.name` | `none` — JDI runs fully offline, no issue, no comments, no status transitions |
| `tracker.research_comment_heading` | `## 🔬 Research findings (JDI)` |
| `split.pieces` | `commits` — task files and one commit per task; nothing written to the tracker |
| `plans.mode` | `repo` |
| `plans.path` | `plans` |
| `docs.path` | `doc` |
| `git.default_branch` | `auto` |
| `models.*` | empty — every tier runs on the session's own model |
| `consumers` | empty |

## Notes

- **`tracker.name: none` is a first-class mode, not a degraded one.** Every tracker step in every
  command is skippable, and skipping must be announced, never silently swallowed.
- **`split.pieces` never changes what gets executed.** Whatever it is set to, the plan folder holds
  the same task files and each task still lands as its own commit. `tasks` and `subtickets` only
  add a mirror of those pieces in the tracker, so progress is visible to people who never open the
  repository.
- **A mode the tracker cannot honour degrades down to `commits`, never up.** No tracker, no issue,
  no reachable integration, or no native checklist all mean `commits` for that run, announced out
  loud. `tasks` must never quietly become `subtickets`: creating issues nobody asked for is worse
  than mirroring nothing.
- **Branch and commit message conventions are not configured here.** They come from the repo's own
  `CLAUDE.md` / `AGENTS.md`, which is where a team already writes them down.
- Run `/jdi:init` to generate this file interactively.
