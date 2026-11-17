status: pending
# 26 — UAT: herd modes and untracked tasks (agent smoke test)

Depends on: 20, 21, 22, 23, 24, 25

## Why
Every clause of issue #38 must be observed in a running Herdr before the pull request, or named as unobservable here with what proves the mechanism instead: a `do`-mode herd of quoted untracked tasks, with no tracker, hands each agent a literal single-quoted `/jdi:do … (untracked, started by /jdi:herd)`; a too-big task continues into `/jdi:prep` in the same session on do's branch with no tracking question; `prep` mode and an invalid mode run `/jdi:prep`; the parse rules ask once and never guess; the record and `--cleanup` handle task entries; and nothing reaches GitHub or the user's own Herdr. It runs as an agent smoke test in a throwaway session; unattended merges, the update-after-a-sibling-merged path and other kinds are the user's scenarios. Rests on: E8, U1, U2, E1, E2, E3, E4, E5, E7, M1, M2, M3, M4, M5, M8.

## Description
Planner's Task 26. An agent smoke test in a throwaway app session (and, if cheap, a nested
throwaway TUI), plus four scenarios only the user can walk. **UAT is walked before `/jdi:pr`.**
Nothing here merges this branch, pushes to any GitHub remote, or presupposes a merge.

Record every scenario's observed result in a new **`## UAT log (#38)`** section in PLAN.md, placed
directly above `## Tasks` (below `## UAT log (#37)`), one `### (<id>) <title>: **pass|fail|…**`
entry per scenario id, then `### Repository checks`, `### Clause map status`, `### Findings` and
`### Cleanup`, as `## UAT log (#37)` does. Sanitise it as that log: `$HOME` becomes `~`, the scratch
path `<scratch>`, no session, machine or user name.

