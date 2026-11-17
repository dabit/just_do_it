# Herdr Surfaces Architecture

## Status

Implemented in 1.0.13 for issue #36, in the same release as the role delegation it extends. Every
decision below is settled, and the live probes ran before the reference was written: the probe
gate stopped once, on D6 and D7, and passed after both were amended (see *Decisions* and
*App-side live probes*). The operations themselves are defined in `reference/herdr.md`; this
document records the design behind them and the observations that shaped it.

Issue #37 adds the herd record and `/jdi:herd --cleanup`, which removes a herd's worktrees from that
record, in the same 1.0.13. They had their own probe gate (Task 12 of the plan), which passed after
three amendments, G1 to G3 (see *The herd record*).

Issue #38 adds herd modes and untracked tasks in the same 1.0.13: `herd.mode` picks the command each
herd agent runs, `/jdi:do` (`do`, the default) or `/jdi:prep` (`prep`, the way back to the earlier
behaviour); `/jdi:herd` takes untracked tasks beside issue IDs; the H9 handoff is single-quoted on
both surfaces; and the herd record gains a `task` key (see *The herd record*).

## Purpose

JDI's Herdr operations (`reference/herdr.md`, H1 to H9) were first written against the Herdr TUI,
the `herdr` CLI. Herdr also ships a desktop app, `herdr-app`, which runs its terminals in
herdr-core, driven by the `hc` CLI. An agent running inside the app has no `herdr` server to talk
to, so before 1.0.13 every Herdr path in JDI found nothing there: `delegation.transport: auto`
silently ran natively, `herdr` announced a failed check, and `/jdi:herd` stopped at its first
check.

This document records how JDI detects which Herdr surface it runs in, how every Herdr operation
maps onto each surface, where the app keeps worktrees, and which constraints and decisions differ
between the two. The operations stay defined in `reference/herdr.md`. The transport rules stay in
`reference/delegation.md` and `docs/delegation-transport-architecture.md`, which this document
extends rather than replaces.

## Two surfaces

| | TUI | App |
|---|---|---|
| Layout CLI | `herdr workspace`, `herdr tab`, `herdr pane` | `herdr-app do space.new`, `tab.new`, `pane.split`, `pane.close`, `pane.focus`, `space.close`, `space.select`; `herdr-app ls`, `herdr-app status` |
| Agents and terminals | `herdr agent start`, `prompt`, `wait`, `get`, `read` | `hc send`, `hc wait`, `hc get`, `hc read`, `hc label`, `hc ls` |
| Worktrees | `herdr worktree create`, `open`, `remove` | no CLI; a shipped dialog mod runs `git worktree add` and then `space.new` |
| Inside-a-terminal signal | `HERDR_ENV=1`, `HERDR_SOCKET_PATH`, `HERDR_PANE_ID` | `HC_TERMINAL_ID`, `HC_TERMINAL_SOCKET`, `HC_SCOPE` |
| Sessions | `herdr --session <name>` | `HC_SESSION` selects a named core; `HERDR_APP_HOME` selects the app home, and with it the window |
| Agent manuals | `herdr --skill` | `herdr-app --skill`, `hc --skill`, `herdr-app commands`, the installed `AGENTS.md` in the app home |

The app splits what the TUI does in one binary. `herdr-app` changes what the person sees: spaces,
tabs and panes. `hc` starts, reads, messages, waits on and cleans up terminals, whether or not a
window shows them. A terminal started with `hc` appears in the window only when it carries the
labels `herdr.space=<id>` (and optionally `herdr.tab=<id>`). JDI starts every app terminal through
`herdr-app do` and uses `hc` only to label, wait on, read and message it (D4, P9).

### Why variants, not a second transport

The contract JDI relies on is the same on both surfaces: a worker runs as its CLI's interactive
agent in a place the user can see and answer, the Butler waits on a lifecycle state, the result
arrives through a file, and every pane JDI opened is closed on every exit. Only the commands that
carry out each step differ.

So JDI keeps one set of named operations, H1 to H9, and gives each operation a TUI variant and an
app variant (D-struct). The callers (`reference/delegation.md`, the step-0 line in nine commands,
`commands/herd.md`) keep calling operations by name and never learn which surface ran them. This
keeps `delegation.transport` meaning what it meant before, keeps the herd's "validate, never
repair" rule, and keeps every surface-specific command inside `reference/herdr.md`, where
`HerdrConfinementTest` confines `herdr`, `HERDR_*`, `herdr-app`, `hc`, `HC_*` and the app's layout
actions.

## Detection

H1 resolves the surface once, at step 0, under the same conditions it ran before: `auto` or
`herdr` for role delegation, and always for `/jdi:herd`. Under `native`, or with no `delegation`
key, nothing is probed for role delegation, exactly as before. The answer is `tui`, `app` or
`none`, with the first failed check and what it returned. No role re-probes.

### The checks

**TUI**, unchanged, in order:

1. `HERDR_ENV` is `1`.
2. The binary resolves: `$HERDR_BIN_PATH`, else `herdr` on `PATH`.
3. `herdr status` reports `running` and `compatible: yes`, and `HERDR_SOCKET_PATH`, when set, is an
   existing socket.

**App**, in order:

1. `HC_TERMINAL_ID` is set and not empty.
2. `hc` and `herdr-app` resolve on `PATH`.
3. `HC_TERMINAL_SOCKET` is an existing socket: `test -S "$HC_TERMINAL_SOCKET"`. This check runs
   **before any `hc` command**, for the reason in *Safety* below.
4. `hc get "$HC_TERMINAL_ID" --json` succeeds, and its `labels` carry `herdr.space`. A terminal
   started with `hc` from a plain shell also has an `HC_TERMINAL_ID`, but no window shows it, so
   without this label there is no space for JDI to work in. Requiring JSON with `labels` also
   rejects a foreign `hc` on `PATH`.
