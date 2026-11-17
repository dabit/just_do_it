# Support the Herdr desktop app alongside the TUI

- Tracker: github
- Project: feature development
- Issue: #36 (also #37 herd cleanup, #38 herd modes and untracked tasks)
- Issue URL: https://github.com/dabit/just_do_it/issues/36
- Created: 2026-11-16
- Summary: One PR against `main`: JDI detects whether it runs inside the Herdr app (`herdr-app` + `hc`) or the Herdr TUI, makes that configurable, and routes every Herdr operation (role delegation, waves, `/jdi:herd` worktrees) through the detected surface. It also carries `/jdi:herd --cleanup` (#37), herd modes and untracked tasks (#38), and the role-delegation work of the closed PR #31. Released as one 1.0.13.
- TDD: on — proven 2026-11-16 with `python3 -m unittest discover -s tests -v`

## References

- `reference/herdr.md` (H1–H9, surfaces, herd record, cleanup; the only file allowed to name `herdr <sub>`, `herdr-app`, `hc`, `HC_*`, `HERDR_*`)
- `reference/delegation.md`
- `reference/config.md`
- `commands/herd.md`
- `commands/do.md`
- `commands/prep.md`
- `commands/init.md`
- `commands/help.md`
- `commands/{research,plan,split,feedback,pr,execute,next,yolo}.md` (step 0)
- `docs/herdr-surfaces-architecture.md`
- `docs/delegation-transport-architecture.md`
- `docs/config-key-lifecycle.md`
- `README.md`
- `AGENTS.md`
- `CHANGELOG.md`
- `jdi.config.example.yml`
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `tests/test_config_schema.py`
- `tests/test_herdr_operations.py`
- `tests/test_herd.py`
- `tests/test_herd_record.py`
- `tests/test_herd_handoff.py`
- `tests/test_herdr_surfaces_doc.py`
- `tests/test_delegation_transport.py`
- `tests/test_step_zero_transport.py`
- `tests/test_transport_docs.py`
- `tests/test_structural_checks.py`
- `plans/herdr-role-delegation/PLAN.md` (PR #31's binding decisions D1–D12: Herdr only for a role on another CLI; JDI never answers a worker's dialog or sends keys; result via run directory)
- External, not in the repo: `herdr-app --skill`, `hc --skill`, `hc <cmd> --help`, the installed app guide, the shipped `worktree` mod. Versions observed: `herdr` 0.9.3, `herdr-app` 0.1.16, `hc` 0.1.21.

## Decisions

### Surfaces (#36)

User, 2026-11-16:
- **Key.** `herdr.surface: auto | app | tui`, default `auto`, usually in `config.local.yml`. On/off stays `delegation.transport` (no `off` value). Passes the five-question test in `docs/config-key-lifecycle.md`.
- **App worktrees** are a documented recipe (H9's app variant) in `reference/herdr.md`, not a shipped script.
- **Structure.** One set of operations H1–H9, each with a TUI and an app variant; every app string confined to `reference/herdr.md`; TUI behaviour unchanged (TUI test assertions only grew: 0 deletions).
- **One PR.** PR #31 is closed; all Herdr work ships in one PR against `main` as one 1.0.13. (The earlier stack-on-#31 plan and its version renumbering are superseded.)

Butler defaults adopted:
- Nested app-in-TUI or TUI-in-app: the innermost surface wins (`hc get` `foreground`); inconclusive says so once, then `tui`. App binary or socket missing means unreachable: `tui`, no note.
- Worker env goes in the argv as `env KEY=VALUE … <kind>`; paths expanded first.
- Single worker: `pane.split --argv` beside the Butler, direction always `right`. Wave: `tab.new --argv` for the first worker, `pane.split` for the rest. Never `hc run`.
- Workers addressed by terminal ID, labelled `jdi.agent=<name>`.
- Codex `--no-daemon` goes in `harnesses.codex.args`; JDI adds nothing, notes once when missing.
- App H1 requires `herdr-app status` to succeed: exit 0 and JSON stdout with no top-level `error` (with no window it exits 2 with plain stderr, A11).

**Amended after the probe gate (user, 2026-11-16):**
- **D6.** JDI types into an agent only after a readiness `hc wait` reports `status: idle`, and always with `hc send … --if idle`. Never `--task`. *Why:* Claude's and Codex's trust/hook-review dialogs report **no status** (not `blocked`), so `hc wait` times out with `status: null` and a plain `hc send` would type into the dialog (breaking #31 D9). A herd worktree is a new folder.
- **D7.** Reject at readiness: no `status: idle` (for example a timeout with no status) means not ready. JDI types nothing, says why (possibly a dialog the user must answer); delegation closes the pane and falls to `native`; the herd reports that issue blocked at startup and leaves its space open.
- Planner P10 narrowed: if a worker's status vanishes mid-run, every check-in also looks for `result.json` and goes to H7 if present.

Planner:
- App H2 resolves the kind with `command -v` and puts the **absolute path** in the argv (terminals get the core's env, not the Butler's PATH); an alias or function fails H2.
- `pane.split` has no folder option and starts in the Butler terminal's folder (A14), so split argv is prefixed `sh -c 'cd -- "$1" && shift && exec "$@"' jdi-worker <root> …`. `exec` through `sh` and `env` keeps status reporting (A6). `tab.new` / `space.new` use `--folder`.
- `pane.split` moves focus (A13); H4 appends `&& herdr-app do pane.focus --pane <butler pane>`.
- A pinned `app`/`tui` never falls to the other surface (delegation degrades to `native`, the herd stops); an invalid value is announced once (only when H1 runs) and treated as `auto`.
- Herd on the app: H9 creates only the worktree (step 6); the space and agent come at step 8, after `herd.seed`. App worktree folder = `worktrees.directory` from the app's `settings.json`, default `~/.herdr/worktrees`; any other relative value fails H9 with its reason.
- JDI closes only via `pane.close`, `tab.close`, `space.close`; never `hc kill`, `hc rm`, `hc keys`, `hc interrupt`, `hc send --force`; never bare `hc` or bare `herdr-app`; never sets `HC_SESSION`, `HC_SOCKET`, `HERDR_APP_HOME` ("inherit, never set").
- Manifest `herdr` object gains `"surface"` on both surfaces (additive; schema stays 1).
- `/jdi:init` offers `herdr.surface` as a sub-bullet of step 10, not a new numbered step (follows the `herd` precedent; a recorded deviation from the lifecycle doc).

Probe facts that shaped the text (A1–A17, throwaway session via an isolation guard):
- `hc wait` returns `reason: timeout, status: null` for an open dialog; it does not report one (A2). A plain send to a status-less terminal types the text (A4).
- `status` prints plain stderr and exits 2 with no window, not `{"error": …}` (A11).
- `pane.close` on an already-gone pane or `tab.close` on a gone tab prints `{"error": "no pane|tab …"}` on stdout, exit 1: H8 treats it as already gone (A7).
- App terminals are not the requester's children (`parent: null`); `--name` with `'`, `$`, backticks arrives literally when single-quoted (A16, A17).
- Under a named session terminals carry `HC_SESSION` and `HERDR_APP_HOME`; a default window has neither.
- **Codex status reporting is unobserved**: its two start-up dialogs were never answered.

### Herd cleanup (#37)

- **Record.** H9 writes `<git-common-dir>/jdi/herds/<herd-id>.json` (`git rev-parse --path-format=absolute --git-common-dir`), identical shape on both surfaces (`schema`, `herd_id`, `created`, `surface`, `state`, `issues[]` with `n, issue, name, worktree, scratch_branch, base_commit, seeded, created, herdr{workspace_id, space_id, tab_id, pane_id, terminal_id, agent_name}`). Never committed; written whole to a temp file then `mv -f`; names no session or app home; `worktree` stored as `git worktree list --porcelain` prints it. `state` is `creating` until step 10, `handed_off` after. An unwritable record gets one sentence and the herd continues.
- **Entry point.** `/jdi:herd --cleanup [<herd-id>]`, a mode of `commands/herd.md` (no new command file). Herd ID must match `^[0-9]{8}T[0-9]{6}$` or the run refuses (never builds a path from an unchecked argument); issue IDs, tasks or `--kind` alongside it stop the run. Without an ID, `creating` records are skipped; with it, included but flagged. No record: say so, clean nothing, point at `git worktree list`; never guess from folder names.
- **Per entry.** Re-find every space/workspace **by worktree path, never by a recorded ID alone** (IDs are reused). Skip `working` or `blocked` agents (checked across the whole space/workspace); skip an entry whose worktree or space holds the session running the cleanup; unreachable surface: skip the close, still offer the worktree removal marked "agent state unknown". Whole-tree `git status --porcelain`: anything shown plus seeded means list it then `--force`; unseeded means skip. Uncommitted plan files take the entry out of the batch for its own question. One list, one question. Order: plan re-check, close space (app) / workspace (TUI), remove worktree, branch rule, update record.
- **Branches.** Delete only `jdi-herd-scratch-<herd-id>-<n>`, only if it still exists, `git rev-list --count <base_commit>..refs/heads/<scratch>` is `0` and its worktree is gone. Never any other branch. Correction: `/jdi:prep` step 6 leaves the scratch branch behind at its base; it does not rename it.
- **Upkeep.** Remove an entry once its worktree leaves `git worktree list --porcelain`; delete the file with the last entry. A "prunable" worktree keeps its entry and the user is told to run `git worktree prune`.
- Cleanup rules live only in `reference/herdr.md`; `commands/herd.md` calls them by name (it may not name app actions). Task 15 dropped `"herd record"` from the banned-keys test (#31 banned a *resume* record; this one is for cleanup only); not red-first.
- **Probe gate (#37) amendments.** G1: a worktree with no open workspace has **no** `open_workspace_id` key (not `null`). G2: busy check reads each terminal's `status` string in `hc ls --json --label herdr.space=<space>` (absent when none reported; `state` there is the lifecycle). G3: the app keeps a space's `folder` as opened, git prints the resolved path, so the app match resolves with `(cd -- <folder> && pwd -P)`. TUI `herdr worktree remove --workspace` deleted no branch and refused a dirty tree without `--force` (R2), so the unamended removal stands. `branch` in `herdr worktree list` is the *current* branch, so match by `path`. Ignored files go silently with a plain `git worktree remove`; untracked or modified files block it (exit 128). The idle-agent `agent_status` shape on the TUI was not observed.
- **Task 19 / R6.** After a turn ends the status is `done` and `--if idle` refuses it (exit 10); nothing JDI does clears `done`. App H6 answers `needs_input` by reading `hc get`: `idle` sends with `--if idle`, `done` sends plain (dialog-safe because dialogs report `blocked`, refused exit 9, or no status at start-up only), anything else types nothing. H5's first prompt and H9's handoff follow a readiness wait that saw `idle` at turn 0 and keep `--if idle`.

### Herd modes and untracked tasks (#38)

User, 2026-11-16: `herd.mode: do | prep`, default `do`; a herd-started too-big `/jdi:do` continues into `/jdi:prep` in the same session; free-text tasks alongside issue IDs with no tracker needed; same branch and PR; M1 (prep invocation carries the clause too) and M4 (below) approved.
- **Clause.** Every herd invocation ends `(started by /jdi:herd)` (issue) or `(untracked, started by /jdi:herd)` (task). do/prep learn they run in a herd only from this clause, never from config. The too-big fallback applies only when the stop is found before do's step 6 changed anything; otherwise the normal stop. Prep keeps do's unpushed branch (prep's step 6 only switches branches when the current one does not name the work). Prep fallback path: `${CLAUDE_PLUGIN_ROOT}/commands/prep.md`, else the prep file beside do (OpenCode `jdi-prep.md`).
- **Other do stops** (product decision, repo-reserved change, non-converging review, no PR host) leave the agent waiting; the sidebar shows `done` (a finished turn, same as merged), and the report says to open the space.
- **Parsing** (herd step 3): a quoted argument is always a task; unquoted is an issue ID only with a tracker configured and an issue-shaped token (`tracker.id_prefix` constrains `<KEY>`); with no tracker nothing is an ID; anything else is ambiguous, shown whole, asked once, nothing started before the answer.
- **Naming.** Suffix `t` + first 6 hex of `printf '%s' '<normalised task>' | git hash-object --stdin` (normalised: lowercased, whitespace collapsed, trimmed). A hash, not an index: same text gives the same suffix, so H9's suffix check finds an earlier folder; an index would make every herd's first task `t1`. Example: `fix the typo in the signup email` gives `t96ae2d`. Label/space name `<suffix> <task text>`; no `jdi-herd-<issue>` fallback; tasks skip every tracker step. Record: `issue` may be `null`, new `task` key, `schema` stays `1` (additive; missing `task` reads `null`).
- **Quoting.** The invocation is one single-quoted shell argument (`'` as `'\''`, never double-quoted); TUI `herdr agent prompt <name> '<invocation>'`, app `hc send <terminal> '<invocation>' --if idle`; TUI `--label '<SHORT-ID> <TITLE>'`. Task text collapses to one line.
- **Invalid `herd.mode`** is announced once and runs as `prep` (less authority).
- **M4.** do step 10: when the PR stops merging cleanly because the default branch moved, update from `origin/<default>` the way the repo allows, re-run step 7's gates, push, wait for checks; a conflict needing a product decision is a step-5 stop. Applies to standalone `/jdi:do` too.
- **Recorded deviation** from the lifecycle doc: `herd.mode` is a repo-level key whose default `do` is not the least-demanding; the user chose it and no herd had shipped. Init offers it in step 10's herd sub-bullet.
- **App handoff (task 27, F-h).** `hc send` from an agent's terminal wraps the text as `<hc from="…">…</hc>`, so Claude does not run it as a slash command. Probe R7: from a plain shell the send is untagged; `env -u HC_TERMINAL_ID hc send …` untags it, still reaches the throwaway core (`HC_SESSION` routes, `HC_TERMINAL_ID` only names the sender), and `--if idle` is still enforced. H9 on the app now hands off with `env -u HC_TERMINAL_ID hc send <terminal> '<invocation>' --if idle`. Passing the work in the agent argv also works but per kind; unused. H5/H6 prompts stay tagged: workers act on tagged plain text. #37's UAT (a) only proved the text was sent, not that the command loaded.
- **Size gate (tasks 28, 29; user, 2026-11-16).** Task 28 made do step 4 a gate with `**Size:** fits one pull request` or `**Size:** too big for one session` as its first field. Re-runs showed no agent posted it in chat (0 of 6, judgment stayed in thinking). User decision: **behaviour is enough**. Step 4 now says the size is decided before any edit; posting is not required. Passing means a too-big task falls back to `/jdi:prep` before any edit and a small one ships.
- **Model note (documented, not enforced).** `do` mode relies on each agent judging size before it builds. In testing, Opus herd agents did (too-big fell back to prep with no edit or push); Sonnet herd agents built the oversized task in 3 of 3 runs and pushed it, and Sonnet agents sometimes worked on the herd's scratch branch. The note sits in `reference/config.md`'s `herd.mode` notes, the README herd paragraph and the CHANGELOG 1.0.13 bullet; for cheaper models use `herd.mode: prep`. No model-name logic.
- **Announcement (F-i): report-only accepted.** Step 8's quoted mode announcement never appeared as a chat line before the first start (thinking block only); the final report names the mode and `herd.mode: prep`. Step 8 stays as is.

## Plan gaps caught during execution and UAT

- **Probe gate (task 02) contradicted D6/D7**; resolved by the user as amended above. P6 refined by A11; P10 narrowed.
- **UAT (task 10) fixes, task 11.** F2: `status_reported` was written before the readiness wait, so always `false`; fixed. F3: the app's wave tab closes itself when its last pane closes (herdr-app 0.1.16); H8 and `### Waves on the app` no longer say it does not, and the "no tab" error is harmless. F4: Claude takes a linked worktree's folder trust from its trusted main checkout, so H9's "always a dialog" was wrong; it *can* appear (untrusted main checkout, or a CLI that does not inherit trust) and D7's handling stays. F5: pinned-surface and `auto` notes were off-pattern and narrated H1; H1 now quotes the exact `Herdr (<surface>) is not usable here: …` note and says silence under `auto` includes summaries. F7: herd space name was double-quoted; H9 now carries a single-quoted example line.
- **Recorded, not fixed.** F1: a Sonnet *Butler* skipped rung 2 after detecting the app (ran `opencode run` behind a spawn line with `run dir: none`); the default-model Butler followed it every time. F6: `herdr` 0.9.3 prints `endpoint_compatible: yes` / `private_protocol_compatible: yes` rather than `compatible: yes`; the Butler accepted both. F-a: the record was created after all worktrees, not at the first; same end state. F-b: removal closed the space by recorded ID after matching by path; text could say it closes the path-matched space. F-d: unseeded herd worktrees do not get the gitignored `config.local.yml` (`herd.seed.copy` is the remedy). F-j: a long-lived Butler reuses its config across `/jdi:herd` runs. F-k: reports sometimes misattribute local-config values to `config.yml`. F-l: one Butler read the real app home before `$HERDR_APP_HOME`.
- **Harness gap, closed.** The probe guard must export `HERDR_SOCKET_PATH` to a nonexistent path outside TUI mode, or `herdr` commands reach the user's default TUI server (it happened once, read-only). The nested TUI needs it unset in its own argv.
- **Not red-first (stated):** the version bump (`VersionTest` only), task 15's loosened ban, the AGENTS.md row.
- **UAT scenario (a) first failed on #38** (F-e: too-big task built and pushed; F-f: scratch branch adopted; F-g: no ten-line plan; F-h: wrapped handoff). F-h was fixed by task 27; F-e/F-f/F-g by tasks 28, 29 only on the behaviour level above; Sonnet still fails (see model note).

## Outcome

### Shipped

| Batch | Commits |
|---|---|
| Role-delegation work from closed PR #31 (transport key, herd block, delegation, 1.0.10 smoke-test fixes) | `1d937f0` … `b06fbdb` (see `git log origin/main..HEAD`) |
| #36 config key, probes, H1/surfaces, user docs, architecture docs (tasks 1–5) | `cd47708`, `ff0930e`, `1141721`, `3d3ff62`, `14482a4` |
| #36 H2–H8/waves on the app, callers, H9/herd on the app (tasks 6–8) | `31c40fa`, `809fc0e`, `0b465ef` |
| #36 release, UAT log, UAT follow-ups (tasks 9–11) | `ec1c224`, `4c5047b`, `c6233df` |
| Merge of `origin/main`; ship all as one 1.0.13 | `129384c`, `cdd1404` |
| #37 plan and probe gate; record (13); cleanup reference (14); `--cleanup` command (15); user docs (16); architecture docs (17) | `48afa2a`, `fe7b60d`, `e7db792`, `da99458`, `1655948`, `1ee00a1` |
| #37 app send after `done` (19); UAT record (18) | `76db238`, `2f30a28` |
| #38 `herd.mode` key (20); H9 modes/clause/quoting/tasks (21); do/prep clause (22); herd command (23); user docs (24); architecture docs (25) | `76a2550`, `9e0e498`, `a5f4bdd`, `c608250`, `b188598`, `1eb979b` |
| #38 real slash-command handoff (27); size gate (28); gate by behaviour + model note (29) | `21dc299`, `a952b74`, `3f588b7` |
| #38 UAT records and user decisions | `b8db0d4`, `0e3515e`, `28b285b` |

A total commit count and push state are deliberately omitted: the commit that stores this file would make them wrong. See `git log origin/main..HEAD` and `git status -sb`.

### Deferred

- User-walked scenarios (u1)–(u7) and re-walking (e)/(g): see **Remaining work**; deferred by the user to PR review, to be carried into the PR description's test plan as unobserved.
- Not delivered, by design: `/jdi:status` on the app, `hc run` workers, Windows verification, a shipped worktree script.
- After merge: `claude plugin update` reaches installed copies with 1.0.13 only once this merges to the branch the marketplace serves; the version match itself is proven by `VersionTest`. Observe it when the PR lands.

## Test result

- Last recorded full suite: `python3 -m unittest discover -s tests -v` gave `Ran 266 tests … OK` in the re-runs after task 28 (earlier checkpoints 166 → 219 → 256 → 260). Task 29 reworded pinning tests after that count; **no count was recorded for the final state**, so re-run the suite before the PR.
- Agent smoke tests, each in a throwaway session behind an isolation guard, with isolation checks and snapshots equal before and after: #36 (a)–(h) (the pinned-surface (e) and (g) first failed on note wording, then fixed in task 11; their re-walk is deferred); #37 (a)–(k) all pass; #38 (a) **fail** on Sonnet and fail on the posted `**Size:**` line on Opus, with the too-big fallback working on Opus; (b)–(e), (g) pass; (f) fully observed on the Opus run. Close-out accepted by the user as behaviour-judged (decision above).
- Not observed: Codex ever ran in any UAT; Windows and macOS; the partial-upkeep case only in the #38 UAT (observed there), not in #37's.

## Risk note

Accepted risks surviving into production:
- **Unattended parallel merges by default (`herd.mode: do`).** Detection: the step-8 announcement, the final report, README/CHANGELOG/help. Remedy: `herd.mode: prep` stops each agent at a plan; the repo's own rules (a `CLAUDE.md`/`AGENTS.md` forbidding merges) stop `do` before the merge. A `do` agent that underestimates size ships a sprawling PR; Sonnet does this (see model note).
- **Visible change for existing app users.** Under `delegation.transport: auto|herdr` roles on another CLI now get app panes and `/jdi:herd` works. Remedy: `transport: native` or `herdr.surface: tui`. Stated in the CHANGELOG.
- **Narrow panes.** Split direction is always `right`; 4-wide waves can hide dialogs at half width (#31's smoke test). Accepted.
- **App workers get the core's environment**, not the Butler's: put needs in `harnesses.<kind>.env` (values appear in the Butler's command line and `hc get` argv; the manifest records keys only).
- **Platforms.** App variants assume POSIX `sh`; `--path-format=absolute` needs git 2.31+; Windows and macOS (default app home `~/.config/herdr-app`) are unverified.
- **Concurrent cleanups:** last writer wins; the record self-heals next run. A record stuck at `creating` after a crash is skipped without an ID and cleaned with one. A blocked-at-startup agent cannot be cleaned while its dialog is open; the skip reason says to answer it or close the space.
- **A person typing the herd clause by hand** opts into the fallback; harmless. SHA-256 repos give different suffixes (stable within the repo); a 24-bit suffix collision leads to one question, never a folder.

## Remaining work

Exempt from the compression target. All user-walked; the agent must never run them. Each was deferred by the user to PR review; `/jdi:pr` asks again and the PR description's test plan lists them as unobserved. For every scenario use a disposable checkout of this branch (a `git worktree add` on a new branch or a clone), run Claude with `claude --plugin-dir <path of this branch's checkout>`, and add a `.jdi/config.local.yml` with `tracker: {name: none}` unless stated.

**(u1) Default app window, no named session.** Checks the app path outside the test harness.
1. In a terminal of your normal Herdr app window, run `printenv HC_SESSION HERDR_APP_HOME`; it should print nothing.
2. Disposable checkout; `.jdi/config.local.yml` with `tracker: {name: none}`, `models.researcher: {harness: opencode, model: ""}` and `delegation: {transport: auto}`, no `herdr` key.
3. In an app terminal in that checkout start `claude --plugin-dir <branch checkout>`; run `/jdi:prep Add a comment line to jdi.config.example.yml`.
4. Expect: no step-0 note; a `JDI spawn` line in the split command's output; one opencode pane to the right of the Butler with focus back on the Butler; the run directory's `manifest.json` `herdr` object with `"surface": "app"`, `terminal_id`, env keys only; the Researcher's result accepted; the pane closed afterwards. A herd from this window would use `~/.herdr/worktrees` or your own `worktrees.directory`.
5. Close the Butler; remove the checkout and its branch.

**(u2) Existing TUI user.**
1. In your own Herdr TUI (`HERDR_ENV=1`), in a disposable checkout, same local config as (u1), no `herdr` key. Start `claude --plugin-dir <branch checkout>`.
2. Run one delegated role, e.g. `/jdi:prep Add a comment line to jdi.config.example.yml`.
3. Expect exactly the 1.0.10 behaviour: no note; the spawn line, then `herdr pane split --current --direction <right|down> --cwd <root> --no-focus`, `herdr agent start … --kind opencode`, `herdr agent prompt … --wait`; `manifest.json` with `"surface": "tui"` in its `herdr` object (the only additive change); H7 valid; pane closed.

**Re-walk of #36 (e) and (g) (wording fixed in task 11), with (u1)/(u2).**
- (e) Inside the app, set `herdr.surface: tui`, `delegation.transport: auto`, run `/jdi:research` on an existing plan. Expect a silent `native` run: no Herdr mention anywhere (summary included), no checks after the first failing one, no app command. Then with `transport: herdr`: exactly one note of the form `Herdr (tui) is not usable here: …`, still `native`, no fall to the app.
- (g) In a plain shell outside any Herdr (no `HC_TERMINAL_ID`, no `HERDR_ENV`), `transport: auto` is silent and native. With `herdr.surface: app` and `transport: herdr`: one note `Herdr (app) is not usable here: …` naming the surface, then native.

**(u3) A real herd cleaned up (#37).**
1. In a checkout of this branch (or with this branch's plugin via `--plugin-dir`), in your own app window or TUI, run a real `/jdi:herd <issue> [<issue> …]`. Note the herd ID the step-11 report names.
2. Let the agents finish (`done` or `idle` in the sidebar); commit each plan on its feature branch, or answer the agents as usual.
3. From the main checkout (not a herd worktree), run `/jdi:herd --cleanup <herd-id>`.
4. Expect one list and one question; on `yes`, each herd space (or TUI workspace) is closed, then its worktree removed; feature branches kept; a scratch branch deleted only with no commits of its own; `.git/jdi/herds/<herd-id>.json` gone once the last entry goes. A worktree with uncommitted plan files gets its own question instead.

**(u4) Parallel merges on GitHub (M4).**
1. Throwaway GitHub repository with one file of a few lines, `herd.mode: do` (the default), this branch's plugin via `--plugin-dir`.
2. `/jdi:herd "change line 2 of notes.md to say alpha" "change line 2 of notes.md to say beta"`.
3. Expect both agents open PRs; the first merges; the second finds its PR no longer merges cleanly, updates its branch from `origin/<default>` the way the repo allows, re-runs its gates, pushes, waits for checks on the new head and merges, or stops in its space if the conflict needs a product decision.

**(u5) A `do` merge from a worktree (R25).**
1. In the same repository, from the main checkout with `main` checked out there, run `/jdi:herd "<one small task>"`.
2. Note whether `gh pr merge` (which deletes the local branch) fails because `main` is checked out in the main checkout, and whether `/jdi:do` step 11 reads the merge back from GitHub either way. Expect the remote merge to be reported correctly regardless.

**(u6) A tracked issue in `do` mode.**
1. With a tracker configured, run `/jdi:herd <issue-id>` in `do` mode.
2. Expect the agent to receive `/jdi:do <issue-id> (started by /jdi:herd)`; the issue moves to In Progress, then In Review, and closes or advances when the PR merges.

**(u7) A Codex or OpenCode herd kind (M8).** Fallback is unverified on both.
1. Run `/jdi:herd --kind codex "<a task too big for one session>"`, and the same with `--kind opencode` (a Codex kind needs `--no-daemon` in `harnesses.codex.args`; Codex dialogs are yours to answer).
2. Expect the agent to say the work is too big, find the prep command although `${CLAUDE_PLUGIN_ROOT}` does not resolve there (OpenCode: `jdi-prep.md` beside `jdi-do.md`), and continue with prep in the same session.
