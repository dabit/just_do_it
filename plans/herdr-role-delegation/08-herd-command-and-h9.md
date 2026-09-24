status: pending
# 08 - `commands/herd.md`, H9, and the command enumerations

Depends on: 01, 05, 06

## Why

`/jdi:herd` needs `reference/herdr.md` to exist (Task 01), needs the renumbered `init` steps and the
README/help sections that describe delegation (Task 05) so its own enumerations do not collide with
them, and needs the architecture doc's "Relationship to PR #5" section (Task 06) that names the
contract this command must meet.

**Separable, together with Task 07: drop both to rebase PR #5 onto `reference/herdr.md` H1, H2 and
H4 instead of superseding it.**

Rests on: the plan's "Relationship to PR #5" note (the herd layer's contract is H1, H2, H4b and H9)
and the "\"Validate, never repair\" versus \"detect, never repair\"" decision ("`/jdi:herd` keeps
'validate, never repair' and stops. It has no fallback, and a herd that quietly became one sequential
prep looks exactly like a herd that worked.").

## Description

Write `tests/test_herd.py` first, class `HerdCommandTest`:

- `commands/herd.md` contains "perform **H1**", "**H2**", "**H4b**", "**H9**",
  "`reference/herdr.md`", "Validate, never repair", "never fall back to a sequential `/jdi:prep`",
  "`jdi-herd-<issue", and "`.jdi/config.local.yml`".
- It does not contain "herd.args", "herd.env" or "AskUserQuestion".
- `commands/herd.md` also contains "one name per issue", "Worktree", and "uncommitted plan files".
- It does not contain "herd record" or "--resume".
- `reference/herdr.md` has `## H9 - Give a Butler its own worktree`, `herdr worktree create`, and the
  three invocation rows exactly as below.
- H9's section also contains `herdr tab rename`, `git -C <worktree> status --porcelain`, `--path`,
  `<worktrees dir>/<repo>/jdi-herd-<issue>`, `[worktrees] directory`, `~/.herdr/worktrees`,
  `jdi-herd-scratch-<herd-id>-<N>`, and `herdr worktree open`.
- It does not contain `--branch jdi-herd-scratch-<N> `.

Confirm it fails (`commands/herd.md` and H9 do not exist yet), then write the files.

**`commands/herd.md`**, reworked from `origin/herd-command:commands/herd.md` (fetch it with
`git show origin/herd-command:commands/herd.md` to see PR #5's exact current text). Keep PR #5's
twelve steps, with these changes:

- **(a) Step 1** becomes main's config load verbatim, including `.jdi/config.local.yml` (copy the
  step-0 shape from any of the six files Task 04 edited, e.g. `commands/pr.md`'s step 0, adapted to
  herd's step 1 numbering), then "reads `herd`, `harnesses`" in place of PR #5's "The optional `herd:`
  block sets `kind`, `max_parallel`, `args`, and `env`."
- **(b) Step 2** performs **H1**, then **H2** for `herd.kind` or a `--kind` in `$ARGUMENTS`, replacing
  PR #5's four-row table of raw `herdr` checks (`test "${HERDR_ENV:-}" = 1`, `command -v herdr`,
  `herdr workspace list`, reading the `kinds:` line) with the named operations.
  - Validate, never repair: the first failure stops the run with its reason.
  - Never fall back to a sequential `/jdi:prep`.
  - `delegation.transport` is irrelevant here.
- **(c) Step 5** (PR #5's "Reserve the agent names") builds **one name per issue**, used as the
  Herdr agent name and the tab label. Getting back to a Butler's work later does not depend on this
  name: the plan on the worktree's branch is the durable state, and a fresh session started in that
  worktree continues it with `/jdi:status` or `/jdi:yolo`.
  - The name is `jdi-herd-` plus the normalized issue ID, lowercased, with every character outside
    `[a-z0-9-]` replaced by `-`. Examples: `ENG-1234` gives `jdi-herd-eng-1234`; GitHub issue `4`
    gives `jdi-herd-4`. PR #5's bare lowercased ID fails Herdr's `^[a-z]` rule for a numeric ID.
  - The name must match Herdr's `[a-z][a-z0-9_-]{0,31}`. When the issue part is too long, cut it to
    fit. When two cut names in one herd collide, append `-2`, `-3`, and say which issue got which.
  - Keep PR #5's collision rule: where a live agent already holds the name, a Butler for that issue
    may already exist. Say which agent holds it and ask, rather than start a second one beside it.
  - The same name is the worktree's folder name (H9), so the folder shows the issue on disk.
  - The workspace label stays the issue ID, as in PR #5. JDI passes no session-name flag to the
    harness.
- **(d) Step 6** (PR #5's "Create one worktree per issue") performs **H9** (written below) in place of
  its inline `herdr worktree create` / `herdr tab create` recipe. Step 8 (PR #5's "Start one agent
  per worktree") performs **H4b** with the step-5 name, `harnesses.<kind>.args` printed verbatim and no model flag,
  because the Butler has no `models` key for a herd worker - replace PR #5's `herd.args` reference
  with `harnesses.<kind>.args`. Step 9 (PR #5's "Send the prompts — do not wait") hands each Butler
  its command per H9's invocation table below, with no wait - keep PR #5's "Never pass `--wait` here"
  rule.
- **(e) Step 11** (PR #5's "Offer the watch loop") asks through "the harness's own multiple-choice
  question facility, where it has one; otherwise inline as a numbered list" in place of PR #5's
  `AskUserQuestion` naming. The watch-loop text refers to H9 *Watch* instead of PR #5's `herdr agent
  read`.
- **(f) Step 12** (PR #5's "Say how to clean up") lists cleanup per H9's *Cleanup* bullet
  (`herdr worktree remove --workspace <id>`, plus `--force` when seeded), keeping PR #5's "Remove
  nothing yourself unless the user asks."
- **(g) The "Limits worth stating in the report" section** drops PR #5's `--lines` bullet ("Long
  output can be unreadable... a larger `--lines` reveals no more..."). Keep the other four bullets,
  adapted to name `harnesses.<kind>` instead of `herd.args`/`herd.env` where PR #5 named those keys.
- **(i) Report the worktree, and guard the cleanup.** Step 10's report keeps PR #5's worktree path
  and scratch-branch columns under a "Worktree" heading, and says that `/jdi:prep` renames the
  branch to one naming the issue, so `git worktree list` finds it later. Step 12 adds the cleanup
  guard from H9: before any worktree is removed, check it for **uncommitted plan files**. When the
  plan folder has any, say so, name the files, and offer the `docs: Add <slug> plan` commit in that
  worktree first. Never remove such a worktree without the user's explicit yes, because a forced
  removal deletes the plan. The body names H9 for the commands and never spells a `herdr` command
  itself.
- **(h) No `herdr` command, `HERDR_` variable, or harness tool name appears anywhere in the body** -
  every `herdr` invocation in this file is named as an H-operation instead. Keep PR #5's steps 3, 4,
  7, 10 essentially as written (parsing issues, checking the repository, seeding, reporting), since
  they contain no raw Herdr commands today, adjusting only cross-references to the renamed steps and
  keys above.

**`## H9 - Give a Butler its own worktree`**, appended to `reference/herdr.md` after `## Waves`, for
`/jdi:herd` only:

- **The worktree folder carries the issue.** Its folder name is the step-5 name,
  `jdi-herd-<issue>`, so after a crash or a closed workspace `git worktree list` (or `ls`) shows
  which folder belongs to which issue, even when prep never reached its branch step. Build the path
  as `<worktrees dir>/<repo>/jdi-herd-<issue>`:
  - `<worktrees dir>` is `[worktrees] directory` from Herdr's config (`~/.config/herdr/config.toml`)
    when that is set, else Herdr's documented default `~/.herdr/worktrees` (from
    `herdr --default-config`), with a leading `~` expanded to `$HOME`;
  - `<repo>` is the basename of the main checkout, matching the layout Herdr already uses
    (`~/.herdr/worktrees/<repo>/<folder>`, observed on this machine).
- **An existing folder is not overwritten.** When `<worktrees dir>/<repo>/jdi-herd-<issue>` already
  exists, a herd has run for this issue before. Say so, show its branch
  (`git -C <path> branch --show-current`) and whether its plan folder has uncommitted files, and ask:
  continue there (a fresh session in that folder, `/jdi:status`), or skip this issue. Never create a
  second folder beside it, and never remove it here.
- **Scratch branches are unique per herd run.** The scratch branch is
  `jdi-herd-scratch-<herd-id>-<N>`, where `<herd-id>` is the herd's UTC start time
  `yyyymmddThhmmss`. Prep switches away from the scratch branch but does not delete it, so PR #5's
  `jdi-herd-scratch-<N>` collides with the branch a previous herd left behind (observed: every
  earlier `jdi-herd-scratch-<N>` still exists in three repositories on this machine). The scratch
  branch still omits the issue ID, for PR #5's reason: prep adopts a branch that already names the
  work, and would then skip its **T6** branch.
- Create it: `herdr worktree create --cwd "$PWD" --path <that path> --branch
  jdi-herd-scratch-<herd-id>-<N> --base origin/<default> --label "<ISSUE-ID>" --no-focus`, reading
  `.result.worktree.path`, `.result.root_pane.pane_id` and `.result.workspace.workspace_id`. Confirm
  `.result.worktree.path` equals the path asked for; when it differs, report both and use the one
  Herdr returned. `--path` is in `herdr worktree create --help` (0.8.2) without stated semantics,
  so UAT probe P8 settles it before the herd scenario runs.
- Reattach after a restart: `herdr worktree open` opens an existing worktree as a workspace again.
  The report's closing line names it.
- When `harnesses.<kind>.env` is not empty, `herdr tab create --workspace <id> --cwd <path> --env
  KEY=VALUE ... --no-focus`, then use `.result.root_pane.pane_id`.
- The invocation table:

  | Kind | Invocation |
  |---|---|
  | `claude` | `/jdi:prep <ISSUE-ID>` |
  | `codex` | `$jdi:run prep <ISSUE-ID>` |
  | `opencode` | `/jdi-prep <ISSUE-ID>` |

  These spellings come from the README install table that
  `tests/test_codex_plugin.py`'s `test_harness_table_uses_jdi_run_and_preserves_other_harnesses`
  pins (`/jdi:prep`, `$jdi:run <command> [arguments]`, `/jdi-prep`). Other kinds are rejected at H2
  for herd.
- Label the tab: `herdr tab rename <tab_id> <name>`, with `tab_id` read from `.result.tab.tab_id`
  (or from the `herdr tab create` result when env forced a new tab). The workspace keeps the
  `--label "<ISSUE-ID>"` it was created with.
- Start the Butler with **H4b** under `<name>`.
- `herdr agent prompt <name> "<invocation>"` with no `--wait`.
- *Watch*: `herdr agent get` and inspection-only `agent read`.
- Cleanup: `herdr worktree remove --workspace <id>`, plus `--force` when seeded. Before either,
  run `git -C <worktree> status --porcelain -- <plans.path>`. Any output means uncommitted plan
  files: stop, name them, and offer the plan commit in that worktree. `--force` is used only after
  that check is empty or the user has said yes to losing the files.

**Enumerations:**
- `AGENTS.md`: add a `commands/herd.md` row to the `## The manual invocation` command table (the same
  table `tests/test_enumerations.py`'s `CommandTableTest` checks), in alphabetical position next to
  `commands/help.md`.
- `README.md`: the `## How it is put together` table row for `commands/` (currently "The 16 workflow
  commands...") becomes "The 17 workflow commands..."; add a short `/jdi:herd` paragraph under
  `## Use it`.
- `skills/run/SKILL.md`: add `herd` to the exact command allowlist (`## Exact command allowlist`), in
  sorted position.
- `docs/harness-adapter-architecture.md`: add `herd` to the `## Canonical Sources` allowlist (the
  fenced `text` block currently listing `done` through `yolo`), in sorted position.
- `commands/help.md`: add a `/jdi:herd` row to the command table.
- `commands/init.md`: in the new step 10 this task's dependency (Task 05) inserted ("Ask how delegated
  roles should run"), add a sub-bullet offering `herd.kind`, `herd.max_parallel` and `herd.seed` when
  the user plans to use `/jdi:herd`.
- `docs/config-key-lifecycle.md`: the "twelve of the sixteen" sentence (already corrected once by
  Task 06's re-derivation) becomes "thirteen of the seventeen", with `commands/herd.md:<line>` (the
  line of its own "Load the JDI config" step) added to the list of command files that repeat the
  config-load step.
- `tests/test_enumerations.py`: `ConfigLoadStepTest`'s hardcoded `12` becomes `13`, and its class
  docstring (currently "in twelve of the sixteen command files") is updated to "thirteen of the
  seventeen".

Note the tests that go red the moment `commands/herd.md` is added, and fix them in this same task
(they are not separate tasks - this one command file touches all of them):
- `DispatcherContractTest.test_allowlist_matches_commands_in_both_directions` - fixed by the
  `skills/run/SKILL.md` allowlist edit above.
- `CommandTableTest` - fixed by the `AGENTS.md` row above.
- `ReadmeCountTest.test_the_readme_command_count_matches_the_commands_directory` - fixed by the
  README count edit above.
- `ConfigLoadStepTest` - fixed by the `12` → `13` edit above, since `commands/herd.md` repeats
  "**Load the JDI config**" in its step 1.
- `OpenCodeGlobalSyncTest` and `OpenCodeProjectSyncTest` - glob-driven; they stay green with 17
  commands without any edit.

`HerdrConfinementTest` (Task 03, `tests/test_delegation_transport.py`) is not edited by this task, but
its scan already covers `commands/*.md` including the new `commands/herd.md` - confirm it stays
green, which is the proof that (h) above holds.

## Files

- `commands/herd.md` (new)
- `reference/herdr.md`
- `AGENTS.md`
- `README.md`
- `skills/run/SKILL.md`
- `docs/harness-adapter-architecture.md`
- `commands/help.md`
- `commands/init.md`
- `docs/config-key-lifecycle.md`
- `tests/test_enumerations.py`
- `tests/test_herd.py` (new)

## Verification

- `python3 -m unittest tests.test_herd.HerdCommandTest -v` - fails before `commands/herd.md` and H9
  exist, passes after.
- `python3 -m unittest tests.test_delegation_transport.HerdrConfinementTest -v` - stays green with
  `commands/herd.md` in the scan, proving no raw `herdr` command leaked into the command body.
- `python3 -m unittest tests.test_codex_plugin.DispatcherContractTest -v` - passes with `herd` in the
  Codex allowlist.
- `python3 -m unittest tests.test_enumerations -v` - `CommandTableTest`, `ReadmeCountTest`, and
  `ConfigLoadStepTest` all pass with the corrected count of 13 and the new AGENTS.md row.
- `python3 -m unittest tests.test_opencode_sync -v` - stays green (glob-driven, no edit needed).
- `grep -n "herdr\|HERDR_\|AskUserQuestion" commands/herd.md` - empty.
- `python3 -m unittest discover -s tests -v` - no new failures.
- `grep -n "one name per issue\|uncommitted plan files" commands/herd.md` - both present.
- `grep -n "jdi-herd-scratch-<N>\b" reference/herdr.md commands/herd.md` - no hit for the old
  collision-prone scratch name.