5. The window check (D9, P6). `herdr-app status` must exit 0 and its stdout must parse as JSON with
   no top-level `error` key. On success it prints JSON carrying an `errors` list (usually `[]`);
   that list is recorded, not treated as a failure. On failure it may print `{"error": …}`, but
   with no window at all it prints nothing on stdout, exits 2 and writes plain text, not JSON, on
   stderr (probe A11). So a non-zero exit, output that is not JSON, or a top-level `error` each
   fail the check. The layout commands need a running window, so a core with no window is not
   enough.

There is no app counterpart to the TUI's `compatible: yes`. The versions are recorded
(`herdr-app --version`, `hc --version`), not compared.

### The matrix

| `HERDR_ENV=1` | `HC_TERMINAL_ID` set | Result under `herdr.surface: auto` |
|---|---|---|
| no | no | `none`. Silent under `delegation.transport: auto`, as before |
| yes | no | `tui`: the TUI checks decide |
| no | yes | `app`: the app checks decide |
| yes | yes | nested: the innermost surface wins (below) |

### The nested case: the innermost surface wins

Environment flows inward. A TUI started from a shell in an app terminal inherits `HC_*`, and its
panes carry both sets of variables (probe A10). An app core started from a TUI pane could likewise
pass `HERDR_*` to its terminals, because hc terminals inherit the core's environment. Both
variable sets present therefore says only that one surface runs inside the other, not which one
this session is in.

The rule is that the innermost surface wins, because that is the one whose pane the user is
looking at and whose server will accept JDI's commands. The observation that settles it is
read-only: when the app checks up to 3 pass, read `hc get "$HC_TERMINAL_ID" --json`. If its
`foreground.argv` is the `herdr` TUI, the app terminal is hosting a TUI and this session is inside
the TUI: the answer is `tui`. Otherwise the session runs directly in the app terminal, and the
answer is `app`. A10 found the observation conclusive in the one nesting it could build.

When it is not conclusive (D2, refined by P4): if app check 2 or 3 fails, the app is unreachable
and the answer is `tui` with no note. Only when `hc get` fails or shows no `foreground` is the case
inconclusive; then the Butler says so once and uses the TUI, which is unchanged behaviour for
existing users.

### The override

`herdr.surface: auto | app | tui` (D1), usually set in `.jdi/config.local.yml` because the surface
is a fact about the machine. `auto` runs the matrix above. `app` and `tui` run only that surface's
checks and report its first failure. A pinned surface never falls to the other one: delegation
degrades to `native` and the herd stops (P7). An invalid value is announced once, only when H1
runs, and treated as `auto`. The key only picks *which* Herdr: whether Herdr is used at all for
role delegation stays `delegation.transport` (`native` is off), and `/jdi:herd` runs only when the
user invokes it. So there is no `off` value and no second way to say off.

### Safety

Detection observes and never starts anything, the same "detect, never repair" rule as before.

- **Check the socket before any `hc` command.** `hc` connects to the core its environment names,
  and a session name with no core behind it auto-starts that core (observed in the probe setup).
  `test -S "$HC_TERMINAL_SOCKET"` first means a stale or missing core is reported, not created.
- **Never construct `HC_SESSION`, `HC_SOCKET` or `HERDR_APP_HOME`.** JDI never sets, exports,
  guesses or hardcodes them. A value JDI invented would either start a new core or address a
  different window.
- **Never launch bare `herdr-app` or bare `hc`.** With no arguments `herdr-app` opens or raises the
  window. Detection uses only `herdr-app status` and `herdr-app ls`, which talk to the running
  window, and `herdr-app commands`, which needs no window.
- **Never use `hc server` as a probe.** The hc manual states that `hc server status` never starts a
  core on Windows, which does not promise the same elsewhere. Never stop, restart or update the
  user's core.

## Sessions and homes

**Inherit, never set.** A terminal inherits its core's environment (probes A10, A15). In a
terminal of a named session, `HC_SESSION` and `HERDR_APP_HOME` are already present; in a terminal
of the default window, neither is. Either way, every `hc` and `herdr-app` command JDI runs from the
Butler's shell reaches the core and the window the Butler is in, without JDI passing anything.

Consequences:

- JDI writes no session name, socket path or home into a command, a manifest, a config value or a
  document.
- Paths that depend on the home are resolved at run time as `${HERDR_APP_HOME:-~/.config/herdr-app}`,
  never written as a fixed path.
- The run manifest records the surface and its identifiers (space, tab, pane, terminal), never
  session names or home paths (P8).

## Operation map

Each row is one named operation in `reference/herdr.md`. The app column is the variant as built,
with the decision or probe behind it.

