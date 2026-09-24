# JDI configuration

Every JDI command reads this configuration **first**, before doing anything else.

## Resolution order

1. `.jdi/config.yml` at the root of the repository being worked in. This is the source of truth,
   and the file a team commits.
2. If that file does not exist, fall back to defaults recorded in the repo's `AGENTS.md` or
   `CLAUDE.md` (a stated issue tracker, a stated plans folder, a stated docs folder).
3. If neither exists, use the built-in defaults in the table below and **ask the user** the one or
   two questions the current command actually depends on. Do not block the workflow over a missing
   config file — offer `/jdi:init` at the end instead.

Then, whichever level answered, **`.jdi/config.local.yml`** — if it exists beside `config.yml` — is
layered over the result, key by key. It is the personal, per-checkout override: never committed, and
the place for a value that is true of this machine or this person rather than of the repository —
the model a role runs on, a `harnesses` entry carrying a path from this disk, `tdd.enabled: false`
while the runner is broken locally. The merge is:

- a mapping merges with the value below it, key by key;
- a scalar or a list replaces the whole value below it;
- a key the local file does not name is left exactly as the lower level resolved it;
- the file can override a value; it can never delete one.

A local file with no `config.yml` beside it still applies, over levels 2 and 3. A local file git
tracks is a mistake, and step 0 says so when it sees one.

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

jev:
  # true | false
  #   false — no role asks Jev anything, nothing is sent anywhere, and no command
  #           says a word about it. This is the default, and the only mode that
  #           needs no API key and no network.
  #   true  — roles may perform the named operations in reference/jev.md: ranking
  #           candidate architecture docs, screening consumers, resolving a tracker
  #           state by role, checking a split is atomic, ranking findings. Jev
  #           narrows a list the role already has; it never decides, writes, or
  #           commits. See reference/jev.md, J1–J5.
  #
  # The key is read from $TYPESAFE_API_KEY, or from ~/.config/typesafe/api_key.
  # It is never written into this file, a plan, or a commit.
  enabled: false

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

# Optional. Names the model each role runs on, and optionally the agent CLI
# it runs in. A role with no entry — or a whole block that is absent — runs
# in this session's harness on whatever model the session is already using.
# That is a supported configuration, not a degraded one.
# See reference/delegation.md for what each role wants from a model and for
# what happens when an entry cannot be honoured.
models:
  researcher:
    model: ""
    harness: ""
  planner:
    model: ""
    harness: ""
  splitter:
    model: ""
    harness: ""
  executor:
    model: ""
    harness: ""
  synthesizer:
    model: ""
    harness: ""
  pr-writer:
    model: ""
    harness: ""
  feedbacker:
    model: ""
    harness: ""

# Optional. Per-CLI settings, keyed by the kind that a `models.<role>.harness`
# names. `args` are handed to that CLI verbatim, after its own flags; `env` is
# set on the process — or, under Herdr, on the pane — that runs it.
#
# Both are passed through exactly as written. JDI never composes, merges, or
# translates them between kinds, and adds no flag of its own beyond the model
# flag and the invocation JDI needs to reach the CLI, and never an approval- or
# sandbox-affecting one. Anything of that kind is a value you
# wrote here, and JDI prints it back before it spawns anything.
#
# Write absolute paths: a leading "~" arrives as a literal tilde.
#
#   harnesses:
#     codex:
#       args: ["--sandbox", "workspace-write"]
#       env: {CODEX_HOME: /home/you/.codex-other}
harnesses:
  claude:
    args: []
    env: {}
  codex:
    args: []
    env: {}
  opencode:
    args: []
    env: {}

# Optional. How a delegated role reaches its own process. See
# reference/delegation.md, "Choosing the transport", and reference/herdr.md.
delegation:
  # native | auto | herdr
  #   native - the delegation JDI has always done: a subagent where the harness
  #            has one, the CLI's non-interactive mode where `models.<role>.harness`
  #            names another kind, inline otherwise. Herdr is reached only for a
  #            kind with no known non-interactive mode. This is the default, and
  #            the only mode that probes nothing at step 0.
  #   auto   - when this session runs inside Herdr, a role whose
  #            `models.<role>.harness` names another CLI runs as that CLI's
  #            interactive agent in its own Herdr pane, where you can answer it,
  #            and the Butler waits for it. Every Executor of a wave gets its own
  #            pane. Outside Herdr, exactly `native`, and nothing is said.
  #   herdr  - as `auto`, but Herdr is expected: when it cannot be used, JDI says
  #            why, once, and delegates as `native`. The phase still runs.
  #
  # A role on this session's own CLI is never affected: it stays a subagent.
  # Whether you work inside Herdr is usually true of your machine, not the
  # repository: set it in .jdi/config.local.yml.
  transport: native

