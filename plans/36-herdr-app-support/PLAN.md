# Support the Herdr desktop app alongside the TUI

- Tracker: github
- Project: feature development
- Issue: #36
- Issue URL: https://github.com/dabit/just_do_it/issues/36
- Created: 2026-11-16
- Base commit: origin/herdr-role-delegation @ b06fbdbfc5ffa48fc2dff3633497e401b5254c19 (stacked on PR #31; origin/main is 31 commits ahead of this base)
- Summary: Detect whether JDI runs inside the Herdr app (herdr-app + hc) or the Herdr TUI, make it configurable, and route every Herdr operation (role delegation, /jdi:herd, worktrees) through the detected surface.
- Started: 2026-11-16
- TDD: on — proven 2026-11-16 with `python3 -m unittest discover -s tests -v`

## References

### Decisions (user, 2026-11-16)
- Config: `herdr.surface: auto | app | tui`; on/off stays `delegation.transport` (no `off` value).
- App worktrees: a documented recipe in `reference/herdr.md` (H9 app variant), not a shipped script.
- Stacked on PR #31; follow-up PR targets `herdr-role-delegation`.

### Past plans
- `plans/herdr-role-delegation/PLAN.md` (PR #31) — binding decisions: D1/D6 (`:85-91`, `:101-106`) Herdr only for a role on another CLI, `delegation.transport: native|auto|herdr`, default `native`, every failure falls to `native`; D8 (`:107-116`) result via a run directory, never a transcript; D9 (`:117-123`) JDI never answers a worker's dialog or sends keys (so never `hc keys` / `hc send --force`); D10 (`:124-129`) `/jdi:herd` validates and stops, delegation detects and falls back; D11 (`:136-153`) herd names `[a-z][a-z0-9_-]{0,31}`, worktree at `<dir>/<repo>/<name>`, scratch branches, plan-file guard on cleanup; D12 (`:154-157`) JDI adds only the model flag. Task 10 (live test with a probe gate) still pending.

### Docs
- `docs/herdr-surfaces-architecture.md` — **new (drafted for this plan)**: surfaces, detection matrix + nested case, sessions/homes, operation map, app worktree layout, app constraints, open decisions, app live-probe list (A1–A12).
- `docs/delegation-transport-architecture.md` — TUI-only today: "Capability detection" (`:64-82`), "Backend choice" (`:51-56`), env via `--env` (`:166-167`); "detect, never repair" (`:175-190`) carries over.
- `docs/config-key-lifecycle.md` — procedure for a new key: nine files (`:61-76`), three `reference/config.md` edits (`:80-86`), example shows a non-default (`:88-92`), init/help (`:94-114`), version bump (`:121-126`), the five-question test (`:320-333`).
- `docs/harness-adapter-architecture.md` — Herdr only at `:27`, `:247-248`; nothing surface-specific.

### Reference and commands
- `reference/herdr.md` — H1 detect (`:47-71`), H2 kinds (`:73-96`), H3 names (`:100-103`), H4 spawn (`:218-239`), H5 prompt/wait, H6 inspect, H8 close, waves (`:403-408`), H9 herd worktrees (`:448-530`). The only file allowed to name `herdr <sub>` / `HERDR_*` (enforced by `tests/test_delegation_transport.py:19-23`, `:76-93`).
- `reference/delegation.md` — transport choice (`:57-78`), rung 2 (`:104-107`), waves (`:131-135`), env "on the pane" (`:150-152`), rungs 4, 6-9 (`:255-270`). Calls operations by name only.
- `reference/config.md` — `delegation` (`:190-210`), `herd` (`:212-221`), defaults table (`:303-323`), notes (`:373-390`).
- `commands/herd.md` — H1/H2 (`:38-49`), H9 calls (`:98`, `:119-155`, `:223-288`), sidebar wording (`:272`).
- `commands/init.md:171-191` (transport question only when H1 passes), `commands/help.md:44`, `:166-178`, step 0 of the nine phase commands (e.g. `commands/prep.md:42-46`).
- `README.md:281-315`, `:365-374`; `AGENTS.md`; `CHANGELOG.md`; `jdi.config.example.yml:124-135`; version files `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json`.

### Tests that pin Herdr strings
- `tests/test_herdr_operations.py` (headings `:18-33`; TUI strings `:89-276`), `tests/test_herd.py` (`:79-83`, `:91-105`, `:128-142`), `tests/test_delegation_transport.py` (confinement `:19-23`, `:76-93`), `tests/test_step_zero_transport.py:17-27`, `tests/test_transport_docs.py:34-44`, `tests/test_config_schema.py` (`:27-102`, `:170-215`), `tests/test_enumerations.py:50-67`, `tests/jdi_files.py`.

### External sources (Herdr app; not in the repo)
- `herdr-app --skill`, `hc --skill`, `herdr-app commands`, `hc <cmd> --help`, `hc schema`.
- Installed guide `~/.config/herdr-app/AGENTS.md` (`:105-161` model, `:565-600` commands, `:720-735` settings incl. `worktrees.directory`, `:900-920` shipped `worktree` mod).
- Shipped worktree mod `~/.config/herdr-app/mods/worktree/main.js`: root from `settings.json` (`:16-24`), `slug()` (`:30-38`), repo name from `--git-common-dir` (`:115-121`), create/remove (`:201-245`); sidebar nesting `mods/spaces/main.js:298-315` (git-only; naming a space doesn't affect it).
- Versions observed: `herdr` 0.9.3, `herdr-app` 0.1.16, `hc` 0.1.21.

### TUI → app operation map (Researcher, verified read-only)
| TUI | App |
|---|---|
| H1: `HERDR_ENV`, `herdr status`, `HERDR_SOCKET_PATH` | `HC_TERMINAL_ID` set; `test -S "$HC_TERMINAL_SOCKET"` **before any `hc` call**; `hc get "$HC_TERMINAL_ID"` has label `herdr.space`; `herdr-app status` has no `error` |
| H2: kinds / `herdr integration status` | none: hc runs any program; status only if the program reports it |
| H3: `herdr agent list` | `hc ls --json` / `hc ls --label k=v` |
| H4: `herdr pane split … --cwd --env --no-focus` + `herdr agent start` | `herdr-app do pane.split --pane <p> --direction <d> --argv '[…]'` (no folder/env/focus args) |
| H5: `herdr agent prompt/wait` (ms) | `hc send <t> … --wait --timeout <s>`, `hc wait <t> --timeout <s>` (**seconds**; states idle/working/done/blocked/error, no `unknown`) |
| H6: `agent get/explain/read --source` | `hc get`, `hc read <t> --lines N`, `herdr-app do agent.focus --terminal <t>` |
| H8: `herdr pane close` / `tab close` | `herdr-app do pane.close --pane` / `tab.close --id --confirmed true`; or `hc kill` + `hc rm` |
| Waves: `herdr tab create` + `tab rename` | `herdr-app do tab.new --name --space --folder --argv --focus false` |
| H9: `herdr worktree create/open/remove` | no CLI: `git worktree add` to `<worktrees.directory>/<repo>/<slug>` + `herdr-app do space.new --name --folder --tab --argv --task --focus false`; open = select a space whose terminal cwd is inside the path, else `space.new`; remove = `space.close --confirmed true` then `git worktree remove`; list = `git worktree list --porcelain` |

### Live probe (Butler, throwaway `HC_SESSION=jdiprobe`, removed afterwards)
- `space.new` prints `{"space","tab","terminal"}`; `pane.split` prints `{"pane","terminal"}`; `herdr-app ls` maps terminal → pane.
- `pane.split` without argv starts in the split pane's folder.
- Terminals inherit the core's environment: under a named session they carry `HC_SESSION` and `HERDR_APP_HOME`; in a default app window neither is set.
- `space.new --argv X --task T` appends T as **an argument to X** (`cat hello-task`), not a typed message; when X exits, that space's terminal falls back to a shell (stays `live`).
- `pane.split --argv X`: when X exits the terminal is `finished` and its pane is removed from the layout.

## Implementation Plan

### Decisions

User (2026-11-16):
- **D1 (key).** `herdr.surface: auto | app | tui`, default `auto`, usually in `config.local.yml`. On/off stays `delegation.transport`; no `off` value. Passes the five-question test (`docs/config-key-lifecycle.md:320-333`): a fact about the machine, never in a repo's docs, not a harness fact, `auto` safe, ladder via D2/P7.
- **D-wt.** App worktrees are a documented recipe (H9's app variant); no shipped script.
- **D-struct.** One set of operations H1–H9, each with a TUI and an app variant; all `herdr-app` / `hc` / `HC_*` / `HERDR_APP_HOME` strings confined to `reference/herdr.md`; TUI behaviour unchanged.
- **D-pr.** Follow-up PR targets `herdr-role-delegation`.

Butler defaults, adopted by the Planner:
- **D2.** Nested check inconclusive → say so once, then `tui`.
- **D3.** Worker env as an argv prefix `env KEY=VALUE … <kind> …`, every path expanded first.
- **D4.** Single worker: `pane.split --argv` beside the Butler. Wave: `tab.new --argv` for the first worker, `pane.split --argv` for the rest. Never `hc run`.
- **D5.** Address workers by terminal ID; label `jdi.agent=<name>` (`hc label`); find with `hc ls --label`.
- **D6 (amended 2026-11-16 after the probe gate).** On the app JDI types into an agent only after a readiness `hc wait` reports `status: idle`, and always with `hc send … --if idle`, so the app refuses to type into anything not idle. This covers H5's short prompt, H6's `needs_input` answer and the herd handoff. Never `--task`. *Was:* `hc wait`, then `hc send`. *Why:* A2/A4 — Claude's and Codex's trust/hook-review dialogs report **no status** (not `blocked`), so `hc wait` times out and a plain `hc send` would type into the dialog; a herd worktree is always a new folder.
- **D7 (amended 2026-11-16 after the probe gate).** Reject at readiness: if the readiness wait does not end with `status: idle` (for example it times out with no status, as with an open dialog or a kind that reports none), the agent is not ready. JDI types nothing, says why (no status; possibly a dialog in its pane, which is the user's to answer), and treats it like the TUI's `agent_not_ready`: delegation closes the pane (H8) and falls to rung 8 (`native`); the herd reports that issue as blocked at startup and leaves its space for the user. *Was:* accept with a one-time note. *Why:* without a status there is no safe moment to type.
- **D8.** Codex `--no-daemon` goes in `harnesses.codex.args`; JDI adds nothing but notes once when it is missing.
- **D9.** App H1 requires `herdr-app status` to succeed.
- **D10.** App split direction is always `right`.

Planner:
- **P1.** App H2 resolves the kind with `command -v <kind>` in the Butler's shell and puts the **absolute path** in the argv (terminals get the core's env, not the Butler's PATH). A non-absolute answer (alias/function) fails H2 on the app with that reason. Probe A15.
- **P2.** `pane.split` has no folder option and starts in the Butler terminal's current folder (observed: can differ from the repo root), so split argv is prefixed with `sh -c 'cd -- "$1" && shift && exec "$@"' jdi-worker <worktree root> …`. `tab.new`/`space.new` take `--folder`, no wrapper. VERIFY-AT-EXECUTION: A14 (folder), A6 (status still reported through `exec`).
- **P3.** If A13 shows `pane.split` moves focus, H4 appends `&& herdr-app do pane.focus --pane <butler pane>` to the same command; otherwise nothing. VERIFY-AT-EXECUTION.
- **P4.** Refines D2: app check (b)/(c) failing (binary or socket missing) means the app is unreachable → `tui`, no note. "Inconclusive" means only `hc get` failed or had no `foreground`; then say so once and use `tui`.
- **P5.** Herd on the app: H9 creates only the worktree at herd step 6; the space and agent are created by H4b-on-the-app at step 8, after `herd.seed` (step 7).
- **P6 (refined by A11).** Window check = `herdr-app status` exits 0 and its stdout parses as JSON with no top-level `error` key; its `errors` list is recorded, not a failure. With no window it exits 2 with plain text on stderr (not JSON).
- **P7.** A pinned `app`/`tui` never falls to the other surface: delegation degrades to `native`, the herd stops. An invalid value is announced once (only when H1 runs) and treated as `auto`.
- **P8.** Manifest `herdr` object gains `"surface"` on both surfaces (additive; schema stays 1).
- **P9.** JDI closes only via `pane.close`, `tab.close`, `space.close`; never `hc kill`, `hc rm`, `hc keys`, `hc interrupt`, `hc send --force`; never bare `hc` or bare `herdr-app`.
- **P10 (narrowed by D7).** A kind that never reports status is rejected at readiness; if a worker's status disappears *mid-run*, every wait check-in also checks whether `result.json` exists, and goes to H7 if it does.
- **P11.** Probes run in a throwaway session and app home through a guard wrapper that unsets inherited terminal variables (Appendix B).
- **P12.** Version 1.0.11 on this branch.

Facts behind them (read-only reads by the Planner): `hc` JSON keeps `cwd` as the launch folder and the current one in `foreground.cwd`; app commands default to "the focused" pane/space, so JDI always passes IDs; `tab.new --argv` runs the agent in an interactive shell that stays after exit (its pane is not removed); `herdr-app status` returns an `errors` list on success, `{"error": …}` on failure; hc errors are `{error:{kind,message,hint}}` on stderr with exit codes 3 not_found, 7 needs_target, 9 blocked, 10 status_mismatch, 11 finished; `hc send` waits up to 60 s for a person's unfinished draft; Claude reports status under hc (opencode/codex: probe A3).

### Order

Wave 1: Tasks 1 and 2 (parallel). Then Tasks 3 → 4 → 5 in sequence (all edit `reference/herdr.md`), with Tasks 7 and 8 alongside. Task 6 after 5; Task 9 after 1–8; Task 10 last. No parallel tasks share a file (Task 8's tests go in a new file).

Every text task: write the named tests, run the module and see it fail (`python3 -m unittest discover -s tests -p '<file>.py' -v`; the `tests.<module>` form fails with `ModuleNotFoundError`), edit the docs, run the module until green, then the full suite. One commit per task. No em dash in `reference/herdr.md` (`test_no_em_dash`).

### Task 1 — `herdr.surface` config key
Files: `tests/test_config_schema.py`, `reference/config.md`, `jdi.config.example.yml`.
1. Tests first: new `HerdrBlockTest` (modelled on `DelegationBlockTest`): `herdr.surface` in `key_paths(schema_block())`; schema line `^  surface: auto$`; comment line exactly `  # auto | app | tui`; a schema comment contains "Whether Herdr is used at all stays `delegation.transport`"; example line `^  surface: (app|tui)$`; defaults row starting ``| `herdr.surface` | `auto` ``; `## Notes` contains "**`herdr.surface` only picks which Herdr.**".
2. `reference/config.md`: schema block (Appendix A1) after `delegation:` and before `herd:`; defaults row after `delegation.transport`; three Notes bullets — "only picks which Herdr", "A pinned surface never falls to the other one" (with P7's invalid-value rule), "usually personal, `config.local.yml`". Confinement-scanned: write "the Herdr app", never the binary names.
3. `jdi.config.example.yml`: commented `herdr:` block with `surface: app` after `delegation:`.

### Task 2 — live app probes
Files: PLAN.md only (a "Probe log" section). Run A1–A12 (architecture doc) plus A13–A17 (Appendix B) in a throwaway session per Appendix B. Record sanitised output (`$HOME` → `~`, scratch → `<scratch>`, no session or machine names). **Probe gate:** any probe contradicting D2–D10 or P1–P6 stops the work: amend the decision here, record why, rerun the affected probes before Task 3.

### Task 3 — `reference/herdr.md`: surfaces, H1, confinement
Files: `tests/test_herdr_operations.py`, `tests/test_delegation_transport.py`, `reference/herdr.md`.
1. Tests first:
   - `HEADINGS` += `## Surfaces`, `### Choosing the surface`, `### H1 on the TUI`, `### H1 on the app`.
   - `test_surfaces_section`: "`herdr.surface`", "Inherit, never set", "`HC_SESSION`", "`HERDR_APP_HOME`", "Never run bare `herdr-app` or bare `hc`", "`hc server`", "seconds".
   - `test_choosing_the_surface`: "innermost surface wins", "`foreground`", "says so once and uses the TUI", "never falls to the other surface".
   - `test_h1_app_checks_in_order`: within `### H1 on the app`, in order: `HC_TERMINAL_ID`, `command -v hc`, `test -S "$HC_TERMINAL_SOCKET"`, `hc get "$HC_TERMINAL_ID" --json`, `herdr.space`, `herdr-app status`; plus "before any `hc` command".
   - `test_no_personal_values`: file has no `/home/`, `/Users/`, `jdiprobe`, `HC_SESSION=`, `HERDR_APP_HOME=`.
   - `test_failure_patterns_name_the_surface`: `## When a step fails` contains "Herdr (<surface>)".
   - Confinement (`tests/test_delegation_transport.py`): add `\bherdr-app\b`, `\bhc\b`, `\bHC_[A-Z]`, `\b(space|tab|pane|agent)\.(new|split|close|select|focus)\b` to `CONFINED_PATTERNS`; add `test_confined_patterns_catch_every_app_name` — forbidden samples (`hc send t3 hi`, `herdr-app do pane.split`, `HC_TERMINAL_ID`, `HERDR_APP_HOME`, `pane.split --pane p1`, `herdr agent start`) each match a pattern; allowed samples ("the Herdr app", "`herdr.surface: app`", "Herdr TUI", "`delegation.transport: herdr`") match none.
2. `reference/herdr.md`:
   - Intro: "`herdr-app` and `hc` are the Herdr app's CLIs, used only by the app variants."
   - New `## Surfaces` after `## Scope`: what each surface is; `herdr.surface` picks one; "Inherit, never set" (never set/export/write `HC_SESSION`, `HC_SOCKET`, `HERDR_APP_HOME` in a command, manifest, config or prose); never bare `herdr-app` or bare `hc`, never `hc server`; hc timeouts are seconds; target IDs are strings; app variants assume POSIX `sh`; each operation has a TUI and an app subsection, shared text applies to both.
   - H1: shared intro kept (incl. every phrase native tests pin); `### Choosing the surface` (matrix, nested rule with P4, pinned/invalid values P7); existing checks (a)–(c) unchanged under `### H1 on the TUI`; `### H1 on the app` with checks (a)–(e) as in the architecture doc, P6 wording, version record. Announcement under `auto`: silent when the chosen surface's first check fails or the answer is `none`. Answers: `tui`, `app`, `none`.
   - `## When a step fails`: "…but Herdr (<surface>) is not usable here…"; add an invalid-`herdr.surface` pattern.
   - Universal rules (pinned phrases kept): rule 4 + "and so is `hc read` on the app"; rule 5 + "`error` on the app"; rule 7 + never `hc keys`, `hc send --force`, `hc interrupt`.

### Task 4 — `reference/herdr.md`: H2–H8, waves
Files: `tests/test_herdr_operations.py`, `reference/herdr.md`.
1. Tests first: headings `### H2 on the TUI`, `### H2 on the app`, `### H3 on the app`, `### H4 on the TUI`, `### H4 on the app`, `#### H4b on the app`, `### H5 on the TUI`, `### H5 on the app`, `### H6 on the TUI`, `### H6 on the app`, `### H8 on the TUI`, `### H8 on the app`, `### Waves on the app`. Methods:
   - `test_h2_app`: "`command -v <kind>`", "absolute path", "no kinds list", "`blocked` and `done` will not appear", "`--no-daemon`", "`harnesses.codex.args`".
   - `test_h3_app`: "`hc ls --json --label jdi.agent=<name>`", "`herdr-app ls`", `"surface"`, `"space_id"`, `"terminal_id"`.
   - `test_h4_app_spawn_line_and_split_are_one_command`: harness of `test_h4_spawn_line_and_pane_split_are_one_command` but scoped to `jdi_files.section(self.text, "### H4 on the app")`; first numbered line starts `1. **Print the spawn line.**`; one fenced line contains both `printf '%s\n' "JDI spawn` and `&& herdr-app do pane.split --pane <butler pane> --direction right --argv`.
   - `test_h4_app_order`: `pane.split` < `hc label <terminal> jdi.agent=<agent name>` < `**Write the run files.**` < `hc wait <terminal> --timeout 120`.
   - `test_h4_app_argv`: `cd -- "$1"`, `env KEY=VALUE`, "Expand every path".
   - `test_h4b_app`: `hc label`, `hc wait <terminal> --timeout 120`.
   - `test_h5_app`: `hc send <terminal> "<short prompt>" --wait --timeout 300`, `hc wait <terminal> --timeout 300`, "seconds, not milliseconds", and the state-table row prefixes below.
   - `test_h6_app`: "never `hc keys`", "never `hc send --force`", "never `hc interrupt`", `hc read <terminal> --lines 80`, `herdr-app do agent.focus --terminal <terminal>`.
   - `test_h8_app`: `herdr-app do pane.close --pane <pane_id>`, `herdr-app do tab.close --id <tab_id> --confirmed true`, "already gone".
   - `test_waves_app`: `herdr-app do tab.new --name jdi-wave-<first run id>`, `--focus false`, `hc wait <terminal> --timeout 30`.
2. `reference/herdr.md` (TUI text moves under `### … on the TUI` unchanged and stays first):
   - H2: model-flag table shared; app: no kinds list or integration status, `command -v` only, absolute path (P1); readiness rejects an agent that never reaches `status: idle` (D7); Codex `--no-daemon` note (D8).
   - H3 on the app: collision check `hc ls --json --label jdi.agent=<name>`; space/tab IDs from `hc get "$HC_TERMINAL_ID" --json` labels; Butler pane = the `herdr-app ls` entry whose `terminal` equals `$HC_TERMINAL_ID` (A16); app manifest object (Appendix A3); `"surface": "tui"` added to the TUI JSON; one sentence: on the app the split starts the agent, so the manifest is written after the split and before the short prompt (pinned H3 row stays).
   - H4 on the app: (1) spawn line + split as one command (Appendix A2); (2) read `.pane`/`.terminal`, restore focus if A13 needs it (P3); (3) `hc label <terminal> jdi.agent=<agent name>`; (4) **Write the run files.**; (5) `hc wait <terminal> --timeout 120` → idle: H5; blocked: H6 with prompt unsent; finished / not found / JSON error: H8 then rung 8; anything else, including a check-in timeout with no `status`: not ready (D7) — say why, H8, rung 8.
   - `#### H4b on the app`: label + readiness wait for a terminal the caller created, same outcomes.
   - H5 on the app: `hc send … --if idle --wait --timeout 300`, then loop `hc wait … --timeout 300` under the 2700 s deadline (shell-tool cap minus 30 s if lower); classify from hc's JSON (stdout/stderr), exit code only confirms. Rows: `working` or `reason: timeout`; `blocked`; `idle`/`done` ("not proof"); `idle`/`done` with no `result.json`; `error` (inspect, never success); no status (P10); overall timeout; refused as blocked (exit 9); `not_started` (don't resend, read first); `reason: message` (not a worker state, wait again); finished (11) / not found (3) / JSON error → transport failure. Note `hc send`'s 60 s draft wait.
   - H6 on the app: `hc get <terminal> --json` (`status.kind`: permission/question/auth), `hc read <terminal> --lines 80` (screen only while blocked/working); focus `herdr-app do agent.focus --terminal <terminal>` only on a yes; answer `needs_input` with `hc send <terminal> "<answer>" --wait --timeout 300`; never `hc keys` / `hc send --force` / `hc interrupt`, even where the hc manual suggests `hc keys` for a trust dialog.
   - H8 on the app: `outcome.json` shared; `herdr-app do pane.close --pane <pane_id>` (a split whose program exited is already gone; the error JSON from A7 is expected); waves `herdr-app do tab.close --id <tab_id> --confirmed true`.
   - Waves on the app: first worker via `tab.new` (Appendix A2, `--folder`, no wrapper; shell-wrapped, stays live after exit, H8 must close it); later workers `pane.split --pane <a live worker pane in the wave tab>` with the wrapper (none live → new wave tab); wait per worker `hc wait <terminal> --timeout 30` or `hc get`; cap 4 and other wave rules shared.
   - `## Why the agent surface, not pane run`: one paragraph — on the app, states come from the program (OSC 7501) through hc, same reason.

### Task 5 — `reference/herdr.md`: H9 on the app
Files: `tests/test_herd.py`, `reference/herdr.md`.
1. Tests first: `H9_APP_HEADING = "### H9 on the app"`; methods asserting: folder like the app's dialog (`${HERDR_APP_HOME:-~/.config/herdr-app}/settings.json`, `worktrees.directory`, `~/.herdr/worktrees`, `--git-common-dir`, `<worktrees dir>/<repo>/<name>`); from the default branch (`git worktree add -b jdi-herd-scratch-<herd-id>-<N> <path> origin/<default>`); space after seeding (`herdr-app do space.new --name`, `--folder <path> --tab <name>`, `--focus false`, "after `herd.seed`"); handoff by send (`hc wait <terminal> --timeout 120`, `hc send <terminal> "<invocation>"`, "Never `--task`"); cleanup order (`git -C <worktree> status --porcelain -- <plans.path>` < `herdr-app do space.close --id <space> --confirmed true` < `worktree remove`); reattach/list (`herdr-app do space.select --id <space>`, `git worktree list --porcelain`).
2. Append `### H9 on the app` (existing H9 text unchanged): kind/name rules shared; folder = `worktrees.directory` from the app's `settings.json`, default `~/.herdr/worktrees` (leading `~` → `$HOME`; any other relative value fails H9 with its reason; trailing `/` dropped; the app doesn't read the TUI's `config.toml`); `<repo>` = basename of `git rev-parse --path-format=absolute --git-common-dir` minus `/.git`; suffix check shared; create returns the path only (P5); at herd step 8: `herdr-app do space.new --name '<SHORT-ID> <TITLE>' --folder <path> --tab <name> --argv '<argv>' --focus false` (env prefix + absolute kind path, no model flag, no wrapper; output `{space, tab, terminal}`, pane from `herdr-app ls`; name quoted so `'`, `$`, backticks arrive literally (A17); tab named at creation; Butler not the herd session's parent (A8 checks `parent`)), then `#### H4b on the app`; handoff `hc send <terminal> "<invocation>"` without `--wait`, shared invocation table, never `--task`; watch `hc get`, `hc read --lines 80`; reattach = space in `herdr-app ls` whose `folder` is inside the path → `space.select --id`, else `space.new --folder <path> --focus false`; cleanup = plan-file check, `space.close --confirmed true`, `git -C <main checkout> worktree remove [--force] <path>`; list `git worktree list --porcelain`.

### Task 6 — callers
Files: `reference/delegation.md`, `commands/{prep,research,plan,split,feedback,pr,execute,next,yolo}.md`, `commands/herd.md`, `tests/test_step_zero_transport.py`, `tests/test_delegation_transport.py`, `tests/test_herd.py`.
1. Tests first: `STEP_ZERO_FRAGMENTS` += "H1 also settles which Herdr this is, the TUI or the app, from `herdr.surface`"; `test_block_name_lists_include_delegation` expects "`models`, `harnesses`, `delegation`, and `herdr` from it" (prep) and "… from that config" (research); `TransportSelectionTest` += "Herdr here is either surface, the Herdr TUI or the Herdr app" and "or `error` on the app"; herd fragments += "`herd`, `herdr`, `harnesses`", "H1 settles which Herdr", "On the app, the space is opened in step 8".
2. Edits: that sentence after "…no role re-probes." at all nine step-0 sites; `herdr` in prep/research block lists; `reference/delegation.md` — either-surface sentence after the transport table, rung 7 keeps the pinned TUI sentence + "On the app there is no kinds list; H2 checks only that the CLI resolves.", rung 9 "(or `error` on the app)", "Where a role runs": "…on the pane, or in the worker's command on the app, as H4 says"; `commands/herd.md` (surface-neutral, no app commands) — step 1 block list + `herdr`; step 2 "H1 settles which Herdr (`herdr.surface`)"; step 6 "H9 returns the worktree path, and on the TUI also the workspace, tab and root pane. On the app, the space is opened in step 8, after seeding." and "H9 says what the environment needs on the surface in use"; step 8 "blocked at startup (on the TUI, `agent_not_ready`)"; step 9 "a blocked result (on the TUI, `agent_blocked`)"; step 10 "pane or terminal ID, workspace (space on the app)", keep the pinned sidebar sentence + "the app also rolls it up per space and tab". Don't touch `roles/butler.md` (a test forbids it naming Herdr).

### Task 7 — user docs
Files: `commands/init.md`, `commands/help.md`, `README.md`, `tests/test_transport_docs.py`.
1. Tests first: init description has "how delegated roles reach their own process" and "which Herdr they use"; `init.md` has "offer `herdr.surface`"; help's opening paragraph has "which Herdr surface"; help's `### Separate agent processes` and `/jdi:init` row name `herdr.surface` / "Herdr surface"; README `### Separate agent processes under Herdr` has "`herdr.surface`" and "the Herdr app"; README init comment (~`:186`) and prose (~`:202`) have "which Herdr".
2. Edits: `commands/init.md` description + "and which Herdr they use"; step 10 skip condition "H1 answers `none`"; sub-bullet: say which surface H1 found, offer `herdr.surface` only to pin it, recommend `auto`, offer `config.local.yml` (no new numbered step — follows the `herd` precedent; record the deviation from the lifecycle doc). `commands/help.md`: closing line "which Herdr surface is pinned, when not `auto`"; `/jdi:init` row; `/jdi:herd` row "inside Herdr, the TUI or the app"; a paragraph in `### Separate agent processes`. `README.md`: both init enumerations; paragraph in "Separate agent processes under Herdr"; `/jdi:herd` paragraph workspace or space; "How it is put together" row for `reference/herdr.md` "on the Herdr TUI or the Herdr app". No app command names in the README.

### Task 8 — architecture docs
Files: `docs/herdr-surfaces-architecture.md`, `docs/delegation-transport-architecture.md`, new `tests/test_herdr_surfaces_doc.py`.
1. Tests first: headings `## Detection`, `## Operation map`, `## The app's worktree layout`, `## Decisions`, `## App-side live probes`; absent: `## Open decisions`, "Nothing here is implemented yet", "in an app terminal of the user's normal window"; probes section has "throwaway"; no `/home/`; transport doc `## Capability detection` has "`docs/herdr-surfaces-architecture.md`" and "`herdr.surface`".
2. Edits: surfaces doc — status implemented in 1.0.11; "Open decisions" → "Decisions" recording D1–D10, P1–P11; fill "open decision" cells in the operation map; the `errors`/`error` fact; probes require a throwaway session and app home, add A13–A17 and a summary of results. Transport doc — "Capability detection" surface-neutral pointing at the surfaces doc; "Configuration" env: "on the pane, or in the worker's argv on the app".

### Task 9 — release
Files: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json` (1.0.11), `CHANGELOG.md`. `## 1.0.11` headline "**JDI drives the Herdr app as well as the Herdr TUI.**"; bullets: `herdr.surface` and its default (no key = unchanged for TUI users); bold bullet for users already in the app — under `delegation.transport: auto`/`herdr`, roles on another CLI now get app panes and `/jdi:herd` works instead of stopping (set `transport: native` or `herdr.surface: tui` to keep the old behaviour); app worktrees follow the dialog layout; JDI never sets session/home variables; Codex users add `--no-daemon` to `harnesses.codex.args`. Commit `feat: Support the Herdr app alongside the TUI (1.0.11)`; body names what was excluded: `/jdi:status`, `hc run` workers, Windows verification, a shipped worktree script.

### Task 10 — end-to-end UAT (throwaway session)
Files: PLAN.md (log). Appendix B harness; branch plugin via `claude --plugin-dir <repo>`, started as the argv of a throwaway `space.new` on a scratch clone with `config.local.yml` `tracker: {name: none}`. Scenarios: (a) `/jdi:prep`, Researcher on opencode, `transport: auto` — no step-0 note, spawn line, split right, worker in the worktree root, valid result, pane closed; (b) two-task wave, Executors on another CLI — wave tab, cap honoured, tab closed; (c) `/jdi:herd` two IDs, fallback names — worktrees under the scratch `worktrees.directory`, spaces named and nested, handoff by `hc send`, report's cleanup commands (close spaces after handoff, don't run prep to completion); (d) `transport: native` — no hc/herdr-app command, no mention, summaries included; (e) `herdr.surface: tui` inside the app under `auto` — silent native; (f) `herdr.surface: bogus` — one note, then `auto`. Clean up per Appendix B. Agent smoke test; real acceptance stays with the user (as #31's Task 10).

### Appendix A — verbatim text

**A1. Schema block (`reference/config.md`):**

```yaml
# Optional. Which Herdr JDI drives when it uses Herdr: the Herdr TUI or the
# Herdr desktop app. See reference/herdr.md, H1.
herdr:
  # auto | app | tui
  #   auto - the Herdr this session runs in. When one runs inside the other,
  #          the innermost wins; when that cannot be told, the TUI.
  #   app  - only the Herdr app is checked.
  #   tui  - only the Herdr TUI is checked.
  #
  # Whether Herdr is used at all stays `delegation.transport` (`native` is
  # off), and /jdi:herd runs only when you invoke it. Which Herdr you run is a
  # fact about your machine: set it in .jdi/config.local.yml.
  surface: auto
```

**A2. App commands** (each one physical line).

Single worker (H4 on the app, step 1):
```text
printf '%s\n' "JDI spawn <run-id>: <Role> on <kind> (<model | CLI default>) - args: <verbatim | none> - env keys: <keys | none> - run dir: <path> - agent: <agent name>" && herdr-app do pane.split --pane <butler pane> --direction right --argv '<argv JSON>'
```
Split-worker `<argv JSON>` (`"env", "KEY=VALUE", …` only when `harnesses.<kind>.env` is non-empty; elements JSON-escaped; array single-quoted, `'` → `'\''`):
```text
["sh", "-c", "cd -- \"$1\" && shift && exec \"$@\"", "jdi-worker", "<worktree root>", "env", "KEY=VALUE", "<absolute path of kind>", "<model flag>", "<model>", "<args...>"]
```
First worker of a wave:
```text
printf '%s\n' "<its JDI spawn line>" && herdr-app do tab.new --name jdi-wave-<first run id> --space <space_id> --folder <worktree root> --argv '<argv JSON without the sh wrapper>' --focus false
```

**A3. App manifest object** (replaces `"herdr"` in the H3 JSON on the app):
```json
"herdr": {
  "surface": "app",
  "space_id": "<herdr.space label of the Butler's terminal>",
  "tab_id": "<herdr.tab label of the Butler's terminal>",
  "butler_pane_id": "<the Butler terminal's pane, from herdr-app ls>",
  "pane_id": "<from pane.split>",
  "terminal_id": "<from pane.split>",
  "agent_name": "jdi-<role>-<4 hex>",
  "status_reported": "<true once hc get shows a status, else false>",
  "versions": {"app": "<herdr-app --version>", "hc": "<hc --version>"}
}
```

### Appendix B — probe harness, A13–A17, cleanup

**Isolation guard** (a wrapper in the Executor's scratch dir, never the repo; every probe command goes through it): refuse unless `JDI_PROBE_SESSION` and `JDI_PROBE_HOME` are set; `unset HC_TERMINAL_ID HC_TERMINAL_SOCKET HC_SCOPE HC_SOCKET HERDR_ENV HERDR_SOCKET_PATH HERDR_PANE_ID HERDR_TAB_ID HERDR_WORKSPACE_ID` (otherwise the inherited socket can address the user's real core); `export HC_SESSION=$JDI_PROBE_SESSION HERDR_APP_HOME=$JDI_PROBE_HOME`; `exec "$@"`. VERIFY-AT-EXECUTION: the hc manual says tests need scratch XDG paths too — check which XDG vars the core reads; if overridden, pass agent CLIs their real config via the env prefix.

**Setup:** record versions and the *count* of the user's `hc ls --json` entries; clone the repo into scratch (local `origin`); create the throwaway home with `settings.json` = `{"worktrees":{"directory":"<scratch>/worktrees"}}`; session name `jdiprobe-<4 hex>`; through the wrapper, `herdr-app status` must fail and `hc ls --json` be empty, then start `herdr-app` in the background (the only allowed bare launch; tell the user a window will appear); run "inside" probes as scripts launched by `space.new` / `pane.split --argv`, writing to scratch files.

**New probes:** A13 focus — does `pane.split` change `herdr-app status` `.focused_pane`? A14 split folder — start folder of `pane.split --argv` with/without the wrapper, from `hc get` `foreground.cwd`, with the "Butler" space started in a parent folder. A15 core env — PATH a terminal gets, whether `command -v <kind>` resolves there, and that a var exported only in the Butler's shell is absent. A16 IDs/labels — `herdr-app ls` `terminal` vs `HC_TERMINAL_ID` form; `hc label` / `hc ls --label` on app-created terminals; `parent`, `die_with_parent`, `notify` show split/space terminals aren't the requester's children. A17 argument forms — `--argv '<json>'` and `--focus false` accepted; a `--name` with `'`, `$`, a backtick arrives literally. Additions: A2/A3 record whether each kind reports status through the `sh` wrapper; A7 records the exact "already gone" error JSON; A11 records the no-window output and whether `window.close` / `app.quit` leaves the core running; codex missing → "not installed".

**Cleanup:** close every space and tab created; quit the throwaway window through the wrapper (VERIFY-AT-EXECUTION that `app.quit` addresses only the window `HERDR_APP_HOME` selects); `hc server stop` through the wrapper only; `git worktree prune` in scratch, remove scratch; confirm the user's `hc ls --json` count is unchanged; stop any throwaway TUI with `herdr --session <throwaway> server stop`.

## Testing Strategy

| Task | Proof | Fails when |
|---|---|---|
| 1 | `HerdrBlockTest`; existing `ConfigSchemaTest` | example block or defaults row removed (`test_schema_keys_appear_in_the_example`, `test_every_schema_block_has_a_defaults_row`, via `key_paths` / `defaults_table_keys` in `tests/jdi_files.py`) |
| 2 | probe log in PLAN.md (gate) | a probe contradicts D2–D10 / P1–P6 |
| 3 | new H1/Surfaces methods; widened `HerdrConfinementTest` + pattern self-test | `hc send` in `commands/herd.md` fails the line scan; dropping `\bhc\b` from `CONFINED_PATTERNS` fails `test_confined_patterns_catch_every_app_name` |
| 4 | H2–H8 and Waves app methods | the app split block removed or reordered |
| 5 | `test_herd` H9-app methods | `space.close` moved after `worktree remove` |
| 6 | `StepZeroTransportTest`, block lists, `TransportSelectionTest`, herd fragments | a step-0 site or caller loses the sentence |
| 7 | `test_transport_docs` methods | init/help/README lose the surface wording |
| 8 | `tests/test_herdr_surfaces_doc.py` | "Open decisions" or a personal path survives |
| 9 | existing `VersionTest` | JSON bumped without CHANGELOG (no red-first step; say so) |
| 10 | UAT log in PLAN.md | any scenario (a)–(f) deviates |

- TDD: tests first, seen failing, per task; full suite after each task (`python3 -m unittest discover -s tests -v`).
- Not unit-observable — run-time behaviour of the app variants, P2 wrapper, P3 focus, P1 path resolution, P6 status semantics, session isolation — proven by Task 2's probe log and Task 10's UAT log. CHANGELOG prose and herd handoff wording are reviewed by reading.
- Pinned fragments that must survive verbatim: "`agent read` is for inspection only", "never counts as success", "Herdr's `kinds:` line lists the kinds it supports", "the Herdr sidebar shows `blocked` and `done` per pane", the H3 manifest table row.
- Indented fences don't toggle `jdi_files.section`'s fence tracking: no line inside an indented fence may start with `#`.

## Risks

- **R1 Probe safety (highest).** Inherited `HC_TERMINAL_SOCKET` / `HC_TERMINAL_ID` can route `hc` to the user's real core: the wrapper's `unset` is mandatory; never `hc server stop` or `herdr-app do app.quit` outside it. Probes spend agent tokens and open a visible window; if the Executor can't open a window, Task 2 needs the user.
- **R2 Wrong worker folder.** Without P2 a split worker starts in the Butler terminal's folder (observed ≠ repo root). If A14/A6 show the wrapper breaks status, the gate stops work; fallback `tab.new --folder` for single workers (amends D4).
- **R3 Different environment.** App workers get the core's env: needs go in `harnesses.<kind>.env` or P1. Env values show in the Butler's command line and `hc get` argv (as `--env` does on the TUI); the manifest records keys only.
- **R4 Visible change for app users.** Under `auto`/`herdr` they move from silent native to app panes; CHANGELOG must say so.
- **R5 Confinement breadth.** `reference/config.md`, `commands/*`, `roles/*`, `skills/run/SKILL.md` must say "the Herdr app", never binary names; `\bhc\b` is broad by design.
- **R6 Platforms.** App variants assume POSIX `sh`; Windows unverified (stated). Default app home `~/.config/herdr-app` per the installed guide; macOS unverified.
- **R7 A foreign `hc`** on `PATH`: check (d) requires JSON with `labels`.
- **R8 Narrow panes** with direction always `right` (4-wide waves; #31's smoke test saw dialogs hidden at half width). Accepted under D10.
- **R9 Version collision.** `origin/main` has its own 1.0.10–1.0.12; whoever rebases #31 must renumber #31 and this PR. `/jdi:do` (1.0.12 on main) will need the step-0 `herdr.surface` sentence if it delegates.
- **R10 Same file.** Tasks 3–5 all edit `reference/herdr.md` (sequential); Tasks 3 and 6 share `tests/test_delegation_transport.py` (sequential); Task 8 uses its own test file.

## Probe log

Task 02, run 2026-11-16 on Linux (Wayland), `herdr` 0.9.3, `herdr-app` 0.1.16, `hc` 0.1.21,
`claude` (mise wrapper), `opencode` 2.2.7, `codex-cli` 0.169.0. Every command ran through the
isolation guard `<scratch>/g` in a throwaway `HC_SESSION` (`<probe-session>`) and a throwaway
`HERDR_APP_HOME` (`~/.config/<probe-home>`, short because the window's control socket path must
fit `SUN_LEN`). "Inside" probes ran in the Butler terminal (`t1`) of a throwaway space named
`butler` whose folder is `<scratch>`, the parent of the clone `<scratch>/repo`, driven by
`hc send t1 "bash <scratch>/in/<probe>.sh > <scratch>/out/<probe>.txt 2>&1"`. IDs (`sp…`, `tb…`,
`p…`, `tN`) are the throwaway session's and are kept as printed.

### Gate

**Stopped. The probes contradict D6 and D7.** No decision text was changed. The Butler and the user
amend.

- **The evidence.** Claude and Codex both open a folder-trust dialog when they start in a folder
  they have not seen before. Codex then opens a second dialog, "Hooks need review". While either
  dialog is open, `hc get` shows `status: null`, not `blocked` (see A2). `hc wait <t>` then returns
  `reason: timeout` with `status: null`. It does not report a dialog.
- **Why that breaks D6.** `hc send` refuses only a terminal whose reported status is `blocked`
  (exit 9; see A4). A terminal that reports no status gets the text typed in and Enter pressed (see
  A4, the `cat` case). So the bare sequence "`hc wait`, then `hc send <t> "<invocation>"`" would
  type the invocation into the trust dialog and answer it. That breaks #31's D9 (JDI never answers
  a worker's dialog). A herd worktree is always a new folder, so the herd hits this case every time
  on Claude and Codex.
- **A possible amendment to D6.** Send only after `hc wait` ended with `reason: status` and
  `status: idle`, and send with `hc send <t> "<invocation>" --if idle`. hc then refuses unless the
  status is exactly `idle`. On a timeout with `status: null`, tell the user the agent may be
  waiting on a dialog in its pane, and keep waiting. The same guard applies wherever H4 and H5 on
  the app type the first prompt after `hc wait` readiness.
- **Why that breaks D7.** A kind that never reports status can never pass `--if idle`. Without
  that guard, a prompt sent to it can answer a dialog. D7 ("accepted with a one-time note") cannot
  be made dialog-safe for prompts typed by `hc send`.
- **What the evidence points to for D7.** On the app, reject a kind that reports no status. Or
  give such a kind its prompt some way other than typed input. Whether Codex reports status at all
  is still **unobserved**: its two start-up dialogs were left unanswered (rule 7), so it never
  reached a prompt.
- **Task files affected.** Task 03 (H1 surfaces text), Task 06 (H4/H5 send wording, H2's D7 note)
  and Task 08 (herd handoff) carry the D6/D7 text and need the Butler's review before Task 03 starts.

**Separate finding: the trust dialog.** It is not a contradiction, but H4 and H9 need it. Claude's
"Accessing workspace … Is this a project you … trust?" dialog and Codex's "Trust this folder?"
dialog appear at agent start for an untrusted folder. Answering it is the user's job (rule 7).
The probe operator answered both dialogs by key for the clone `<scratch>/repo`. That was the
probe's own action, done before the Butler's instruction not to, and JDI must never do it. The
saved trust entries were removed in cleanup.

### Isolation guard and setup

- **The guard** is `<scratch>/g` (POSIX `sh`). It refuses with exit 64 and a message on stderr,
  writing nothing to stdout, unless `JDI_PROBE_SESSION` and `JDI_PROBE_HOME` are both set and the
  session matches `jdiprobe-*`. It then unsets `HC_TERMINAL_ID HC_TERMINAL_SOCKET HC_SCOPE
  HC_SOCKET HERDR_ENV HERDR_SOCKET_PATH HERDR_PANE_ID HERDR_TAB_ID HERDR_WORKSPACE_ID`, exports
  `HC_SESSION` and `HERDR_APP_HOME` and ends with `exec "$@"`. The refusal check
  (`env -u JDI_PROBE_SESSION <scratch>/g echo X`) gave `exit=64`, 0 stdout bytes, and the stderr
  line `probe guard: JDI_PROBE_SESSION and JDI_PROBE_HOME must both be set; refusing`.
- **XDG (VERIFY-AT-EXECUTION).** The core keys both of its paths by session name. Its socket is
  `$XDG_RUNTIME_DIR/herdr-core/<session>.sock` and its state is
  `$XDG_STATE_HOME/herdr-core/<session>/`. So `HC_SESSION` alone isolates it, and XDG was **not**
  overridden. That means the agent CLIs kept their real config and needed no env-prefix passthrough.
  Some state lands outside the scratch dir because of this, and cleanup removes it:
  `~/.local/state/herdr-core/<probe-session>/`, and for A10
  `~/.config/herdr/sessions/<probe-session>/` and
  `~/.local/state/herdr-automatic-rename/sessions/<probe-session>/`.
- **Setup.** The user's own `hc ls --json` (read-only, outside the guard) had 1 live terminal.
  The clone `<scratch>/repo` uses a bare local `origin`, and `origin/HEAD` is set to `main`. The
  throwaway home's `settings.json` is `{"worktrees":{"directory":"<scratch>/worktrees"}}`. Before
  launch, through the guard, `herdr-app status` gave exit 2 and `no Herdr window at
  ~/.config/<probe-home>/herdr-app.sock`. `hc ls --json` gave `{"hidden_finished":0,"terminals":[]}`
  and auto-started the throwaway core. Then `herdr-app &` ran (the one bare launch). `status`
  printed JSON with `"errors": []` and a `frame-welcome` overlay, which was closed with
  `herdr-app do overlay.close`.

### Probes

**A1, `tab.new` output.**
- **Command.** `herdr-app do tab.new --name jdi-wave-r1 --space <butler space> --folder
  <scratch>/repo --argv '["sh","-c","pwd > <scratch>/out/a1-pwd.txt; sleep 3; exit 0"]' --focus
  false`.
- **Output.** `{"space":"sp42a9…","tab":"tb8295…","terminal":"t4"}`, exit 0. The terminal
  started in `<scratch>/repo` (`cwd` and `pwd` agree).
- **The argv is wrapped.** `hc get` shows the argv wrapped as `["/usr/bin/bash","-ic","\"$@\"; exec
  \"$0\" -i","/usr/bin/bash","sh","-c",…]`. After the program exited, the terminal stayed `live`
  with foreground `bash -i`, and the tab and pane stayed open.
- **Focus.** `focused_pane`, `space` and `tab` in `herdr-app status` did not change.
- **Close.** `tab.close --id <tab> --confirmed true` gave `{"ok": true}`.
- **Tests and verdict.** Tests D4 and the wave tab. *Confirms*: the wave's tab outlives its first
  worker, so H8 must close it.

**A2, readiness.** Each kind was started by `pane.split --pane <butler pane> --direction right
--argv` through the P2 `sh` wrapper and the D3 `env` prefix (see A6).
- **claude** (`--model haiku`). The folder-trust dialog appeared with `status: null`.
  `hc wait t6 --timeout 45` returned after 45 s with `{"ended":false,"reason":"timeout",
  "status":null,"turn":0}`, exit 0. The dialog was answered by the probe operator, and the next
  `hc wait t6` returned in 1 s with `{"ended":true,"reason":"status","status":"idle","turn":0}`.
  `hc get` showed `"status":{"app":"claude-code","state":"idle"}` and `"reported":true`.
- **opencode.** No dialog. `hc wait t7` returned at once with `reason: status, status: idle`, and
  `hc get` showed `{"app":"opencode","state":"idle"}`.
- **codex** (`--no-daemon`). Its folder-trust dialog, then its "Hooks need review" dialog. Each
  `hc wait --timeout 40` ended in `reason: timeout, status: null`. `hc get` showed `status: null`
  and `reported: false` throughout.
- **Tests and verdict.** Tests D6 and D7 (and H4 readiness). **Amends (gate)**: `hc wait`
  readiness is `idle` only for an agent that reports status, and a start-up dialog shows as
  `status: null` plus a timeout, not as `blocked`.

**A3, status reporting.** The question was whether each kind reports status through the `sh` wrapper.
- **claude.** Reports `idle`, `working`, `done` and `blocked`, all through the wrapper. When a
  question tool was used, `hc get` showed `{"app":"claude-code","kind":"question","msg":"answer:
  Red or blue? (Red · Blue)","state":"blocked"}`.
- **No permission dialog for claude.** No permission dialog appeared: the user's Claude settings
  run in bypass-permissions mode, and the worker inherited them.
- **opencode.** Reports `idle` and `working` through the wrapper, and a turn ends as `idle` (never
  `done`). `blocked` was not triggered.
- **codex.** Reported nothing while its start-up dialogs showed. Whether it reports once it is
  ready is unobserved.
- **Tests and verdict.** Tests D7, P2 and P10. **Amends (gate, D7)**: see Gate.

**A4, send and wait.**
- **Idle claude.** `hc send t6 "Reply with only the word OK." --wait --timeout 60 --json` gave
  `{"started":true,"status":"idle","turn":0,"wait":{"ended":true,"reason":"status",
  "status":"done","turn":1}}`, exit 0, on stdout.
- **Idle opencode.** The same send returned `wait.status: "idle"`, `turn: 1`.
- **Blocked claude.** `hc send t6 "hello" --wait --timeout 10` gave exit 9, an empty stdout, and
  on stderr `{"error":{"hint":"typing would answer its dialog; read its screen first (hc read t6),
  or --force","kind":"blocked","message":"t6 is blocked (question)"}}`. The screen was unchanged,
  so nothing was typed.
- **`not_started` was not reproduced.** `hc send <cat terminal> "hello" --wait --timeout 8` (a
  program with no status) gave exit 0 and `{"started":null,"status":null,"turn":0,
  "wait":{"ended":false,"reason":"timeout","status":null}}`. The text **was typed**.
- **Tests and verdict.** Tests D6, H5 and H6. *Confirms* the blocked refusal. **Amends (gate,
  D6)**: a status-less terminal (a dialog included) is not protected.

**A5, timeouts.** `hc send t6 "<a long counting prompt>"`, then `hc wait t6 --timeout 3 --json`
on the working agent.
- **Output.** `{"children":[],"ended":false,"exit_code":null,"reason":"timeout",
  "signal":null,"status":"working","terminal":"t6","turn":2}` arrived on **stdout** with **exit
  0** after 3 s. The stderr was empty.
- **opencode.** The same shape, with `status: working`.
- **Tests and verdict.** Tests H5's check-in. *Confirms*.

**A6, environment.**
- **Command.** The argv was `["sh","-c","cd -- \"$1\" && shift && exec \"$@\"","jdi-worker",
  "<scratch>/repo","env","JDI_A6=a6-value","<absolute path of kind>",…]`.
- **Output.** `/proc/<foreground pid>/environ` held `JDI_A6=a6-value` for claude, opencode and
  codex. Claude and opencode still reported status (see A3), so `exec` through `sh` and `env`
  keeps OSC 7501.
- **Tests and verdict.** Tests D3 and P2. *Confirms*. R2's fallback is not needed.

**A7, close.**
- **Live pane.** `herdr-app do pane.close --pane <pane>` gave `{"ok": true}`, exit 0. The
  terminal became `finished` with `reason: "killed"` (claude: `exit_code` 129; opencode: 143).
  `hc ls --json` no longer lists it, and it is counted in `hidden_finished`. `hc get <t>` still
  answers.
- **`pane.close` returns before the end.** For codex, `hc get` immediately after the close still
  showed `live`, and showed `finished` a moment later.
- **Already gone.** `pane.close --pane <gone>` gave `{"error": "no pane \"<id>\""}` on
  **stdout**, with exit 1 and an empty stderr. `tab.close --id <gone> --confirmed true` gave
  `{"error": "no tab \"<id>\""}` on stdout, with exit 1.
- **Tests and verdict.** Tests H8. *Confirms*. H8 should treat exit 1 with `no pane` or `no tab` as
  "already gone".

**A8, the herd path.**
- **Worktrees.** `git worktree add -q -b jdi-herd-issue1 <scratch>/worktrees/repo/issue1
  origin/main` succeeded, and the same for `issue2`.
- **Spaces.** A space `main` was opened on `<scratch>/repo`. Then `herdr-app do space.new --name
  "Issue 1: probe label" --folder <scratch>/worktrees/repo/issue1 --tab issue1 --argv '["sh","-c",
  …]' --focus false` printed `{"space":"sp398b…","tab":"tbbd22…","terminal":"t11"}`.
- **Result.** `herdr-app ls` kept the name `Issue 1: probe label` and the tab `issue1`.
  `hc get t11` answered with `herdr.space` and `herdr.tab` labels. A screenshot of the sidebar shows
  the space nested under `main` with its branch `jdi-herd-issue1`.
- **Tests and verdict.** Tests P5 and D5. *Confirms*: the worktree is created alone, and the space
  can be opened later on the existing folder.

**A9, nesting.**
- **Command.** The same as A8 for `issue2`, without `--name`.
- **Result.** It is listed as `issue2`, named after its folder, and it nests under `main` exactly
  like the named space.
- **Tests and verdict.** *Confirms*: only git decides nesting.

**A10, the nested surface.**
- **Command.** `pane.split --argv '["<absolute herdr>","--session","<probe-session>"]'`.
- **Output.** `hc get <t>` showed `foreground.argv: ["<absolute herdr>","--session",
  "<probe-session>"]`. A shell in the TUI's pane carried both variable sets: `HERDR_ENV=1`,
  `HERDR_PANE_ID=w1:p1`, `HERDR_SOCKET_PATH=~/.config/herdr/sessions/<probe-session>/herdr.sock`,
  `HC_TERMINAL_ID=t13`, `HC_TERMINAL_SOCKET`, and `HC_SESSION`.
- **Stopping the TUI.** `herdr --session <probe-session> server stop` (through the guard) gave
  exit 0. The TUI exited and its split pane went with it, so a later `pane.close` gave `no pane`.
- **Tests and verdict.** Tests D2 and P4. *Confirms*: the observation is conclusive here. The
  inconclusive branch could not be produced, and nothing contradicts it.

**A11, no window.**
- **Closing the window.** All spaces were closed, then `herdr-app do window.close` gave
  `{"ok": true}`. `app.quit` is listed as "Quit (macOS)", so `window.close` is the Linux quit.
- **Status with no window.** `herdr-app status` then gave **exit 2**, an empty stdout and a
  non-JSON stderr: `herdr-app: no Herdr window at ~/.config/<probe-home>/herdr-app.sock:
  Connection refused (os error 111)`. `herdr-app ls` also gave exit 2.
- **The core kept running.** `hc ls --json` still answered (exit 0) and the core socket stayed.
  `window.close` ended only the throwaway window process, and the user's windows kept running.
- **On success**, `status` prints JSON with an `errors` list (`[]`).
- **Tests and verdict.** Tests D9 and P6. *Confirms*: a missing window fails the "parses as JSON"
  test. **Note for Task 03:** the Planner's fact that `status` prints `{"error": …}` on failure does
  not hold for a missing window. H1 must treat a non-zero exit or output that is not JSON as a
  failure.

**A12, the worker's writes.**
- **Command.** In each terminal started by `space.new --argv`: `mkdir -p "$(git rev-parse
  --absolute-git-dir)/jdi-runs/r1" && echo '{"ok":true}' > …/result.json`.
- **Output.** It wrote `<scratch>/repo/.git/jdi-runs/r1/result.json` (the main checkout),
  `<scratch>/repo/.git/worktrees/issue1/jdi-runs/r1/result.json` and
  `<scratch>/repo/.git/worktrees/issue2/…` (the linked worktrees).
- **Tests and verdict.** Tests H7 and the run directory. *Confirms*. An agent CLI's own sandbox is
  not exercised by this probe.

**A13, focus.**
- **Output.** `focused_pane` was the Butler pane before the split. After `pane.split --pane
  <butler pane> --direction right --argv …`, `focused_pane` was the **new** pane, and the same
  after a second split.
- **Restoring focus.** `herdr-app do pane.focus --pane <butler pane>` restored it.
- **Tests and verdict.** Tests P3. *Confirms* P3's "moves" branch: H4 appends `&& herdr-app do
  pane.focus --pane <butler pane>`.

**A14, the split folder.** The Butler space's folder is `<scratch>`, the parent of the repo.
- **Without the wrapper.** `pane.split --argv '["sh","-c","pwd > …; exec sleep 600"]'` gave
  `foreground.cwd` `<scratch>` (the Butler's folder), and `pwd` agreed.
- **With the wrapper.** `pane.split --argv '["sh","-c","cd -- \"$1\" && shift && exec
  \"$@\"","jdi-worker","<scratch>/repo","sh","-c",…]'` gave `foreground.cwd` `<scratch>/repo`.
  The terminal's own `cwd` stays `<scratch>`, which is the launch folder.
- **Tests and verdict.** Tests P2. *Confirms*.

**A15, the core's environment.**
- **PATH.** A split terminal's environment is the core's. Its `PATH` is the core launcher's
  `PATH` (here, the shell that auto-started the throwaway core), and its order differs from the
  Butler's interactive bash.
- **Kinds on that PATH.** `command -v` resolved `claude` →
  `~/.local/share/mise/command-wrappers/bin/claude`, `opencode` →
  `~/.local/share/mise/installs/npm-opencode-cli/latest/node_modules/.bin/opencode` and `codex` →
  `~/.local/share/mise/command-wrappers/bin/codex`, all absolute.
- **The Butler's own variable.** `JDI_BUTLER_ONLY`, exported only in the Butler's shell, is
  **absent** from the split terminal. It is the only key the two environments differ in.
- **Tests and verdict.** Tests P1 and D3. *Confirms*. The PATH a real core gives depends on how
  that core was started, which is P1's reason for absolute paths.

**A16, IDs and labels.**
- **ID forms.** `herdr-app ls` lists `"terminal": "t2"`, the same form as `HC_TERMINAL_ID=t1`.
- **Labels.** `hc label t2 jdi.agent=jdi-probe-a16 --json` succeeded (exit 0), and the labels kept
  `herdr.space` and `herdr.tab`. `hc ls --label jdi.agent=jdi-probe-a16 --json` returned only `t2`,
  and an unknown label returned `[]`.
- **Not the Butler's children.** Split, tab and space terminals all show `"parent": null` and
  `"die_with_parent": false` (`"notify": true`, which does nothing without a parent). So they
  are not the requester's children.
- **Tests and verdict.** Tests D5 and D4 (never `hc run`). *Confirms*.

**A17, argument forms.**
- **Accepted forms.** `--argv '<json>'` was accepted on `pane.split`, `tab.new` and `space.new`.
  `--focus false` was accepted on `tab.new` and `space.new`, and focus did not change.
- **A literal name.** `space.new --name "$NAME"`, where the shell value of `NAME` is
  ``q's $HOME `echo x` ``, is listed by `herdr-app ls` as exactly that string, with no expansion.
- **Tests and verdict.** Tests the A2 command forms. *Confirms*.

### Decisions not covered by a probe

- **D8.** `codex --no-daemon` is accepted as an argv element (codex-cli 0.169.0), so it can live in
  `harnesses.codex.args`. *Confirms*.
- **D10.** `--direction right` worked every time. No geometry was available to contradict it.
  *Confirms*.

### Cleanup

- **What was closed.** All spaces (`space.close --confirmed true`). `window.close` through the
  guard ended only the throwaway window. `hc server stop` through the guard gave
  `{"stopped":true}`. The A10 TUI was stopped with `herdr --session <probe-session> server stop`.
- **What was removed.** The throwaway home, `~/.local/state/herdr-core/<probe-session>/`,
  `~/.config/herdr/sessions/<probe-session>/` and
  `~/.local/state/herdr-automatic-rename/sessions/<probe-session>/`, followed by `git worktree
  prune` and removal of `<scratch>`. The Codex trust entry for `<scratch>/repo` was removed from
  `~/.codex/config.toml` (restored from a copy taken before the probe). The `~/.claude.json`
  `projects` entries under `<scratch>` were removed as well.
- **Checks afterwards.**
  - The user's `hc ls --json` still has 1 live terminal, unchanged.
  - The list of core state folders is unchanged.
  - Through the guard, `herdr-app status` exits 2.
  - The real repository's `git worktree list` has 1 entry.

Gate: stopped — contradicts D6 and D7 (pending amendment by the Butler and the user; no decision text changed)

Gate resolved 2026-11-16: the user chose "wait for idle, then `hc send --if idle`" (D6) and "reject at readiness" (D7); P6 refined by A11 and P10 narrowed. Decisions and task files 06, 08 amended; the gate is passed for Task 03 onward.

Gate: passed (after amendment)

## Tasks

**Wave 1** — run together
- [x] [01](01-herdr-surface-config-key.md) — Add the `herdr.surface` config key (depends on: none) — Planner Task 1
- [x] [02](02-live-app-probes.md) — Run the live Herdr app probes in a throwaway session (the probe gate) (depends on: none) — Planner Task 2

**Wave 2** — run together
- [x] [03](03-herdr-surfaces-h1-confinement.md) — `reference/herdr.md`: the two surfaces, H1 on each, and app-name confinement (depends on: 02) — Planner Task 3
- [x] [04](04-user-docs-herdr-surface.md) — User docs: `/jdi:init`, `/jdi:help` and the README name the Herdr surface (depends on: 01) — Planner Task 7
- [x] [05](05-architecture-docs.md) — Architecture docs: record the surfaces design as decided and probed (depends on: 02) — Planner Task 8

**Wave 3** — run together
- [x] [06](06-herdr-h2-h8-waves-app.md) — `reference/herdr.md`: app variants of H2–H8 and waves (depends on: 03) — Planner Task 4
- [x] [07](07-callers-step-zero-and-delegation.md) — Callers: the step-0 line in nine commands, and `reference/delegation.md`, name either surface (depends on: 03) — Planner Task 6, minus `commands/herd.md`

**Wave 4**
- [x] [08](08-h9-app-worktrees-and-herd.md) — H9 on the app (worktree create, open, list, remove) and `/jdi:herd` on either surface (depends on: 06) — Planner Task 5 + Task 6's `commands/herd.md` part

**Wave 5**
- [x] [09](09-release-1-0-11.md) — Release 1.0.11: version bump and CHANGELOG (depends on: 01, 02, 03, 04, 05, 06, 07, 08) — Planner Task 9

**Wave 6**
- [ ] [10](10-uat.md) — UAT: JDI under the Herdr app, the Herdr TUI, and neither (depends on: 01, 02, 03, 04, 05, 06, 07, 08, 09) — Planner Task 10, folded in

Critical path: 02 → 03 → 06 → 08 → 09 → 10 (six tasks).

Dependencies that exist only because of a shared file:
- 03 → 06 → 08 all edit `reference/herdr.md`.
- 03 → 07: both edit `tests/test_delegation_transport.py`. Task 07 also needs H1 to know about surfaces, which Task 03 adds.

The tasks are renumbered from the Planner's order so the numbers follow the waves. Each task file names its Planner task.