| Operation | TUI | App |
|---|---|---|
| H1 Detect | `HERDR_ENV`, binary, `herdr status` | the app checks above |
| H2 Check the kind | the kind is on `herdr agent`'s `kinds:` line; `command -v <kind>`; `herdr integration status` | `command -v <kind>` only, in the Butler's shell, and its **absolute path** goes into the argv; an alias or function fails H2 (P1). The app has no kinds list and no integration status: an agent has a status only if its program reports it (OSC 7501). Claude and opencode report it; a kind that never reports is rejected at readiness (D7). Codex needs `--no-daemon` in `harnesses.codex.args` (D8) |
| H3 Names, collision check | `herdr agent list` | `hc ls --json --label jdi.agent=<name>` (D5) |
| H3 Manifest identifiers | `HERDR_WORKSPACE_ID`, `HERDR_TAB_ID`, `HERDR_PANE_ID` | `herdr.space` and `herdr.tab` from the labels in `hc get "$HC_TERMINAL_ID" --json`; the Butler's pane is the `herdr-app ls` entry whose `terminal` equals `$HC_TERMINAL_ID`, which has the same ID form (A16). `HC_TERMINAL_ID` is not a pane ID. Both surfaces record `"surface"` (P8). The app object records no status: it is written before the readiness wait, and a worker that reports none is rejected there (D7) |
| H4 Choose a direction | `herdr pane layout` | always `right` (D10) |
| H4 Spawn line and pane | `printf … && herdr pane split --current --direction <d> --cwd <root> [--env …] --no-focus` | `printf … && herdr-app do pane.split --pane <butler pane> --direction right --argv '[…]'`, which prints `{pane, terminal}`. The split takes no folder, env or focus option, so the argv is `sh -c 'cd -- "$1" && shift && exec "$@"' jdi-worker <worktree root>` (P2, A14), then the `env KEY=VALUE …` prefix (D3, A6), then the kind's absolute path (P1). The split moves focus (A13), so the same command ends `&& herdr-app do pane.focus --pane <butler pane>` (P3) |
| H4 Start the agent | `herdr agent start <name> --kind <kind> --pane <id> --timeout 120000` | the agent is the split's `argv`. Then `hc label <terminal> jdi.agent=<agent name>` (D5), the run files, and a readiness `hc wait <terminal> --timeout 120`. Only `status: idle` is ready; anything else, including a timeout with no status, is not ready: H8 and the native rung (D7) |
| H5 Prompt and wait | `herdr agent prompt … --wait --timeout 300000`, then `herdr agent wait` | `hc send <terminal> "<short prompt>" --if idle --wait --timeout 300` (D6), then `hc wait <terminal> --timeout 300`. **hc timeouts are seconds, not milliseconds** |
| H5 States | `working`, `blocked`, `idle`, `done`, `unknown` | `working`, `blocked`, `idle`, `done`, `error`; a program that reports nothing has no status. `reason: timeout` is a check-in on stdout with exit 0 (A5). `reason: message` ends a wait when the Butler itself receives a message. `not_started` from `send --wait` is the counterpart of `agent_prompt_stalled`. If a status disappears mid-run, each check-in also looks for `result.json` (P10). Exit codes: 3 not found, 9 blocked, 10 status mismatch, 11 finished |
| H6 Inspect | `herdr agent get`, `agent explain`, `agent read --source …` | `hc get <terminal>` (a blocked status may carry `kind`: permission, question or auth) and `hc read <terminal> --lines 80`. While a terminal is blocked or working, history reads return only the screen. Focus on a yes: `herdr-app do agent.focus --terminal <t>`. A `needs_input` answer is sent only after `hc get` shows `idle` (then `--if idle`) or `done` (then a plain send, since `--if` cannot target `done` and a dialog is never `done`); anything else types nothing (R6) |
| H6 Never answer a dialog | never `send-keys` | never `hc keys`, never `hc send --force`, never `hc interrupt` (P9). `hc send` refuses a blocked terminal with exit 9 (A4), the counterpart of `agent_blocked`; `--if idle` extends that refusal to a terminal with no status, such as one showing a start-up dialog |
| H7 Validate | unchanged | unchanged. The result still arrives through the run directory, which a worker on the app can write (A12) |
| H8 Close | `herdr pane close <pane>`; `herdr tab close <tab>` | `herdr-app do pane.close --pane <pane>`, which ends its terminal; `herdr-app do tab.close --id <tab> --confirmed true`. A `pane.split --argv` terminal whose program exited is already finished and its pane removed, so exit 1 with `{"error": "no pane …"}` or `{"error": "no tab …"}` on stdout means "already gone" (A7) |
| Waves, the tab | `herdr tab create --workspace … --cwd … [--env …] --no-focus`, then `herdr tab rename` | `herdr-app do tab.new --name jdi-wave-<first run id> --space <space> --folder <root> --argv '[…]' --focus false`, which prints `{space, tab, terminal}` (A1). The name is given at creation, so there is no rename; `--folder` replaces the `sh` wrapper. The app runs the argv in an interactive shell that stays live after the agent exits, so the tab stays open until H8 closes it; closing its last pane closes the tab with it (UAT, herdr-app 0.1.16), so H8's `tab.close` then returns the harmless `no tab` error (A7). Later workers split a live pane of the wave tab (D4) |
| Waves, the wait | `herdr agent wait <name> --timeout 30000` per worker | `hc wait <terminal> --timeout 30` per worker |
| H9 Create a worktree | `herdr worktree create --cwd … --path … --branch … --base … --label … --no-focus` | `git worktree add -b <scratch branch> <path> origin/<default>` only, at herd step 6 (P5). The space comes at step 8, after `herd.seed`: `herdr-app do space.new --name '<label>' --folder <path> --tab <name> --argv '[…]' --focus false`, which prints `{space, tab, terminal}` (A8). The name is always single-quoted, with each `'` written as `'\''`, so a `'`, `$` or backtick arrives literally (A17), then H4b's label and readiness wait |
| H9 Hand it the work | `herdr agent prompt <name> '<invocation>'` | after the readiness wait reports `status: idle`, `hc send <terminal> '<invocation>' --if idle` (D6). Never `space.new --task`. On both surfaces the invocation is one shell argument, single-quoted, with each `'` written as `'\''`, so a `'`, `$` or backtick in a task arrives literally (M2) |
| H9 Reattach | `herdr worktree open` | find the space in `herdr-app ls` whose folder is inside the worktree and `herdr-app do space.select --id <space>`; otherwise `herdr-app do space.new --folder <path> --focus false` |
| H9 Watch | `herdr agent get <name>` | `hc get <terminal>`, `hc read <terminal> --lines 80`. In the window, a space's and a tab's status is its most urgent agent's (blocked, then done, then working, then idle) |
| H9 Cleanup | `herdr worktree remove --workspace <id> [--force]` | after JDI's plan-file check, `herdr-app do space.close --id <space> --confirmed true`, then `git -C <main checkout> worktree remove [--force] <path>`. Terminals first, then the folder, as the app's own dialog does it |
| H9 List | `git worktree list` | `git worktree list --porcelain` |
| H9 Herd record | the same record, `<git-common-dir>/jdi/herds/<herd-id>.json`; herd step 6 appends each issue's entry and fills `workspace_id`, `tab_id`, `pane_id` and `agent_name` | the same record, `<git-common-dir>/jdi/herds/<herd-id>.json`; step 6 appends the entry with the worktree only, and step 8 fills `space_id`, `tab_id`, `pane_id`, `terminal_id` and `agent_name` |
| H9 Cleanup from the record | the entry in `herdr worktree list --cwd <main checkout>` whose `path` equals the record's `worktree`, and its `open_workspace_id` (absent or `null` means no open workspace, G1); busy from `herdr workspace get <workspace_id>`'s `agent_status`; then the removal R2 confirmed, `herdr worktree remove --workspace <workspace_id> [--force]`, which deletes no branch | the `herdr-app ls` space whose `folder`, resolved with `pwd -P`, is the record's `worktree` or inside it (G3); busy from the `status` of every terminal in `hc ls --json --label herdr.space=<space>` (G2; no per-terminal `hc get` needed); then `herdr-app do space.close --id <space> --confirmed true`, then `git -C <main checkout> worktree remove [--force] <path>` |