# Optional. Sibling repositories or client codebases that consume this repo's
# public interfaces (APIs, webhooks, tool surfaces, published packages). The
# Researcher sweeps these when a change alters an externally-consumed contract,
# so "does a client need updating?" is never left unanswered.
consumers: []
```

## Example model mappings

None of these is a default — pick what your harness and account actually have. The value is handed
to the harness that will run the role, exactly as written — so write the identifier that harness
accepts: Claude Code's Agent tool takes an alias, while Codex and OpenCode take full identifiers.
A role left empty falls back to the session's own model, which is always a valid configuration.

```yaml
# Claude Code — aliases      # Codex / OpenAI — full IDs    # Mixed — a role elsewhere
models:                      models:                        models:
  researcher:                  researcher:                    researcher:
    model: opus                  model: gpt-5.1-codex-max       model: gpt-5.1-codex-max
    harness: ""                  harness: ""                    harness: codex
  planner:                     planner:                       planner:
    model: opus                  model: gpt-5.1-codex-max       model: opus
    harness: ""                  harness: ""                    harness: ""
  splitter:                    splitter:                      splitter:
    model: sonnet                model: gpt-5.1                 model: qwen3-coder
    harness: ""                  harness: ""                    harness: opencode
  executor:                    executor:                      executor:
    model: opus                  model: gpt-5.1-codex-max       model: opus
    harness: ""                  harness: ""                    harness: ""
  synthesizer:                 synthesizer:                   synthesizer:
    model: sonnet                model: gpt-5.1-mini            model: sonnet
    harness: ""                  harness: ""                    harness: ""
  pr-writer:                   pr-writer:                     pr-writer:
    model: sonnet                model: gpt-5.1-mini            model: sonnet
    harness: ""                  harness: ""                    harness: ""
  feedbacker:                  feedbacker:                    feedbacker:
    model: opus                  model: gpt-5.1                 model: gpt-5.1
    harness: ""                  harness: ""                    harness: codex
```

## Defaults when nothing is configured

| Key | Default |
|---|---|
| `tracker.name` | `none` — JDI runs fully offline, no issue, no comments, no status transitions |
| `tracker.research_comment_heading` | `## 🔬 Research findings (JDI)` |
| `split.pieces` | `commits` — task files and one commit per task; nothing written to the tracker |
| `tdd.enabled` | `false` — the Executor works as it always has; nothing is announced |
| `tdd.test_instructions` | empty — the Butler works the test invocation out from the repo |
| `jev.enabled` | `false` — no role asks Jev anything; nothing is sent and nothing is announced |
| `plans.mode` | `repo` |
| `plans.path` | `plans` |
| `docs.path` | `doc` |
| `git.default_branch` | `auto` |
| `models.*` | empty — every role runs in this session's harness, on the session's own model |
| `harnesses.*` | empty — a CLI JDI spawns receives no arguments and no extra environment |
| `delegation.transport` | `native` - roles are delegated exactly as before this key existed; nothing is probed at step 0 and nothing is announced |
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
- **`jev` narrows, it never decides.** A Jev answer may reorder a list, flag a candidate, or
  pre-select one option from a set the caller already enumerated. It is never the reason a step is
  skipped, a file is written, a tracker is updated, a commit is made, or a pull request is opened.
  Those stay the role's judgment and the user's approval, exactly as they are with `jev` off.
- **`jev` degrades to more work, never less.** No key, no network, a failed request, or a state too
  large all mean the role reads every candidate itself — which is precisely what it does with
  `enabled: false`. Dropping a consumer sweep or an unread document because an optional model was
  unavailable is a worse failure than never having asked. The Butler runs the ladder in
  `reference/jev.md` once, at step 0, and roles are handed the resolved answer rather than the key.