**Safety first (R30, the highest risk). Every command that addresses Herdr or GitHub goes through the
guard.** Read `## Probe log` → *Isolation guard and setup* and `## UAT log (#37)` → *Findings* F-c
(the old guard left `HERDR_SOCKET_PATH` unset, so a `herdr` command reached the user's default TUI)
and F-d (an unseeded worktree never sees `.jdi/config.local.yml`; herd agents run the **committed**
`.jdi/config.yml`). If a window cannot be opened, hand the scenarios to the user. No Codex, so
`~/.codex/config.toml` is not touched.

### Harness

1. **The guard** `<scratch>/g`, POSIX `sh` (#37's guard plus E8):
   - Refuse with exit 64, one stderr line and **no stdout** unless `JDI_PROBE_SESSION` and
     `JDI_PROBE_HOME` are both set and the session matches `jdiprobe-*`.
   - `unset HC_TERMINAL_ID HC_TERMINAL_SOCKET HC_SCOPE HC_SOCKET HERDR_ENV HERDR_SOCKET_PATH HERDR_PANE_ID HERDR_TAB_ID HERDR_WORKSPACE_ID`,
     every `CLAUDECODE`, `CLAUDE_CODE_*`, `CLAUDE_PID`, `CLAUDE_EFFORT`, and
     `GH_TOKEN GITHUB_TOKEN GH_REPO GH_HOST GH_ENTERPRISE_TOKEN`.
   - `export HC_SESSION=$JDI_PROBE_SESSION HERDR_APP_HOME=$JDI_PROBE_HOME GH_CONFIG_DIR=<scratch>/gh-empty`
     (an empty directory created at setup).
   - `export HERDR_SOCKET_PATH=<scratch>/no-tui/herdr.sock` (a path that does not exist) **unless**
     `JDI_PROBE_TUI=1`; then export the throwaway TUI's socket,
     `~/.config/herdr/sessions/<probe-session>/herdr.sock`, and refuse (exit 64) if it is missing.
   - `exec "$@"`. XDG is not overridden (the core keys its socket and state by session name).
2. **Self-checks, logged before anything else:**
   - `env -u JDI_PROBE_SESSION <scratch>/g echo X` → exit `64`, `0` stdout bytes.
   - The user's `herdr session list` (read-only, **outside** the guard) captured; then
     `<scratch>/g herdr status` → non-zero exit; then `herdr session list` again → identical.
     VERIFY-AT-EXECUTION: if `herdr status` creates anything under `<scratch>/no-tui/` (a server
     started on that socket), record it, stop it through the guard, and fix the guard before going on.
   - `<scratch>/g gh auth status` → reports not logged in.
3. **Snapshots** (outside the guard, read-only): the **count** of the user's own `hc ls --json`
   terminals; the real repository's `git worktree list`; the `~/.claude.json` `projects` keys;
   `ls ~/.local/state/herdr-core/` and `ls ~/.config/herdr/sessions/`.
4. **The scratch repository.** A bare `<scratch>/origin.git` whose `main` holds, in one commit:
   `README.md` containing the line `Install into $HOME/bin and recieve updates.`; `greet.py` with
   `def greet(name): return "Hello, " + name + "!"` and `test_greet.py` (stdlib `unittest`, one
   test); `AGENTS.md` saying tests run with `python3 -m unittest`; `.gitignore` with
   `.jdi/config.local.yml`; a committed `.jdi/config.yml` with `tracker: {name: none}`,
   `tdd: {enabled: false}`, `jev: {enabled: false}`. Clone it to `<scratch>/repo`, set
   `origin/HEAD` → `main`, and record `git -C <scratch>/origin.git rev-parse main` (the **origin
   SHA**). Throwaway app home `settings.json`: `{"worktrees":{"directory":"<scratch>/worktrees"}}`;
   session `jdiprobe-<4 hex>`. Through the guard, `herdr-app status` fails and `hc ls --json` is
   empty; then start `herdr-app` in the background (tell the user a window will appear) and close
   its welcome overlay.
5. **Local config** `<scratch>/repo/.jdi/config.local.yml` (the Butler's; herd agents never see it):
   ```yaml
   herd:
     kind: claude
     mode: do
   harnesses:
     claude:
       args: ["--model", "sonnet", "--plugin-dir", "<this repo>", "--settings", '{"enabledPlugins":{"jdi@just-do-it":false}}']
   ```
   with `<this repo>` the absolute path of this checkout, so herd agents load **this branch's**
   plugin. Back up `~/.claude.json`; pre-trust only `<scratch>/repo` (`jq` to a temporary file, then
   `mv`).
6. **The Butler.** `claude --plugin-dir <this repo> --settings '{"enabledPlugins":{"jdi@just-do-it":false}}'`
   as the argv of a throwaway `space.new` on `<scratch>/repo`, through the guard. Its first message
   tells it to ask questions in plain text, not with the question tool. Drive it with `hc send`,
   read it with `hc read`. Evidence: the Butler's and agents' transcripts (every command they ran,
   every message they received), `herdr-app ls`, `hc get`, the record files under
   `<scratch>/repo/.git/jdi/herds/`, `git -C <scratch>/repo worktree list --porcelain`,
   `git -C <scratch>/repo branch --list`, `git -C <scratch>/origin.git branch --list` and
   `rev-parse main`.
7. **Cost.** Herd agents run on sonnet and cost tokens: stop the fallback and prep agents early, as
   each scenario says. The driver answers no herd agent's dialog on JDI's behalf.

### Expected suffixes (observed at base with the documented command)
`printf '%s' '<normalised task>' | git hash-object --stdin`, first six hex, prefixed `t`:

| Task text (as typed) | Normalised | Suffix |
|---|---|---|
| `fix the typo 'recieve' in README.md and keep $HOME/bin as it is` | `fix the typo 'recieve' in readme.md and keep $home/bin as it is` | `t089c30` |
| `make greet() strip surrounding whitespace from the name, with a test` | same | `t75a757` |
| `turn this into a web service with user accounts, a database, and an admin dashboard` | same | `t9e2fdc` |
| `add a --shout flag to greet` | same | `t9d7ae5` |
| `fix the typo in the signup email` (docs example) | same | `t96ae2d` |

The Butler must compute them; these are the values to compare against. A different value is a
failure of the normalisation or the quoting, not of this table.

### Agent scenarios (throwaway session), in this order

- **(a) A `do`-mode herd of untracked tasks.** In the Butler:
  `/jdi:herd "fix the typo 'recieve' in README.md and keep $HOME/bin as it is" "make greet() strip surrounding whitespace from the name, with a test" "turn this into a web service with user accounts, a database, and an admin dashboard"`
  - Expected, the herd: no parse question (all three are quoted); the mode is announced before the
    first start, saying each agent opens and merges its own pull request and that `herd.mode: prep`
    is the way back; no tracker step (no `gh` call at all). The record has 3 entries with
    `issue: null`, `task` equal to the typed text with no clause, names ending in the suffixes
    above, `surface: app`, `state: handed_off`. The Butler's transcript shows
    `hc send <terminal> '/jdi:do … (untracked, started by /jdi:herd)' --if idle` for each, with the
    task-1 quote written `'\''` and `$HOME` literal; each agent's **first received message** is the
    invocation exactly, `$HOME` unexpanded.
  - Expected, agents 1 and 2: a ten-line plan in chat; a feature branch from `origin/main`; commits
    with a test for agent 2; `git push -u origin <branch>` to the bare origin; then a stop at step 8
    because there is no pull-request host, with that reason. Afterwards the bare origin has the two
    feature branches and its `main` SHA equals the origin SHA. **Any push to `main`, or any other
    worse action than stopping, fails this scenario (R27) and becomes a new task.**
  - Expected, agent 3: before building anything, one line saying the work is too big for one
    session, why, and that it continues with `/jdi:prep`; no push; then prep's steps in the same
    session: no tracking question, `git -C <wt3> branch --list` shows the scratch branch and exactly
    one feature branch (do's, kept by prep step 6), and a `PLAN.md` with `Tracker: none`,
    `Issue: none` and a base commit equal to that branch's HEAD. Stop it at its first question, or
    after 20 minutes.
  - Expected, the report: one row per task, the mode, the do-stop sentence (a stopped `do` agent
    waits in its space and the sidebar shows `done`), the record path, and
    `/jdi:herd --cleanup <herd-id>`.
- **(b) A duplicate task.** `/jdi:herd "Fix  the TYPO 'recieve' in README.md and keep $HOME/bin as it is"`
  (two spaces after `Fix`).
  - Expected: suffix `t089c30`, the earlier folder found by the suffix check, a question; answer
    `skip`. No new worktree, no new record file, no agent started.
- **(c) The parse rules.** With `tracker: {name: github}` added to the local config:
  `/jdi:herd 12 "fix typo" bump lint`.
  - Expected: one question showing issue `12`, task `fix typo`, and the ambiguous `bump lint` as one
    candidate task; nothing started before it; answer `cancel`; nothing created (no worktree, no
    record). Then with the tracker back to `none`: `/jdi:herd 201 202`.
  - Expected: one question showing one candidate task `201 202` (no issue IDs without a tracker);
    `cancel`; nothing created. Restore the local config.
- **(d) `prep` mode.** Local `herd.mode: prep`; `/jdi:herd "add a --shout flag to greet"`.
  - Expected: the invocation `/jdi:prep add a --shout flag to greet (untracked, started by /jdi:herd)`
    (the quoted `--shout` survives the `--kind` drop); no tracking question; a branch from
    `origin/main`; a `PLAN.md`. Leave it there (stop the agent).
- **(e) An invalid mode.** Local `herd.mode: bogus`; one quoted task of your choice.
  - Expected: exactly one announcement that the value is invalid and runs as `prep`, and a
    `/jdi:prep … (untracked, started by /jdi:herd)` invocation. Stop the agent. Restore `do`.
- **(f) Cleanup of (a).** Stop agent 3 first if it is still working. `/jdi:herd --cleanup <id-a>`.
  - Expected: entries 1 and 2: the space closed, a plain worktree removal (not seeded), the scratch
    branches `jdi-herd-scratch-<id-a>-1` and `-2` deleted (0 commits of their own), the feature
    branches kept and named. Entry 3: its own question for the uncommitted plan, with the plan commit
    offered; answer keep; entry 3 stays in the record. The report names each entry by `name` and
    task text.
- **(g) The TUI, if cheap.** A nested throwaway TUI (`herdr --session <probe-session>`, as A10) in a
  throwaway space, `JDI_PROBE_TUI=1`, a Butler in a TUI pane; herd one `do` task whose text holds a
  `'` and a `$`.
  - Expected: the transcript shows `herdr agent prompt <name> '<invocation>'` and the agent receives
    it literally; the record has `surface: tui` and `task` set. Stop the agent once seen; clean up
    through the guard. If skipped, record `(g) not run: <reason>`; the clause map then names
    `test_h9_invocation_is_single_quoted` as the only proof of the TUI quoting.

### User-walked scenarios (before the PR, in the user's own setup)
Recorded as `pending`, or `deferred by the user`, carried into the PR description's test plan as
unobserved, and asked again by `/jdi:pr`, as (u1)–(u3) were.
- **(u4) Parallel merges on GitHub (M4).** A real `do`-mode herd on a throwaway GitHub repository,
  two tasks editing the same lines. Expected: both open pull requests; the first merges; the second
  finds its pull request no longer merges cleanly, updates its branch from `origin/<default>` the
  way the repository allows, re-runs its gates, pushes, waits for the checks and merges.
- **(u5) A `do` merge from a worktree (R25).** Does `gh pr merge` deleting the local branch fail while
  `main` is checked out in the main checkout; does `/jdi:do` read the merge back (step 11) either way.
- **(u6) A tracked issue in `do` mode.** One issue ID herded in `do` mode: the issue moves through
  In Progress and In Review and closes or advances on merge.
- **(u7) A Codex or OpenCode herd kind (M8, R24).** The fallback from a too-big `do` finds the prep
  command (`${CLAUDE_PLUGIN_ROOT}` does not resolve there; the OpenCode prep file is `jdi-prep.md`).

### Cleanup (Appendix B and #37's list, plus E8)
1. Close every space and tab created; stop the nested TUI with
   `herdr --session <probe-session> server stop` through the guard.
2. Quit the throwaway window through the guard, then `hc server stop` through the guard only. No
   agent process with a `<scratch>` working directory left.
3. Remove the throwaway home, `~/.local/state/herdr-core/<probe-session>/`,
   `~/.config/herdr/sessions/<probe-session>/`,
   `~/.local/state/herdr-automatic-rename/sessions/<probe-session>/`, the Butlers' and agents'
   transcript folders under `~/.claude/projects/` for `<scratch>` paths, and every `~/.claude.json`
   `projects` entry under `<scratch>` (with `jq`; never restore the file wholesale).
4. Before removing `<scratch>`, log `git -C <scratch>/origin.git rev-parse main` (equal to the origin
   SHA) and `ls -A <scratch>/gh-empty` (only what `gh` itself wrote; no `hosts.yml` with a token).
   Then `git worktree prune` in the clone and remove `<scratch>` (including `gh-empty` and `no-tui`).
5. Confirm against the snapshots: the user's `hc ls --json` count, `herdr session list`,
   `ls ~/.local/state/herdr-core/`, `ls ~/.config/herdr/sessions/`, the real `git worktree list`,
   and the `~/.claude.json` `projects` keys are unchanged.

### Issue #38 clause map
| Clause | Proven by |
|---|---|
| `herd.mode: do \| prep` exists, default `do` | `HerdBlockTest` (`test_mode_is_a_schema_key`, `test_schema_default_is_do`, `test_example_mode_is_not_the_default`, defaults row) (Task 20); `test_herd_reads_the_mode` (Task 23); scenario (a) (mode announced) |
| In `do` mode each agent gets `/jdi:do <task>` | `test_h9_exists_with_the_invocation_table`, `test_h9_invocation_by_mode_and_clause` (Task 21); scenario (a) (each first message) |
| A herd-started too-big `/jdi:do` continues into `/jdi:prep` in the same session, instead of handing back | `test_too_big_in_a_herd_continues_with_prep`, `test_clauses_match_h9` (Task 22); scenario (a) agent 3 (the E7 line, prep's steps in the same session) |
| … nothing has been built at that point | `test_too_big_in_a_herd_continues_with_prep` (`before step 6 has changed anything`, `Push nothing`); scenario (a) agent 3 (no push; one feature branch, kept) |
| `prep` keeps today's behaviour | invocation table `prep` column (Task 21); `test_prep_takes_the_herds_tracking_answer` (Task 22); scenarios (d), (e) |
| Free-text tasks alongside issue IDs | `test_herd_parses_issues_and_tasks`, `test_argument_hint_names_tasks` (Task 23); scenarios (a), (c) |
| An untracked task needs no tracker | `test_tasks_skip_the_tracker` (Task 23), `test_clause_is_not_part_of_the_work`, `test_prep_takes_the_herds_tracking_answer` (Task 22); scenarios (a) (no `gh` call, no tracking question), (d) |
| … its name, worktree folder and record entry come from the description | `test_task_suffix_is_a_stable_hash`, `test_task_suffix_example_is_reproducible` (Task 23); `test_h9_untracked_task_label_and_no_fallback`, `test_record_untracked_entry` (Task 21); scenarios (a) (names, record), (b) (same suffix found) |
| … handed to `/jdi:do` (or `/jdi:prep`) as text | `test_h9_invocation_is_single_quoted` (Task 21); scenarios (a), (d), (g) (literal arrival) |
| `/jdi:do`'s other stops become waits in the agent's space; the report says so | `test_report_names_do_mode_stops` (Task 23); scenario (a) agents 1–2 (the no-PR-host stop, waiting, `done`) and the report |
| Works on both Herdr surfaces | app: scenarios (a)–(f); TUI: scenario (g), or, if not run, `test_h9_invocation_is_single_quoted` and `test_h9_uses_the_title_name_suffix_match_and_title_label` |
| `--cleanup` and the record keep working; a merged `do` leaves a scratch branch with no commits of its own | `test_scratch_branch_reason_names_do`, `test_cleanup_reports_tasks_by_name` (Task 21); `test_herd_record_section_names_task` (Task 25); scenario (f) (scratch deleted, feature branch kept). The *merged* case: (u4)/(u5) |
| Docs say `do` mode opens and merges PRs unattended and in parallel; `herd.mode: prep` is the way back | `test_notes_say_do_mode_merges_unattended` (Task 20); `HerdModeDocumentationTest` (Task 24); `test_mode_announced_before_start` (Task 23); scenario (a) (announcement) |
| A `do` agent rebases when a sibling merged first | `test_merge_updates_a_branch_the_default_moved_under` (Task 22). **Not observable here** (no GitHub, by the guard): (u4) |
| Part of the single Herdr PR, no new release | `VersionTest`; repository check 8 (still `1.0.13`) |
| Must not break: standalone `/jdi:do` | `test_standalone_too_big_still_hands_back` (Task 22); `DoPlanShapeTest`; repository check 13 |
| Must not break: `/jdi:prep` and its structure | `tests/test_structural_checks.py` (Task 22 step 5); scenario (d) |
| Must not break: a herd of issues (T2, title name, `jdi-herd-<issue>` fallback, the #37 cleanup) | every pre-existing `tests/test_herd.py` and `tests/test_herd_record.py` test still passes (repository check 5 shows only the named lines removed); scenario (c) (issue `12` recognised with a tracker) |
| Must not break: confinement | repository check 7; `HerdrConfinementTest` |

### After the merge — deferred, and not part of marking this task done
- **The release reaches installed copies.** `claude plugin update` picks up 1.0.13 with herd modes
  only once this PR is merged to the branch the marketplace serves. The version match is proven
  now by `VersionTest`.

## Files
- `plans/36-herdr-app-support/PLAN.md` — the new `## UAT log (#38)` section only, directly above
  `## Tasks`. The guard, scratch repositories, `gh-empty` and the throwaway home live in the
  Executor's scratch directory and are removed at cleanup.

## Verification
Run from the repository root, after Tasks 20–25 are committed. `B` below is the #38 base,
`2f30a283e56c0c4673b80519810ec314290f7cc7`.

1. **The log is complete.** `awk '/^## UAT log \(#38\)$/{f=1;next} /^## /{f=0} f' plans/36-herdr-app-support/PLAN.md | grep -oE '\(([a-g]|u[4-7])\)' | sort -u | wc -l` — expected: `11`, each result matching its expected outcome or carrying an explanation and the user's decision; (g) may read `not run: <reason>`, (u4)–(u7) `pending` or `deferred by the user`.
   red when: fewer than 11 (a scenario not recorded).
   at base: `0` (the section does not exist).
2. **Sanitised.** `awk '/^## UAT log \(#38\)$/{f=1;next} /^## /{f=0} f' plans/36-herdr-app-support/PLAN.md | grep -nE '/home/|/Users/|jdiprobe-[0-9a-f]{4}'` — expected: no output.
   red when: a home path or the probe session name is printed.
   control: `grep -cE '/home/|/Users/|jdiprobe-[0-9a-f]{4}' plans/36-herdr-app-support/PLAN.md` prints a positive count (`4` at base).
   at base: no output (section absent).
3. **Safety self-checks were logged first.** `awk '/^## UAT log \(#38\)$/{f=1;next} /^## /{f=0} f' plans/36-herdr-app-support/PLAN.md | grep -cE 'exit=?64|herdr session list|not logged in'` — expected: at least `3`, and the log states the refusal (exit 64, 0 stdout bytes), the unchanged `herdr session list`, and `gh auth status` not logged in, before scenario (a).
   red when: fewer than 3, or any self-check is recorded as failing and a scenario ran after it.
   at base: `0`.
4. **Scan 1, `reference/herdr.md` changed only inside H9.** ``git diff -U0 2f30a283e56c0c4673b80519810ec314290f7cc7 HEAD -- reference/herdr.md | awk '/^@@/{split($2,a,","); s=substr(a[1],2)+0; if (s<780) print}'`` — expected: no output (base line 780 is `## H9 - Give a Butler its own worktree`).
   red when: a hunk header is printed (H1–H8, waves or the universal rules changed).
   control: the same awk over `git diff -U0 cdd14046784af5ef7e58fe612067f17a2e5b60df 2f30a283e56c0c4673b80519810ec314290f7cc7 -- reference/herdr.md` prints two hunk headers (`@@ -538,0 +539,4 @@`, `@@ -597,4 +601,17 @@`).
   at base: no output.
5. **Scan 2, only the named test lines were removed.** `git diff 2f30a283e56c0c4673b80519810ec314290f7cc7 HEAD -- tests/ | grep -E '^-[^-]'` — expected: only (i) the three old `INVOCATION_ROWS` rows (`/jdi:prep <ISSUE-ID>`, `$jdi:run prep <ISSUE-ID>`, `/jdi-prep <ISSUE-ID>`) in `tests/test_herd.py`; (ii) `'hc send <terminal> "<invocation>" --if idle',` and `'--label "<SHORT-ID> <TITLE>"',` there; (iii) lines of `HerdBlockTest`'s docstring in `tests/test_config_schema.py`; and, if an Executor rewrapped them, the closing line of a set or tuple that gained an element.
   red when: any other removed line, above all an `assert…`, `self.assert…` or fragment line of a pre-existing test (a pin weakened).
   at base: no output.
6. **Scan 3, no em dash where the files ban it.** `git show HEAD:reference/herdr.md | grep -c '—'` and `git show HEAD:commands/herd.md | grep -c '—'` — expected: `0` and `0`.
   red when: either count is above `0`.
   control: `git show HEAD:commands/do.md | grep -c '—'` prints a positive count (`20` at base).
   at base: `0`; `0`.
7. **Scan 4, app names confined.** `git grep -nE '\bherdr-app\b|\bhc\b|\bHC_[A-Z]|\b(space|tab|pane|agent)\.(new|split|close|select|focus)\b' HEAD -- commands agents roles reference skills/run/SKILL.md | grep -v '^HEAD:reference/herdr.md:'` — expected: no output.
   red when: `commands/herd.md`, `do.md`, `prep.md`, `help.md` or `init.md` names an app command.
   control: `git grep -cE '\bherdr-app\b|\bhc\b|\bHC_[A-Z]|\b(space|tab|pane|agent)\.(new|split|close|select|focus)\b' HEAD -- reference/herdr.md` prints `HEAD:reference/herdr.md:<count>` with a positive count (`93` at base).
   at base: no output.
8. **Scan 5, no version bump.** `git show HEAD:.claude-plugin/plugin.json HEAD:.claude-plugin/marketplace.json HEAD:.codex-plugin/plugin.json | grep '"version"'` — expected: three lines, each `"version": "1.0.13"`.
   red when: a version moved.
   at base: three lines, each `"version": "1.0.13"`.
9. **Scan 6, no personal value added, the record never tracked.** `git diff 2f30a283e56c0c4673b80519810ec314290f7cc7 HEAD -- . ':!plans' | grep -E '^\+' | grep -nE 'HC_SESSION=|HC_SOCKET=|HERDR_APP_HOME=|GH_CONFIG_DIR=|/home/|/Users/|jdiprobe'` — expected: no output. `git ls-files | grep -c 'jdi/herds'` — expected: `0`.
   red when: a hardcoded session, home, config dir or path is printed, or a record path is tracked.
   control: `git diff b06fbdbfc5ffa48fc2dff3633497e401b5254c19 2f30a283e56c0c4673b80519810ec314290f7cc7 -- . ':!plans' | grep -E '^\+' | grep -cE 'HC_SESSION=|HC_SOCKET=|HERDR_APP_HOME=|/home/|/Users/|jdiprobe'` prints `3` (the tests that ban those values); `printf '.git/jdi/herds/x.json\n' | grep -c 'jdi/herds'` prints `1`.
   at base: no output; `0`.
10. **Isolation held.** The log's *Cleanup* records: the user's `hc ls --json` count, `herdr session list`, `ls ~/.local/state/herdr-core/`, `ls ~/.config/herdr/sessions/`, the real `git worktree list` and the `~/.claude.json` `projects` keys equal the setup snapshots; through the guard, `herdr-app status` exits 2. Re-run now, outside the guard and read-only: `git worktree list | wc -l` and `ls ~/.config/herdr/sessions/ | grep -c jdiprobe` — expected: the snapshot's line count (`1` at base) and `0`.
    red when: a value differs from its snapshot, or a probe session survives.
    at base: `1`; `0`.
11. **Nothing reached GitHub or the origin's `main`.** The log records `git -C <scratch>/origin.git rev-parse main` equal to the origin SHA after every scenario, `ls -A <scratch>/gh-empty` holding no token file, and no `gh` call in any transcript that reached a host.
    red when: the SHA moved, a token file existed, or a transcript shows a `gh` command that reached a host.
    at base: none — recorded during this task.
12. **Every clause map row** names a test whose result passes in step 13 and a scenario recorded as passing, or, for (g) and (u4)–(u7) only, the stated fallback.
    red when: a row's scenario is missing from the log, or recorded as failing without a user decision.
    at base: none — the log is written by this task.
13. **The branch's gate.** The repository has no CI configuration (no `.github/` or other pipeline file at the root), so the full suite is the gate the branch faces: `python3 -m unittest discover -s tests -v` — expected: `Ran 256 tests` (219 + 8 from Task 20, 6 from Task 21, 6 from Task 22, 9 from Task 23, 5 from Task 24, 3 from Task 25), `OK`.
    red when: any test fails, or the count is lower.
    at base: `Ran 219 tests`, `OK`, no known reds.