## The app's worktree layout

The app has no worktree CLI. Its shipped `worktree` mod (in the app home, `mods/worktree/main.js`)
is the reference for where checkouts go, and JDI's app variant of H9 follows it so a herd worktree
lands where the app's own New worktree dialog would put it (D-wt: a documented recipe, not a
shipped script).

- **The path** is `<root>/<repo>/<slug(branch)>`.
- **`<root>`** is `worktrees.directory` from `settings.json` in the app home
  (`${HERDR_APP_HOME:-~/.config/herdr-app}/settings.json`), default `~/.herdr/worktrees`. A
  leading `~` expands to the home of the space's machine. Any other relative value is an error, and
  trailing slashes are dropped. The app does not read the TUI's `[worktrees] directory` in its
  `config.toml`, so the two surfaces can disagree, and each variant reads its own setting.
- **`<repo>`** is the basename of `git rev-parse --path-format=absolute --git-common-dir`, with a
  trailing `/.git` removed. It is the same from the main checkout and from any linked worktree.
- **`slug()`** normalises the branch to Unicode NFC, replaces each run of characters outside
  letters, marks, digits, `.`, `_` and `-` with `-`, and trims `-` from both ends. A branch with
  nothing left becomes `branch-` plus an 8-digit hex FNV-1a hash of the name.
- **The herd keeps its own folder name.** H9 names the folder after the herd's `<name>`, not after
  the scratch branch, so the folder shows the issue. `<name>` matches `[a-z][a-z0-9_-]{0,31}`, which
  `slug()` leaves unchanged, so the folder is exactly where the dialog would put a branch of that
  name.
- **The base is `origin/<default>`.** The dialog branches a new branch from the current checkout's
  `HEAD`. A herd branches from `origin/<default>`, as `commands/herd.md` step 4 and H9 require, so
  uncommitted or unpushed work in the Butler's checkout never reaches a herd worktree.
- **The space comes later.** H9 on the app creates only the worktree; the space and its agent are
  opened at herd step 8, after `herd.seed` has run in the folder (P5). A8 confirmed that a space
  can be opened on an existing worktree folder.
- **Nesting is git-only.** The sidebar nests a space under its repository when the space's first
  terminal is in a linked worktree and a space on that repository's main checkout is shown. The
  space's name plays no part (A8, A9). The dialog leaves spaces unnamed so the name follows the
  folder, but the herd names each space after its issue and it still nests.
- **Removal order.** The dialog closes the space first and then runs `git worktree remove`, forced
  when the tree is dirty or has submodules. JDI keeps that order, and its own rule before it: a
  worktree whose plan folder holds uncommitted files is never removed without the user's explicit
  yes.

## The herd record

`/jdi:herd` writes down what it made, so that `/jdi:herd --cleanup [<herd-id>]` can later remove
exactly that and nothing else. The rules are defined only in `reference/herdr.md`, under H9's
*The herd record* and *Cleanup from the herd record*; `commands/herd.md` calls them by name and
never restates them (C11). This section records the design and the probes behind it.

### Where it lives and how it is written

- **One file per herd** at `<git-common-dir>/jdi/herds/<herd-id>.json`, where `<git-common-dir>` is
  `git rev-parse --path-format=absolute --git-common-dir` (C1). The flag is `--git-common-dir`,
  not `--absolute-git-dir`, which in a linked worktree names that worktree's own directory. Every
  linked worktree of a repository shares the common directory, so the Butler of any herd worktree, and the main checkout,
  see the same record. The relative part, `jdi/herds/<herd-id>.json`, sits inside git's own
  directory, so the record is never committed.
- **Written whole, never edited in place.** Each write goes to `<dir>/.<herd-id>.json.tmp` and is
  then moved over the record with `mv -f`, so a reader never sees half a file. The record is created
  on the first worktree that succeeds, never before.
- **The same shape on both surfaces.** A key that does not apply to the surface is `null`. The
  `worktree` is stored as `git worktree list --porcelain` prints it.
- **An untracked task has a `task`.** `issue` is `null` for an untracked task, and `task` holds
  the task's text as handed to the agent, without the herd clause; for an issue, `task` is `null`.
  `task` is additive, so `schema` stays `1`, and a reader treats a missing `task` as `null`.
- **No session and no app home.** The record follows *Inherit, never set*: it names neither, and
  which surface is reachable is observed at cleanup, never recorded.
- **`creating`, then `handed_off`.** `state` is `creating` until herd step 10 and `handed_off`
  after (C9). A cleanup with no herd ID skips a `creating` record, because its herd may still be
  running; given that herd's ID, it includes the record and flags it.
- **A failed write costs one sentence.** A record that cannot be written is reported once and the
  herd continues; step 11's manual commands still cover that herd (C10).