- **`jev: false` is silent; a `jev: true` that could not run is announced once.** Nothing was
  skipped when the feature is off, so a default run says nothing at all. Get this backwards and
  every repo that never enabled it is told about it on every command.
- **The API key never lands in the repository.** It is read from `$TYPESAFE_API_KEY` or
  `~/.config/typesafe/api_key` and passed by reference. No key value belongs in `.jdi/config.yml`,
  `.jdi/config.local.yml`, a plan, a task file, or a commit message.
- **`models` is the only place a role's model is named.** No file under `agents/` carries a
  `model:` key. A role with no entry runs on the session's own model.
- **A value in `models` is passed to the named harness verbatim.** Write the identifier that
  harness accepts: Claude Code's Agent tool takes an alias (`opus`, `sonnet`, `haiku`), while Codex
  and OpenCode take full identifiers. A model the harness cannot express is **announced** and the
  role runs on that harness's own default; it is never silently swapped for a different one. Under
  a separate process, including Herdr, the model is passed as the CLI's own model flag, so a full
  identifier the Agent tool's enum cannot express can be expressed there.
- **`harness` degrades down, never up.** An unreachable CLI, an unresolvable role instruction, or a
  transport that never reported means the role runs here instead, announced once. It never means
  the phase is skipped, never means JDI acquires a flag the user did not write, and never means the
  role lands somewhere less supervised than this session.
- **`delegation.transport: native` is today's delegation, unchanged.** A repo with no `delegation`
  block behaves exactly as before the key existed.
- **`auto` and `herdr` are detected once, at step 0, and never repaired.** Operation H1 in
  `reference/herdr.md` defines the detection and the announcement rules.
- **The transport never grants authority.** A Herdr worker is a separately spawned CLI, and its
  dialogs belong to the user.
- **The transport only changes how a role on another CLI runs.** A role with no
  `models.<role>.harness`, or one naming this session's own CLI, stays a subagent under every value.
- **The transport degrades to `native`, never beyond.** A failed Herdr run returns the role to
  native resolution for its kind. It never skips the phase, never opens a third CLI, and never
  acquires a flag.
- **`delegation.transport` is usually personal.** It belongs in `config.local.yml`, because working
  inside Herdr is a fact about the machine.
- **There is no `models.butler`.** The Butler is the session you are already in, and no harness
  lets a config file change the model of a session that is already running. Its absence is
  deliberate, not an omission.
- **`config.local.yml` overrides; it never replaces.** A local file is read on top of the resolved
  config, key by key, so a two-line file that sets `models.executor.model` changes exactly that and
  nothing else. It cannot remove a key, and it does not turn a missing `config.yml` into a
  configured repo: the levels below it still answer for everything it does not name. The decisions
  a plan records — the `TDD:` line in `PLAN.md` — are read from the plan, so a local file, like
  `config.yml`, changes nothing mid-plan.
- **A local override is announced once, in one line, by block.** It is neither a feature that is
  off (silent) nor a degradation (announced with its cause): the user asked for it and got it. It is
  still announced, because it is the one divergence a collaborator reading the committed file
  cannot see — "TDD is off here" is a puzzle until someone says the local file turned it off. Step 0
  names the top-level blocks the local file touches (`models`, `tdd`), never the values.
- **`config.local.yml` is per checkout.** It is an untracked file, so a linked worktree, a fresh
  clone, and a colleague's machine do not have it, and a setting written into the local file of a
  worktree about to be removed is scheduled for deletion. A setting that must survive the checkout
  belongs in `config.yml`, committed.
- **`config.local.yml` is not a secret store.** Uncommitted is not the same as secret: the file sits
  in plain text in the working tree, is read by every command, and is one careless `git add -A`
  from the history. The Jev key stays in `$TYPESAFE_API_KEY` or `~/.config/typesafe/api_key`; neither
  config file carries it.
- **`/jdi:init` writes `config.yml` only.** It reads the local file to report what it overrides, and
  it checks that `.jdi/config.local.yml` is gitignored — a personal override that gets committed is
  applied to everyone, which is the destructive direction — but it never writes the local file: a
  personal override is written by the person it belongs to.
- **Branch and commit message conventions are not configured here.** They come from the repo's own
  `CLAUDE.md` / `AGENTS.md`, which is where a team already writes them down.
- Run `/jdi:init` to generate this file interactively.
