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

tdd:
  # true | false
  #   false — the Executor writes tests and implementation in whatever order the
  #           task calls for, exactly as it always has. This is the default and the
  #           only mode that needs nothing proven about the repository's test runner.
  #   true  — the Executor writes the failing test first, once the suite has been
  #           seen to run. Tests and implementation still land in the same commit,
  #           one per task; only the order they are written in changes.
  enabled: false

  # Free-form prose an agent reads and translates into an invocation — never a
  # string to execute. "run `bin/rails test` inside the devcontainer" is the shape:
  # the literal text is usually not runnable as typed, because the real invocation
  # depends on a container, a service, or a working directory. Leave it empty to have
  # the Butler work the invocation out from the repo. See reference/testing.md, TS1/TS2.
  test_instructions: ""

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

# Optional. Read only by /jdi:herd, which preps several issues in parallel,
# one Herdr worktree and agent per issue.
herd:
  # Herdr agent kind to start. Must be one of the kinds the installed Herdr
  # reports on the `kinds:` line of `herdr agent`.
  kind: claude

  # How many issues one /jdi:herd run may start without asking again. Each
  # agent is a full session with a real token cost, so this is a spend guard,
  # not a technical limit.
  max_parallel: 5

  # Arguments handed to the agent CLI itself, after Herdr's `--` separator.
  # Keyed by agent kind, because every CLI has its own flags. A kind with no
  # entry starts with no arguments, and JDI never adds one of its own.
  #
  # This is where an unattended herd gets its permission-bypass flag. Approvals
  # are what make a spawned agent stop and wait for you, so turning them off
  # means nothing reviews what the agent does. The worktree isolates the branch
  # and the working tree, and nothing else: same credentials, same network,
  # same machine. Set it deliberately.
  #
  #   args:
  #     claude: ["--dangerously-skip-permissions"]
  args: {}

  # Environment variables set on the pane each agent starts in. Use it to run
  # the herd under a different account, provider, or CLI configuration than
  # this session uses.
  #
  # Values are passed verbatim, so write absolute paths: a leading "~" arrives
  # as a literal tilde and the variable then points nowhere.
  #
  #   env:
  #     CLAUDE_CONFIG_DIR: /Users/you/.claude-other
  env: {}

  # What to put into each new worktree before its agent starts. A worktree is
  # created from origin/<default>, so nothing gitignored reaches it: no .env,
  # no installed dependency, no local database name. Everything here is
  # optional, and an empty block seeds nothing.
  #
  # Applied per worktree in the order copy -> set -> setup, from JDI's own shell
  # with the worktree as the working directory — never in the pane the agent
  # is about to claim.
  #
  # Placeholders, substituted in every `set` value and every `setup` command:
  #   {{n}}            the worktree's 1-based index in this herd
  #   {{issue}}        the issue ID, e.g. JUT-3073
  #   {{issue_lower}}  the same, lowercased
  #   {{worktree}}     absolute path to the new worktree
  #   {{repo_root}}    absolute path to the checkout /jdi:herd ran in
  #
  # Use {{n}} for anything concurrent runs would otherwise share — a test
  # database, a port, a cache directory, a container name. Two worktrees on
  # one test database produce thousands of failures that read as a regression
  # in the branch under test.
  #
  #   seed:
  #     copy:                              # paths relative to the repo root,
  #       - apps/core/api/.env             # copied from this checkout; a path
  #       - apps/core/frontend/.env        # absent here is skipped, not an error
  #     set:                               # dotenv-style key replacement, after copy
  #       apps/core/api/.env:
  #         TEST_DATABASE: jute_testing_herd{{n}}
  #     setup:                             # cwd is the worktree root; a non-zero
  #       - npm ci --prefix apps/core/frontend   # exit disqualifies that
  #       - cd apps/core/api && bin/rails db:test:prepare   # worktree: no agent
  #                                                        # is started for it
  seed: {}

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
| `tdd.enabled` | `false` — the Executor works as it always has; nothing is announced |
| `tdd.test_instructions` | empty — the Butler works the test invocation out from the repo |
| `plans.mode` | `repo` |
| `plans.path` | `plans` |
| `docs.path` | `doc` |
| `git.default_branch` | `auto` |
| `models.*` | empty — every tier runs on the session's own model |
| `herd.kind` | `claude` |
| `herd.max_parallel` | `5` |
| `herd.args` | empty — spawned agents start with no CLI arguments, so approvals stay on |
| `herd.env` | empty — spawned agents inherit the environment Herdr gives a new pane |
| `herd.seed` | empty — worktrees are created bare, with nothing gitignored copied in and nothing run |
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
- **`tdd` never changes what gets committed.** Tests and implementation land in the same commit,
  one per task, exactly as without it. It changes the order the Executor writes them, not history.
- **`tdd` degrades down to off, never up to on.** An unproven runner, an unreachable environment,
  or an unanswerable ambiguity all mean off for that plan, announced out loud. A repo with
  `enabled: false` is never turned on because a test folder happens to exist: running "on" against
  a runner nobody watched run produces fabricated red-run evidence, which is worse than not doing
  TDD at all.
- **`herd` is read by `/jdi:herd` and by nothing else.** No other command changes behaviour because
  the block exists, and a repo without Herdr never reaches a line that reads it. The whole block is
  optional, and every key in it has a working default.
- **`/jdi:herd` validates Herdr and stops; it never repairs.** No server, no binary, no socket, or
  no such agent kind each end the run with the reason. It starts nothing, installs nothing, and
  never silently degrades to a sequential `/jdi:prep`: a herd that quietly became one prep looks
  exactly like a herd that worked.
- **`herd.seed` is the only thing that puts gitignored state into a worktree.** A worktree comes
  from `origin/<default>`, so `.env` files, installed dependencies and local database names are
  simply absent. Left empty, each agent works that out for itself, differently — and two agents
  that settle on the same test database produce thousands of failures that read as a regression.
  Put `{{n}}` in anything concurrent runs would share.
- **`herd.args` is passed through, never composed.** JDI adds no flag of its own and translates
  none between agent kinds. A permission-bypass flag is therefore a value the user wrote down, not
  a mode JDI decided to enter on their behalf.
- **Branch and commit message conventions are not configured here.** They come from the repo's own
  `CLAUDE.md` / `AGENTS.md`, which is where a team already writes them down.
- Run `/jdi:init` to generate this file interactively.