### How cleanup uses it

- **A checked herd ID.** The ID must match `^[0-9]{8}T[0-9]{6}$` before anything is read, because
  JDI never builds a path from an unchecked argument (C2). Issue IDs or `--kind` beside `--cleanup`
  stop the run.
- **No record, no guess.** With no record, or an unknown ID, cleanup says so, removes nothing, and
  points at `git worktree list` and step 11's manual commands. It never guesses from folder names
  (C6).
- **Found by path.** Every space, workspace and terminal is re-found from the entry's worktree
  path, never by a recorded ID alone, because app terminal IDs and TUI workspace IDs are reused once
  their owner is gone (C3). The recorded IDs are a description, not an address. How each surface
  finds them is in the *Operation map* rows *H9 Herd record* and *H9 Cleanup from the record*.
- **The skips.** An entry is skipped when its agent is `working` or `blocked` (a reattached session
  counts as busy), when the worktree holds the session running the cleanup or its space or
  workspace is the Butler's own, and when the tree has uncommitted changes and was not seeded. When
  the record's surface is not reachable from here, the space or workspace is left alone and the
  worktree removal is still offered, marked "agent state unknown". A worktree that git lists as
  `prunable` keeps its entry, and the user is told to run `git worktree prune` (C5).
- **The plan-file guard and one question.** An entry whose plan folder holds uncommitted files
  leaves the batch and gets its own yes, with the plan commit offered. Everything else is shown as
  one list, and the user is asked once.
- **`--force` only for seeded worktrees.** `git -C <worktree> status --porcelain` runs on the whole
  tree. Anything it shows, in a worktree that `herd.seed` wrote into, is listed and then removed
  with `--force`; in a worktree that was not seeded, the entry is skipped for uncommitted changes.
- **The scratch branch.** Cleanup deletes only the recorded scratch branch, and only when its name
  is `jdi-herd-scratch-<herd-id>-<N>` for this herd, it still exists, it has no commits past its
  `base_commit`, and its worktree is gone (C4). Never any other branch. The scratch branch is left
  behind because `/jdi:do` and `/jdi:prep` start the real work on a branch of their own (`/jdi:do`
  with **T6** from `origin/<default>` at its step 2, `/jdi:prep` with
  `git switch -c <branch> origin/<default>`); neither renames the scratch branch, so it still
  points at its base. A merged `do` therefore leaves a worktree whose scratch branch has no commits
  of its own.
- **Record upkeep.** An entry is removed once its worktree is no longer in
  `git worktree list --porcelain`, and the file is deleted when the last entry goes (C5).
- **The report.** Removed, or skipped with the reason, per issue, plus the record's state (C7). An
  entry with a `null` issue, an untracked task, is reported by its `name` and its task text. A
  normal herd's own report names `/jdi:herd --cleanup <herd-id>` (C8).

### What the probes showed

Run on Linux with `herdr` 0.9.3, `herdr-app` 0.1.16, `hc` 0.1.21 and `git` 2.56.0, in a throwaway
session and app home through the isolation guard, with a nested throwaway TUI on a scratch clone.

- **R1, the TUI listing.** `herdr worktree list --cwd <main checkout>` gives each worktree's `path`
  byte for byte as `git worktree list --porcelain` prints it, and its `open_workspace_id`. Its
  `branch` is the worktree's current branch, so matching by `branch` would miss after `/jdi:prep`
  switches; matching by `path` does not. `herdr workspace get` carries `agent_status` as a
  top-level string. Neither command needed `--trust-repository`.
- **R2, TUI removal.** `herdr worktree remove --workspace <workspace_id>` removes the folder and
  closes the workspace but deletes **no branch**, and refuses a dirty tree without `--force`. The
  planned fallback (close the workspace, then `git worktree remove`) was not needed.
- **R3, a closed workspace.** Its worktree is still listed, with **no** `open_workspace_id` key at
  all rather than `null`. G1 amended the wording: absent or `null` means no open workspace.
- **R4, app agent state.** `hc ls --json --label herdr.space=<space>` carries each terminal's agent
  state as a `status` string (`idle`, `working`, `done`, …), absent when the terminal reports none;
  `state` there is the terminal's lifecycle (`live`). G2 pins `status` as the key to read, so no
  per-terminal `hc get` is needed. A known follow-up came out of the same probe: after a finished
  turn the status is `done`, and `hc send --if idle` refuses a `done` agent. R6 showed nothing
  JDI does clears `done`, so H6 answers a `done` worker with a plain send after checking its
  status (see the H6 row); cleanup sends nothing.
- **R5, git.** The porcelain prints a worktree's resolved path even when it was added through a
  symlink, while an app space keeps its `folder` in the form it was opened with. G3 amended the app
  match to resolve the folder with `pwd -P` first. A worktree whose folder was deleted is marked
  `prunable`. An untracked or modified file blocks a plain `git worktree remove` and shows in
  `git status --porcelain`; an ignored file does neither and goes with the worktree, so the one
  list says so.

Gate: passed after G1, G2 and G3. The TUI removal, the app listing as the busy source, C4 and C5
stand as planned.

## Constraints that differ on the app

### Environment

No app or hc CLI command takes an environment. `herdr-app do` has no env argument on `space.new`,
`tab.new` or `pane.split`, and `hc run` has no `--env`. The hc API's `terminal.run` accepts an
`env` map, reachable only through `hc connect`, which JDI does not use.

A terminal also does not inherit the Butler's environment. It gets the core's environment, so a
variable exported only in the Butler's shell is absent, and its `PATH` is whatever the core's
launcher had, in a different order from the Butler's (A15). Two decisions follow:

- `harnesses.<kind>.env` reaches the worker as an `env KEY=VALUE … <kind> …` prefix in its argv,
  with every path expanded first (D3). A6 confirmed the worker sees the value and still reports its
  status through `env` and the `sh` wrapper's `exec`. On the TUI the same key is still passed with
  `--env`.
- The kind is resolved in the Butler's shell and passed as an absolute path, so the worker starts
  the same binary the Butler checked, whatever the core's `PATH` (P1).

### Lifetime

- JDI never starts a worker with `hc run` (D4). A terminal started that way is a child of the
  terminal that ran it and ends with it, hc types notes about it into its parent's input unless it
  was started with `--no-notify`, and it has no pane of its own. JDI's contract is a pane the user
  can answer, so workers come from `pane.split` and `tab.new`, and herd agents from `space.new`.
  Terminals created that way have `parent: null` and `die_with_parent: false` (A16), so they are
  never the requester's children, and a herd Butler outlives the session that started the herd.
- `pane.split --argv X`: when X exits, its terminal is finished and its pane is removed. This
  matches H8's "the pane is gone" outcome.
- `tab.new --argv X`: the app wraps X in an interactive shell, so when X exits the terminal stays
  live with a shell and the tab and pane stay open (A1). H8 closes the wave tab. In UAT, closing its
  last pane closes the tab with it, so H8's `tab.close` usually finds `no tab`, which is harmless.
- `space.new --argv X`: when X exits, the terminal falls back to a live shell. A herd space
  therefore outlives its agent, as a TUI workspace does.
- `pane.close` returns before the terminal has finished; a `hc get` a moment later shows it
  `finished` (A7).

### Names

`hc run --name` accepts 1 to 32 characters of `a-z`, `0-9`, `-` and `_`, but terminals the app
creates (`space.new`, `tab.new`, `pane.split`) are unnamed, and hc has no rename command. So JDI
addresses each worker and herd agent by the terminal ID the creating command printed, labels it
`jdi.agent=<name>` with `hc label`, and finds it again with `hc ls --label` (D5, A16). A space name
passed to `space.new --name` arrives literally, with no shell expansion of `'`, `$` or backticks
(A17).

### The first message

`space.new --argv X --task T` passes T to X as a command-line argument, not as typed input (`cat`
received the task as a filename). For an agent CLI, T is therefore its positional argument. That
is a prompt for some CLIs and something else for others, so `--task` is not a kind-neutral way to
hand over the work, and the app does not wait for the agent to be ready before passing it. JDI
never uses `--task`; it types the first message with `hc send … --if idle` once the agent is ready
(D6).

### Dialogs and states

hc timeouts are in seconds, with a default of 180. H5's `--timeout 300000` becomes `--timeout 300`.
hc has no `unknown` state. A program that reports no status has none, and `hc wait` on it waits
until its timeout, so a worker kind that does not report status cannot be told apart from a stuck
one.

The same holds for a start-up dialog. Claude and Codex open a folder-trust dialog when they start
in a folder they have not seen, and Codex then opens a "Hooks need review" dialog. While either is
open, `hc get` shows `status: null`, not `blocked`, and `hc wait` returns `reason: timeout` (A2).
`hc send` refuses only a terminal whose status is `blocked`; a terminal with no status gets the
text typed and Enter pressed (A4). A herd worktree is a new folder, so the herd can meet this
dialog, though not always: in UAT a linked worktree takes Claude's folder trust from its main checkout,
so a herd from a trusted repository started at `idle`, and the dialog appeared only when the main
checkout was untrusted. A CLI that does not carry trust over would show it every time. That is why the probe gate amended D6 and D7: JDI types only into an agent whose
readiness wait ended in `status: idle`, always with `--if idle`, and treats any other readiness
result as "not ready". Answering the dialog stays the user's job; JDI never does it.

## Decisions

Settled for issue #36. Where the probe gate amended a decision, the amended text is recorded, with
what it replaced and why.

### The user's decisions

- **D1, the key.** `herdr.surface: auto | app | tui`, default `auto`, usually in
  `config.local.yml`. Whether Herdr is used at all stays `delegation.transport` (`native` is off),
  so there is no `off` value. It passes the five-question test in `docs/config-key-lifecycle.md`.
- **D-wt, app worktrees.** A documented recipe in `reference/herdr.md` (H9's app variant), not a
  shipped script.
- **D-struct, one set of operations.** H1 to H9 each have a TUI and an app variant; every
  `herdr-app`, `hc`, `HC_*` and `HERDR_APP_HOME` string is confined to `reference/herdr.md`; TUI
  behaviour is unchanged.

### The Butler's defaults

- **D2, an inconclusive nested check.** Say so once, then use the TUI. Refined by P4.
- **D3, worker environment.** `harnesses.<kind>.env` goes into the argv as an
  `env KEY=VALUE … <kind> …` prefix, every path expanded first.
- **D4, how a worker starts.** A single worker is a `pane.split --argv` beside the Butler. In a
  wave, the first worker is a `tab.new --argv` and the rest are `pane.split --argv` in that tab.
  Never `hc run`.
- **D5, naming.** Workers and herd agents are addressed by terminal ID, labelled
  `jdi.agent=<name>` with `hc label`, and found with `hc ls --label`.
- **D6, typing into an agent (amended after the probe gate).** On the app JDI types into an agent
  only after a readiness `hc wait` reports `status: idle`, and always with `hc send … --if idle`,
  so the app refuses to type into anything that is not idle. This covers H5's short prompt, H6's
  `needs_input` answer and the herd handoff. Never `--task`. *Was:* `hc wait`, then `hc send`.
  *Why:* A2 and A4 showed that Claude's and Codex's trust and hook-review dialogs report no status
  rather than `blocked`, so `hc wait` times out and a plain `hc send` would type into the dialog;
  a herd worktree is a new folder, which can open one (UAT later showed that Claude takes a linked
  worktree's trust from its main checkout, so it does so only when that checkout is untrusted).
- **D7, kinds without a status (amended after the probe gate).** Reject at readiness: if the
  readiness wait does not end with `status: idle`, the agent is not ready. JDI types nothing, says
  why (no status, possibly a dialog in its pane that is the user's to answer), and treats it like
  the TUI's `agent_not_ready`: delegation closes the pane (H8) and falls to the native rung; the
  herd reports that issue as blocked at startup and leaves its space for the user. *Was:* accept
  such a kind with a one-time note that `blocked` and `done` will never appear. *Why:* without a
  status there is no safe moment to type.
- **D8, Codex.** Codex's `--no-daemon` belongs in `harnesses.codex.args`. JDI adds nothing, but
  notes once when it is missing. Codex accepts it as an argv element.
- **D9, the window requirement.** App H1 requires `herdr-app status` to succeed; a core with no
  window is not enough.
- **D10, the split direction.** Always `right` on the app, which reports no pane geometry JDI
  reads.

### The Planner's decisions

- **P1, absolute kind path.** App H2 resolves the kind with `command -v <kind>` in the Butler's
  shell and puts the absolute path in the argv, because terminals get the core's `PATH`. A
  non-absolute answer (an alias or a function) fails H2 on the app with that reason.
- **P2, the worker's folder.** `pane.split` has no folder option and starts in the Butler
  terminal's current folder, which can differ from the repository root. So a split's argv starts
  with `sh -c 'cd -- "$1" && shift && exec "$@"' jdi-worker <worktree root>`. `tab.new` and
  `space.new` take `--folder` and need no wrapper.
- **P3, focus.** `pane.split` moves focus to the new pane (A13), so H4 appends
  `&& herdr-app do pane.focus --pane <butler pane>` to the same command.
- **P4, refining D2.** If app check 2 or 3 fails, the app is unreachable: the answer is `tui`, with
  no note. "Inconclusive" means only that `hc get` failed or showed no `foreground`; then say so
  once and use the TUI.
- **P5, the herd on the app.** H9 creates only the worktree at herd step 6. The space and its agent
  are created by H4b on the app at step 8, after `herd.seed` (step 7).
- **P6, the window check (refined by A11).** `herdr-app status` exits 0 and its stdout parses as
  JSON with no top-level `error` key; its `errors` list is recorded, not a failure. *Was:* "prints
  JSON with no `error`", on the reading that it returns `{"error": …}` on failure. *Why:* with no
  window it exits 2 with plain text on stderr, not JSON, so the exit code and the parse are part of
  the check.
- **P7, a pinned surface.** A pinned `app` or `tui` never falls to the other surface: delegation
  degrades to `native` and the herd stops. An invalid value is announced once, only when H1 runs,
  and treated as `auto`.
- **P8, the manifest.** The run manifest's `herdr` object gains `"surface"` on both surfaces. The
  change is additive, and the schema stays 1.
- **P9, what JDI runs.** JDI closes only through `pane.close`, `tab.close` and `space.close`. It
  never runs `hc kill`, `hc rm`, `hc keys`, `hc interrupt` or `hc send --force`, and never bare
  `hc` or bare `herdr-app`.
- **P10, a status that disappears (narrowed by D7).** A kind that never reports status is rejected
  at readiness. If a worker's status disappears mid-run, every wait check-in also checks whether
  `result.json` exists, and goes to H7 if it does. *Was:* this rule also covered kinds that never
  report status. *Why:* D7 now rejects those before any prompt is sent.
- **P11, probe isolation.** Live probes run in a throwaway session and app home, through a guard
  wrapper that unsets the inherited terminal variables (see *App-side live probes*).

## App-side live probes

Probes run only in a **throwaway** session and a throwaway app home, never in the user's own
window or core, and every probe command goes through an isolation guard (P11). The guard is a
small POSIX `sh` wrapper kept in a scratch directory, never in the repository. It:

1. refuses, writing nothing to stdout, unless the probe variables naming the throwaway session and
   the throwaway home are both set;
2. `unset`s every inherited terminal variable, `HC_TERMINAL_ID`, `HC_TERMINAL_SOCKET`, `HC_SCOPE`,
   `HC_SOCKET`, `HERDR_ENV`, `HERDR_SOCKET_PATH`, `HERDR_PANE_ID`, `HERDR_TAB_ID` and
   `HERDR_WORKSPACE_ID`, because an inherited socket can otherwise address the user's real core;
3. exports the throwaway `HC_SESSION` and `HERDR_APP_HOME`;
4. `exec`s the probe command.

Before the throwaway window is launched, `herdr-app status` through the guard must fail and
`hc ls --json` must list no terminals. "Inside" probes run as scripts started in a throwaway space
on a scratch clone, writing their output to scratch files. Afterwards every space and tab the
probes created is closed, the throwaway window and core are stopped through the guard, the scratch
directory and the throwaway home are removed, and the user's own `hc ls --json` count is checked to
be unchanged. A probe that contradicts this document or `reference/herdr.md` stops the work until
the text is fixed.

### The probes

- **A1, `tab.new` output.** What `herdr-app do tab.new --name … --folder … --argv … --focus false`
  prints, and which folder its terminal starts in.
- **A2, readiness.** For `claude`, `opencode` and `codex` started by `pane.split --argv` through the
  `sh` wrapper: does `hc wait <terminal>` return once the agent is ready for input, and what does
  `hc get` show?
- **A3, status reporting.** Which kinds report OSC 7501 status under hc through the `sh` wrapper
  (`hc get` shows a `status` with `app` and `state`), and whether `blocked` appears for an approval
  dialog. Record any kind that reports nothing.
- **A4, send and wait.** `hc send <terminal> "<text>" --wait --timeout 30` on an idle agent, on a
  blocked agent (expect a refusal and exit 9, no input typed), and on an agent that never starts
  the turn (`not_started`). Record the JSON and the exit codes.
- **A5, timeouts.** `hc wait <terminal> --timeout 5` on a working agent: the `reason`, the stream
  it arrives on, and the exit code.
- **A6, environment.** An `env KEY=VALUE <kind> …` prefix in `argv`: does the worker see the
  value, and does the terminal still report the agent's status?
- **A7, close.** `herdr-app do pane.close --pane <id>` ends the agent, and `hc ls` no longer lists
  it. `pane.close` and `tab.close` on a pane or tab that is already gone: the exact error JSON.
- **A8, the herd path.** `git worktree add -b <scratch> <root>/<repo>/<name> origin/<default>`,
  then `space.new --name "<label>" --folder <path> --tab <name> --argv … --focus false`: the space
  keeps its name, nests under the main checkout's space when that is shown, and its agent is
  addressable by the printed terminal ID.
- **A9, nesting.** The same space with and without `--name`, to confirm that only git decides
  nesting.
- **A10, the nested surface.** A TUI started inside an app terminal: confirm that both variable
  sets are present in the TUI's panes, and that `hc get "$HC_TERMINAL_ID"` shows the TUI as the
  foreground program.
- **A11, no window.** With the app window closed and the core still running: what
  `herdr-app status` returns, so the window check fails with a clear reason, and whether closing
  the window leaves the core running.
- **A12, the worker's writes.** A worker started on the app can write the run directory under
  `git rev-parse --absolute-git-dir`, in the main checkout and in a linked worktree.
- **A13, focus.** Does `pane.split` change `focused_pane` in `herdr-app status`?
- **A14, the split folder.** The start folder of `pane.split --argv` with and without the `sh`
  wrapper, read from `foreground.cwd` in `hc get`, with the Butler's space started in a parent of
  the repository.
- **A15, the core's environment.** The `PATH` a terminal gets, whether `command -v <kind>` resolves
  there, and that a variable exported only in the Butler's shell is absent.
- **A16, IDs and labels.** Whether `herdr-app ls`'s `terminal` has the same form as
  `HC_TERMINAL_ID`; `hc label` and `hc ls --label` on terminals the app created; and whether
  `parent`, `die_with_parent` and `notify` show that split, tab and space terminals are not the
  requester's children.
- **A17, argument forms.** `--argv '<json>'` and `--focus false` are accepted, and a `--name`
  containing `'`, `$` and a backtick arrives literally.

### Results

Run on Linux with `herdr` 0.9.3, `herdr-app` 0.1.16, `hc` 0.1.21, `opencode` 2.2.7 and `codex-cli`
0.169.0, plus the installed `claude`. The core keys its socket and its state folder by session
name, so a throwaway `HC_SESSION` alone isolates it, and the agent CLIs kept their real
configuration.

- **The gate stopped once, on D6 and D7.** A2 showed that Claude's and Codex's start-up dialogs
  (folder trust, and Codex's hook review) report `status: null`, not `blocked`, so `hc wait`
  times out; A4 showed that `hc send` types into a terminal with no status. A bare "wait, then
  send" would answer the dialog, which JDI must never do. The user amended D6 (wait for `idle`,
  then `hc send --if idle`) and D7 (reject at readiness); P6 was refined by A11 and P10 narrowed.
  The gate then passed.
- **Confirmed as designed.** A1 (`tab.new` prints `{space, tab, terminal}`, starts in `--folder`,
  does not move focus, and its shell stays live after the agent exits), A5 (a check-in timeout is
  JSON on stdout with exit 0), A6 (the `env` prefix and the `sh` wrapper keep status reporting),
  A8 and A9 (worktree first, space later, nesting decided by git alone), A10 (the nested
  observation is conclusive), A12 (the run directory is writable from a worker in the main
  checkout and in a linked worktree), A14 (without the wrapper a split starts in the Butler's
  folder; with it, in the repository), A15 (terminals get the core's environment and `PATH`), A16
  (the same terminal ID form in `herdr-app ls`; labels work on app terminals; `parent: null`) and
  A17 (the argument forms are accepted and names arrive literally).
- **Status by kind.** Claude reports `idle`, `working`, `done` and `blocked` (a question shows
  `kind: question`). opencode reports `idle` and `working`, and ends a turn as `idle`, never
  `done`. Codex reported nothing while its dialogs were open; whether it reports once ready is
  unobserved, because the probes left its dialogs unanswered.
- **Send.** On a blocked terminal `hc send` exits 9 with `{"error":{"kind":"blocked",…}}` on
  stderr and types nothing. `not_started` was not reproduced: on a program with no status the text
  was typed.
- **Close.** `pane.close` on a live pane gives `{"ok": true}` and the terminal finishes as
  `killed`, though it can still be `live` for a moment after the command returns. On a pane or tab
  already gone, `pane.close` and `tab.close` exit 1 with `{"error": "no pane …"}` or
  `{"error": "no tab …"}` on stdout.
- **Focus.** `pane.split` moves focus to the new pane, and `pane.focus --pane <butler pane>`
  restores it, which settled P3.
- **No window.** With the window closed, `herdr-app status` and `herdr-app ls` exit 2 with plain
  text on stderr and nothing on stdout, while the core keeps answering `hc`. On Linux the window is
  closed with `window.close`; `app.quit` is listed as macOS-only.
- **Not covered by a probe.** D8: `codex --no-daemon` is accepted as an argv element. D10:
  `--direction right` worked every time, and no geometry was available to contradict it. An agent
  CLI's own sandbox was not exercised by A12. Windows and macOS were not probed.

## Relationship to other documents

- `docs/delegation-transport-architecture.md` describes role delegation. Its "Capability
  detection" section is surface-neutral and points here for each surface's checks, and its
  "Configuration" section says where `harnesses.<kind>.env` goes on each surface.
- `reference/herdr.md` remains the only file that names Herdr commands and variables. The app
  variants of H1 to H9 live there, and `HerdrConfinementTest` confines `herdr-app`, `hc`, `HC_*`
  and the app's layout actions as it confines `herdr` and `HERDR_*`.
- `docs/config-key-lifecycle.md` is the procedure `herdr.surface` (D1) followed.
