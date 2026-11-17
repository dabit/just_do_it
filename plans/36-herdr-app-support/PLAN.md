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
- Merged: origin/main @ c7bc66b into this branch, 2026-11-16 (main had its own 1.0.10–1.0.12). Versions renumbered: PR #31's release is 1.0.13, this branch's is 1.0.14 (was 1.0.11; P12 and task 09's "1.0.11" are superseded).
- One PR (2026-11-16, user): PR #31 will be closed; this branch carries all the Herdr work in one PR against `main`, released as a single 1.0.13 (the 1.0.13/1.0.14 split above is superseded). Herd cleanup (#37) is added to this plan.

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

## Herd cleanup (#37) — plan

- Issue: #37 (https://github.com/dabit/just_do_it/issues/37)
- Added: 2026-11-16, same branch and PR as #36 (one Herdr PR, release 1.0.13, no version bump).
- Summary: `/jdi:herd --cleanup [<herd-id>]` driven by a herd record H9 writes under the git common dir.

### Decisions (Butler defaults adopted by the Planner, 2026-11-16)

- **C1 Record.** H9 writes `<git-common-dir>/jdi/herds/<herd-id>.json` (`<git-common-dir>` = `git rev-parse --path-format=absolute --git-common-dir`, so every worktree sees one record); shape in Appendix C, identical on both surfaces (keys that don't apply are `null`). Created on the first successful worktree, never before; written whole to `<dir>/.<herd-id>.json.tmp` then `mv -f` over the record; never edited in place; never committed. *Planner:* the record names no session and no app home ("Inherit, never set"); reachability is observed at cleanup. `worktree` is stored exactly as `git worktree list --porcelain` prints it, taken from the entry whose `branch` is `refs/heads/<scratch branch>`.
- **C2 Entry point.** `/jdi:herd --cleanup [<herd-id>]`, a mode of `commands/herd.md` (no new command file; counts unchanged). *Planner:* a herd ID must match `^[0-9]{8}T[0-9]{6}$` or the run refuses (JDI never builds a path from an unchecked argument); issue IDs or `--kind` alongside `--cleanup` stop the run with a sentence naming the two modes.
- **C3 Per entry.** Skip an agent that is `working` or `blocked`; if the record's surface is not reachable from here, say so, skip the space/workspace close, still offer the worktree removal marked "agent state unknown"; run the plan-file guard; show one list and ask once; close, then remove (app: space first); `--force` only when seeded. *Planner:* re-find every ID **by worktree path, never by a recorded ID alone** (app terminal IDs and TUI workspace IDs are reused): app = the `herdr-app ls` space whose `folder` is inside the path; TUI = the `herdr worktree list --cwd <main checkout>` entry whose `path` equals the record, via `open_workspace_id`. Busy is checked across the whole space/workspace (app: every terminal in `hc ls --json --label herdr.space=<space>`; TUI: the workspace's `agent_status`); a reattached session counts as busy. Own-location guard: skip an entry whose worktree contains the session running the cleanup, or whose space/workspace is the Butler's own. Run `git -C <worktree> status --porcelain` on the whole tree: anything shown + seeded → list the files, then `--force`; not seeded → skip "uncommitted changes". Entries with uncommitted plan files leave the batch and get their own yes, with the plan commit offered.
- **C4 Branches.** Delete only the recorded scratch branch, and only if its name is `jdi-herd-scratch-<record herd_id>-<n>`, it still exists, `git rev-list --count <base_commit>..refs/heads/<scratch>` is `0`, and its worktree is gone. Never delete any other branch. (Correction: `/jdi:prep` step 6 runs `git switch -c <branch> origin/<default>`, so it leaves the scratch branch behind at its base; it does not rename it.)
- **C5 Record upkeep.** Remove an entry once its worktree is no longer in `git worktree list --porcelain`; delete the file when the last entry goes. A listed-but-missing ("prunable") worktree keeps its entry and the user is told to run `git worktree prune`.
- **C6 No record.** No record (or an unknown herd ID): say so, clean nothing, point at `git worktree list` and step 11's manual commands. Never guess from folder names.
- **C7 Report.** Removed / skipped (with reason) per issue, plus the record's state.
- **C8 Herd report.** A normal herd's step 11 names `/jdi:herd --cleanup <herd-id>`.
- **C9 (Planner) Herd still running.** Record `state` is `creating` until step 10, `handed_off` after. Without an ID, cleanup skips `creating` records ("its herd may still be running; pass its herd ID to clean it anyway"); given its ID, a `creating` record is included but flagged.
- **C10 (Planner)** A record that cannot be written gets one sentence and the herd continues; step 11's manual commands still cover it.
- **C11 (Planner)** The cleanup steps are defined only in `reference/herdr.md` (H9); `commands/herd.md` calls them by name and never restates the rules.

### Order

Wave 8: 12 ‖ 13. Wave 9: 14 ‖ 15 ‖ 16 ‖ 17 (no shared files; all depend on 12's gate and 13). Wave 10: 18. Critical path 13 → 14 → 18 (and 12 → 14). Every text task: named tests first, `python3 -m unittest discover -s tests -p '<file>.py' -v` red on its own assertion, edit, green, full suite; one commit per task; no em dash in `reference/herdr.md`.

### Task 12 — probe gate for the cleanup mechanics
Files: PLAN.md only (`## Probe log (#37)`). Through the Appendix B guard, throwaway app session + home; the TUI nested as in A10 (`herdr --session <probe>`) on a scratch clone. Sanitised output.
- **R1 (TUI)** `herdr worktree create … --branch jdi-herd-scratch-T-1 --base origin/main`; inside, `git switch -c probe-feature` + one commit; record `herdr worktree list --cwd <clone>` fields (`path`, `branch`, `open_workspace_id`) and `herdr workspace get <ws>`'s `agent_status` shape; note whether either needs `--trust-repository` (never pass it; if needed, the TUI counts as unreachable).
- **R2 (TUI, safety)** `herdr worktree remove --workspace <ws>` on a clean tree: folder gone? workspace closed? do `probe-feature` and the scratch branch still exist? On a dirty tree without `--force`: does it refuse?
- **R3 (TUI)** `herdr workspace close <ws>` then `herdr worktree list` → expect `open_workspace_id: null`.
- **R4 (app)** `hc ls --json --label herdr.space=<space>` with an idle shell and with a Claude agent idle and working (a long counting prompt): where is the state (expected `status.state`), are `cwd` and `labels` present?
- **R5 (git)** porcelain path form when the path is given through a symlink; `git worktree remove` on a registered worktree whose folder was deleted (exit, message, `prunable`?); do ignored files alone, or untracked files, block a plain `git worktree remove`?
- **Gate:** R2 deletes a branch → TUI removal becomes `herdr workspace close <ws>` then `git -C <main checkout> worktree remove`. R4 has no state → busy check uses `hc get <terminal> --json` per listed terminal. R1 fields differ → amend Task 14's fragments. Record amendments here before Task 14. Clean up per Appendix B; the user's `hc ls --json` count unchanged.

### Task 13 — `reference/herdr.md`: `### The herd record`
Files: new `tests/test_herd_record.py`, `reference/herdr.md`.
1. Tests first, class `HerdRecordTest` modelled on `HerdCommandTest` (`tests/test_herd.py:35-56`):
   - `test_record_shape_matches_appendix_c`: raw lines of `jdi_files.section(text, "### The herd record")`, slice from the line equal to ```` ```json ```` to the next line starting with ```` ``` ````, `json.loads`, assert exact key sets — top `{schema, herd_id, created, surface, state, issues}`; `issues[0]` `{n, issue, name, worktree, scratch_branch, base_commit, seeded, created, herdr}`; `issues[0]["herdr"]` `{workspace_id, space_id, tab_id, pane_id, terminal_id, agent_name}`. The fence starts at column 0.
   - `test_record_heading_is_inside_h9`: `### The herd record` after `## H9 - Give a Butler its own worktree` and after `### H9 on the app`.
   - `test_record_location_and_lifecycle`: `git rev-parse --path-format=absolute --git-common-dir`, `<git-common-dir>/jdi/herds/<herd-id>.json`, `never committed`, `one file per herd`, `mv -f`, `never edited in place`, `names no session and no app home`.
   - `test_record_write_points`: `step 6`, `step 7`, `step 8`, `step 10`, `` `creating` ``, `` `handed_off` ``, `git worktree list --porcelain`, `refs/heads/<scratch branch>`, `git -C <path> rev-parse HEAD`, `the herd continues`.
   - `test_create_steps_point_at_the_record`: the `## H9` lines before `### H9 on the app` contain `*The herd record*`, and so does `### H9 on the app`.
2. Append `### The herd record` after `### H9 on the app` with Appendix C verbatim; C1, C9, C10; write points: step 6 after each create (append the entry; TUI fills `workspace_id`, `tab_id`, `pane_id`, `agent_name`), step 7 (`seeded: true` when a seed step wrote into the worktree), step 8 app only (`space_id`, `tab_id`, `pane_id`, `terminal_id`, `agent_name`), step 10 (`state: handed_off`). One sentence pointing at *The herd record* under the shared `**Create it.**` and the app's `**Create it**`. Placeholders only; no `/home/`, no em dash.

### Task 14 — `reference/herdr.md`: `### Cleanup from the herd record`
Files: `tests/test_herd_record.py`, `reference/herdr.md`.
1. Tests first, class `HerdCleanupFromRecordTest` (section after `### The herd record`):
   - `test_selects_records_safely`: `` `^[0-9]{8}T[0-9]{6}$` ``, `never builds a path from`, `` `creating` ``, `Never guess from folder names`, `git worktree list`.
   - `test_resolves_by_worktree_path` (per Task 12's gate): `never by a recorded ID alone`, `herdr-app ls`, `hc ls --json --label herdr.space=<space>`, `herdr worktree list --cwd <main checkout>`, `open_workspace_id`, `herdr workspace get <workspace_id>`.
   - `test_skips`: `` `working` or `blocked` ``, `not reachable from here`, `agent state unknown`, `the session running the cleanup`, `prunable`, `git worktree prune`.
   - `test_guards_and_force`: `git -C <worktree> status --porcelain -- <plans.path>`, `git -C <worktree> status --porcelain`, `` `--force` only when the entry's `seeded` is true ``, `uncommitted changes`, `one list`, `asks once`, `its own yes`.
   - `test_scratch_branch_rule`: `jdi-herd-scratch-<herd-id>-<N>`, `git show-ref --verify --quiet refs/heads/<scratch branch>`, `git rev-list --count <base_commit>..refs/heads/<scratch branch>`, `git branch -D <scratch branch>`, `Never delete any other branch`.
   - `test_record_upkeep`: `removes the entry`, `deletes the record file`.
   - `test_removal_order` (precedent `test_h9_app_cleanup_order`, `tests/test_herd.py:200-217`; deviation: indices only in the normalised text after `**The removal, per entry, in this order:**`): plan-file status `-- <plans.path>` < `herdr-app do space.close --id <space> --confirmed true` < `git -C <main checkout> worktree remove` < `git branch -D <scratch branch>` < `removes the entry`.
2. Write the section with C2–C7, C9, C11: choosing the records; H1's answer against the record's `surface`; per entry (find by path, own-location guard, busy, plan-file guard, whole-tree status and force decision); one list, one question (plan-file entries get their own); the numbered removal under the marker (plan re-check; app `space.close` / TUI the Task 12-gated command; remove the worktree; branch rule; update the record); the per-issue report. One pointer sentence in the TUI `**Cleanup.**` paragraph and the app's `**Cleanup (remove)**`. Keep every pinned H9 fragment.

### Task 15 — `commands/herd.md`: the `--cleanup` mode
Files: `commands/herd.md`, `tests/test_herd.py`.
1. Tests first:
   - In `test_herd_drops_the_superseded_keys_and_tools` drop `"herd record"` (keep `"--resume"`), with a comment: #31 banned a *resume* record (D12); #37's record is for cleanup only. Not red-first; say so.
   - `test_herd_cleanup_mode`: `` `--cleanup` ``, `` `/jdi:herd --cleanup <herd-id>` ``, `*The herd record*`, `*Cleanup from the herd record*`, `asks once`, `Never guess from folder names`, `never names or resumes a session`, `cleanup never stops on H1's answer`.
   - `test_argument_hint_names_cleanup`: `argument-hint` contains `--cleanup [<herd-id>]`.
   - `test_step_eleven_points_at_cleanup`: the paragraph starting `11. **Say how to clean up` contains `` `/jdi:herd --cleanup <herd-id>` ``.
   - `test_prep_leaves_the_scratch_branch_behind`: contains `leaves the scratch branch behind`, not `` `/jdi:prep` renames the branch ``.
   - Confinement already scans this file: write "closes the space or workspace", never the app action name.
2. Edits: frontmatter `description` + cleanup clause, `argument-hint: "<issue-id> [<issue-id> ...] [--kind <kind>] | --cleanup [<herd-id>]"`; after the `$ARGUMENTS` paragraph, "with `--cleanup`, perform step 1, then *Clean up a herd from its record* below, instead of steps 2–11"; step 5 (record path; take a new herd ID if a record with it exists); steps 6, 7, 8 one sentence each on what H9 records; step 10 prints the record path and replaces the "renames the branch" sentence; step 11 adds C8, keeps the manual commands; new `## Clean up a herd from its record` before `## Limits worth stating in the report`: config (step 1) → parse args and validate the herd ID (C2) → H1 only to learn which surface is reachable → find the records (*The herd record*) → sort entries (*Cleanup from the herd record*) → one list, one question → remove → report (C7). No restated rules (C11).

### Task 16 — user docs and CHANGELOG
Files: `README.md`, `commands/help.md`, `AGENTS.md`, `CHANGELOG.md`, `tests/test_transport_docs.py`.
1. Tests first, class `HerdCleanupDocumentationTest`: help row starting `` | `/jdi:herd` | `` contains `` `--cleanup` ``; the README paragraph starting `` `/jdi:herd --cleanup `` contains `herd record`, `never committed`, `asks once`; the `## 1.0.13` CHANGELOG section contains `` `/jdi:herd --cleanup [<herd-id>]` ``.
2. README: new paragraph after the `/jdi:herd ENG-1234` paragraph (record under the git dir, never committed; what is skipped; one question; only scratch branches with no commits of their own are deleted; no app command names). Help: the `--cleanup [<herd-id>]` clause in the `/jdi:herd` row. AGENTS.md: matching clause in the herd row (not pinned; say so). CHANGELOG: a bullet after the `/jdi:herd` bullet in `## 1.0.13`; no version bump.

### Task 17 — architecture docs
Files: `docs/herdr-surfaces-architecture.md`, `docs/delegation-transport-architecture.md`, `tests/test_herdr_surfaces_doc.py`.
1. Tests first: `## The herd record` in `PRESENT_HEADINGS`, containing `` `jdi/herds/<herd-id>.json` ``, `` `--git-common-dir` ``, `never by a recorded ID alone`; `## Operation map` rows starting `| H9 Herd record |` and `| H9 Cleanup from the record |`; the transport doc no longer contains `is planned in the same branch as a separable wave`, and its `## Two layers` contains `` `/jdi:herd --cleanup` ``.
2. Surfaces doc: Status names #37; the two map rows (TUI and app columns, per the Task 12 gate); the new section (C1–C11 and Task 12 results; no `/home/`). Transport doc: fix the stale Status sentence; one cleanup sentence in `## Two layers`.

### Task 18 — UAT (agent smoke test)
Files: PLAN.md (`## UAT log (#37)`). Appendix B guard, throwaway session + home, scratch clone with `tracker: {name: none}`, Butler `claude --plugin-dir <repo>` in a throwaway space (as Task 10). No Codex. Scenarios:
- (a) Herd + record: `/jdi:herd 201 202 203` on the app → record with `surface: app`, IDs after step 8, `state: handed_off`, report names `--cleanup <herd-id>`.
- (b) Busy: driver sends 202 a long prompt → cleanup skips 202 as `working`.
- (c) Plan guard: uncommitted `plans/x/NOTE.md` in 201 → its own question; nothing of 201 touched.
- (d) Branches: in 203 `git switch -c feat-203` + commit → worktree removed, `feat-203` kept, scratch deleted; an entry with a commit on its scratch branch → scratch kept.
- (e) Upkeep: entries drop as worktrees go; file deleted after the last; a rerun says no record.
- (f) No record: a clone with no herds → C6 message, nothing removed.
- (g) Bad ID: `--cleanup ../x` refused.
- (h) Own location: cleanup from inside a herd space skips that entry.
- (i) Seeded: `herd.seed.setup: ["touch untracked-seed.txt"]` → the file listed, removal forced.
- (j) TUI, if cheap: one-issue herd in a nested throwaway TUI → record `surface: tui`; cleanup there finds the workspace through `herdr worktree list`; cleanup from the outer app space reports "not reachable" and still offers the worktree.
- Repository scans: confinement, no personal paths, full suite. Clean up per Appendix B (user's `hc ls` count and real `git worktree list` unchanged). Real acceptance stays with the user.

### Appendix C — herd record shape (verbatim; must stay valid JSON)
```json
{
  "schema": 1,
  "herd_id": "<yyyymmddThhmmss>",
  "created": "<UTC yyyy-mm-ddThh:mm:ssZ>",
  "surface": "<tui | app>",
  "state": "<creating | handed_off>",
  "issues": [
    {
      "n": 1,
      "issue": "<ISSUE-ID>",
      "name": "<slug>-<suffix>",
      "worktree": "<path as git worktree list --porcelain prints it>",
      "scratch_branch": "jdi-herd-scratch-<herd-id>-<N>",
      "base_commit": "<full SHA of the worktree's HEAD right after creation>",
      "seeded": false,
      "created": "<UTC yyyy-mm-ddThh:mm:ssZ>",
      "herdr": {
        "workspace_id": "<TUI workspace, else null>",
        "space_id": "<app space, else null>",
        "tab_id": "<tab the agent runs in>",
        "pane_id": "<the agent's pane>",
        "terminal_id": "<app terminal, else null>",
        "agent_name": "<name>"
      }
    }
  ]
}
```

### Testing strategy (#37)
| Task | Proof | Fails when |
|---|---|---|
| 12 | probe log + gate | R2 deletes a branch, or R4 shows no state |
| 13 | `HerdRecordTest` | a key renamed/dropped in the fence; `--git-common-dir` swapped for `--absolute-git-dir` |
| 14 | `HerdCleanupFromRecordTest` | the `rev-list --count` guard removed; branch deletion before worktree removal or `space.close` after it; "never by a recorded ID alone" removed |
| 15 | new `test_herd.py` methods + confinement | the step-11 pointer removed; `space.close` written into `commands/herd.md` |
| 16 | `HerdCleanupDocumentationTest` | help row, README paragraph or CHANGELOG bullet loses `--cleanup` |
| 17 | `test_herdr_surfaces_doc.py` additions | record section or map rows missing; stale Status sentence present |
| 18 | UAT log | any of (a)–(j) deviates |

The rules live in `reference/herdr.md` and are guarded by `tests/test_herd_record.py`; `tests/test_herd.py` only proves the command calls them. Not unit-observable (record actually written atomically, path resolution, skips, `--force`, branch deletion, TUI removal semantics): proved by Task 12's probe log and Task 18's UAT log. Not red-first: the loosened ban (Task 15) and the AGENTS.md row (Task 16).

### Risks (#37)
- **R11** Reused IDs close the wrong space/workspace → resolve everything by path (C3).
- **R12** TUI removal deletes a branch → unknown until R2; the gate amends the command.
- **R13** Forced removal loses non-plan work in seeded worktrees → whole-tree status listed before the single yes.
- **R14** Closing the Butler's own space mid-run → own-location guard.
- **R15** Two concurrent cleanups: last writer wins; self-healing on the next run.
- **R16** A record stuck at `creating` after a crash → skipped without an ID, cleaned with one.
- **R17** `--path-format=absolute` needs git ≥ 2.31 (already needed by H9 on the app); `mv -f` is POSIX; Windows unverified.
- **R18** A blocked-at-startup agent can't be cleaned while its dialog is open → the skip reason tells the user to answer it or close the space.

## Herd modes and untracked tasks (#38) — plan

- Issue: #38 (https://github.com/dabit/just_do_it/issues/38)
- Added: 2026-11-16, same branch and PR, release 1.0.13, no version bump. Base: `2f30a28` (219 tests OK).
- Summary: `herd.mode: do | prep` (default `do`); in `do` mode a too-big `/jdi:do` continues into `/jdi:prep` in the same session; `/jdi:herd` also takes free-text tasks whose name, folder and record entry come from the text.

### Decisions

User (2026-11-16): **U1** `herd.mode: do | prep`, default `do`; a herd-started too-big `/jdi:do` continues into `/jdi:prep` in the same session. **U2** free-text tasks alongside issue IDs, no tracker needed. **U3** this branch, same PR. **M1 and M4 approved by the user** (below).

- **E1 How do learns it is in a herd.** Every herd invocation ends with a fixed clause: `(started by /jdi:herd)` for an issue, `(untracked, started by /jdi:herd)` for a task. do.md step 5's *Too big* bullet gains a rule that applies only when the stop is found **before step 6 has changed anything**: say so in one line, push nothing, note nothing on the issue, follow prep's steps on the same request in this session. Branching checked: do step 2 (`commands/do.md:60-63`) creates the feature branch with T6 from `origin/<default>` before step 3; prep step 6 (`commands/prep.md:79-86`) only runs `git switch -c` "if the current branch does not already name this work", so prep keeps do's (unpushed, commit-less) branch; a fallback from do step 1 (a container with no children) happens before step 2, so prep creates its own branch. No PR exists (do opens one at step 8). After step 6 has changed anything the normal *too big* stop applies. Standalone `/jdi:do` is unchanged.
- **E2 do's other stops** (a product decision, a change the repo reserves for a person, a review that won't converge, a PR it cannot open) leave the agent waiting in its space. Correction to the Butler default: that is a finished turn, so the sidebar shows `done` (same as a merged agent); the report says to open the space to see which.
- **E3 Parsing (refined).** In herd.md step 3: a quoted argument (`"…"` or `'…'`, opened at the start of an argument) is always a task; an unquoted argument is an issue ID only when a tracker is configured and it has an issue's shape (an issue URL, `#<digits>` or `<digits>` for GitHub, or `<KEY>-<digits>`; with `tracker.id_prefix` set, `<KEY>` must be that prefix); with no tracker configured, nothing is an issue ID; any other unquoted words, or an unmatched quote, are ambiguous — each run joined into one candidate task — and the herd shows its whole reading, asks once, and starts nothing before the answer.
- **E4 Naming untracked tasks.** Suffix = `t` + first 6 hex of `printf '%s' '<normalised task>' | git hash-object --stdin` (normalised = lowercased, whitespace runs collapsed, ends trimmed). A hash, not an index: the same text always gives the same suffix, so H9's suffix check still finds an earlier folder for that task; an index would make every herd's first task `t1`. Worked example: `fix the typo in the signup email` → `96ae2d07982d30fb9e3b6a127640b39f0f7bb696` → `t96ae2d` → `fix-typo-signup-email-t96ae2d`. Label / space name `<suffix> <task text>`. Record: `issue` may be `null`; new key `task` (text without the clause, `null` for an issue); `schema` stays `1` (additive; record never shipped; a missing `task` reads as `null`). Cleanup reports a `null`-issue entry by `name` and task text.
- **E5 No tracker work for tasks.** Tasks skip T2 and every tracker step; no `jdi-herd-<issue>` fallback; nothing read from or posted to a tracker. `{{issue}}` / `{{issue_lower}}` expand to the task's suffix.
- **E6 Docs and config.** CHANGELOG, README, help, herd.md and `reference/config.md` say plainly that `do` mode merges unattended and in parallel, `herd.mode: prep` is the way back. Repo-level key in `config.yml` (five-question test: team policy differs per repo; no repo states it; not a harness fact; degradation: invalid → `prep`, too-big do → prep, a repo forbidding merges stops do before merge, no PR host stops do at step 8). **Recorded deviation** from `docs/config-key-lifecycle.md`: `do` is not the least-demanding default; U1 chose it, and no herd has shipped (`commands/herd.md` is not on `origin/main`). Init offers the key in step 10's existing herd sub-bullet (no new numbered step; herd / `herdr.surface` precedent).
- **E7 The switch is visible:** one line "too big for one session, because …, continuing with `/jdi:prep`" before prep's step 1.
- **E8 UAT** (task 26): guard additions below; small scratch repo with a local bare `origin`; with no GitHub remote do pushes to the bare `origin` and stops at step 8 with the reason (acceptable, stated; no do.md rule); rebase-on-conflict and merge-in-a-worktree are user scenarios.
- **M1 (approved)** Prep mode's invocation carries the clause too; prep step 2 gains: the herd answered step 2's and step 3's questions (an issue uses the configured tracker; `untracked` means not tracked) — ask neither; the clause is not part of the work. Only herd-started preps are affected.
- **M2 Quoting.** The invocation is one shell argument, single-quoted, never double-quoted, `'` written `'\''`: TUI `herdr agent prompt <name> '<invocation>'`, app `hc send <terminal> '<invocation>' --if idle`, TUI label `--label '<SHORT-ID> <TITLE>'` (double-quoted today). Task text is one line: whitespace runs incl. line breaks collapse to one space (a typed line break can submit early).
- **M3** Invalid `herd.mode` → announced once, runs as `prep` (less authority), never the other way.
- **M4 (approved)** do.md step 10: when the PR stops merging cleanly because the default branch moved, update the branch from `origin/<default>` the way the repo allows, re-run step 7's gates, push, wait for checks on the new head; a conflict needing a product decision is a step-5 stop. Applies to standalone `/jdi:do` too.
- **M5** herd step 8 announces the mode before the first start (in `do`: each agent opens and merges its own PR, unattended, in parallel). The herd invocation is the authorization, as do's request is.
- **M6 Where rules live.** Parsing: herd.md step 3. Naming + task suffix: herd.md step 5 (H9 *Names* gets a pointer + label + no-fallback rule). Invocation table, clause, quoting, record: H9. herd.md calls H9 by name (as C11).
- **M7** No `--mode` flag; no `mode` field in the record.
- **M8** The fallback resolves prep as `${CLAUDE_PLUGIN_ROOT}/commands/prep.md`, or, if that does not resolve, the prep command file beside this one (OpenCode: `jdi-prep.md`). Codex/OpenCode fallback unverified (R24, u7).

### Order (#38)

Wave 11: 20 ‖ 21. Wave 12: 22 ‖ 23 ‖ 24 ‖ 25 (22: `commands/do.md`, `commands/prep.md`, `tests/test_herd_handoff.py`; 23: `commands/herd.md`, `tests/test_herd.py`; 24: `README.md`, `commands/help.md`, `commands/init.md`, `AGENTS.md`, `CHANGELOG.md`, `tests/test_transport_docs.py`; 25: two docs + `tests/test_herdr_surfaces_doc.py`) — all depend on 21; 24 also on 20. Wave 13: 26. Critical path 21 → 22/23 → 26. Expected test methods: 233 after wave 11, 256 after wave 12 (executors report actual). TDD rhythm as before; one commit per task; no em dash in `reference/herdr.md`; `commands/herd.md` uses ` - `. Fences in Appendix M are literal physical lines (table rows, YAML, commands byte for byte); prose may be rewrapped unless noted.

### Task 20 — the `herd.mode` key
Files: `tests/test_config_schema.py`, `reference/config.md`, `jdi.config.example.yml`.
1. Tests first, in `HerdBlockTest`: `test_mode_is_a_schema_key` (`herd.mode` in `key_paths(schema)`); `test_schema_default_is_do` (`^  mode: do$`); `test_schema_comment_lists_mode_values` (a comment line exactly `  # do | prep`); `test_schema_comment_says_do_merges` (`opens its pull request and merges it,`); `test_example_mode_is_not_the_default` (`^  mode: prep$`); `test_defaults_table_covers_herd` + ``("herd.mode", "`do`")``; `test_notes_say_do_mode_merges_unattended` (``**`herd.mode: do` opens and merges pull requests unattended.**``); `test_notes_say_invalid_mode_runs_prep` (``An invalid `herd.mode` is announced once and runs as `prep` ``); `test_notes_say_do_and_prep_learn_from_the_invocation` (`learn they run in a herd from the invocation`). Update the class docstring.
2. `reference/config.md`: M-A schema lines after `  kind: claude`; herd intro comment → "Read only by /jdi:herd, which runs several issues or untracked tasks in parallel, one Herdr worktree and agent each."; `{{issue}}`/`{{issue_lower}}` comment lines + "(an untracked task: its suffix)"; defaults row ``| `herd.mode` | `do` - each herd agent runs `/jdi:do` and merges its own pull request; `prep` stops each at a plan |``; Notes: M-A's two bullets and the appended sentence.
3. `jdi.config.example.yml`: in `herd:` after `  kind: opencode`, a two-line comment then `  mode: prep`.
4. Verify: module green; full suite; `grep -rn "herd.mode" reference/config.md jdi.config.example.yml` shows schema, defaults, notes, example.

### Task 21 — H9: modes, clause, quoting, tasks, record
Files: `reference/herdr.md`, `tests/test_herd.py`, `tests/test_herd_record.py`.
1. Tests first. `tests/test_herd.py`: replace `INVOCATION_ROWS` with the four M-B table lines (header + 3 rows); `test_h9_app_hands_off_by_send` fragment → `hc send <terminal> '<invocation>' --if idle`; in `test_h9_uses_the_title_name_suffix_match_and_title_label` the label fragment → `--label '<SHORT-ID> <TITLE>'` plus `assertNotIn('--label "', h9)`; new `test_h9_invocation_by_mode_and_clause` (normalized H9 contains `` `herd.mode` ``, `` `(started by /jdi:herd)` ``, `` `(untracked, started by /jdi:herd)` ``, `it is not part of the work`, `collapsed to one space`); new `test_h9_invocation_is_single_quoted` (H9 contains `` `herdr agent prompt <name> '<invocation>'` `` and `single-quoted, never double-quoted`; H9 does NOT contain `"<invocation>"`); new `test_h9_untracked_task_label_and_no_fallback` (`` `<suffix> <task text>` ``, ``has no `jdi-herd-<issue>` fallback``). `tests/test_herd_record.py`: the shape test's entry key set gains `"task"`; new `test_record_untracked_entry` (`` `null` for an untracked task ``, `` `schema` stays `1` ``, `` a missing `task` as `null` ``); new `test_cleanup_reports_tasks_by_name` (cleanup section: `` reported by its `name` and its task text ``); new `test_scratch_branch_reason_names_do` (cleanup section: `` `/jdi:do` and `/jdi:prep` both leave the scratch branch behind ``).
2. `reference/herdr.md`, H9 only: intro "running the herd's command, `/jdi:do` or `/jdi:prep` by `herd.mode`"; *Names*: "one name per issue or task", pointer to herd.md step 5 for a task's suffix, and M-C; existing-folder check "or, for an issue, is named `jdi-herd-<issue>`"; TUI create fence `--label '<SHORT-ID> <TITLE>'` and the quoting sentence → "single-quoted, with a `'` written as `'\''`"; invocation table → M-B (keep the "These spellings come from…" paragraph); TUI handoff `herdr agent prompt <name> '<invocation>'`; app handoff fence `hc send <terminal> '<invocation>' --if idle` and "the prep command must arrive typed" → "the herd's command must arrive typed"; record fence `"issue": "<ISSUE-ID, else null>",` then next line `"task": "<task text, else null>",` (column-0 fence, valid JSON) + M-D write-rule bullet; cleanup step 4 reason and *The report* sentence per M-D; app space-name bullet "the issue title …, or `<suffix> <task text>` for an untracked task".
3. Verify: both modules green; full suite; `grep -n '"<invocation>"\|--label "' reference/herdr.md` prints nothing.

### Task 22 — `/jdi:do` and `/jdi:prep` honour the herd clause (+ M4)
Files: `commands/do.md`, `commands/prep.md`, new `tests/test_herd_handoff.py`. Depends on 21 (reads H9).
1. Tests first, using `jdi_files.paragraph_starting_with` (deviation from `DoPlanShapeTest`: its `step()` lives in `test_structural_checks.py`, importing it would run its classes twice; `paragraph_starting_with` stops at the first blank line, so every insertion must stay inside its paragraph):
   - `test_too_big_in_a_herd_continues_with_prep`: paragraph starting `   - **Too big for one session.**` (do.md), flattened; every fragment lies between the index of `**Too big for one session.**` and of `**A product decision outside the request.**`: `` `(started by /jdi:herd)` ``, `` `(untracked, started by /jdi:herd)` ``, `before step 6 has changed anything`, `do not hand back`, `Say in one line that the work is too big for one session`, ``continue with `/jdi:prep` ``, `in this session`, `Push nothing`, `prep's step 6 keeps the branch step 2 created`.
   - `test_standalone_too_big_still_hands_back`: same paragraph still has ``Recommend `/jdi:prep` with what you learned``.
   - `test_clause_is_not_part_of_the_work`: do paragraph `1. **Identify the work**` contains `that clause is not part of the work`.
   - `test_merge_updates_a_branch_the_default_moved_under`: paragraph `10. **Merge**` contains `a parallel change merged first`, `run step 7's gates again`, `a step-5 stop`.
   - `test_prep_takes_the_herds_tracking_answer`: prep paragraph `2. **Determine the tracking context**` contains both clauses, `Ask neither`, `The clause is not part of the work`.
   - `test_clauses_match_h9`: both backticked clauses appear in H9's normalized section, in do.md and in prep.md.
2. Append M-E text to: the first paragraph of do step 1 (`:48-51`), the *Too big* bullet (`:89-91`), step 10's paragraph (`:139-143`), prep step 2 (`:51-53`). No blank line inside those paragraphs; don't renumber.
3. Verify: module green; full suite (confinement scans both files); `DoPlanShapeTest` and prep's structural tests stay green.

### Task 23 — `commands/herd.md`: modes, tasks, report
Files: `commands/herd.md`, `tests/test_herd.py`. Depends on 21.
1. Tests first, with a local helper `step_text(text, n)` (from the first line starting `"%d. **" % n` to the next line matching `^\d+\. \*\*` or `^## `):
   - `test_herd_reads_the_mode` (step 1): `` `herd.mode` ``, `` announced once and runs as `prep` ``.
   - `test_herd_parses_issues_and_tasks` (step 3): `A quoted argument is always a task`, `an issue ID only when a tracker is configured`, `` `tracker.id_prefix` ``, `With no tracker configured, no argument is an issue ID`, `ask once`, `Never guess`, `start nothing before the answer`.
   - `test_tasks_skip_the_tracker` (step 3): `Tasks skip **T2** and every other tracker step`, `nothing is read from or posted to a tracker for a task`.
   - `test_task_suffix_is_a_stable_hash` (step 5): `printf '%s' '<normalised task>' | git hash-object --stdin`, `` `t96ae2d` ``, `` `fix-typo-signup-email-t96ae2d` ``, `an index in the herd would give every herd's first task the same suffix`.
   - `test_task_suffix_example_is_reproducible`: take the herd.md line whose stripped form starts with `printf '%s' '<normalised task>'`, substitute `fix the typo in the signup email`, run `subprocess.run(["sh","-c",cmd], cwd=jdi_files.ROOT, capture_output=True, text=True)`, assert `stdout.strip()[:6] == "96ae2d"` (precedent `tests/test_structural_checks.py:84`; `hash-object` without `-w` writes nothing).
   - `test_mode_announced_before_start` (step 8): `opens and merges its own pull request`, `` `herd.mode: prep` ``.
   - `test_report_names_do_mode_stops` (step 10): `` a `do` agent that stopped ``, `` the sidebar shows `done` for it ``.
   - `test_cleanup_refuses_tasks_alongside`: `` Issue IDs, tasks or `--kind` ``.
   - `test_argument_hint_names_tasks`: hint contains `'task text'` and `--cleanup [<herd-id>]`.
   - Existing pins must survive: `one name per issue`, `perform **T2**`, `` falls back to the old name `jdi-herd-<issue>` for that issue and says so once ``, `The workspace label is the issue title`, `leaves the scratch branch behind`, `` never fall back to a sequential `/jdi:prep` ``.
2. Edits: frontmatter (M-F); intro "one session per issue or task, each running `/jdi:do` or `/jdi:prep` by `herd.mode`"; step 1 `herd.mode`, default `do`, M3; step 3 → M-F parse rules; step 5 "one name per issue or task" + M-F task bullet; step 6 task label `<suffix> <task text>` and "continue there … `/jdi:status`, or `/jdi:do` again where no plan exists"; step 7 placeholder rows "(an untracked task: its suffix, e.g. `t96ae2d`)"; step 8 M5 announcement; step 9 "H9's invocation table for the kind and `herd.mode`, with `<WORK>` filled in"; step 10 one row per issue or task, the mode, the M-F do-stop sentence, and the scratch sentence → "`/jdi:do` or `/jdi:prep` leaves the scratch branch behind at its base …"; step 11 "a prep-mode worktree, or one whose `do` agent continued with prep, usually holds an uncommitted plan"; cleanup step 2 "Issue IDs, tasks or `--kind`"; Limits: two bullets "`do` mode ships unattended" and "Parallel merges can conflict".
3. Verify: module green; full suite; confinement green.

### Task 24 — user docs and CHANGELOG
Files: `README.md`, `commands/help.md`, `commands/init.md`, `AGENTS.md`, `CHANGELOG.md`, `tests/test_transport_docs.py`. Depends on 20, 21.
1. Tests first, class `HerdModeDocumentationTest` (precedent `HerdCleanupDocumentationTest`): help row starting `` | `/jdi:herd` | `` has `` `/jdi:do` ``, `` `herd.mode: prep` ``, `merges`; help opening paragraph (normalized) has ``which herd mode is set, when not `do` ``; init.md has `` offer `herd.mode` ``; README paragraph starting `` `/jdi:herd ENG-1234 `` has `` `herd.mode` ``, `unattended`, `in parallel`, `` `herd.mode: prep` ``, `"fix the typo in the signup email"`; `## 1.0.13` section has `` `herd.mode` ``, `unattended`, `in parallel`, `` `herd.mode: prep` ``, `untracked`.
2. README: rewrite the herd paragraph to open with `` `/jdi:herd ENG-1234 "fix the typo in the signup email"` `` covering modes, fallback, stops and the way back; help: herd row, closing-line clause, unpinned `/jdi:do` row clause "(under `/jdi:herd` it continues with `/jdi:prep` instead)"; init step 10 herd sub-bullet offers `herd.mode` (what `do` does; a team choice for `config.yml`); AGENTS.md herd row (unpinned; say so); CHANGELOG headline names `/jdi:do` + a bold bullet after the `--cleanup` bullet.
3. Verify: module green; full suite; `VersionTest` green (no bump).

### Task 25 — architecture docs
Files: `docs/herdr-surfaces-architecture.md`, `docs/delegation-transport-architecture.md`, `tests/test_herdr_surfaces_doc.py`. Depends on 21.
1. Tests first: `test_operation_map_single_quotes_the_invocation` (row `| H9 Hand it the work |` has `` `herdr agent prompt <name> '<invocation>'` `` and `` `hc send <terminal> '<invocation>' --if idle` ``, and no `"<invocation>"`); `test_herd_record_section_names_task` (`## The herd record` has `` `task` `` and `` `/jdi:do` ``); `test_two_layers_names_herd_mode` (`## Two layers` has `` `herd.mode` `` and `` `/jdi:do` ``).
2. Surfaces doc: the map row's quoting; record bullets (the `task` key; "`/jdi:do` and `/jdi:prep` start the real work …"); Status names #38. Transport doc: *Two layers* (agents run `/jdi:do` or `/jdi:prep` by `herd.mode`) and *Isolation* (in `do` mode each opens and merges its own PR; a later one updates its branch).
3. Verify: module green; full suite.

### Task 26 — UAT (agent smoke test)
Files: PLAN.md (`## UAT log (#38)`, directly above `## Tasks`). Depends on 20–25.
**Guard** `<scratch>/g` (#37's plus E8): refuse unless `JDI_PROBE_SESSION` and `JDI_PROBE_HOME` are set and the session matches `jdiprobe-*`; unset the nine `HC_*`/`HERDR_*` variables, `CLAUDECODE`, `CLAUDE_CODE_*`, `CLAUDE_PID`, `CLAUDE_EFFORT`, `GH_TOKEN`, `GITHUB_TOKEN`, `GH_REPO`, `GH_HOST`, `GH_ENTERPRISE_TOKEN`; export `HC_SESSION`, `HERDR_APP_HOME`, `GH_CONFIG_DIR=<scratch>/gh-empty`; `HERDR_SOCKET_PATH=<scratch>/no-tui/herdr.sock` (nonexistent) unless `JDI_PROBE_TUI=1`, then the throwaway TUI's socket (refuse if missing). **Self-checks logged first:** refusal exit 64 with 0 stdout bytes; `<scratch>/g herdr status` exits non-zero and the user's `herdr session list` (read-only, outside the guard) is identical before and after (VERIFY-AT-EXECUTION: if it creates anything under `<scratch>/no-tui/`, record and stop it through the guard); `<scratch>/g gh auth status` reports not logged in. **Snapshots** (outside the guard, read-only): user's `hc ls --json` count, real repo `git worktree list`, `~/.claude.json` project keys.
**Scratch repo** `<scratch>/repo` cloned from bare `<scratch>/origin.git` (`origin/HEAD` → `main`): `README.md` with `Install into $HOME/bin and recieve updates.`; `greet.py` + `test_greet.py` (stdlib unittest); `AGENTS.md` (tests run with `python3 -m unittest`); `.gitignore` with `.jdi/config.local.yml`; committed `.jdi/config.yml` (`tracker: {name: none}`, `tdd.enabled: false`, `jev.enabled: false`). Local config (Butler's):
```yaml
herd:
  kind: claude
  mode: do
harnesses:
  claude:
    args: ["--model", "sonnet", "--plugin-dir", "<this repo>", "--settings", '{"enabledPlugins":{"jdi@just-do-it":false}}']
```
(herd agents load this branch's plugin; pre-trust `<scratch>/repo` only; the Butler is `claude --plugin-dir <this repo> --settings '…'` as the argv of a throwaway `space.new`, asking its questions in plain text.)
**Scenarios:**
- (a) do-mode herd: `/jdi:herd "fix the typo 'recieve' in README.md and keep $HOME/bin as it is" "make greet() strip surrounding whitespace from the name, with a test" "turn this into a web service with user accounts, a database, and an admin dashboard"` → no parse question; mode announced before start; record 3 entries `issue: null`, `task` = text without clause, each suffix = the documented command on the normalised text; transcripts show `hc send … '/jdi:do … (untracked, started by /jdi:herd)' --if idle` with `'\''` and literal `$HOME`, each agent's first message literal; agents 1–2: ten-line plan, branch from `origin/main`, commits+tests, `git push -u origin <branch>` to the bare origin, stop at step 8 with a no-PR-host reason, bare origin `main` SHA unchanged; agent 3: the E7 line, no push, prep keeps do's branch (`git -C <wt3> branch --list` = scratch + one feature branch), no tracking question, `PLAN.md` with `Tracker: none`, `Issue: none`, base commit = branch HEAD (leave it at its first question or after 20 min); report names mode, do-stop sentence, `--cleanup <herd-id>`.
- (b) duplicate: re-herd task 1 as `"Fix  the TYPO 'recieve' in README.md and keep $HOME/bin as it is"` → same suffix → found by suffix → question → `skip`; no new worktree or record.
- (c) parse: with `tracker: {name: github}` locally, `/jdi:herd 12 "fix typo" bump lint` → one question (issue `12`, task `fix typo`, ambiguous `bump lint`) → `cancel`, nothing created; with tracker `none`, `/jdi:herd 201 202` → one question showing one task `201 202` → `cancel`.
- (d) prep mode: `herd.mode: prep`, `/jdi:herd "add a --shout flag to greet"` → invocation `/jdi:prep add a --shout flag to greet (untracked, started by /jdi:herd)` (the quoted `--shout` survives the `--kind` drop), no tracking question, branch from `origin/main`, a `PLAN.md`; leave it.
- (e) invalid mode: `herd.mode: bogus`, one task → exactly one announcement and a `/jdi:prep` invocation; leave it.
- (f) cleanup of (a): `/jdi:herd --cleanup <id-a>` → entries 1–2 space closed, plain remove, scratch `-1`/`-2` deleted (0 commits), feature branches kept and named; entry 3 its own plan question → keep → entry stays; report by name + task text.
- (g) TUI, if cheap: nested throwaway TUI (A10), `JDI_PROBE_TUI=1`, one do task with `'` and `$` → `herdr agent prompt <name> '<invocation>'` arrives literally; record `surface: tui`, `task` set; stop once seen.
**Repository checks:** full-suite count; confinement; no personal paths in the log; bare origin `main` unchanged; `<scratch>/gh-empty` holds no credentials.
**User scenarios (pending):** (u4) real do-mode herd on GitHub, two tasks editing the same lines → the second updates its branch and merges (M4); (u5) a do merge from a worktree (does `gh pr merge` deleting the local branch fail while `main` is checked out in the main checkout; does do read the merge back); (u6) a tracked issue in do mode moves through issue states; (u7) a Codex or OpenCode herd kind: the fallback finds prep (M8).
**Cleanup:** Appendix B and #37's list plus `<scratch>/gh-empty`; user's `hc ls` count, `herdr session list`, real `git worktree list`, `~/.claude.json` keys match the snapshots.

### Appendix M — verbatim text

**M-A. `reference/config.md`** — schema lines after `  kind: claude`:
```yaml

  # do | prep
  #   do   - each agent runs /jdi:do: it reads, plans in chat, builds, verifies,
  #          opens its pull request and merges it, unattended and in parallel
  #          with the others. An agent whose work is too big for one session
  #          continues with /jdi:prep in the same session instead.
  #   prep - each agent runs /jdi:prep and stops at a plan.
  #
  # The repository's own rules still win: where its CLAUDE.md / AGENTS.md says
  # an agent may not merge, a `do` agent stops before the merge. Whether a herd
  # may ship unattended is the team's call: set it in .jdi/config.yml.
  mode: do
```
Notes bullets: "**`herd.mode: do` opens and merges pull requests unattended.** Each herd agent runs `/jdi:do`, which treats its request as the authorization to merge, so a `do` herd ships several changes in parallel with nobody approving each one. The repository's own rules still win, and `herd.mode: prep` stops every agent at a plan instead. It is the team's call, so it belongs in `config.yml`." and "**An invalid `herd.mode` is announced once and runs as `prep`**, the mode with less authority, never the other way." Appended to the "`herd` is read by `/jdi:herd` and nothing else" bullet: "`/jdi:do` and `/jdi:prep` learn they run in a herd from the invocation, never from this block."

**M-B. H9 invocation table** (replaces the current one):
```text
**The invocation table.** The command each herd Butler receives, by kind and `herd.mode`:

| Kind | `herd.mode: do` | `herd.mode: prep` |
|---|---|---|
| `claude` | `/jdi:do <WORK>` | `/jdi:prep <WORK>` |
| `codex` | `$jdi:run do <WORK>` | `$jdi:run prep <WORK>` |
| `opencode` | `/jdi-do <WORK>` | `/jdi-prep <WORK>` |

`<WORK>` is the issue ID followed by `(started by /jdi:herd)`, or, for an untracked task, the task text followed by `(untracked, started by /jdi:herd)`, with one space between. The clause tells `/jdi:do` and `/jdi:prep` that a herd started them; it is not part of the work. The task text is one line: every run of whitespace, line breaks included, is collapsed to one space, because a line break typed into an agent can submit it early. For example, `/jdi:do ENG-12 (started by /jdi:herd)` and `/jdi:do fix the typo in the signup email (untracked, started by /jdi:herd)`.

Pass the invocation as one shell argument, single-quoted, never double-quoted, with a `'` inside written as `'\''`: a task is text a person typed, and inside double quotes the shell expands `$` and backticks first.
```
**M-C. H9 *Names*, appended:** "An untracked task's suffix is built as `commands/herd.md` step 5 says. An untracked task has no `jdi-herd-<issue>` fallback. Its label, the TUI's `--label` and the app's space name, is `<suffix> <task text>`."

**M-D. Record and cleanup.** Write-rule bullet: "`issue` is the issue ID, or `null` for an untracked task; `task` is the task text as handed to the agent, without the clause, or `null` for an issue. `task` is additive, so `schema` stays `1`, and a reader treats a missing `task` as `null`." Cleanup step 4's reason: "`/jdi:do` and `/jdi:prep` both leave the scratch branch behind at its base and work on a branch of their own, so the scratch branch holds nothing, and any other branch may hold the work." *The report*: "An entry whose `issue` is `null` is reported by its `name` and its task text."

**M-E. do.md and prep.md.**
1. do step 1, end of its first paragraph: "A request that ends with `(started by /jdi:herd)` or `(untracked, started by /jdi:herd)` came from a herd: that clause is not part of the work, so leave it out of the branch name, the commits and the pull request, and with `untracked` run no tracker step at all."
2. do step 5, end of the *Too big* bullet: "**Started by `/jdi:herd`** (the request ends with `(started by /jdi:herd)` or `(untracked, started by /jdi:herd)`) **and found before step 6 has changed anything:** do not hand back. Say in one line that the work is too big for one session, why, and that you continue with `/jdi:prep`; then read JDI's prep command (`${CLAUDE_PLUGIN_ROOT}/commands/prep.md`, or, if that variable does not resolve, the prep command file beside this one) and follow its steps on the same request in this session, with what you learned. Push nothing and note nothing on the issue first: prep's step 6 keeps the branch step 2 created, because it already names this work, and creates one when step 2 has not run yet."
3. do step 10, appended: "When the pull request no longer merges cleanly because the default branch moved (a parallel change merged first), bring the branch up to date with `origin/<default>` the way the repository allows, run step 7's gates again, push, and wait for the checks on the new head; a conflict whose resolution needs a product decision is a step-5 stop."
4. prep step 2, appended: "When the request ends with `(started by /jdi:herd)` or `(untracked, started by /jdi:herd)`, the herd has answered this step and step 3's question: an issue in it uses the configured tracker, and `untracked` means not tracked. Ask neither. The clause is not part of the work: leave it out of the slug and the title."

**M-F. herd.md.** Frontmatter:
```text
description: "Run several issues or untracked tasks in parallel - one Herdr worktree, pane, and agent each, running /jdi:do (or /jdi:prep, by herd.mode) - or clean a herd up from its record."
argument-hint: "<issue-id | 'task text'> [...] [--kind <kind>] | --cleanup [<herd-id>]"
```
Step 3 titled `3. **Parse the issues and tasks**`, E3's rules in four bullets beginning "**A quoted argument is always a task.**", "**An unquoted argument is an issue ID only when a tracker is configured** …", "**With no tracker configured, no argument is an issue ID** …", "**Anything else is ambiguous** … ask once … Never guess, and start nothing before the answer." Then: "Tasks skip **T2** and every other tracker step: nothing is read from or posted to a tracker for a task." Keep the existing T2 and fallback sentences for issues.
Step 5's task bullet: "**An untracked task** has no title and no issue ID. `<slug>` comes from the task text's key words by the same rules, and `<suffix>` is `t` followed by the first six hex digits of its hash, where the normalised task is the task text lowercased, with every run of whitespace collapsed to one space and none at either end:" then an indented `text` fence holding exactly `printf '%s' '<normalised task>' | git hash-object --stdin`, then: "Single-quote the task as H9's invocation table says. The same text always gives the same suffix, so a second herd for the same task finds the first one's folder by the suffix check in step 6; an index in the herd would give every herd's first task the same suffix and make that check fire for unrelated work. `fix the typo in the signup email` hashes to `96ae2d07…`, so its suffix is `t96ae2d` and its name `fix-typo-signup-email-t96ae2d`."
Step 10's do-stop sentence: "In `do` mode, a `do` agent that stopped before merging (a product decision, a change the repository reserves for a person, a review that will not converge, or a pull request it could not open) waits in its space with its reason, and the sidebar shows `done` for it, as for one that merged: open its space to see which. An agent whose work was too big says so and continues with `/jdi:prep` in the same space."

### Testing strategy (#38)
Every new case is red at HEAD and reddened by removing the text this plan adds at its definition site (config.md schema/defaults/notes; H9 table, clause, quoting, record, cleanup; do.md steps 1/5/10 and prep step 2; herd.md steps 1/3/5/8/10 and frontmatter; help/init/README/CHANGELOG; the two docs). Guards kept green, not the fix: `ConfigSchemaTest.test_schema_keys_appear_in_the_example`, `test_standalone_too_big_still_hands_back`, the surviving herd pins (#31 D11, C4), `VersionTest`, `HerdrConfinementTest`. `test_clauses_match_h9` crosses the do↔H9 boundary so both sides keep one string. `test_task_suffix_example_is_reproducible` executes the documented command (`printf '%s'` vs `echo` would change the hash). Not unit-observable → T26: the fallback really happens and is announced and keeps its branch (a); parse rules applied (c); hash at run time (a, b); literal quoting on each surface (a, g); prep skips the tracking question (a, d); record `task` and cleanup by name (a, f); the no-PR-host stop (a); invalid mode as prep (e); unattended merge and M4 → (u4, u5); Codex/OpenCode → (u7). Blocker record (2f30a28): only `tests/test_opencode_sync.py` and `tests/test_structural_checks.py` use subprocess (shell snippets/sync script, never an agent CLI); stdlib unittest only; no test yet mentions `herd.mode`, the clause or `hash-object`. CHANGELOG/README/init prose reviewed by reading.

### Risks (#38)
- **R19** Unattended parallel merges by default (U1) → M5 announcement, docs, the repo's own rules win, `prep` the way back.
- **R20** Shell expansion of task text → single-quoting everywhere (M2); the hash command quotes the same way; collapsed whitespace stops an early submit.
- **R21** 24-bit suffix collision → one question, never a folder.
- **R22** SHA-256 repos give different suffixes → stable within the repo.
- **R23** A person typing the clause by hand opts into the fallback → harmless.
- **R24** Fallback on Codex/OpenCode may not find prep → M8 path rule; (u7).
- **R25** `gh pr merge` from a worktree may fail to delete the local branch while the remote merge succeeds → do step 11 reads the merge back; (u5).
- **R26** A fallback prep asking questions waits and shows `done` → the report says so.
- **R27** The no-host stop is agent judgment → a worse action in (a) (e.g. pushing to `main`) is a failure and a new task.
- **R28** A do agent underestimating size ships a sprawling PR unattended → repo review, `prep` mode.
- **R29** The lifecycle-doc deviation (E6) is recorded so the next key doesn't copy it.
- **R30** UAT safety (highest): guard isolates the TUI socket (F-c) and GitHub (empty `GH_CONFIG_DIR`, tokens unset); herd agents inherit the guarded env; they load this branch's plugin; sonnet herd agents cost tokens, the fallback and prep agents are stopped early.
- **R31** Cleanup of a stopped do worktree with an open PR → feature branch never deleted; do pushed it before stopping.

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

## UAT log

Task 10, run 2026-11-16 on Linux (Wayland), `herdr` 0.9.3, `herdr-app` 0.1.16, `hc` 0.1.21,
`claude` (mise wrapper), `opencode` 2.2.7. Codex was not used, so `~/.codex/config.toml` was not
touched.

**Harness.**
- **Guard.** Every Herdr command ran through the guard `<scratch>/g`, recreated from Task 02. It
  refuses with exit 64, 0 stdout bytes and a stderr line unless `JDI_PROBE_SESSION` and
  `JDI_PROBE_HOME` are set and the session matches `jdiprobe-*`. It unsets the nine inherited
  `HC_*`/`HERDR_*` variables, exports `HC_SESSION=<probe-session>` and
  `HERDR_APP_HOME=~/.config/<probe-home>`, then `exec "$@"`.
- **XDG.** As in the probe log, XDG was not overridden, because the core keys its socket and
  state by session name.
- **Claude variables.** The guard also unset the driver's own Claude session variables
  (`CLAUDECODE`, `CLAUDE_CODE_*`, `CLAUDE_PID`, `CLAUDE_EFFORT`), so the throwaway core and its
  Butlers did not inherit the driving session's identity.
- **Setup.**
  - The user's own `hc ls --json` had **1** terminal (read-only, outside the guard).
  - The clone `<scratch>/repo` has a bare local `origin`, whose `main` is this branch's HEAD
    `ec1c224`.
  - The throwaway home's `settings.json` was `{"worktrees":{"directory":"<scratch>/worktrees"}}`.
  - Through the guard, `herdr-app status` exited 2 ("no Herdr window"). `hc ls --json` printed
    `{"hidden_finished":0,"terminals":[]}`.
  - `herdr-app` was started in the background, and its welcome overlay was closed.
- **Trust.** Only `<scratch>/repo` was pre-trusted in `~/.claude.json`, from a backup. The herd
  worktree folders were not.
- **Clone config.** `.jdi/config.local.yml` set:
  - `tracker: {name: none}`, `jev.enabled: false` and `tdd.enabled: false`;
  - `models.researcher` and `models.executor` on `harness: opencode` (CLI default model), and the
    other roles on sonnet or haiku;
  - `delegation.transport` and `herdr.surface` per scenario.
- **The Butler.** It ran as `claude --plugin-dir <this repo> --settings
  '{"enabledPlugins":{"jdi@just-do-it":false}}'`, the argv of a throwaway `space.new` on the
  clone. The installed copy of the plugin was disabled for that session only. It was driven with
  `hc send` and read with `hc read`. Evidence comes from the Butler's session transcript (every
  Bash command it ran), `herdr-app ls`, `hc get`, and the run directories.

**A first attempt with a sonnet Butler (not a scenario result).** Before (a) passed, two runs used
`claude --model sonnet` as the Butler.
- **First run.** The prompt said "keep research and the plan minimal". The Butler skipped step 0
  entirely and did the research inline. The prompt invited that.
- **Second run** (neutral prompt). H1 answered `app` correctly. The Butler then ran the
  Researcher through `opencode run` instead of rung 2, behind a spawn line reading `run dir:
  none`.
- **Decision.** Both runs were discarded. Every scenario below uses the account's default model.
  Whether a weaker Butler model must follow rung 2 is a question for the user (see *Findings*, F1).

### (a) Role delegation on the app: **pass**

`transport: auto`, no `herdr` key, `/jdi:prep Add one comment line "# Scratch UAT marker" as the
first line of jdi.config.example.yml.`
- **No step-0 note.** H1 ran app checks (a)–(e) in order, `test -S` before any `hc`. Its only
  message about it was a progress line, "Running the Herdr app checks (step 0)".
- **The spawn line appears in the output.** The output of the one command
  `printf '%s\n' "JDI spawn 20261116T214925Z-researcher-a1c4: Researcher on opencode (CLI default)
  - args: none - env keys: none - run dir: <scratch>/repo/.git/jdi/runs/20261116T214925Z-researcher-a1c4
  - agent: jdi-researcher-a1c4" && herdr-app do pane.split --pane <butler pane> --direction right
  --argv '["sh","-c","cd -- \"$1\" && shift && exec \"$@\"","jdi-worker","<scratch>/repo","<absolute
  opencode>"]' && herdr-app do pane.focus --pane <butler pane>` starts with the spawn line,
  followed by `{"pane": …, "terminal": "t3"}` and `{"ok": true}`.
- **One pane to the right.** After the command, `focused_pane` was the Butler's pane again.
- **The worker runs in the worktree root.** `hc get t3` showed `foreground.cwd` =
  `<scratch>/repo`, the clone's root, and the label `jdi.agent=jdi-researcher-a1c4`. Its
  `parent` was `null`.
- **The H4/H5 order** was `hc label`, then the manifest and `prompt.md`, then `hc wait t3
  --timeout 120` (`idle`), then `hc send t3 "Read …/prompt.md and follow it exactly. This is JDI
  run …" --if idle --wait --timeout 300`. That returned `wait.status: idle, turn 1`.
- **`manifest.json`** has `"transport": "herdr"` and `"herdr": {"surface": "app", "space_id",
  "tab_id", "butler_pane_id", "pane_id", "terminal_id": "t3", "agent_name", "status_reported":
  false, "versions": {"app": "herdr-app 0.1.16", "hc": "hc 0.1.21"}}`. `worker.env_keys` is `[]`,
  so no values were recorded.
- **H7 accepted `result.json`.** It had `status: complete` and an unchanged `head_commit`. The
  Butler's spot-check dropped one invented citation.
- **The pane was closed.** `herdr-app do pane.close` ran. `herdr-app ls` then listed only the
  Butler's terminal, and `outcome.json` has `final: valid, pane_closed: true`.
- **Notes.** `status_reported` was `false` even though `hc get` already showed `opencode: idle`
  (F2). The Butler's visible message did not repeat the spawn line in this run (it did in (b) and
  (f)). It wrote the task files itself instead of running the Splitter, which this scenario does
  not test.

### (b) A wave on the app: **pass**

A hand-written plan `plans/uat-wave` with one wave of two tasks: create `uat-a.txt` and
`uat-b.txt`. The Executors ran on opencode, then `/jdi:execute` and `/jdi:done`.
- **The wave tab.** `herdr-app do tab.new --name jdi-wave-20261116T215303Z-executor-a1c3 --space
  <butler space> --folder <scratch>/repo --argv '["<absolute opencode>"]' --focus false` opened
  the tab `jdi-wave-20261116T215303Z-executor-a1c3`.
- **First worker.** `t4` ran in the tab's root through the app's `bash -ic` wrapper, with no `sh`
  wrapper.
- **Second worker.** `t5` came from `pane.split --pane <t4's pane> --direction right` with the
  `sh` wrapper and the focus restore.
- **Folders and the cap.** Both workers had `foreground.cwd` = `<scratch>/repo`. Two worker panes
  were open, within the cap of 4.
- **The commands that followed** were labels, readiness `hc wait … --timeout 120` (both `idle`),
  `hc send … --if idle --wait`, H7 per task, and the union file check.
- **Spawn lines.** Both were printed by their own spawn commands and repeated in the Butler's
  message.
- **Commits.** `/jdi:done` made one commit per task, each with its own path: `e4e8ff0`
  (`uat-a.txt` and task 01) and `0772408` (`uat-b.txt` and task 02).
- **The wave tab is gone afterwards.** `pane.close` on both panes, then `tab.close --id <tab>
  --confirmed true`, which returned `{"error": "no tab …"}`. The tab had **closed itself** when
  its last pane was closed, so the error was harmless and the Butler treated it as such. It also
  flagged that `### Waves on the app` and H8 say the wave tab "does not close itself" (F3).

### (c) `/jdi:herd` on the app: **pass**

`/jdi:herd 101 102`, with the default `herd.kind: claude` and no tracker.
- **Fallback names.** `jdi-herd-101` and `jdi-herd-102`, announced once.
- **Worktrees** are at `<scratch>/worktrees/repo/jdi-herd-101` and `…/jdi-herd-102`. `repo` is
  the clone's name from `--git-common-dir`.
- **Branches.** `git worktree add -b jdi-herd-scratch-20261116T215532-<N> <path> origin/main`, for
  N = 1 and 2.
- **Spaces open only after seeding.** `herdr-app do space.new --name "<id>" --folder <path> --tab
  jdi-herd-<id> --argv '["<absolute claude>"]' --focus false` ran after the worktree step. Seeding
  was empty, and there was no `--task`.
- **Space names.** `herdr-app ls` named the spaces `101` and `102`, the issue ID because no title
  was read. Their tabs were `jdi-herd-101` and `jdi-herd-102`.
- **Nesting.** A screenshot of the sidebar shows both as branch-icon children of the clone's
  space, like a dialog-made worktree.
- **The handoff was typed.** `hc label`, then `hc wait t6/t7 --timeout 120` (both `idle`), then
  `hc send t6 "/jdi:prep 101" --if idle` (and the same for `t7`). `hc read t6` shows the input
  `<hc from="t2">/jdi:prep 101</hc>` arriving as a typed message, and the agent's prep started.
- **The report** lists each issue's terminal (`t6`, `t7`), pane, space ID, state, worktree and
  branch. It gives the reattach commands and the cleanup order: plan-file check, `space.close`,
  then `worktree remove`.
- **No trust dialog.** None appeared, so the amended D7 path was not exercised here. The two
  agents reached `idle`. No `~/.claude.json` entry was created for the worktree paths, so Claude
  evidently takes a linked worktree's trust from its trusted main checkout (F4). (c4) below
  exercises D7.
- **Prep was not run to completion.** The herd agents stopped on their own, asking for the issue
  body, and their spaces were then closed.

### (c2) Open and list: **pass**

The driver closed space `102` (`space.close`), leaving its worktree, and asked the Butler to
perform H9's reattach twice.
- **First reattach.** `herdr-app ls` showed no space with a folder inside the worktree, so the
  Butler ran `herdr-app do space.new --folder <scratch>/worktrees/repo/jdi-herd-102 --focus
  false`. That printed `{space, tab, terminal: "t8"}`, exit 0.
- **Second reattach.** The space was found by its folder, so the Butler ran `herdr-app do
  space.select --id <that space>`, which printed `{"ok": true}`.
- **List.** `git worktree list --porcelain` listed the main checkout and both herd worktrees, each
  on its `jdi-herd-scratch-…` branch.

### (c3) Remove: **pass**

The driver left `plans/uat-left/NOTE.md` uncommitted in `jdi-herd-101`, then asked the Butler to
follow the report's cleanup for both issues.
- **101 was refused.** `git -C <worktree> status --porcelain -- plans` printed
  `?? plans/uat-left/NOTE.md`. The Butler stopped on 101, named the file, and offered the plan
  commit or a forced removal. It touched neither the space nor the worktree.
- **102 was removed.** Its check was empty, then `herdr-app do space.close --id <space>
  --confirmed true` (`{"ok": true}`), **then** `git -C <scratch>/repo worktree remove <path>`
  (exit 0, no `--force`).
- **101 after the file was deleted.** The check was empty, then `space.close` before `worktree
  remove`, both exit 0. Afterwards `herdr-app ls` listed only the Butler's space,
  `git worktree list` listed only the main checkout, and the scratch branches were kept as asked.

### (c4) `worktrees.directory` is honoured: **pass**

- **A second absolute path.** `settings.json` was changed to
  `{"worktrees":{"directory":"<scratch>/wt2"}}`, then `/jdi:herd 103`. The worktree was created
  at `<scratch>/wt2/repo/jdi-herd-103`.
- **This run also exercised amended D7.** The clone's trust entry was removed for this run only,
  then restored.
  - The agent opened Claude's "Accessing workspace … Is this a project you created or one you
    trust?" dialog. `hc wait t9 --timeout 120` ended with no status.
  - The Butler reported issue 103 as **blocked at startup**, named the terminal, pane and space,
    and said the dialog is the user's to answer. It left the space open.
  - The transcript has no `hc send` (and no `hc keys`) to `t9`, so nothing was typed. The
    driver did not answer the dialog either. It closed the space and removed the worktree
    itself.
  - The report wrongly blamed the dialog on the missing bypass flag, and said every new
    worktree hits it, which (c) contradicts (F4).
- **A relative value.** `{"worktrees":{"directory":"relative/dir"}}`, then `/jdi:herd 104`. The
  herd stopped at step 6 with "worktrees.directory is "relative/dir" … only accepts an absolute
  path or one starting with ~". It created no worktree, branch, space or agent, did not fall back
  to `~/.herdr/worktrees`, and `<scratch>/repo/relative` does not exist.

### (d) `transport: native`: **pass**

`/jdi:prep Create a file uat-native.txt at the repository root containing the single word native.`
ran to completion: branch, research, plan and tasks.
- **No Herdr command.** The transcript's 22 tool calls contain no `hc`, `herdr-app` or `herdr`
  command. The only "herdr" strings are reads of this branch's `plans/36-herdr-app-support/`
  files used as format examples.
- **No mention.** No progress line or final summary mentions Herdr, the transport or a pane. The
  Researcher ran through `opencode run` (rung 4's exec mode), and the summary says only that it
  "ran on opencode with the CLI's default model". `herdr-app ls` listed only the Butler
  throughout.

### (e) Pinned `tui` inside the app: **fail (announcement only; routing passes)**

`/jdi:research` on the plan from (d).
- **Under `auto`, routing passes.** No `hc` or `herdr-app` command ran, and the Researcher ran
  natively through `opencode run`.
- **Under `auto`, it was not silent.** The Butler printed the progress line "Surface pinned to
  `tui`; running the TUI checks." Its summary said "Herdr wasn't running here, so the Researcher
  ran directly in OpenCode, outside Herdr."
- **It kept checking after (a) failed.** It ran the TUI checks (a)–(c) in one command, including
  the read-only `herdr status`, although (a) (`HERDR_ENV` unset) had failed. Expected: a silent
  `native` and no further checks after the first failure.
- **Under `herdr`, routing passes.** `native` through `opencode run`, no app command, and no
  fall to the app.
- **The note is off-pattern.** The note said "Delegation is configured as `herdr`, but the Herdr
  check failed: `HERDR_ENV` is empty … I delegated without it.", plus the progress line "Herdr
  check failed". It does not name the surface. Expected exactly one note in the pattern
  "Herdr (tui) is not usable here: …".
- **Diagnosis.** The decision logic works, but the Butler paraphrases the announcement and
  narrates H1 under `auto`. `## When a step fails` holds the pattern, and step 0 does not quote
  it. The "nothing … mentions the transport, summaries included" rule is written only for
  `native`, not for a silent `auto` (F5).
- **Decision needed from the user.** Accept this as is, or open a follow-up task (F5).

### (f) Invalid value: **pass**

`herdr.surface: bogus`, `transport: auto`, `/jdi:research`.
- **One note.** The summary says once: "`herdr.surface` in the local file is `bogus`, which isn't
  a valid value. I treated it as `auto`, and that resolved to the Herdr app."
- **Then (a)'s behaviour.**
  - Spawn line plus `pane.split … --direction right` plus focus restore, then a label, the
    readiness `hc wait` (`idle`), and `hc send … --if idle --wait`.
  - H7 `valid` (`20261116T221140Z-researcher-e525`), then `pane.close`.
  - The spawn line is repeated in the summary.
  - The Butler flagged `status_reported: false` itself (F2).

### (g) Outside any Herdr, with a named session set: **pass on routing; the pinned note is off-pattern**

The Butler ran in the driver's plain shell through the guard: `claude -p --plugin-dir <this repo>
… --output-format stream-json --verbose "/jdi:research"` in `<scratch>/repo`.
`HC_SESSION=set HERDR_APP_HOME=set`, and `HC_TERMINAL_ID` and `HERDR_ENV` were unset.
- **Under `auto`: pass.** It was silent: the result text never mentions Herdr. No `hc`,
  `herdr-app` or `herdr` command ran. The H1 step was `printenv HERDR_ENV; echo "HC=[$(printenv
  HC_TERMINAL_ID)]"`, then native through `opencode run`. The throwaway `hc ls --json` count was
  1 before and 1 after, so no core was auto-started.
- **`herdr.surface: app` and `transport: herdr`, routing passes.** App checks (a)–(c) were
  `printenv`, `command -v` and `test -S`, with no `hc` and no `herdr` TUI command. The run then
  went `native` through `opencode run`.
- **The note is off-pattern.** One note: "Herdr couldn't be used. Its first check failed because
  `printenv HC_TERMINAL_ID` printed nothing, and `HC_TERMINAL_SOCKET` is also unset." It does not
  name the surface, where "Herdr (app) is not usable here: …" was expected (F5). The count was
  still 1.
- **Stray file.** The Butler wrote `opencode run`'s output to a file in its own temporary folder
  (outside `<scratch>`). The driver removed it in cleanup.

### (h) The TUI path, nested: **pass**

A throwaway space ran `<absolute herdr> --session <probe-session>` (a TUI inside an app
terminal). The Butler was started in its pane `w1:p1` with `herdr agent start uat-butler --kind
claude --pane w1:p1 -- --plugin-dir <this repo> …` and given `/jdi:research` with
`herdr agent prompt`, under `transport: auto`.
- **The innermost surface wins.** Both variable sets were present. App checks (a)–(c) passed,
  then `hc get "$HC_TERMINAL_ID" --json` showed `foreground` = `herdr`, so the Butler said
  "Foreground is `herdr` → surface is TUI". It then ran TUI checks (b) and (c).
- **The worker started as in 1.0.10.** The spawn line plus `herdr pane split --current
  --direction down --cwd <scratch>/repo --no-focus` (the layout picked `down`), then `herdr agent
  start jdi-researcher-f47d --kind opencode --pane w1:p2 --timeout 120000`, then `herdr agent
  prompt … --wait --timeout 300000`.
- **Manifest.** `"herdr": {"surface": "tui", "workspace_id": "w1", "tab_id": "w1:t1",
  "butler_pane_id": "w1:p1", "pane_id": "w1:p2", "agent_name": "jdi-researcher-f47d",
  "integration": "opencode: current (v13)"}`.
- **It completed through H7**, with `result.json` `complete` and `outcome.json` `final: valid,
  pane_closed: true`.
- **Its pane was closed.** `herdr pane close w1:p2` ran, and `herdr pane list` then listed only
  `w1:p1`.
- **A `herdr status` wording mismatch.** 0.9.3 prints `endpoint_compatible: yes` and
  `private_protocol_compatible: yes`, with no plain `compatible: yes` line. The Butler took
  both as passing check (c) (F6).

### (u1) The default app window, with no named session: **pending, user to walk**

Not run by the agent. Steps for the user:
1. **Check the window.** In a terminal of your normal Herdr app window, run `printenv HC_SESSION
   HERDR_APP_HOME`. It should print nothing.
2. **Make a disposable checkout of this repository.** For example, run `git worktree add
   ../jdi-u1 36-herdr-app-support-u1` from a new branch, or clone the repo. Add a
   `.jdi/config.local.yml` with `tracker: {name: none}`, `models.researcher: {harness: opencode,
   model: ""}` and `delegation: {transport: auto}`, with no `herdr` key.
3. **Start the Butler.** In an app terminal in that checkout, start `claude --plugin-dir <path of
   this branch's checkout>`. Run `/jdi:prep Add a comment line to jdi.config.example.yml`.
4. **Expected** (as in (a)):
   - no step-0 note;
   - a `JDI spawn` line in the split command's output;
   - one opencode pane opening to the **right** of the Butler, with focus returning to the Butler;
   - the run directory's `manifest.json` having `"herdr": {"surface": "app", …, "terminal_id": …}`
     and env keys only;
   - the Researcher's result accepted;
   - the pane closed afterwards.

   A herd from this window would use `~/.herdr/worktrees`, or your own `worktrees.directory`.
5. **Clean up.** Close the Butler and remove the disposable checkout and its branch.

### (u2) An existing TUI user: **pending, user to walk**

Not run by the agent. Steps for the user:
1. **Start the Butler.** In your own Herdr TUI (`HERDR_ENV=1`), in a disposable checkout of this
   branch, set `.jdi/config.local.yml` to `tracker: {name: none}`, `models.researcher: {harness:
   opencode, model: ""}` and `delegation: {transport: auto}`, with no `herdr` key. Start `claude
   --plugin-dir <this branch's checkout>`.
2. **Run one delegated role.** For example, `/jdi:prep Add a comment line to
   jdi.config.example.yml`.
3. **Expected:** exactly the 1.0.10 behaviour, as in (h):
   - no note;
   - the spawn line, then `herdr pane split --current --direction <right|down> --cwd <root>
     --no-focus`, then `herdr agent start … --kind opencode`, then `herdr agent prompt … --wait`;
   - `manifest.json` having `"surface": "tui"` in its `herdr` object, which is the only
     additive change;
   - H7 valid and the pane closed.

### Repository scans

1. **TUI assertions only grew.** `git diff --numstat b06fbdb… -- tests/test_herdr_operations.py
   tests/test_herd.py` printed `81 0 tests/test_herd.py` and `198 0
   tests/test_herdr_operations.py`. The deletions column is 0 for both files.
2. **No hardcoded session, home or personal path.** Three lines matched, all of them the guard
   tests' own needle lists, which assert those strings are *absent*:
   - `tests/test_herdr_operations.py`: the comment about `${HERDR_APP_HOME:-...}` and the
     `for fragment in (…)` needle list in `test_no_personal_values`;
   - `tests/test_herdr_surfaces_doc.py`: the `assertNotIn` on a home-directory path.

   No hardcoded value was added. The scan's literal "no output" cannot hold while those guard
   tests exist.
3. **App names are confined.** No output.
4. **Full suite.** `python3 -m unittest discover -s tests -v`: `Ran 166 tests … OK`.

### Clause map status

> Superseded for the rows that (a) and (f) prove by the re-run's clause map, under
> *Re-run after task 27 (2026-11-16)* below. This table is the first run's record.

| Clause | Status |
|---|---|
| Detect app vs TUI vs none | **pass**: tests green; (a) app, (h) TUI, (g) none |
| … with a config override | **routing passes**: (e), (g) pinned, (f) invalid. **Announcement wording fails** in (e) and (g) (F5), which needs the user's decision |
| Route role delegation | **pass**: (a), and (f) |
| Route waves | **pass**: (b) |
| Route `/jdi:herd` | **pass**: (c), and (c4) for amended D7 |
| App worktrees: create in the dialog's layout | **pass**: (c), (c4) |
| … open | **pass**: (c2) |
| … list | **pass**: (c2) |
| … remove | **pass**: (c3) |
| … honour `worktrees.directory` | **pass**: (c), (c4) |
| … spaces nest under their repo | **pass**: (c), sidebar screenshot |
| Sessions: never hardcode or set | **pass**: scans 2 and 3, and tests |
| … works with them set | **pass**: every agent scenario ran under a named session and app home, and (g) with no terminal |
| … works without them | **pending**: (u1) |
| TUI path unchanged | **pass**: scan 1 and (h). (u2) is **pending** |
| `native` stays silent | **pass**: (d) |

### Findings for follow-up (not fixed here; product docs are a new task)

- **F1. Butler model.** A sonnet Butler skipped rung 2 after detecting the app. It used
  `opencode run` behind a spawn line with "run dir: none". The default-model Butler followed rung
  2 every time.
- **F2. `status_reported`.** It was `false` in every app manifest, (a) and (f), although the
  worker already reported `idle`. H4 on the app writes the manifest (step 4) before the readiness
  wait (step 5), and the manifest is never edited. Either H4 checks `hc get` before writing it,
  or A3 defines the field as "at write time".
- **F3. The wave tab closes itself.** On herdr-app 0.1.16 it closes when its last pane is closed
  with `pane.close`. `### Waves on the app` and `### H8 on the app` say it "does not close
  itself". That is true only while the first worker's shell is live. The `no tab` handling
  already covers it.
- **F4. Trust dialogs and worktrees.** Claude takes a linked worktree's folder trust from its
  trusted main checkout. H9 on the app's "a new worktree is a folder Claude … has not seen, so
  they open a folder-trust dialog" is therefore not always true. A herd from a trusted repository
  hands off directly, and only an untrusted main checkout produces D7's blocked-at-startup path.
- **F5. Step-0 announcements.** Under a pinned surface, the `herdr` note did not name the surface
  or follow `## When a step fails`' pattern, in (e) and in (g). Under `auto` with the pinned
  surface's first check failing, the Butler narrated H1 and mentioned Herdr in its summary, and
  kept checking after the first failure, in (e). Step 0 could quote the note's pattern and say
  that silence under `auto` covers summaries too.
- **F6. `herdr status` wording.** H1 on the TUI, check (c), says `compatible: yes`. `herdr`
  0.9.3 prints `endpoint_compatible: yes` and `private_protocol_compatible: yes`.
- **F7. Name quoting.** In (c) the Butler passed the space name double-quoted (`--name "$i"`),
  where H9 says to single-quote it. That is harmless for numeric IDs, and in (c4) the Butler
  single-quoted it.

### Cleanup

- **Throwaway TUI and window.**
  - The throwaway TUI was stopped with `herdr --session <probe-session> server stop`, through the
    guard.
  - Every remaining space was closed with `space.close --confirmed true`.
  - `herdr-app do window.close` through the guard printed `{"ok": true}`. Only the throwaway
    window process ended, and the user's own `herdr-app` processes kept running.
  - `hc server stop` through the guard printed `{"stopped":true}`.
- **What was removed.**
  - `git worktree prune` was run in the clone. The throwaway home, `<scratch>`, and the session
    folders `~/.local/state/herdr-core/<probe-session>/`, `~/.config/herdr/sessions/<probe-session>/`
    and `~/.local/state/herdr-automatic-rename/sessions/<probe-session>/` were removed.
  - Every `~/.claude.json` `projects` entry under `<scratch>` was removed. The `projects` keys now
    equal the pre-UAT backup.
  - The Butlers' transcript folders under `~/.claude/projects/` and their temporary folders for
    `<scratch>` paths were removed.
- **Checks afterwards.**
  - The user's `hc ls --json` still has **1** terminal, unchanged.
  - `~/.local/state/herdr-core/` lists only the user's four sessions, as before.
  - Through the guard, `herdr-app status` exits 2.
  - The real repository's `git worktree list` has 1 entry.
  - No `~/.config/<probe-home>` remains.

### Decisions after the UAT (user, 2026-11-16)
- (u1) and (u2) are **deferred to PR review**: task 10 closes as an agent smoke test, not user acceptance. `/jdi:pr` asks again.
- (e) and (g) behaved correctly but their notes were off-pattern (F5). Fixed by task 11 with tests pinning the wording; re-walking (e)/(g) is deferred with (u1)/(u2).
- F2, F3, F4, F5, F7 are fixed in task 11 before the PR. F1 (a Sonnet Butler skipping Herdr) and F6 (`endpoint_compatible: yes` still matches) stay recorded here only.

## Probe log (#37)

Task 12, run 2026-11-16 on Linux (Wayland), `herdr` 0.9.3, `herdr-app` 0.1.16, `hc` 0.1.21,
`git` 2.56.0, `claude` (mise wrapper, `--model haiku`). Tasks 14, 15, 17 and 18 read this section
first; an amendment `G<n>` here overrides their own text.

**Harness.**
- **Guard.** `<scratch>/g` (POSIX `sh`), recreated from Task 10. It refuses unless
  `JDI_PROBE_SESSION` and `JDI_PROBE_HOME` are both set and the session matches `jdiprobe-*`; it
  unsets the nine `HC_*`/`HERDR_*` variables and the driver's `CLAUDECODE`, `CLAUDE_CODE_*`,
  `CLAUDE_PID`, `CLAUDE_EFFORT`, exports `HC_SESSION=<probe-session>` and
  `HERDR_APP_HOME=~/.config/<probe-home>`, then `exec "$@"`. The refusal check
  (`env -u JDI_PROBE_SESSION <scratch>/g echo X`) gave `exit=64`, 0 stdout bytes and the stderr line
  `probe guard: JDI_PROBE_SESSION and JDI_PROBE_HOME must both be set; refusing`. XDG was not
  overridden (see the Task 02 XDG finding).
- **TUI address (VERIFY-AT-EXECUTION).** For TUI commands the guard, after its `unset`, sets
  `HERDR_SOCKET_PATH=~/.config/herdr/sessions/<probe-session>/herdr.sock` and refuses (exit 64) if
  that socket does not exist. Proof before R1: through the guard, `herdr status server` printed
  `socket: ~/.config/herdr/sessions/<probe-session>/herdr.sock`, and `herdr workspace list` listed
  one workspace only, `[1] probe37` (the nested TUI's own, on `<scratch>`).
- **Setup.** The user's own `hc ls --json` had **1** terminal and the real repository's
  `git worktree list` had **1** line (both read-only, outside the guard). The clone `<scratch>/repo`
  has a bare local `origin` whose `HEAD` is `main` (`origin/HEAD` → `origin/main`). The throwaway
  home's `settings.json` was `{"worktrees":{"directory":"<scratch>/worktrees"}}`. Through the guard,
  `herdr-app status` exited 2 ("no Herdr window") and `hc ls --json` printed
  `{"hidden_finished":0,"terminals":[]}`. `herdr-app` was started in the background (the only bare
  launch) and its `frame-welcome` overlay closed with `herdr-app do overlay.close`. A space `probe`
  was opened on `<scratch>`, and the nested TUI started in it as in A10:
  `pane.split --pane <pane> --direction right --argv '["<absolute herdr>","--session","<probe-session>"]'`.
- **Trust.** Only `<scratch>/repo` was pre-trusted in `~/.claude.json` (backup taken first), for R4.
  No `--trust-repository` was passed anywhere.

### R1 (TUI): create and read back

- **Command.** `herdr worktree create --cwd <scratch>/repo --path <scratch>/worktrees/repo/probe-1
  --branch jdi-herd-scratch-T-1 --base origin/main --label "probe 1" --no-focus`, exit 0, no trust
  prompt. Then, inside it, `git switch -c probe-feature` and one commit.
- **Create output (abridged).** `{"type":"worktree_created","workspace":{"workspace_id":"w3","label":"probe 1",
  "agent_status":"unknown","worktree":{"checkout_path":"<scratch>/worktrees/repo/probe-1",
  "is_linked_worktree":true,"repo_root":"<scratch>/repo",…}},"worktree":{"branch":"jdi-herd-scratch-T-1",
  "open_workspace_id":"w3","path":"<scratch>/worktrees/repo/probe-1","is_prunable":false,…},
  "root_pane":{"pane_id":"w3:p1","tab_id":"w3:t1","terminal_id":"term_…",…}}`.
- **Side effect.** The create also opened a workspace `w2` (`[2] repo`) on the main checkout
  `<scratch>/repo`; `herdr worktree list` reports it as `source_workspace_id`.
- **`herdr worktree list --cwd <scratch>/repo`**, exit 0, no trust prompt:
  `{"type":"worktree_list","source":{"source_checkout_path":"<scratch>/repo","source_workspace_id":"w2",…},
  "worktrees":[{"branch":"main","open_workspace_id":"w2","path":"<scratch>/repo",…},
  {"branch":"probe-feature","is_bare":false,"is_detached":false,"is_linked_worktree":true,
  "is_prunable":false,"label":"repo","open_workspace_id":"w3","path":"<scratch>/worktrees/repo/probe-1"}]}`.
  - `path` is byte-for-byte what `git worktree list --porcelain` prints after `worktree `.
  - `branch` is the worktree's **current** branch, without `refs/heads/` (here `probe-feature`, not
    the scratch branch it was created on). Matching by `path` (C3) is unaffected; matching by
    `branch` would miss.
- **`herdr workspace get w3`**, exit 0: `{"type":"workspace_info","workspace":{"workspace_id":"w3",
  "agent_status":"unknown","active_tab_id":"w3:t1","pane_count":1,"tab_count":1,"worktree":{…}}}`.
  `agent_status` is a top-level **string** on the workspace, `"unknown"` with no agent. The idle-agent
  shape was not observed (skipped to keep agent spend to R4).
- **Tests.** C1, C3 (TUI fragments). *Confirms*: `path`, `branch`, `open_workspace_id` and
  `agent_status` exist under those names, and neither command needs `--trust-repository`.

### R2 (TUI, safety): what removal deletes

- **Clean tree.** `git -C <worktree> status --porcelain` empty; `herdr worktree remove --workspace w3`
  gave `{"type":"worktree_removed","forced":false,"path":"<scratch>/worktrees/repo/probe-1","workspace_id":"w3"}`,
  exit 0.
  - The folder is gone; `w3` is no longer in `herdr workspace list` (only `w1`, `w2` remain).
  - `git -C <scratch>/repo show-ref --verify refs/heads/probe-feature` and
    `… refs/heads/jdi-herd-scratch-T-1` both exit 0: **no branch is deleted**.
- **Dirty tree.** Second worktree `--path <scratch>/worktrees/repo/probe-2 --branch jdi-herd-scratch-T-2`
  (workspace `w4`), one untracked file, `herdr worktree remove --workspace w4` without `--force`:
  exit 1, stdout empty, stderr `{"error":{"code":"dirty_worktree_requires_force","message":"fatal:
  '<scratch>/worktrees/repo/probe-2' contains modified or untracked files, use --force to delete it"},
  "id":"cli:worktree:remove"}`. The file and the workspace stayed. (At cleanup the same command
  with `--force` gave `"forced":true` and removed it.)
- **Tests.** C3, C4 and R12. *Confirms*: the unamended TUI removal
  `herdr worktree remove --workspace <workspace_id>` (`--force` per the force rule) stands; the
  "R2 deletes a branch" amendment is **not** triggered.

### R3 (TUI): a closed workspace

- **Command.** Third worktree (`probe-3`, `jdi-herd-scratch-T-3`, workspace `w5`);
  `herdr workspace close w5` gave `{"type":"ok"}`, exit 0; then `herdr worktree list --cwd <scratch>/repo`.
- **Output.** The entry is still listed, with **no `open_workspace_id` key at all** (not `null`):
  `{"branch":"jdi-herd-scratch-T-3","is_bare":false,"is_detached":false,"is_linked_worktree":true,
  "is_prunable":false,"label":"repo","path":"<scratch>/worktrees/repo/probe-3"}`. The folder stays.
  `herdr workspace get w5` then gave exit 1 and `{"error":{"code":"workspace_not_found",…}}`.
- **Tests.** C3. **Amends the fragment** (field shape differs from the plan's `open_workspace_id: null`): G1.

### R4 (app): where the agent state lives

- **Command.** A throwaway space `r4` on `<scratch>/repo` (`space.new --folder <scratch>/repo
  --focus false`), then `hc ls --json --label herdr.space=<space>`.
- **Idle shell only.** `{"hidden_finished":0,"terminals":[{"address":"t3","agent":"bash",
  "cwd":"<scratch>/repo","state":"live","turn":0,"where":"r4 / 1"}]}`. No `status` key.
- **Claude agent idle** (`pane.split … --argv '["<absolute claude>","--model","haiku"]'`, then
  `hc wait t4` → `reason: status, status: idle`): the agent's entry is
  `{"address":"t4","agent":"claude-code","cwd":"<scratch>/repo","state":"live","status":"idle","turn":0,"where":"r4 / 1"}`.
- **Working.** After `hc send t5 "Count from 1 to 1500, one number per line, in plain text. No
  tools." --if idle --json` (`{"started":true,"status":"idle","turn":0}`), eight listings over
  about 3 s all showed `{"address":"t5","state":"live","status":"working"}`; `hc get t5 --json`
  showed `"status":{"app":"claude-code","state":"working"}`.
- **Shape.** In `hc ls --json`, per terminal: `status` is a **string** (`idle`, `working`, `done`, …)
  and the key is **absent** for a terminal that reports none; `state` is the terminal's lifecycle
  (`live`), not the agent's. `cwd` is present. `labels` is **not** present (only `where`); the
  `--label` filter selects the space, so the listing needs none. `status.state` is `hc get`'s shape,
  not `hc ls`'s.
- **Side observation (Task 18).** After a finished turn the status is `done`, and
  `hc send <t> "…" --if idle` refuses: `{"error":{"hint":"nothing was typed","kind":"status_mismatch",
  "message":"t4 is done, not idle"}}`. A second short agent (`t5`) was therefore started to observe
  `working`; both were closed with `pane.close` at once (`finished`, `reason: killed`).
- **Tests.** C3 (app busy check). *Confirms*: the state **is** in the listing, so the
  "R4 shows no state" amendment is **not** triggered and no `hc get` per terminal is needed. The key
  to read is pinned by G2.

### R5 (git): path forms and blocked removals

- **Symlinked parent.** `ln -s <scratch>/real <scratch>/link`; `git -C <scratch>/repo worktree add
  -b r5-sym <scratch>/link/sym origin/main`. `git worktree list --porcelain` prints
  `worktree <scratch>/real/sym` (**resolved**, not the link form), and `herdr worktree list` prints
  the same `path`. An app space opened with `space.new --folder <scratch>/link/sym` is listed by
  `herdr-app ls` with `"folder":"<scratch>/link/sym"` (the **link** form, as given), and its
  terminal's `cwd` in `hc ls --json` is the link form too.
- **Deleted folder.** `git worktree add -b r5-gone <scratch>/worktrees/repo/gone origin/main`, then
  `rm -rf` the folder. `git worktree list --porcelain` marks the entry
  `prunable gitdir file points to non-existent location`. `git -C <scratch>/repo worktree remove
  <scratch>/worktrees/repo/gone` then gave **exit 0**, no output, and the entry was gone from the
  porcelain list (git 2.56.0 deregisters a missing worktree).
- **Ignored file alone** (`.jdi/config.local.yml`, listed in `.gitignore`):
  `git status --porcelain` printed nothing (`--ignored` shows `!! .jdi/config.local.yml`); a plain
  `git worktree remove` gave **exit 0** and deleted the folder, ignored file included.
- **Untracked file alone** (`?? new.txt`): plain `git worktree remove` gave **exit 128**,
  `fatal: '<scratch>/worktrees/repo/unt' contains modified or untracked files, use --force to delete it`.
  A tracked modification (` M README.md`) gave the same exit and message.
- **Tests and verdicts.**
  - C1 path form: *confirms*. The record stores the resolved form git prints, and the TUI's `path`
    compares equal to it.
  - C3 path comparison on the app: **amends**, G3. A space's `folder` keeps the form it was opened
    with, so a plain string comparison with the record misses when any parent is a symlink.
  - C5 `prunable`: *confirms*. The porcelain marks the entry `prunable`, so it can be detected;
    keeping the entry and telling the user to run `git worktree prune` stays safe. (A plain
    `git worktree remove` on it would also succeed; C5 does not use that, and this log does not
    change it.)
  - C3 force rule: *confirms*. An untracked or modified file blocks a plain removal and shows in
    `git status --porcelain`, so "anything shown → `--force` if seeded, else skip" matches git. An
    ignored file does not block and does not show; a plain removal deletes it silently. Note for
    Task 14's one list: ignored files (for example `.jdi/config.local.yml`) go with the worktree.

### Amendments

- **G1 (amends C3's TUI fragment; overrides Tasks 14, 17 and 18).** A worktree with no open
  workspace has **no** `open_workspace_id` key (R3), not `open_workspace_id: null`. Replacement
  fragment for Task 14's text: `` its `open_workspace_id` (absent or `null` means no open
  workspace) `` in place of `` its `open_workspace_id` (`null` means no open workspace) ``. The
  fragment `open_workspace_id` that `test_resolves_by_worktree_path` pins is unchanged; its
  docstring names G1. Tasks 17 (TUI column) and 18 (scenario (j)) use the same wording.
- **G2 (precises C3's app busy check; overrides Tasks 14, 17 and 18).** Applied under the "fields
  differ: use the observed names" rule, extended from R1 to R4's listing. In
  `hc ls --json --label herdr.space=<space>` the agent state is each terminal's **`status`
  string** (absent when the terminal reports none); `state` is the lifecycle (`live`). Replacement
  fragment for Task 14's busy bullet: `` app, the `status` of every terminal in
  `hc ls --json --label herdr.space=<space>` (a string; absent when the terminal reports none;
  `state` there is the terminal's lifecycle, not the agent's) ``. No `hc get` per terminal. Task 14
  pins `` the `status` of every terminal `` in `test_resolves_by_worktree_path` and names G2 in its
  docstring.
- **G3 (amends C3's app path comparison; overrides Tasks 14, 17 and 18).** The app keeps a space's
  `folder` in the form it was opened with, while the record holds git's resolved form (R5). The
  comparison resolves the folder first. Replacement fragment for Task 14's app find: `` App: the
  `herdr-app ls` space whose `folder`, resolved with `(cd -- <folder> && pwd -P)`, is the entry's
  `worktree` or inside it; a folder that no longer exists matches nothing `` in place of `` App: the
  `herdr-app ls` space whose `folder` is the entry's `worktree` or inside it ``. Task 14 pins
  `pwd -P` in `test_resolves_by_worktree_path` and names G3 in its docstring. The TUI side (`path`
  equals the record) is unchanged.

Not amended: the TUI removal (R2 kept every branch), the app listing as the busy source (R4 has
state), `--trust-repository` (not needed), C4 and C5.

### Cleanup

- **Closed.** Every probe worktree was removed (`probe-2` by `herdr worktree remove --workspace w4
  --force`; the rest by `git worktree remove [--force]`) and every probe branch deleted in the
  scratch clone. The nested TUI was stopped with `herdr --session <probe-session> server stop`
  (exit 0). Both spaces were closed with `space.close --confirmed true`; `window.close` ended the
  throwaway window; `hc server stop` gave `{"stopped":true}`. All through the guard.
- **Removed.** The throwaway home, `~/.local/state/herdr-core/<probe-session>/`,
  `~/.config/herdr/sessions/<probe-session>/`,
  `~/.local/state/herdr-automatic-rename/sessions/<probe-session>/`, and the probe agents' Claude
  transcript folder under `~/.claude/projects/`. The `~/.claude.json` `projects` entry for
  `<scratch>/repo` was deleted with `jq` (the file was not restored wholesale from the backup,
  because the driving Claude session writes to it meanwhile); no entry under `<scratch>` survives.
  Then `git worktree prune` in the clone and removal of `<scratch>`.
- **Checks afterwards.**
  - The user's `hc ls --json` still has **1** terminal, unchanged.
  - The real repository's `git worktree list` has 1 line, unchanged.
  - Through the guard, `herdr-app status` exits 2.
  - `~/.local/state/herdr-core/` and `~/.config/herdr/sessions/` list only the user's own sessions;
    `herdr session list` shows only the user's pre-existing sessions.

Gate (#37): passed after amendments G1, G2, G3

Butler, 2026-11-16: G2 accepted. It corrects a field name (the listing's `status` string, not `state`) within the R4 rule the gate pre-agreed, and changes no decision.

Finding carried to task 19: after an agent's turn ends its status is `done`, and `hc send --if idle` refuses it ("done, not idle"). The app H6 answer to `needs_input` (task 06) uses `--if idle`, so it would always be refused for a worker that stopped to ask. Task 19 probes how `done` becomes sendable and fixes H6 (and any other `--if idle` send that can meet `done`).

### R6 (app): sends that meet a `done` agent (task 19)

Run 2026-11-16, same versions as above (`hc send --help` lists `--if` values `idle` and `working` only,
and neither `hc send --help`, `hc wait --help` nor `hc --skill` documents a "seen" step that moves
`done` to `idle`). A new guard `<scratch>/g` as in the harness above (refusal check: `exit=64`, the
same stderr line), a new `<probe-session>` and `~/.config/<probe-home>`, and a fresh app window
(`frame-welcome` closed). A space `butler` on `<scratch>` (focused) and a space `worker` on
`<scratch>/work` opened with `space.new --argv '["<absolute claude>","--model","haiku",
"--permission-mode","default"]' --focus false` (terminal `t2`). Only `<scratch>/work` was
pre-trusted in `~/.claude.json`. Every command went through the guard.

- **Reaching `done`.** `hc wait t2 --timeout 60` → `reason: status, status: idle, turn: 0`. Then
  `hc send t2 "Reply with the single word OK. No tools." --if idle --wait --timeout 90 --json` →
  `{"started":true,"status":"idle","turn":0,"wait":{…"reason":"status","status":"done","turn":1}}`.
  `hc get t2 --json` → `"status":{"app":"claude-code","state":"done"}`; `hc ls --json` →
  `"status":"done","turn":1`.
- **Nothing JDI does clears `done`.** Three `hc get t2 --json` in a row, `hc read t2 --lines 15`,
  `hc wait t2 --timeout 5` (returned at once: `reason: status, status: done, turn: 1`), and
  `herdr-app do agent.focus --terminal t2` (the window then reported `agent: t2`) each left
  `hc get` at `state: done`. `herdr-app ls` showed the tab `settled: false` throughout.
- **Sends to a `done` agent.** `--if idle` → exit 10, `{"error":{"hint":"nothing was typed",
  "kind":"status_mismatch","message":"t2 is done, not idle"}}`. `--if working` → exit 10, the same
  error with `done, not working`. Plain `hc send t2 "Reply with the single word TWO. No tools."
  --wait --timeout 90 --json` (no `--if`) → exit 0,
  `{"started":true,"status":"done","turn":1,"wait":{…"status":"done","turn":2}}`; the screen shows
  `● TWO`. A plain send types into a `done` agent and starts its next turn; `--wait` follows it.
- **A `blocked` agent.** Plain `hc send t2 "Use the Bash tool to run exactly: touch probe.txt"`
  (from `done`) started turn 3; `hc wait` → `status: blocked`; `hc get` →
  `{"kind":"permission","msg":"approve Bash: touch probe.txt","state":"blocked"}`. Plain
  `hc send t2 "no" --json` → exit 9, `{"error":{"hint":"typing would answer its dialog; read its
  screen first (hc read t2), or --force","kind":"blocked","message":"t2 is blocked (permission)"}}`;
  `--if idle` → the same exit 9 and error. The dialog stayed open and `probe.txt` was never
  created. The dialog was left unanswered (rule 7) and closed with its space.
- **Verdict for H6.** Reading does not clear `done`, so the "read first, then `--if idle`" rule is
  not available. Smallest rule R6 supports: read `hc get <terminal> --json`; `idle` → send with
  `--if idle`; `done` → plain send (no `--if`); anything else → type nothing. The plain send is
  dialog-safe on `done` because a dialog reports `blocked` (refused without `--force`, exit 9) or,
  at start-up only, no status, and `done` is neither. The remaining gap is the moment between the
  check and the send; H6 runs them back to back. H5's first prompt and H9's handoff follow a
  readiness wait that saw `idle` at turn 0, so they cannot meet `done` and keep `--if idle`.
- **Cleanup.** `space.close --confirmed true` on both spaces, `window.close`, `hc server stop`
  (`{"stopped":true}`), all through the guard; `herdr-app status` then exited 2. Removed the
  throwaway home, `~/.local/state/herdr-core/<probe-session>/`, the probe agent's transcript folder
  under `~/.claude/projects/`, the `~/.claude.json` `projects` entry for `<scratch>/work` (deleted
  with `jq`, not restored wholesale) and `<scratch>`. No TUI was started, so no
  `~/.config/herdr/sessions/` or rename state was created. Checks afterwards: the user's
  `hc ls --json` has 1 terminal (as before); `~/.local/state/herdr-core/`, `herdr session list`,
  `~/.config/herdr/sessions/`, `~/.claude/projects/`, the `~/.claude.json` project keys and the
  real repository's `git worktree list` (1 line) are unchanged.

### R7 (app): a handoff that arrives as a real slash command (task 27)

Run 2026-11-16, same versions (`hc` 0.1.21, `herdr-app` 0.1.16, `claude` through the mise wrapper,
`--model haiku`). The #38 guard `<scratch>/g` (refusal check: `exit=64`, 0 stdout bytes, the same
stderr line; `herdr status` through it failed with the `sun_path` error and `<scratch>/no-tui/`
stayed empty; `gh auth status` through it: not logged in), a new `<probe-session>` and the short
home `~/.config/<probe-home>`, and a fresh app window (`frame-welcome` closed). Only `<scratch>/repo`
and the Butler agent's folder `<scratch>/bt` were pre-trusted (`jq` to a temporary file, then `mv`).
Herd-like agents were started as `space.new --folder <scratch>/repo --tab <t> --argv
'["<absolute claude>","--model","haiku","--plugin-dir","<this repo>","--settings","{\"enabledPlugins\":{\"jdi@just-do-it\":false}}"]' --focus false`
and reached `status: idle` at turn 0 before any send. The Butler side ran inside throwaway app
terminals (a script `<scratch>/b.sh` that logs its environment and one command's stdout, stderr and
exit code to scratch files). How each message arrived was read from the agent's transcript: a real
slash command is `<command-message>jdi:help</command-message>` with `<command-name>/jdi:help`.

- **Inside an app terminal.** `HC_TERMINAL_ID=t<n>`, `HC_SESSION=<probe-session>`,
  `HC_TERMINAL_SOCKET=$XDG_RUNTIME_DIR/herdr-core/<probe-session>.sock` and `HC_SCOPE` are set.
  `hc ls --json` with and without `HC_TERMINAL_ID` listed the same throwaway terminals.
- **(i) Tagged? It depends on the sender.** From a plain shell's terminal (`t4`, agent `bash`),
  `hc send t2 '/jdi:help' --if idle --wait --timeout 150 --json` → exit 0, and the agent received a
  real slash command (no `<hc` in its transcript). From a Claude agent's terminal (Butler `t5`,
  `claude --model haiku --allowedTools Bash`, told to run the same script), `hc send t6 /jdi:help
  --if idle --json` → `{"started":true,"status":"idle","turn":0}`, and the agent's first message was
  `<hc from="t5">/jdi:help</hc>`: not expanded; the model called `Skill(jdi:help)` itself. This is
  F-h: a herd's Butler is an agent, so its handoff is tagged.
- **(ii) `env -u HC_TERMINAL_ID`, from the agent Butler `t5`: holds.**
  `env -u HC_TERMINAL_ID hc send t7 /jdi:help --if idle --json` → exit 0,
  `{"started":true,"status":"idle","turn":0}`; agent `t7`'s first message was a real slash command
  (0 `<hc` in its transcript), and `t7` went to `done` at turn 1. **Same core:** the user's own
  `hc ls --json` (read-only, outside the guard) was `t1` (turn 39) and `t5` (turn 10) before and
  after, with no new terminal and no turn change; the targets `t7`, `t2`, `t8` do not exist in the
  user's core. **`--if idle` still enforced:** to `t2` (`done`) → exit 10,
  `{"error":{"hint":"nothing was typed","kind":"status_mismatch","message":"t2 is done, not idle"}}`,
  `t2` stayed at turn 1; to `t8` (`sh -c 'cat > <scratch>/out/nostatus.txt'`, no status) → exit 10,
  `"t8 is silent, not idle"`, and the file stayed 0 bytes. **What picks the core:** in a shell
  terminal, `env -u HC_TERMINAL_ID -u HC_SESSION hc ls --json` listed the **user's default core**
  (`t1`, `t5`), with or without `HC_TERMINAL_SOCKET` and `HC_SCOPE` also removed. So `HC_SESSION`
  routes and `HC_TERMINAL_ID` only names the sender: drop `HC_TERMINAL_ID` and nothing else.
- **(iii) The work in the argv: works, but per kind.** The agent argv above plus `"/jdi:help"` as
  its last element: in the pre-trusted `<scratch>/repo` the first message was a real slash command,
  turn 1 `done`. In an untrusted folder the app showed Claude's trust dialog, and `hc get` reported
  `{"app":"claude-code","kind":"permission","msg":"trust this folder","state":"blocked"}` (not "no
  status" as in A2; `No, exit` is preselected). It was not answered there (rule 7; never `hc keys`).
  Held or lost was read outside Herdr instead: the same argv in a pty in a second untrusted folder,
  through the guard, the dialog left open about 40 s, then "Yes, I trust this folder" chosen by the
  pty driver; the transcript's first message was the real `/jdi:help` slash command. **Held.**
- **Other untagged paths in the help.** `space.new`/`tab.new --task` pass the task as the agent's
  launch argument (the surfaces doc's *The first message*), which is (iii). `hc run <cmd> [task]` is
  never used (D4). `notes = false` in `~/.config/herdr-core/config.toml` drops every tag, but it is
  the user's setting (rule 2). Not re-probed.
- **Verdict: (ii).** It is the smallest change, keeps amended D6 (still `--if idle`, still only after
  readiness saw `idle`, so nothing is ever typed into a dialog), works for every kind in the
  invocation table rather than only CLIs whose positional argument is a prompt, changes no Herdr
  setting, and sets no session or home variable: it removes one inherited variable for one
  command. H9 on the app now hands off with `env -u HC_TERMINAL_ID hc send <terminal> '<invocation>'
  --if idle`. (iii) stays unused; "Never `--task`" stands.
- **H5 and H6.** Their prompt and answer are plain text and still arrive tagged. A tag does not stop
  a worker from reading and following plain text: #36's UAT (a) and (b) workers did their tasks from
  a tagged H5 prompt, and (i)'s tagged agent still acted on the text. They are unchanged, and H5 on
  the app now says why only H9's handoff drops the tag.
- **#37's UAT (a)** recorded "handoff by `hc send`" as a pass on the text that was sent, not on the
  command loading; its first message was tagged in the same way (#36's `<hc from="t2">/jdi:prep
  101</hc>`), so it never showed that `/jdi:prep` loaded as a slash command.
- **Cleanup.** `space.close --confirmed true` on all 8 spaces, `window.close`, `hc server stop`
  (`{"stopped":true}`), all through the guard; `herdr-app status` then exited 2, and no process
  named the probe session or `<scratch>`. `<scratch>/gh-empty` and `<scratch>/no-tui` were empty.
  Removed the throwaway home, `~/.local/state/herdr-core/<probe-session>/`, the probe agents'
  transcript folders under `~/.claude/projects/` and Claude's temporary folders for `<scratch>`
  paths, every `~/.claude.json` `projects` entry under `<scratch>` (`repo`, `bt` and the
  pty-trusted folder; deleted with `jq`, not restored wholesale) and `<scratch>`. No TUI was
  started. Checks afterwards, all equal to the setup snapshots: the user's `hc ls --json` has 2
  terminals; `~/.local/state/herdr-core/` = `default jute personal vault`; `herdr session list`,
  `~/.config/herdr/sessions/`, `~/.claude/projects/` and the `~/.claude.json` project keys (4) are
  unchanged; the real repository's `git worktree list` has 1 line; no `~/.config/<probe-home>`.

## UAT log (#37)

Task 18, run 2026-11-16 on Linux (Wayland), `herdr` 0.9.3, `herdr-app` 0.1.16, `hc` 0.1.21,
`git` 2.56.0, `claude` 2.1.325 (mise wrapper). Codex was not used, so `~/.codex/config.toml` was not
touched. This is an agent smoke test; real acceptance is (u3), the user's.

**Harness.**
- **Guard.** `<scratch>/g` (POSIX `sh`), recreated as in Task 12: refuses with exit 64, 0 stdout
  bytes and the stderr line `probe guard: JDI_PROBE_SESSION and JDI_PROBE_HOME must both be set;
  refusing` unless both are set and the session matches `jdiprobe-*` (refusal check: `exit=64`);
  unsets the nine `HC_*`/`HERDR_*` variables and `CLAUDECODE`, `CLAUDE_CODE_*`, `CLAUDE_PID`,
  `CLAUDE_EFFORT`; exports `HC_SESSION=<probe-session>` and `HERDR_APP_HOME=~/.config/<probe-home>`;
  `exec "$@"`. For TUI commands it also sets `HERDR_SOCKET_PATH=~/.config/herdr/sessions/<probe-session>/herdr.sock`
  and refuses if that socket is missing. XDG was not overridden.
- **Setup.** The user's own `hc ls --json` had **1** terminal and the real repository's
  `git worktree list` **1** line (read-only, outside the guard). `<scratch>/repo` is a clone of a
  bare local `origin` whose `main` is this branch's HEAD `76db238` (`origin/HEAD` → `origin/main`).
  Throwaway home `settings.json`: `{"worktrees":{"directory":"<scratch>/worktrees"}}`. Through the
  guard, `herdr-app status` exited 2 and `hc ls --json` printed `{"hidden_finished":0,"terminals":[]}`;
  then `herdr-app` was started in the background and its `frame-welcome` overlay closed.
- **Trust.** Only `<scratch>/repo` was pre-trusted in `~/.claude.json` (`jq` to a temporary file,
  then `mv`). No herd worktree was trusted; none opened a trust dialog (Task 10's F4 holds).
- **Clone config.** `.jdi/config.local.yml`: `tracker: {name: none}`, `jev.enabled: false`,
  `tdd.enabled: false`, `herd.kind: claude`, and `harnesses.claude.args: ["--model", "haiku"]` so
  every herd agent ran on a small model (the Butler passes the args verbatim and adds no model flag).
- **The Butler.** `claude --plugin-dir <this repo> --settings '{"enabledPlugins":{"jdi@just-do-it":false}}'`
  on the account's default model (Task 10's F1), as the argv of a throwaway `space.new` on
  `<scratch>/repo`. Driven with `hc send`, read with `hc read`; evidence from its transcript (every
  Bash command), `herdr-app ls`, `hc ls`, the record files, `git worktree list --porcelain` and
  `git branch --list`. Its first message told it to ask questions in plain text and not with the
  question tool, so every answer could be typed with `hc send`; no dialog was answered with keys.
- **Herd agents.** Each stopped on its own after `/jdi:prep` asked for the issue text (`done`), so
  the driver had none to stop. They ran on the committed `.jdi/config.yml`, because the gitignored
  local file does not reach an unseeded worktree (the Butler warned about exactly this), so prep
  tried `gh issue view <n>` against the real tracker: read-only lookups that found no such issue;
  nothing was written there.

### (a) Herd and record: **pass**

`/jdi:herd 201 202 203` on the app.
- **The record.** `<scratch>/repo/.git/jdi/herds/20261116T235708.json`, valid JSON. Top keys
  `created, herd_id, issues, schema, state, surface`; entry keys `base_commit, created, herdr, issue,
  n, name, scratch_branch, seeded, worktree`; `herdr` keys `agent_name, pane_id, space_id, tab_id,
  terminal_id, workspace_id` (Appendix C exactly). `surface: app`, `state: handed_off`, three entries.
- **Per entry.** `worktree` = `<scratch>/worktrees/repo/jdi-herd-20N`, byte-for-byte the
  `git worktree list --porcelain` line of the entry whose `branch` is
  `refs/heads/jdi-herd-scratch-20261116T235708-N`; `base_commit` = `76db238…` = each worktree's
  `rev-parse HEAD`; `space_id`, `tab_id`, `pane_id`, `terminal_id` (`t2`, `t3`, `t4`) and
  `agent_name` match `herdr-app ls`; `workspace_id: null`; `seeded: false`.
- **Never committed.** `git -C <scratch>/repo ls-files | grep -c jdi/herds` → `0`.
- **Report.** Step 11 says "Run /jdi:herd --cleanup 20261116T235708" and still lists the manual
  commands (plan-file check, `space.close`, `worktree remove`, `git branch -D`); the Worktree
  section prints the record path and "/jdi:prep … leaves the scratch branch at its base".
- **Write mechanics (observed, minor).** The Butler collected the three entries in a scratch file
  and wrote the record once all three worktrees existed, then updated it after step 8 and at
  step 10. Every write went whole to `.<herd-id>.json.tmp` and was renamed over the record (a
  Python `os.replace`, the same atomic rename as `mv -f`). H9 says the record is created at the
  first successful worktree; here it was created after the third (no failure in between, so the
  result is identical). See F-a.
- **Decoy.** `git worktree add <scratch>/worktrees/repo/decoy-201 -b decoy-201 origin/main` by the
  driver.

### (b) Busy: **pass**

The driver plain-sent 202's `done` agent "Count from 1 to 6000, one number per line …" (R4/R6:
`--if idle` refuses `done`), saw `status: working`, and started `/jdi:herd --cleanup 20261116T235708`.
(A first attempt with a long `sleep` was refused by the agent's harness, so the task's long count
was used.)
- The Butler's sort step ran `hc ls --json --label herdr.space=<space>` per entry while `t3` reported
  `working` (sampled every 6 s throughout).
- The list held 201 and 203 only; 202 was reported as "Skipped: 202: its agent (t3) is still
  working. Run cleanup again once it settles." The skip was decided before the question, and
  printed in a *Skipped* block under the list.
- Answer `no`: nothing removed; the record still had three entries; the decoy was named as "not
  in this record, so not touched".

### (c) Plan guard: **pass**

Uncommitted `plans/x/NOTE.md` in 201's worktree; cleanup run again.
- 202 and 203 formed the batch (question 1); 201 left it with "it now holds an uncommitted plan
  file, plans/x/NOTE.md" and got its own question, offering "Commit, then keep" (`docs: Add x plan`
  in that worktree), "Remove anyway" (`--force`, deletes the file) or "Keep it as it is".
- Answered no to both. 201's space, worktree, scratch branch, `?? plans/x/` and record entry all
  remained.

### (h) Own location: **pass**

A second Butler was opened in 201's worktree (H9's reattach: `tab.new` in 201's existing space with
the worktree as folder) and ran `/jdi:herd --cleanup 20261116T235708`.
- 201 was skipped: "this cleanup session is running inside that worktree (…/jdi-herd-201), in its
  space sp75c7…, so I won't remove the tree I'm working in", plus its plan file; 202 and 203 were
  listed. Answer `no`; nothing removed. That Butler's tab was closed before (d).

### (d) Branches: **pass**

In 203's worktree `git switch -c feat-203` and one commit; in 202's worktree one commit on
`jdi-herd-scratch-20261116T235708-2`; 201's `NOTE.md` removed. Cleanup, answer `yes`.
- The list named every change since the last run, marked 202's scratch branch "kept, because it
  holds commit b563311", and listed `feat-203`, `decoy-201` and `main` as not touched.
- **Order, per entry, from the transcript:** `git -C <wt> status --porcelain -- plans` (re-check) →
  busy check → `herdr-app do space.close --id <space> --confirmed true` → `git -C <main checkout>
  worktree remove <path>` (plain) → branch rule (`show-ref --verify --quiet`, `rev-list --count
  <base_commit>..refs/heads/<scratch>` = 0, worktree gone) → `git branch -D`.
- **After.** `git worktree list`: main and `decoy-201`. Branches: `feat-203` (with `088432c`),
  `jdi-herd-scratch-20261116T235708-2` (kept), `decoy-201`, `main`; scratch `-1` and `-3` deleted.
  `herdr-app ls`: the Butler's space only.
- **Observed, minor.** The removal loop printed the by-path space match but closed the space by
  its recorded ID without gating on that match (the sort step had matched each space by
  `os.path.realpath` of its folder, so the IDs agreed). See F-b.

### (e) Upkeep: **pass**

- After (b), (c) and (h) (all answered `no`) the record still had all three entries, `handed_off`.
- In (d) all three worktrees went in one run; the Butler then counted no herd worktree in
  `git worktree list --porcelain` and deleted the record file; `.git/jdi/herds/` was empty.
- Rerun `/jdi:herd --cleanup 20261116T235708`: "There is no record for herd 20261116T235708, so I
  cleaned nothing", pointing at `git worktree list` (main and `decoy-201`) and naming the kept
  scratch branch with its manual `git branch -D`. `decoy-201` and its branch survived every run.
- **Not observed:** an entry dropping on its own while others remain (every run removed nothing or
  all remaining entries). That rule rests on `test_record_upkeep` only.

### (f) No record: **pass**

A fresh clone `<scratch>/repo2` (no `.git/jdi/` at all), run headless through the guard as Task 10's
(g): `claude -p --plugin-dir <this repo> … "/jdi:herd --cleanup"`.
- "There's nothing to clean up: this repository has no herd records, so I removed nothing", the
  records folder does not exist, cleanup "finds a herd only through its record, never by guessing
  from folder names", `git worktree list` shows only the main checkout, and the manual steps
  (close the space or workspace, `git worktree remove [--force]`, `git branch -D …`, plan-file
  check) were printed. Nothing removed; no `.git/jdi/` created.
- H1 found no Herdr (no `HERDR_ENV`, no `HC_TERMINAL_ID`) and cleanup continued.
- **Isolation incident (read-only).** In this run the Butler also ran `herdr status`. The guard
  unsets `HERDR_SOCKET_PATH` and this run had no throwaway TUI, so that status query reached the
  user's own default TUI server. It is a read-only query (client and server version); nothing was
  changed, and `herdr session list` was identical before and after. From then on the app Butler ran
  with `HERDR_SOCKET_PATH` pointing at a socket path under `<scratch>` that does not exist. See F-c.

### (g) Bad ID: **pass**

- `/jdi:herd --cleanup ../x`: "I refused the cleanup: ../x is not a valid herd ID … in the form
  yyyymmddThhmmss … JDI never builds a file path from an argument that hasn't passed that check".
  The transcript has **no tool call** for this turn: no path read or written.
- `/jdi:herd --cleanup 201`: refused, no tool call; "As an issue ID, it can't be combined with
  --cleanup. The two modes work separately: Start a herd: /jdi:herd <issue-id> ... Clean one up:
  /jdi:herd --cleanup [<herd-id>]".

### (i) Seeded: **pass**

A new app Butler (same argv) in a new space; local config plus
`herd.seed.setup: ["touch untracked-seed.txt"]`; `/jdi:herd 204`.
- Record `20261117T000531.json`: `surface: app`, `state: handed_off`, `seeded: true`, app IDs filled.
  `git status --porcelain` in the worktree: `?? untracked-seed.txt`. Step 11 said the manual
  removal "needs --force because the seed step" wrote into it.
- After (k): the list said "Remove worktree with --force … It was seeded, and the force discards one
  untracked file, untracked-seed.txt. Any ignored files in it go with it", then one question.
  `yes` → plan re-check, `space.close`, `git worktree remove --force <path>`, the branch rule
  (`-1` deleted, 0 commits), record deleted (last entry). The worktree and space are gone.

### (k) A herd still `creating`: **pass**

Before (i)'s cleanup the driver rewrote the record whole with `state: creating`
(`jq … > .20261117T000531.json.tmp && mv -f`).
- `/jdi:herd --cleanup` (no ID): "I removed nothing. The only herd record, 20261117T000531, is in
  state creating … Its herd may still be running; pass its herd ID to clean it anyway." The record
  was unchanged. (The Butler also noticed that the file had been rewritten after its own herd run.)
- `/jdi:herd --cleanup 20261117T000531`: "Record: 20261117T000531 reads creating. It is included
  because you named it", busy check done, entry listed. Answer `no`. Then `handed_off` restored
  (same whole-file `mv -f`) and (i) finished.

### (j) TUI: **pass**

A throwaway space ran `env HERDR_CONFIG_PATH=<scratch>/herdr-config.toml <absolute herdr> --session
<probe-session>` (A10), where that config holds only `[worktrees] directory = "<scratch>/worktrees"`,
so the TUI herd's `--path` lands under `<scratch>`. A Butler was started in its pane `w1:p1` with
`herdr agent start uat-butler --kind claude --pane w1:p1 -- --plugin-dir <this repo> --settings …`
and told once that `HERDR_CONFIG_PATH` names Herdr's config in that session (H9 names
`~/.config/herdr/config.toml`). All TUI commands from the driver went through the guard.
- **Herd.** `/jdi:herd 205` via `herdr agent prompt`. Record `20261117T000939.json`:
  `surface: tui`, `state: handed_off`, `worktree` `<scratch>/worktrees/repo/jdi-herd-205`,
  `workspace_id: "w2"`, `tab_id: "w2:t1"`, `pane_id: "w2:p1"`, `agent_name: "jdi-herd-205"`,
  `space_id: null`, `terminal_id: null`. Nothing was created under `~/.herdr/worktrees/`.
- **From the outer app Butler.** "This herd ran on the Herdr TUI, and only the Herdr app is
  reachable from here, so cleanup can't see or close its workspace"; the entry was offered marked
  "agent state unknown" with "Workspace w2: skipped", a plain `git worktree remove`, the scratch
  branch and the record. Its transcript has no `herdr` (TUI) command. Answer `no`: nothing removed.
- **From inside the TUI.** The Butler ran `herdr worktree list --cwd <main checkout>` (entry with
  `path` = the record's `worktree`, `open_workspace_id: "w2"`), `herdr workspace get w2`
  (`agent_status` done), the own-location check (`pwd -P`, `$HERDR_WORKSPACE_ID`), both status
  checks, and listed "w2, which I found by its path … herdr worktree remove --workspace w2, without
  --force". `yes` → plan re-check, `herdr worktree remove --workspace w2`, worktree confirmed gone
  from the porcelain list, branch rule → `git branch -D jdi-herd-scratch-20261117T000939-1`, record
  deleted. `herdr workspace list` then held `w1` only; no other branch was deleted (`feat-203`,
  `jdi-herd-scratch-20261116T235708-2`, `decoy-201`, `main` remain).

### (u3) A real herd cleaned up: **pending, user to walk**

Not run by the agent. Steps for the user, in their own app window (or TUI):
1. In a checkout of this branch (or with the 1.0.13 plugin from this branch via `--plugin-dir`),
   run a real `/jdi:herd <issue> [<issue> …]`. Note the herd ID the step-11 report names.
2. Let the agents finish (`done` or `idle` in the sidebar); commit each plan on its feature branch,
   or answer the agents as usual.
3. From the main checkout (not from a herd worktree), run `/jdi:herd --cleanup <herd-id>`.
4. **Expected:** one list and one question; on `yes`, each herd space (or TUI workspace) is closed
   and then its worktree removed; feature branches are kept; a scratch branch is deleted only when
   it has no commits of its own; `.git/jdi/herds/<herd-id>.json` is gone once the last entry goes.
   A worktree with uncommitted plan files gets its own question instead.

### Repository checks

1. **Log complete.** 12 scenario ids, (a)–(k) and (u3).
2. **Sanitised.** No home path or probe session name in this section.
3. **Scan 1.** `git diff cdd1404 HEAD -- reference/herdr.md | grep -E '^-[^-]'` prints 4 lines, all
   the old app `needs_input` paragraph in H6 (`hc send … --if idle --wait …`), removed by Task 19's
   commit `76db238` (approved after the Task 12 gate). No H9 line was removed. Control: 18.
4. **Scan 2.** The only removed line in `tests/test_herd.py` is the ban tuple in
   `test_herd_drops_the_superseded_keys_and_tools` that held `"herd record"`.
5. **Scan 3.** No output (control: 3).
6. **Scan 4.** No output (control: 93).
7. **Scan 5.** Three lines, each `"version": "1.0.13"`.
8. **Scan 6.** `git ls-files | grep -c 'jdi/herds'` → `0` (control: 1).
9. **Isolation.** See *Cleanup*.
10. **Clause map.** Every row's scenario passed; (e)'s partial-upkeep case rests on its test only.
11. **Full suite.** `python3 -m unittest discover -s tests -v`: `Ran 219 tests … OK` (218 expected
    by the task, plus one added by Task 19).

### Findings (not fixed here; product docs are a new task)

- **F-a. Record creation point.** H9 says the record is created at the first successful worktree
  and each issue's entry appended at step 6. The Butler created it once after all worktrees were
  made. Same end state; it only matters if a later create fails or the run dies mid-step 6.
- **F-b. Close by the matched space.** In (d) the removal closed each space by its recorded ID
  and only printed the by-path match. The sort step had matched by path, so nothing went wrong; the
  text could say the close uses the space found by path, re-found just before the close.
- **F-c. Harness gap (test tooling, not product).** The guard unsets `HERDR_SOCKET_PATH`, so a run
  with no throwaway TUI reaches the user's default TUI server with any `herdr` command. Future
  guards should export `HERDR_SOCKET_PATH` to a non-existent path under `<scratch>` outside TUI
  mode.
- **F-d. Unseeded herds ignore `config.local.yml`.** As the Butler warned in (a), a gitignored
  local config does not reach a herd worktree, so herd agents run the committed config (here a
  real tracker). Known by design (`herd.seed.copy` is the documented remedy); noted because a UAT
  harness must seed it.

### Cleanup

- **Closed, through the guard.** The nested TUI with `herdr --session <probe-session> server stop`
  (exit 0); every space with `space.close --confirmed true`; `window.close` (`{"ok":true}`);
  `hc server stop` (`{"stopped":true}`). No agent process with a `<scratch>` working directory was
  left.
- **Removed.** The throwaway home, `~/.local/state/herdr-core/<probe-session>/`,
  `~/.config/herdr/sessions/<probe-session>/`,
  `~/.local/state/herdr-automatic-rename/sessions/<probe-session>/`, the Butlers' and agents'
  transcript folders under `~/.claude/projects/` and their temporary folders for `<scratch>` paths,
  and every `~/.claude.json` `projects` entry under `<scratch>` (with `jq`; the file was not restored
  wholesale). Then `git worktree prune` in the clone and removal of `<scratch>`.
- **Checks afterwards.**
  - The user's `hc ls --json` has **1** terminal, as before.
  - `~/.local/state/herdr-core/` lists the user's four sessions only; `~/.config/herdr/sessions/`,
    the rename state and `herdr session list` are identical to the setup snapshot.
  - Through the guard, `herdr-app status` exits 2; no `~/.config/<probe-home>` remains.
  - The `~/.claude.json` project keys and `~/.claude/projects/` equal the setup snapshot.
  - The real repository's `git worktree list` has 1 line, and its git directory has no `jdi/herds`.

## UAT log (#38)

Task 26, run 2026-11-16 on Linux (Wayland), `herdr` 0.9.3, `herdr-app` 0.1.16, `hc` 0.1.21,
`git` 2.56.0, `claude` 2.1.326 (mise wrapper). Codex was not used, so `~/.codex/config.toml` was not
touched. This is an agent smoke test; (u4)–(u7) are the user's.

**Harness.**
- **Guard.** `<scratch>/g` (POSIX `sh`), #37's guard plus E8: refuses unless `JDI_PROBE_SESSION` and
  `JDI_PROBE_HOME` are both set and the session matches `jdiprobe-*`; unsets the nine
  `HC_*`/`HERDR_*` variables, `CLAUDECODE`, every `CLAUDE_CODE_*`, `CLAUDE_PID`, `CLAUDE_EFFORT`,
  `GH_TOKEN GITHUB_TOKEN GH_REPO GH_HOST GH_ENTERPRISE_TOKEN`; exports
  `HC_SESSION=<probe-session>`, `HERDR_APP_HOME=~/.config/<probe-home>`,
  `GH_CONFIG_DIR=<scratch>/gh-empty`, and `HERDR_SOCKET_PATH=<scratch>/no-tui/herdr.sock` (does not
  exist) unless `JDI_PROBE_TUI=1`, when it exports `~/.config/herdr/sessions/<probe-session>/herdr.sock`
  and refuses if that socket is missing; `exec "$@"`. XDG was not overridden.
- **Self-checks, run and logged before anything else.**
  1. `env -u JDI_PROBE_SESSION <scratch>/g echo X`: `exit=64`, 0 stdout bytes, stderr
     `probe guard: JDI_PROBE_SESSION and JDI_PROBE_HOME must both be set; refusing`. **Pass.**
  2. The user's `herdr session list` (read-only, outside the guard) captured; `<scratch>/g herdr status`
     exited 1 with `Error: Custom { kind: InvalidInput, error: "local socket name length exceeds
     capacity of sun_path of sockaddr_un" }`; `herdr session list` again: byte-identical to the first
     capture and to the setup snapshot. VERIFY-AT-EXECUTION: `<scratch>/no-tui/` stayed empty (no
     server started). **Pass.** The same guarded value reached the throwaway app's terminals: in
     (c), the in-app Butler's own H1 `herdr status` failed with the same `sun_path` error, so F-c of
     #37 is closed.
  3. `<scratch>/g gh auth status`: exit 1, `You are not logged into any GitHub hosts`. **Pass.**
- **Snapshots** (outside the guard, read-only): the user's `hc ls --json` had **2** terminals; the real
  repository's `git worktree list` **1** line; `~/.claude.json` had **4** `projects` keys;
  `~/.local/state/herdr-core/` = `default jute personal vault`; `~/.config/herdr/sessions/` = four
  entries; `herdr session list` = five sessions (none `jdiprobe-*`).
- **Scratch repository.** Bare `<scratch>/origin.git`, one commit `d9f57e0` (the **origin SHA**) with
  `README.md` (`Install into $HOME/bin and recieve updates.`), `greet.py`, `test_greet.py`,
  `AGENTS.md`, `.gitignore` (`.jdi/config.local.yml`, `__pycache__/`) and a committed
  `.jdi/config.yml` (`tracker: {name: none}`, `tdd.enabled: false`, `jev.enabled: false`). The user's
  global gitignore excludes `.jdi/`, so the config was added with `git add -f`. Clone
  `<scratch>/repo`, `origin/HEAD` → `origin/main`. The clone's own git config sets a throwaway
  identity and `commit.gpgsign false` (the user's global config signs through an external program,
  which a herd agent must not trigger); nothing global was changed.
- **Local config** (the Butler's): `herd: {kind: claude, mode: do}` and
  `harnesses.claude.args: ["--model", "sonnet", "--plugin-dir", "<this repo>", "--settings", '{"enabledPlugins":{"jdi@just-do-it":false}}']`.
- **Throwaway app.** Home `settings.json` `{"worktrees":{"directory":"<scratch>/worktrees"}}`. Through
  the guard, `herdr-app status` exited 2 and `hc ls --json` printed
  `{"hidden_finished":0,"terminals":[]}`; then `herdr-app` started in the background (a window
  appeared). `overlay.close` returned `{"ok":true}`, though `status` kept listing `frame-welcome`.
- **Trust.** `~/.claude.json` backed up; only `<scratch>/repo` pre-trusted (`jq` to a temporary file,
  then `mv`). No herd worktree opened a trust dialog.
- **The Butler.** `claude --plugin-dir <this repo> --settings '{"enabledPlugins":{"jdi@just-do-it":false}}'`
  on the account's default model, as the argv of a throwaway `space.new` (`butler`, terminal `t1`) on
  `<scratch>/repo`. Its first message told it to ask in plain text, never with the question tool.
  Driven with `hc send`, read with `hc read` and its transcript. Every answer was typed; no dialog was
  answered with keys. The driver's sends arrive as real slash commands (`<command-name>/jdi:herd`),
  because the guard strips `HC_TERMINAL_ID`. From (c) on, the Butler was given `/clear` and the
  plain-text instruction again before each scenario whose local config changed (see F-j).
- **Expected suffixes.** Re-computed at setup with the documented command: `t089c30`, `t75a757`,
  `t9e2fdc`, `t9d7ae5`, `t96ae2d`, as the task's table.

### (a) A `do`-mode herd of untracked tasks: **fail** (agent 3; see F-e, F-f, F-g, F-h, F-i)

> **Re-run after task 27: still fail** (agent 3, F-e; F-h closed). See *Re-run after task 27 (2026-11-16)* below.
>
> **Re-runs after task 28: still fail.** Sonnet: agent 3 built and pushed again (F-e), no agent posted `**Size:**`. Opus: agent 3 continued into prep before any edit, with no push and a correct `PLAN.md`, but no agent posted the verdict in chat (F-n), and the pre-start announcement was not a chat line on either run (F-i). See *Re-run after task 28 (Sonnet)* and *(Opus)* below.

`/jdi:herd "fix the typo 'recieve' in README.md and keep $HOME/bin as it is" "make greet() strip surrounding whitespace from the name, with a test" "turn this into a web service with user accounts, a database, and an admin dashboard"`, herd ID `20261117T011544`.
- **The herd: pass, but the announcement is weak.**
  - No parse question. No `gh` call anywhere in the Butler's transcript (0 matches).
  - Hashes with the documented command, the normalised text single-quoted with `'\''`:
    `printf '%s' 'fix the typo '\''recieve'\'' in readme.md and keep $home/bin as it is' | git hash-object --stdin`.
    Names `fix-typo-recieve-readme-t089c30`, `greet-strip-whitespace-t75a757`,
    `web-service-accounts-t9e2fdc`: all three suffixes match the table.
  - Record `<scratch>/repo/.git/jdi/herds/20261117T011544.json`: `surface: app`, `state: handed_off`,
    3 entries, each `issue: null`, `task` equal to the typed text without the clause (`$HOME` literal),
    `seeded: false`, app IDs filled. As in #37's F-a, it was written once after all three worktrees
    existed (state `creating`), then rewritten after the sends with `handed_off` (whole file, `mv -f`).
  - Spaces named `'t089c30 fix the typo '\''recieve'\'' in README.md and keep $HOME/bin as it is'` etc.
    (single-quoted), tab = the name, `hc wait` → `idle` for each, then
    `hc send t2 '/jdi:do fix the typo '\''recieve'\'' in README.md and keep $HOME/bin as it is (untracked, started by /jdi:herd)' --if idle`
    and the same form for `t3`, `t4`.
  - **Each agent's first received message** is the invocation exactly, `$HOME` unexpanded, but
    wrapped by hc: `<hc from="t1">/jdi:do fix the typo 'recieve' in README.md and keep $HOME/bin as it is (untracked, started by /jdi:herd)</hc>`.
    It is therefore not a slash command; each agent invoked `Skill(jdi:do)` itself (F-h).
  - **Mode announcement (M5): partial.** Before the first `space.new` the pane showed one narration
    line, "Each agent will open and merge its own PR unattended and in parallel, using `do` mode
    instead of `prep`, with the args passed verbatim." It is not a chat message and does not name
    `herd.mode: prep` as the way back (F-i).
  - **Report: pass, but partial.** It names the mode ("in `do` mode … Each one will open and merge its
    own pull request without anyone approving it, in parallel"), gives one row per task, the args,
    the seeding, the record path and `/jdi:herd --cleanup 20261117T011544`. Its do-stop sentence is
    shorter than H9's: "`done` can also mean an agent stopped before merging, so open its space to
    check." It never names `herd.mode: prep`.
- **Agent 1 (typo): pass on outcome, with deviations.** It edited `README.md` **before** loading
  `/jdi:do` (F-h), then ran `git switch -c fix-typo-recieve-readme origin/main`. It committed
  `af06b7c`, ran `python3 -m unittest` (OK), ran `git push -u origin fix-typo-recieve-readme`, and
  `gh pr create` printed `To get started with GitHub CLI, please run: gh auth login`. Its stop: "I
  couldn't open or merge a pull request. `gh` isn't authenticated, and `origin` is a local bare repo
  with no PR host." `$HOME/bin` was left literal ("untouched"). It posted **no ten-line plan** (F-g).
- **Agent 2 (strip): pass on outcome, with deviations.** It edited `greet.py` and `test_greet.py`
  before loading `/jdi:do`, then ran **`git branch -m greet-strip-whitespace`**, which renamed the
  scratch branch rather than branching from `origin/main` (F-f). It added the test
  `test_strips_surrounding_whitespace` (2 tests OK) and pushed with `git push -u origin
  greet-strip-whitespace`; `gh repo view` said not logged in. It stopped with "`gh` isn't
  authenticated and the remote is a local bare repo with no PR host". No ten-line plan.
- **Agent 3 (web service): fail.** Expected: the E7 line, no push, and prep's steps in the same
  session. Observed: it loaded `/jdi:do`, then **built the whole thing** on the scratch branch
  `jdi-herd-scratch-20261117T011544-3`: `app.py` (stdlib WSGI, SQLite, scrypt passwords, cookie
  sessions, admin dashboard), `test_app.py` (10 tests), a README rewrite and `*.db` in `.gitignore`.
  It ran a server on `localhost:8765` (pid file in `/tmp`, killed after), committed `062af12`, ran
  `git push -u origin HEAD` (the scratch branch reached origin) and `gh pr create --fill` (not logged
  in). It never said "too big", never continued with prep, wrote no `PLAN.md`, posted no ten-line
  plan and created no feature branch. `git -C <wt3> branch --show-current` =
  `jdi-herd-scratch-20261117T011544-3`. This is "a worse action than stopping" (R27 class): a new
  task, see F-e.
- **Origin afterwards.** `git -C <scratch>/origin.git rev-parse main` = `d9f57e0` (= origin SHA).
  Branches on origin: `fix-typo-recieve-readme`, `greet-strip-whitespace`,
  `jdi-herd-scratch-20261117T011544-3`, `main`. **No push to `main`.**

### (b) A duplicate task: **pass**

`/jdi:herd "Fix  the TYPO 'recieve' in README.md and keep $HOME/bin as it is"` (two spaces).
- One tool call, `printf '%s' 'fix the typo '\''recieve'\'' in readme.md and keep $home/bin as it is' | git hash-object --stdin`
  → `089c30e1…`, suffix `t089c30`.
- "I haven't started anything … Both give suffix t089c30, so a worktree for it already exists". It
  named the folder, its branch `fix-typo-recieve-readme` ("the earlier agent moved off its scratch
  branch"), "Uncommitted plan files: none" and the earlier agent `t2` (`done`), then asked: continue
  there with `/jdi:status`, run `/jdi:do` again there, or skip.
- Answer `skip`: "this herd started nothing. It created no worktree, branch, space or herd record."
  Checked: still one record file, 3 herd folders, 4 `git worktree list` lines, 4 terminals.

### (c) The parse rules: **pass** (on the second attempt; see F-j)

- **First attempt (same Butler session, tracker `github` added to the local config).**
  `/jdi:herd 12 "fix typo" bump lint` was answered with **no tool call**. The Butler reused the
  configuration it had read in (a) ("This repo has no tracker configured (tracker.name: none)") and
  offered `12`, `fix typo` and `bump lint` as three tasks. That is the right reading for the config
  it held, but the edited config was never read. Answer `cancel`; nothing created. Then `/clear`.
- **Second attempt (after `/clear`).** The config was read ("`.jdi/config.local.yml` overrides the
  herd, harnesses and tracker blocks"). One question, nothing started before it, no `gh` and no T2
  call: "1. Issue #12  2. Task: "fix typo" (you quoted it)  3. Unclear: bump lint isn't an issue ID.
  As written it becomes one task, "bump lint"." Answer `cancel`: "No worktrees, branches, workspaces
  or agents were created" (checked: one record, 3 herd folders).
- **Tracker `none` again, `/clear`, `/jdi:herd 201 202`.** One question: "This repo has no tracker
  (tracker.name: none), so 201 and 202 can't be treated as issue IDs … they become one candidate
  task, word for word: Task 1: 201 202". `cancel`; nothing created. The same reply said "No
  `.jdi/config.local.yml` exists" while quoting that file's `do` mode and args (F-k).
- Local config restored.

### (d) `prep` mode: **pass**

Local `herd.mode: prep`, `/clear`, `/jdi:herd "add a --shout flag to greet"` (herd `20261117T012450`).
- Name `add-shout-flag-greet-t9d7ae5`. The Butler sent
  `hc send t5 '/jdi:prep add a --shout flag to greet (untracked, started by /jdi:herd)' --if idle`
  (the quoted `--shout` survived the `--kind` drop). The agent received
  `<hc from="t1">/jdi:prep add a --shout flag to greet (untracked, started by /jdi:herd)</hc>`.
- The agent asked no tracking question. It ran
  `git switch -c add-shout-flag-to-greet origin/main` and wrote
  `plans/add-shout-flag-to-greet/{PLAN.md,01-implement-shout.md,02-uat.md}` (uncommitted).
  `PLAN.md` has `Tracker: none`, `Issue: none`,
  `Base commit: origin/main @ d9f57e0…`. Prep finished in under a minute (research and planning
  inline, "the repo is five files") and stopped on its own (`done`), so there was nothing to stop.
- The Butler's report named prep mode ("it will stop at a plan and open no PR").

### (e) An invalid mode: **pass** (announced twice; see note)

Local `herd.mode: bogus`, `/clear`,
`/jdi:herd "rename greet.py's greeting to say Hi instead of Hello"` (herd `20261117T012727`).
- One progress line before the worktree, "Note: herd.mode: bogus is invalid, so this herd runs as
  prep", and the report repeated it: "It ran in prep mode, not do: … herd.mode: bogus, which isn't a
  valid mode, so the herd used prep". The second mention is step 10's mode naming, not a second
  warning. The report put the value in `.jdi/config.yml` and said no local config existed (F-k).
- Sent `hc send t6 '/jdi:prep rename greet.py'\''s greeting to say Hi instead of Hello (untracked, started by /jdi:herd)' --if idle`;
  received literally. The prep agent made `rename-greeting-hi` from `origin/main` and a plan, and
  stopped on its own. Local config restored to `do`.

### (f) Cleanup of (a): **pass** (entry 3's plan question observed in the re-run after task 28, Opus)

> **Re-run after task 27:** entry 3's plan question is still not reachable, because (a)'s agent 3 again
> never reached prep. The first run's pass stands for the rest. See *Re-run after task 27 (2026-11-16)* below.
>
> **Re-run after task 28 (Opus): entry 3's own plan question observed**, with the plan commit offered; "keep" left entry 3 in the record. The Sonnet re-run could not reach it (agent 3 built instead). See *Re-run after task 28 (Opus)* below.

`/clear`, `/jdi:herd --cleanup 20261117T011544`; all agents `done`.
- One list, one question. Entry 1: space `sp813873…`, plain removal, scratch `-1` "→ delete (still
  at its base)". Entry 2: scratch `-2` "→ already gone" (agent 2 renamed it). Entry 3: scratch `-3`
  "→ kept" ("committed onto the scratch branch itself (062af12, 1 commit past its base)"). The
  feature branches `fix-typo-recieve-readme` and `greet-strip-whitespace` were named and left
  alone. The other records (`…012450`, `…012727`) were left alone.
- **Not reachable:** agent 3 never ran prep, so its worktree held no plan and got no plan question.
  To keep entry 3 in the record anyway, the answer was "yes for entries 1 and 2; skip entry 3 and keep it".
- **Removal, from the transcript:** `git -C <wt> status --porcelain -- plans` →
  `herdr-app do space.close --id <space> --confirmed true` → `git worktree remove <path>` (plain) →
  `show-ref --verify --quiet` and `rev-list --count d9f57e0..refs/heads/<scratch>` = 0 →
  `git branch -D`.
- **After.** Record `state: handed_off` with one entry, `n: 3`, `web-service-accounts-t9e2fdc`, its task
  text. Worktrees 1 and 2 gone, scratch `-1` deleted, both feature branches kept, entry 3's space,
  worktree and branch intact. This is the partial upkeep (one entry kept while others go) that #37
  could not observe.
- **Report:** per task, `name: task text` and the result; "The herd record … now lists only entry 3."

### (g) The TUI: **pass** (quoting and record; the agent repeated F-f)

A throwaway space `tui` on `<scratch>/repo` ran
`["/usr/bin/env","-u","HERDR_SOCKET_PATH","HERDR_CONFIG_PATH=<scratch>/herdr-config.toml","<absolute herdr>","--session","<probe-session>"]`.
`-u` drops the guard's `no-tui` path so the nested server takes its session socket. The config held
only `[worktrees] directory = "<scratch>/worktrees"`. Through the guard with `JDI_PROBE_TUI=1`:
`herdr status server` → `socket: ~/.config/herdr/sessions/<probe-session>/herdr.sock`;
`herdr workspace list` → only `w1` (`[1] repo`).
- Butler: `herdr agent start uat-butler --kind claude --pane w1:p1 -- --plugin-dir <this repo> --settings …`.
  It was told once to ask in plain text and that `HERDR_CONFIG_PATH` names Herdr's config.
- `/jdi:herd "add a line to README.md saying don't expand $PATH in examples"` via `herdr agent prompt`.
  Suffix `t624af2` (documented command; recomputed by the driver: `624af2`).
- Transcript: `herdr worktree create … --label 't624af2 add a line to README.md saying don'\''t expand $PATH in examples' --no-focus`,
  then `herdr agent prompt readme-dont-expand-path-t624af2 '/jdi:do add a line to README.md saying don'\''t expand $PATH in examples (untracked, started by /jdi:herd)'`.
- The agent received a **real slash command** (no hc wrapper):
  `<command-args>add a line to README.md saying don't expand $PATH in examples (untracked, started by /jdi:herd)</command-args>`,
  `'` and `$PATH` literal. Its commit added `Don't expand $PATH in examples.` to `README.md`.
- Record `20261117T013145.json`: `surface: tui`, `state: handed_off`, `issue: null`, `task` = the
  text, `workspace_id: "w2"`, `tab_id: "w2:t1"`, `pane_id: "w2:p1"`, `space_id: null`,
  `terminal_id: null`.
- This Butler's announcement and report did name it: "Set herd.mode: prep if you want future herds
  to stop at a plan instead."
- The `do` agent posted no ten-line plan and committed on the scratch branch
  `jdi-herd-scratch-20261117T013145-1`, then pushed it to origin. `gh` was not logged in; it stopped
  with the no-PR-host reason. The nested TUI was stopped at cleanup.

### (u4) Parallel merges on GitHub (M4): **pending, user to walk**

1. Create a throwaway GitHub repository with one file of a few lines, `herd.mode: do` (the default)
   and this branch's plugin (`--plugin-dir`).
2. `/jdi:herd "change line 2 of notes.md to say alpha" "change line 2 of notes.md to say beta"`.
3. **Expected:** both agents open pull requests; the first merges; the second finds its PR no longer
   merges cleanly, updates its branch from `origin/<default>` the way the repository allows, re-runs
   its gates, pushes, waits for the checks on the new head and merges, or stops in its space if the
   conflict needs a product decision.

### (u5) A `do` merge from a worktree (R25): **pending, user to walk**

1. In the same repository, `/jdi:herd "<one small task>"` from the main checkout, with `main` checked
   out there.
2. **Expected, and what to note:** whether `gh pr merge` (deleting the local branch) fails because
   `main` is checked out in the main checkout, and whether `/jdi:do` step 11 reads the merge back from
   GitHub either way.

### (u6) A tracked issue in `do` mode: **pending, user to walk**

1. With a tracker configured, `/jdi:herd <issue-id>` in `do` mode.
2. **Expected:** the agent receives `/jdi:do <issue-id> (started by /jdi:herd)`; the issue moves to In
   Progress, then In Review, and closes or advances when the PR merges.

### (u7) A Codex or OpenCode herd kind (M8, R24): **pending, user to walk**

1. `/jdi:herd --kind codex "<a task too big for one session>"` (and the same with `opencode`).
2. **Expected:** the agent says the work is too big, then finds the prep command although
   `${CLAUDE_PLUGIN_ROOT}` does not resolve there (OpenCode: `jdi-prep.md` beside `jdi-do.md`),
   and continues with prep in the same session.

### Repository checks

1. **Log complete.** 11 scenario ids, (a)–(g) and (u4)–(u7).
2. **Sanitised.** No home path or probe session name in this section (control count for the whole
   file: 4).
3. **Self-checks.** Logged under *Harness*, before (a); all three passed.
4. **Scan 1.** No hunk before line 780 (control: `@@ -538,0 +539,4 @@`, `@@ -597,4 +601,17 @@`).
5. **Scan 2.** The removed lines are the three old `INVOCATION_ROWS` rows, `'--label "<SHORT-ID> <TITLE>"',`,
   `'hc send <terminal> "<invocation>" --if idle',`, two lines of `HerdBlockTest`'s docstring, and one
   more: `self.schema_keys = jdi_files.key_paths(jdi_files.schema_block())` in `HerdBlockTest.setUp`
   (commit `76a2550`). It was replaced by `self.schema = jdi_files.schema_block()` and
   `self.schema_keys = jdi_files.key_paths(self.schema)`, the same value, so it is a refactor and no
   pin was weakened. No `assert` line was removed.
6. **Scan 3.** `0` and `0` (control: 20).
7. **Scan 4.** No output (control: 93).
8. **Scan 5.** Three lines, each `"version": "1.0.13"`.
9. **Scan 6.** No output; `git ls-files | grep -c 'jdi/herds'` → `0` (controls: 3 and 1).
10. **Isolation.** See *Cleanup*. Re-run afterwards: `git worktree list | wc -l` → `1`; probe sessions
    under `~/.config/herdr/sessions/` → `0`.
11. **GitHub and origin.** `rev-parse main` on the bare origin was `d9f57e0` after (a) and (g) and
    at cleanup. `<scratch>/gh-empty` was empty at cleanup (no `hosts.yml`). Every `gh` call (agents
    1–3 and (g): `gh pr create`, `gh repo view`) printed "To get started with GitHub CLI, please
    run: gh auth login". None reached a host. The Butlers ran no `gh` command.
12. **Clause map.** See below.
13. **Full suite.** `python3 -m unittest discover -s tests -v`: `Ran 256 tests … OK`.

### Clause map status

| Clause | Status |
|---|---|
| `herd.mode` exists, default `do` | tests pass; (a) ran `do` and named the mode (announcement weak, F-i) |
| `do` mode hands each agent `/jdi:do <task>` | tests pass; (a) and (g): each first message is the invocation, literal (app: inside an `<hc from>` wrapper, F-h) |
| Too-big continues into `/jdi:prep` in the same session | tests pass; **(a) agent 3 failed**: no E7 line, built and pushed instead (F-e). Not observed working; new task |
| … nothing built at that point | tests pass; not observed (agent 3 built everything) |
| `prep` keeps today's behaviour | tests pass; (d), (e) pass |
| Free-text tasks alongside issue IDs | tests pass; (a), (c) pass |
| An untracked task needs no tracker | tests pass; (a) no `gh` in the Butler; (d) no tracking question |
| Name, folder and record entry from the description | tests pass; (a) names and record, (b) suffix found |
| Handed over as text | tests pass; (a), (d), (e), (g) literal `'` and `$` |
| `do` stops become waits; the report says so | tests pass; (a) agents 1–3 and (g) waited with the no-PR-host reason; the report's sentence is shorter than H9's |
| Both Herdr surfaces | app: (a)–(f); TUI: (g) |
| `--cleanup` and the record keep working | tests pass; (f) pass (scratch deleted at base, feature branches kept, partial upkeep). Merged case: (u4)/(u5) |
| Docs: `do` merges unattended; `herd.mode: prep` is the way back | tests pass; (a) partial (F-i), (g) pass |
| A `do` agent updates when a sibling merged first | tests pass; not observable here: (u4) |
| Same PR, no new release | `VersionTest`; check 8 |
| Standalone `/jdi:do`, `/jdi:prep`, issue herds, confinement | tests pass (256); checks 5 and 7; (c) recognised issue `12` with a tracker |

### Findings (not fixed here; product docs are a new task)

- **F-e. The too-big fallback did not fire (R27 class, a new task).** On sonnet, a herd-started
  `/jdi:do` "turn this into a web service with user accounts, a database, and an admin dashboard"
  built and pushed the whole service, with no step-4 plan and no step-5 sizing judgment visible.
  *Diagnosis:* do.md's *too big* stop is a judgment the agent never paused to make. Nothing in
  `/jdi:do` forces a visible sizing verdict before step 6 (the ten-line plan's **Stops** field is
  where it would show, and it was skipped, F-g). Under bypass permissions and on a small model the
  path of least resistance is to build. A candidate fix is an explicit gate in step 4 or step 5
  ("before any edit, state *fits one PR* or *too big*, with the reason"), plus a repeat on a larger
  model. One run only; not re-run, to keep spend down.
- **F-f. `do` agents adopt the herd's scratch branch.** 3 of 4 `do` agents did not create a feature
  branch from `origin/<default>`. Agent 2 renamed the scratch branch (`git branch -m`); agent 3 and
  (g) committed on it and pushed it to origin. Only agent 1 ran `git switch -c … origin/main`.
  *Diagnosis:* do.md step 2 has no rule for a branch the herd created. Prep step 6's "if the
  current branch does not already name this work" has no counterpart in do, and the scratch branch
  looks like a clean branch at `origin/<default>`. Consequences: `jdi-herd-scratch-*` names reach
  origin (and would title a PR), and cleanup keeps those scratch branches because they hold commits,
  which is correct by H9's rule but leaves them behind.
- **F-g. No ten-line plan.** None of the four `do` agents posted step 4's Change/Files/Proof/Stops.
  Agents 1 and 2 edited files before loading `/jdi:do` at all (see F-h).
- **F-h. On the app, the invocation arrives wrapped and is not a slash command.** `hc send` from
  inside a terminal (the Butler's `t1`) delivers `<hc from="t1">/jdi:do …</hc>`, so Claude Code does
  not expand the command. The model decides whether and when to call `Skill(jdi:do)`, and agents 1
  and 2 started editing first. The same wrapper was seen in #36 (`<hc from="t2">/jdi:prep 101</hc>`),
  where prep happened to start first. On the TUI, `herdr agent prompt` delivered a real
  `<command-message>jdi:do`. H9's app handoff may need a way to send unwrapped (hc has no flag for it
  in 0.1.21), or a first line telling the agent to run the command before anything else.
- **F-i. The M5 announcement is fragile.** On the app it appeared only as a narration line before the
  first start, and neither it nor the report named `herd.mode: prep`. On the TUI both did. This
  points to model variance; herd.md step 8's sentence could be a required verbatim line.
- **F-j. A Butler reuses its config across turns.** A second `/jdi:herd` in the same session did not
  re-read `.jdi/config.local.yml` after it changed, and answered with no tool call. herd.md step 1
  says to read the config, but a long-lived session skipped it. UAT harness remedy: `/clear` between
  config changes. A product remedy would make step 1 say "read it again on every run".
- **F-k. Concatenated config read.** The Butler `cat`-ed `config.yml` and `config.local.yml` in one
  command and then attributed local values to `config.yml` ("No `.jdi/config.local.yml` exists").
  The merged values were right; only the override line was wrong. Minor.
- **F-l. A read of the real app home.** Before using `$HERDR_APP_HOME`, the (a) Butler ran
  `cat ~/.config/herdr-app/settings.json` (read-only, harmless; H9 says
  `${HERDR_APP_HOME:-~/.config/herdr-app}`). Minor.
- **F-m. Harness notes.** The user's global gitignore hides `.jdi/` (the committed config needed
  `git add -f`). Global commit signing was disabled in the scratch clone only. Agent 3 wrote
  `/tmp/p8765` outside `<scratch>`, removed at cleanup. The nested TUI needs `HERDR_SOCKET_PATH`
  unset in its own argv, because the guard's `no-tui` value reaches the app's terminals.

### Cleanup

- **Closed, through the guard.** The nested TUI with `herdr --session <probe-session> server stop`
  (exit 0); every app space (5) with `space.close --confirmed true` (`{"ok":true}` each);
  `window.close` (`{"ok":true}`, the app process exited); `hc server stop` (`{"stopped":true}`).
  No process with a `<scratch>` working directory and none naming the probe session remained.
- **Logged before removal.** `git -C <scratch>/origin.git rev-parse main` = `d9f57e0…` (= origin
  SHA); `ls -A <scratch>/gh-empty` → empty; `<scratch>/no-tui/` → empty.
- **Removed.** The throwaway home, `~/.local/state/herdr-core/<probe-session>/`,
  `~/.config/herdr/sessions/<probe-session>/`,
  `~/.local/state/herdr-automatic-rename/sessions/<probe-session>/`, the Butlers' and agents'
  transcript folders under `~/.claude/projects/` and their temporary folders for `<scratch>` paths,
  `/tmp/p8765`, and the one `~/.claude.json` `projects` entry under `<scratch>` (with `jq`, not
  restored wholesale). Then `git worktree prune` in the clone, and `<scratch>` removed (including
  `gh-empty` and `no-tui`).
- **Checks afterwards** (outside the guard, read-only), all equal to the setup snapshots:
  - The user's `hc ls --json`: **2** terminals.
  - `~/.local/state/herdr-core/`: `default jute personal vault`.
  - `~/.config/herdr/sessions/`, the rename state, `herdr session list` and `~/.claude/projects/`:
    unchanged.
  - `~/.claude.json` `projects` keys: the same 4.
  - The real repository: `git worktree list` has 1 line, and its git directory has no `jdi/` folder.
  - `herdr-app status` with the probe home exits 2, and no `~/.config/<probe-home>` remains.

### Re-run after task 27 (2026-11-16)

Scenario (a) again, after task 27 (R7 in `## Probe log (#37)`) changed H9 on the app to hand off with
`env -u HC_TERMINAL_ID hc send <terminal> '<invocation>' --if idle`, and (f)'s entry-3 plan question
only if (a) reached prep. (b)–(e) and (g) passed in the first run and were not repeated. Same
versions (`herdr` 0.9.3, `herdr-app` 0.1.16, `hc` 0.1.21, `git` 2.56.0, `claude` 2.1.326), branch
HEAD `21dc299`.

**Harness, rebuilt as the first run's.**
- **Guard** `<scratch>/g`, the same script (refusal unless `JDI_PROBE_SESSION` and `JDI_PROBE_HOME`
  are set and the session matches `jdiprobe-*`; the nine `HC_*`/`HERDR_*` variables, `CLAUDECODE`,
  every `CLAUDE_CODE_*`, `CLAUDE_PID`, `CLAUDE_EFFORT` and the five `GH_*` token variables unset;
  `HC_SESSION`, `HERDR_APP_HOME`, `GH_CONFIG_DIR=<scratch>/gh-empty` and
  `HERDR_SOCKET_PATH=<scratch>/no-tui/herdr.sock` exported). A new `<probe-session>` and a short
  throwaway home `~/.config/<probe-home>` (six characters).
- **Self-checks, run and logged before anything else.**
  1. `env -u JDI_PROBE_SESSION <scratch>/g echo X`: `exit=64`, 0 stdout bytes, stderr
     `probe guard: JDI_PROBE_SESSION and JDI_PROBE_HOME must both be set; refusing`. **Pass.**
  2. The user's `herdr session list` captured outside the guard; `<scratch>/g herdr status` exited 1
     with the `sun_path` error; `herdr session list` again: byte-identical. `<scratch>/no-tui/`
     stayed empty. **Pass.**
  3. `<scratch>/g gh auth status`: exit 1, `You are not logged into any GitHub hosts`. **Pass.**
- **Snapshots** (outside the guard, read-only): the user's `hc ls --json` **2** terminals; the real
  `git worktree list` **1** line; `~/.claude.json` **4** `projects` keys;
  `~/.local/state/herdr-core/` = `default jute personal vault`; `~/.config/herdr/sessions/` four
  entries; `herdr session list` five sessions; `~/.claude/projects/` and the rename state listed.
- **Scratch repository**, as the first run's: bare `<scratch>/origin.git`, one commit `9e725ba` (the
  **origin SHA**), the same six files (the committed `.jdi/config.yml` added with `git add -f`),
  clone `<scratch>/repo`, `origin/HEAD` → `origin/main`, throwaway identity and
  `commit.gpgsign false` in the clone only. Suffixes recomputed with the documented command:
  `t089c30`, `t75a757`, `t9e2fdc`. The local config: `herd: {kind: claude, mode: do}` and
  `harnesses.claude.args: ["--model", "sonnet", "--plugin-dir", "<this repo>", "--settings", '{"enabledPlugins":{"jdi@just-do-it":false}}']`,
  so herd agents load this branch's plugin.
- **App.** Home `settings.json` `{"worktrees":{"directory":"<scratch>/worktrees"}}`. Through the
  guard, `herdr-app status` exited 2 and `hc ls --json` printed `{"hidden_finished":0,"terminals":[]}`;
  `herdr-app` started in the background (a window appeared); `overlay.close` → `{"ok":true}`.
- **Trust.** `~/.claude.json` copied aside; only `<scratch>/repo` pre-trusted (`jq` to a temporary
  file, then `mv`). No herd worktree opened a trust dialog.
- **The Butler.** `claude --plugin-dir <this repo> --settings '{"enabledPlugins":{"jdi@just-do-it":false}}'`
  on the default model, as the argv of a throwaway `space.new` (`butler`, terminal `t1`) on
  `<scratch>/repo`; `hc wait` → `idle`. First message: ask in plain text, never with the question
  tool (reply `OK`). The herd command was then sent without `--if idle`, because after its first turn
  `t1` reported `done`, and `hc send t1 … --if idle` refused with exit 10, `t1 is done, not idle`
  (nothing typed). No dialog was answered and no `hc keys` was used.

#### (a) A `do`-mode herd of untracked tasks: **fail** (agent 3 again; F-h closed)

`/jdi:herd "fix the typo 'recieve' in README.md and keep $HOME/bin as it is" "make greet() strip surrounding whitespace from the name, with a test" "turn this into a web service with user accounts, a database, and an admin dashboard"`,
herd ID `20261117T030221`.

- **The herd: pass on the handoff; the announcement is still weak (F-i).**
  - No parse question. 0 `gh` commands in the Butler's transcript.
  - The documented hash command, with the normalised task-1 text single-quoted as `'\''`; names
    `fix-typo-recieve-readme-t089c30`, `greet-strip-whitespace-t75a757`,
    `web-service-accounts-t9e2fdc`, all three suffixes as the table. The app home was read as
    `${HERDR_APP_HOME:-$HOME/.config/herdr-app}/settings.json` (the throwaway one, so F-l did not
    recur).
  - Three `git worktree add -b jdi-herd-scratch-20261117T030221-<N> <path> origin/main`, three
    `space.new --name '<suffix> <task text>'` (task 1 single-quoted with `'\''`, `$HOME` literal),
    `hc wait` → `idle` for `t2`, `t3`, `t4`, then:
    `env -u HC_TERMINAL_ID hc send t2 '/jdi:do fix the typo '\''recieve'\'' in README.md and keep $HOME/bin as it is (untracked, started by /jdi:herd)' --if idle`,
    and the same form for `t3` and `t4`; each `{"started":true,"status":"idle","turn":0}`, exit 0.
  - Record `<scratch>/repo/.git/jdi/herds/20261117T030221.json`: `surface: app`,
    `state: handed_off`, 3 entries, each `issue: null`, `task` the typed text without the clause
    (`$HOME` literal), `seeded: false`, `base_commit` = origin SHA, app IDs filled.
  - **Each agent's first received message is a real slash command, no `<hc` wrapper (F-h closed).**
    Transcript of `t2`: `<command-message>jdi:do</command-message>` `<command-name>/jdi:do</command-name>`
    `<command-args>fix the typo 'recieve' in README.md and keep $HOME/bin as it is (untracked, started by /jdi:herd)</command-args>`,
    followed by the expanded `# JDI: Do` body; the same for `t3` and `t4`. `grep -c '<hc'` over the
    three agent transcripts: `0`, `0`, `0`. `$HOME` arrived unexpanded.
  - **Mode announcement (M5): partial, as before.** Before the first `space.new` the pane showed only
    Claude Code's tool summary line ("… opening the agent spaces in do mode so each one opens and
    merges its own PR unattended and in parallel …"); no chat message, and `herd.mode: prep` is named
    nowhere (0 matches in the Butler's text).
  - **Report: pass, partial as before.** Names `do` mode ("Each one will open and merge its own pull
    request, unattended and in parallel"), one row per task, args, seeding, the record path,
    `/jdi:herd --cleanup 20261117T030221`, and the do-stop sentence ("`done` can mean merged or
    stopped before merging … Open the space to see which"). It does not name `herd.mode: prep`, and
    it said "`.jdi/config.local.yml` is absent" while applying that file's args (F-k again).
- **Agent 1 (typo): pass on outcome; no ten-line plan.** `/jdi:do` loaded before any action. It read
  the config and repository, saw it was on `jdi-herd-scratch-20261117T030221-1`, then
  `git fetch -q origin && git switch -q -c fix-typo-receive-readme origin/main` (**from
  `origin/main`, not the scratch branch: F-f did not recur here**), fixed the typo, `$HOME/bin`
  literal, `python3 -m unittest` OK, committed `e9607df`, `git push -q -u origin
  fix-typo-receive-readme`, `gh pr create --fill` → "please run: gh auth login". Stop: "`origin` is
  a plain local bare repo, and `gh` isn't authenticated, so I couldn't open a PR. I didn't push to
  `main` or merge locally". **No step-4 plan (Change/Files/Proof/Stops) was posted** (F-g).
- **Agent 2 (strip): pass on outcome; no ten-line plan.** `/jdi:do` loaded first. `git fetch`, then
  `git checkout -q -b greet-strip-whitespace origin/main` (**from `origin/main`**), `name.strip()`
  and the test `test_strips_surrounding_whitespace` (2 tests OK), committed `19e0d1d`, pushed
  `greet-strip-whitespace`, `gh pr create` not logged in. Stop: "`origin` is a local bare repo with
  no PR host, and `gh` isn't authenticated. Merging would mean pushing straight to `main`, which
  this workflow forbids." No step-4 plan (F-g).
- **Agent 3 (web service): fail, the same way as the first run.** Expected: the E7 line before any
  edit, no push, prep's steps in the same session (no tracking question, one feature branch,
  `PLAN.md` with `Tracker: none` / `Issue: none`). Observed, with `/jdi:do` loaded as a real slash
  command: two read-only commands, then it **built the service** on the scratch branch
  `jdi-herd-scratch-20261117T030221-3`: a `webapp/` package (stdlib WSGI, SQLite, scrypt, sessions,
  CSRF, admin dashboard), `test_webapp.py` (11 tests OK), a README section; it ran the server on
  `localhost:8765` (killed after), committed `4ef8793`, ran `git push -u origin HEAD` (the scratch
  branch reached origin) and `gh pr create` (not logged in). Its assistant text never says "too big",
  never mentions prep (0 assistant messages do; the only "too big" strings in its transcript are in
  the expanded `do.md` body), posted no plan, created no feature branch, wrote no `PLAN.md`. The
  final message stopped on the no-PR-host reason. It also left `mktemp` files in `/tmp` (a cookie
  jar and the SQLite file), outside `<scratch>`; removed at cleanup. Agent 3 finished in about two
  minutes and was `done` before the driver looked, so there was nothing to stop.
- **Origin afterwards.** `git -C <scratch>/origin.git rev-parse main` = `9e725ba` (= origin SHA).
  Branches on origin: `fix-typo-receive-readme`, `greet-strip-whitespace`,
  `jdi-herd-scratch-20261117T030221-3`, `main`. **No push to `main`.**

| Check (task file, (a)) | Result | Why |
|---|---|---|
| No parse question | pass | all three quoted; no question asked |
| Mode announced before the first start, naming `herd.mode: prep` | fail (partial) | only a tool-summary line; `herd.mode: prep` never named (F-i) |
| No tracker step, no `gh` call (Butler) | pass | 0 `gh` commands in the Butler's transcript |
| Record: 3 entries, `issue: null`, `task` text, suffixes, `surface: app`, `handed_off` | pass | as listed above |
| Handoff `env -u HC_TERMINAL_ID hc send <t> '/jdi:do … (untracked, started by /jdi:herd)' --if idle`, `'\''`, `$HOME` literal | pass | the three commands in the transcript, exit 0 |
| Each agent's first message is the invocation, a real slash command, no `<hc` | pass | `<command-name>/jdi:do`, 0 `<hc` in all three transcripts |
| Agents 1–2: ten-line plan in chat | **fail** | neither posted Change/Files/Proof/Stops (F-g) |
| Agents 1–2: feature branch from `origin/main` | pass | `git switch -c … origin/main`, `git checkout -b … origin/main` (F-f not seen in 1–2) |
| Agent 2: a test | pass | `test_strips_surrounding_whitespace`, 2 tests OK |
| Agents 1–2: push to origin, stop at step 8 with the no-PR-host reason | pass | both pushed their branches and stopped naming the bare origin and `gh` |
| Origin `main` unchanged, no push to `main` | pass | `9e725ba` before and after |
| Agent 3: E7 line ("too big", why, continues with `/jdi:prep`) | **fail** | never judged size; built the whole service (F-e) |
| Agent 3: no push | **fail** | pushed `jdi-herd-scratch-20261117T030221-3` to origin |
| Agent 3: prep keeps do's branch; no tracking question; `PLAN.md` with `Tracker: none` / `Issue: none` | **fail (not reached)** | prep never ran; no feature branch, no `PLAN.md` |
| Report: rows, mode, do-stop sentence, record path, cleanup command | pass | all present; `herd.mode: prep` not named (F-i) |

#### (f) Cleanup of (a), entry 3's plan question: **not run (not reachable)**

Agent 3 never reached prep, so its worktree held no `plans/` folder and cleanup would have no plan
question to ask for entry 3. Per the brief, (f) was not repeated; the herd was removed by hand at
cleanup, through the guard. The first run's (f) pass stands for the rest of the scenario; entry 3's
own plan question remains **unobserved**.

#### Diagnosis (no product docs changed here)

- **F-h is closed.** Task 27's `env -u HC_TERMINAL_ID` handoff worked on all three agents: each
  received a real `/jdi:do` slash command and loaded it before its first tool call. Agents 1 and 2
  no longer edited files before loading `/jdi:do`.
- **F-f is narrowed, not closed.** With the command loaded first, agents 1 and 2 followed step 2 and
  branched from `origin/main`. Agent 3, which skipped steps 4–5, also skipped step 2 and committed on
  the scratch branch, so the scratch name reached origin again. The step-2 rule held only where the
  agent followed the steps at all.
- **F-e is not caused by the tag.** Agent 3 had the full `do.md` body in context, including step 5's
  herd rule, and still went from two reads straight to building. No `do` agent in either run (0 of
  6, both runs, plus (g)) posted step 4's ten-line plan, and step 5's sizing judgment lives in that
  plan's **Stops** field, so nothing made the agent pause where the too-big judgment would be made.
  On sonnet with bypass permissions, "the request is the authorization … do not wait for approval"
  wins over an unforced judgment. A candidate fix (a new task, not done here): make step 4 a gate
  whose first line is a required verdict, "Fits one PR" or "Too big for one session: <why>", posted
  before any edit or branch, and repeat (a) on sonnet and once on a larger model.
- **F-g persists (3 of 3 here).** The ten-line plan is skipped even on small tasks. The same gate
  would cover it.
- **F-i persists.** The mode announcement does not appear as a chat line before the first start, and
  `herd.mode: prep` is not named. The TUI Butler of (g) did name it, so it is model variance on a
  sentence that is not required verbatim.
- **F-k recurred.** The report said the local config was absent while applying its args.

#### Clause map status (re-run; replaces the first run's rows for (a) and (f))

| Clause | Status |
|---|---|
| `herd.mode` exists, default `do` | tests pass; (a) ran `do` and named it in the report; the pre-start announcement is weak (F-i) |
| `do` mode hands each agent `/jdi:do <task>` | tests pass; **(a) pass**: each first message is a real `/jdi:do` slash command with the literal task (F-h closed) |
| Too-big continues into `/jdi:prep` in the same session | tests pass; **(a) agent 3 failed again** (F-e): no E7 line, built and pushed. Not observed working; needs a new task |
| … nothing built at that point | tests pass; not observed (agent 3 built everything again) |
| An untracked task needs no tracker | tests pass; (a) no `gh` in the Butler; no tracking question observed only in (d) (agent 3 never reached prep) |
| Name, folder and record entry from the description | tests pass; (a) pass |
| Handed over as text | tests pass; (a) pass, now also arriving as a real slash command |
| `do` stops become waits; the report says so | tests pass; (a) agents 1–3 stopped on the no-PR-host reason; the report's sentence present |
| Both Herdr surfaces | app: (a) re-run and (b)–(f) of the first run; TUI: (g) |
| `--cleanup` and the record keep working | tests pass; first run's (f) pass; **entry 3's own plan question still unobserved** (not reachable) |
| Docs: `do` merges unattended; `herd.mode: prep` is the way back | tests pass; (a) partial (F-i), (g) pass |
| Other rows | unchanged from the first run's table |

#### Repository checks (re-run)

- **Full suite.** `python3 -m unittest discover -s tests`: `Ran 260 tests … OK` (256 from Tasks
  20–25 plus task 27's tests).
- **GitHub and origin.** Origin `main` = `9e725ba` after (a) and at cleanup; `<scratch>/gh-empty`
  empty (no `hosts.yml`); every `gh` call (agents 1–3) printed "please run: gh auth login", none
  reached a host; the Butler ran none.

#### Cleanup (re-run)

- **Closed, through the guard.** The four app spaces (`butler` and the three herd spaces) with
  `space.close --confirmed true` (`{"ok":true}` each), `window.close` (`{"ok":true}`; `herdr-app
  status` then exited 2), `hc server stop` (`{"stopped":true}`). No process naming the probe session
  or `<scratch>` remained. No TUI was started.
- **Logged before removal.** Origin `main` = `9e725ba` (= origin SHA); `ls -A <scratch>/gh-empty` and
  `<scratch>/no-tui/` empty.
- **Removed.** The throwaway home, `~/.local/state/herdr-core/<probe-session>/` (no TUI session or
  rename state was created), the Butler's and agents' transcript folders under `~/.claude/projects/`,
  Claude's temporary and cache folders for `<scratch>` paths, agent 3's two `/tmp` files, the one
  `~/.claude.json` `projects` entry under `<scratch>` (with `jq`, not restored wholesale), and the
  copy of `~/.claude.json`. Then `git worktree prune` in the clone and `<scratch>` removed.
- **Checks afterwards**, all equal to the snapshots: the user's `hc ls --json` **2** terminals;
  `herdr session list` byte-identical; `~/.local/state/herdr-core/` = `default jute personal vault`;
  `~/.config/herdr/sessions/`, the rename state and `~/.claude/projects/` unchanged; `~/.claude.json`
  `projects` keys the same 4; the real `git worktree list` 1 line, and no `jdi/` folder in its git
  directory.

### Re-run after task 28 (Sonnet) (2026-11-16)

Scenarios (a) and (f) again, after task 28 made `/jdi:do` step 4 a gate whose first field is
`**Size:** fits one pull request` or `**Size:** too big for one session — <why>`, posted before any
edit, and made herd step 8 quote its announcement ("Mode `do`: each agent opens and merges its own
pull request, unattended and in parallel with the others; `herd.mode: prep` stops each at a plan
instead."). Herd agents on Sonnet (`--model sonnet` in `harnesses.claude.args`), the Butler on the
account's default model (the pane showed Opus 5.5). Same versions (`herdr` 0.9.3, `herdr-app`
0.1.16, `hc` 0.1.21, `git` 2.56.0, `claude` 2.1.326), branch HEAD `a952b74`. (b)–(e) and (g) were
not repeated.

**Harness, rebuilt as the previous re-run's**, in a fresh `<scratch>` used for this run only.
- **Guard** `<scratch>/g`, the same script (refusal unless `JDI_PROBE_SESSION` and `JDI_PROBE_HOME`
  are set and the session matches `jdiprobe-*`; the nine `HC_*`/`HERDR_*` variables, `CLAUDECODE`,
  every `CLAUDE_CODE_*`, `CLAUDE_PID`, `CLAUDE_EFFORT` and the five `GH_*` token variables unset;
  `HC_SESSION`, `HERDR_APP_HOME`, `GH_CONFIG_DIR=<scratch>/gh-empty` and
  `HERDR_SOCKET_PATH=<scratch>/no-tui/herdr.sock` exported). A new `<probe-session>` and a short
  throwaway home `~/.config/<probe-home>` (six characters).
- **Self-checks, run and logged before anything else.**
  1. `env -u JDI_PROBE_SESSION <scratch>/g echo X`: `exit=64`, 0 stdout bytes, stderr
     `probe guard: JDI_PROBE_SESSION and JDI_PROBE_HOME must both be set; refusing`. **Pass.**
  2. The user's `herdr session list` captured outside the guard; `<scratch>/g herdr status` exited 1
     with the `sun_path` error; `herdr session list` again: byte-identical to the first capture and
     to the snapshot. `<scratch>/no-tui/` stayed empty. **Pass.**
  3. `<scratch>/g gh auth status`: exit 1, `You are not logged into any GitHub hosts`. **Pass.**
- **Snapshots** (outside the guard, read-only, taken once before this run and reused for the Opus
  run): the user's `hc ls --json` **2** terminals; the real `git worktree list` **1** line;
  `~/.claude.json` **4** `projects` keys; `~/.local/state/herdr-core/` = `default jute personal vault`;
  `~/.config/herdr/sessions/` four entries; `herdr session list` five sessions; `~/.claude/projects/`,
  the rename state, `~/.config/` and `/tmp` listed; no `jdi/` folder in the real repository's git
  directory.
- **Scratch repository**, as before: bare `<scratch>/origin.git`, one commit `ba8d317` (the **origin
  SHA**), the same six files (the committed `.jdi/config.yml` added with `git add -f`), clone
  `<scratch>/repo`, `origin/HEAD` → `origin/main`, throwaway identity and `commit.gpgsign false` in the
  clone only. Suffixes recomputed: `t089c30`, `t75a757`, `t9e2fdc`. Local config
  `herd: {kind: claude, mode: do}`,
  `harnesses.claude.args: ["--model", "sonnet", "--plugin-dir", "<this repo>", "--settings", '{"enabledPlugins":{"jdi@just-do-it":false}}']`.
- **App.** Home `settings.json` `{"worktrees":{"directory":"<scratch>/worktrees"}}`. Through the
  guard, `herdr-app status` exited 2 and `hc ls --json` printed `{"hidden_finished":0,"terminals":[]}`;
  `herdr-app` started in the background; `overlay.close` → `{"ok":true}`.
- **Trust.** `~/.claude.json` copied aside; only `<scratch>/repo` pre-trusted (`jq` to a temporary
  file, then `mv`). No herd worktree opened a trust dialog.
- **The Butler**, as before: `claude --plugin-dir <this repo> --settings '{"enabledPlugins":{"jdi@just-do-it":false}}'`
  as the argv of a throwaway `space.new` (`butler`, `t1`) on `<scratch>/repo`, `hc wait` → `idle`,
  then the plain-text instruction (reply `OK`). The herd command was sent without `--if idle` (`t1`
  was `done`). `/clear` and the instruction again before (f). No dialog was answered and no
  `hc keys` was used.
- **Reading the panes.** A pane line of the form `● <text> · summary` is Claude Code's display of a
  **thinking block**, not a chat message: the transcript holds it as `{"type":"thinking"}` in the
  assistant turn, with no `text` block. Every check below that says "in chat" was read from the
  transcript's `text` blocks.

#### (a) A `do`-mode herd of untracked tasks: **fail** (no size verdict posted; agent 3 built and pushed again)

Herd ID `20261117T033406`.

- **The herd.** No parse question; 0 `gh` commands in the Butler's transcript; the documented hash
  command with the task-1 text single-quoted as `'\''`; names `fix-typo-recieve-readme-t089c30`,
  `greet-strip-whitespace-t75a757`, `web-service-accounts-t9e2fdc`. Three
  `git worktree add -b jdi-herd-scratch-20261117T033406-<N> … origin/main`, three
  `space.new --name '<suffix> <task text>'` (task 1 with `'\''`, `$HOME` literal), then
  `env -u HC_TERMINAL_ID hc send t2 '/jdi:do fix the typo '\''recieve'\'' in README.md and keep $HOME/bin as it is (untracked, started by /jdi:herd)' --if idle`
  and the same form for `t3`, `t4`. Record `<scratch>/repo/.git/jdi/herds/20261117T033406.json`:
  `surface: app`, `state: handed_off`, 3 entries (each `issue: null`, `task` the typed text without the
  clause, `$HOME` literal, `seeded: false`).
- **The announcement: not a chat line.** Before the first `space.new` the Butler's only words on the
  mode were a thinking block, shown on the pane as `● Each agent will open and merge its own pull
  request unattended and in parallel, or stop at a plan if herd.mode is prep. … · summary`. No
  `text` block before the start says it, step 8's quoted sentence was not used, and `herd.mode: prep`
  appears in no assistant text of the run (0 matches). The report names `do` mode, gives one row per
  task, the args, the record path, `/jdi:herd --cleanup 20261117T033406` and the do-stop sentence
  ("An agent that stops before merging also shows done in the sidebar … Open its space to see its
  reason"), but not `herd.mode: prep`. It also said "there's no `.jdi/config.local.yml` override"
  while applying that file's args (F-k again).
- **Agent 1 (typo).** First message a real slash command (`<command-name>/jdi:do`, 0 `<hc`). Two
  reads, then `git fetch -q origin && git checkout -q -b fix-typo-recieve-readme origin/main`, then
  `sed -i` on `README.md`, commit, `git push -q -u origin fix-typo-recieve-readme`, `gh pr create`
  (not logged in). Stop: "`gh` isn't authenticated here, and the origin is a local bare repo, not a
  GitHub remote." **No plan and no `**Size:**` line in any `text` block**; its only pre-edit words
  were a thinking block ("I'm fixing the "recieve" typo on line 3 …").
- **Agent 2 (strip).** Real slash command. Two reads, then the edit, the test
  `test_strips_surrounding_whitespace` (2 tests OK), a commit and `git push -qu origin HEAD` **on
  `jdi-herd-scratch-20261117T033406-2`** (F-f recurred). Stop on the no-PR-host reason. Its sizing
  was a thinking block only: "The change is small enough for one pull request … I'm using the
  existing herd-created branch". No plan in chat.
- **Agent 3 (web service): fail, as in both earlier runs.** Real slash command. Two reads, then it
  wrote `db.py`, `auth.py`, `app.py`, `serve.py`, `test_app.py` (13 tests OK) and a README rewrite on
  the scratch branch, ran the server on `localhost:8765` with a `mktemp -d` folder in `/tmp` (outside
  `<scratch>`; removed at cleanup), committed `2c79d9b`, ran `git push -q -u origin HEAD` (the scratch
  branch reached origin) and `gh pr create --fill`. Its one sizing thought came **after** the code
  was written, and judged wrongly: "The `greet` change is scoped to one pull request: a stdlib-only
  web service …". No E7 line, no prep, no `PLAN.md`, no feature branch.
- **Origin afterwards.** `main` = `ba8d317` (= origin SHA). Branches: `fix-typo-recieve-readme`,
  `jdi-herd-scratch-20261117T033406-2`, `jdi-herd-scratch-20261117T033406-3`, `main`. **No push to
  `main`.**

| Check (task file, (a)) | Result | Why |
|---|---|---|
| No parse question | pass | all three quoted; none asked |
| Announcement as its own chat line, naming `herd.mode: prep` | **fail** | a thinking block only; `herd.mode: prep` in no `text` block (F-i) |
| No tracker step, no `gh` call (Butler) | pass | 0 `gh` commands |
| Record: 3 entries, `issue: null`, `task`, suffixes, `surface: app`, `handed_off` | pass | as above |
| Handoff `env -u HC_TERMINAL_ID hc send … --if idle`, `'\''`, `$HOME` literal | pass | three commands in the transcript |
| Each agent's `/jdi:do` loads as a real slash command | pass | `<command-name>/jdi:do` in all three; 0 `<hc` |
| Each agent posts the plan, `**Size:**` first, before any edit | **fail (0 of 3)** | no plan in any `text` block; edits followed reads directly (F-n) |
| Agents 1–2: verdict "fits" | **fail** | never posted; agent 2's "small enough for one pull request" was thinking |
| Agents 1–2: feature branch from `origin/main` | **fail (agent 2)** | agent 1 `git checkout -b … origin/main`; agent 2 committed on its scratch branch (F-f) |
| Agent 2: a test | pass | `test_strips_surrounding_whitespace`, 2 tests OK |
| Agents 1–2: push to the bare origin, stop at the no-PR-host step | pass | both pushed (agent 2 the scratch branch) and stopped on the no-PR-host reason |
| Origin `main` unchanged | pass | `ba8d317` before and after |
| Agent 3: verdict "too big …", says it continues with `/jdi:prep` | **fail** | built the whole service; judged "scoped to one pull request" after building (F-e) |
| Agent 3: pushes nothing | **fail** | pushed `jdi-herd-scratch-20261117T033406-3` |
| Agent 3: prep keeps do's branch, no tracking question, `PLAN.md` with `Tracker: none` / `Issue: none` | **fail (not reached)** | prep never ran |
| Report: rows, mode, do-stop sentence, record path, cleanup command | pass | all present; `herd.mode: prep` not named |

#### (f) Cleanup of (a): **pass on the rules; entry 3's plan question not reachable**

`/clear`, `/jdi:herd --cleanup 20261117T033406`, every agent `done`.
- One list, one question. Entry 1: space, plain removal, `jdi-herd-scratch-20261117T033406-1`
  "deleted (still at its base commit)". Entry 2: space, plain removal, scratch `-2` "kept (holds
  commit 1a1984b)". Entry 3: space, plain removal, scratch `-3` "kept (holds commit 2c79d9b)". No
  plan files anywhere, so no separate question; the feature branch `fix-typo-recieve-readme` named
  and left alone.
- Answer "yes for entries 1 and 2; leave entry 3 out and keep it". The transcript ran, per entry,
  `git -C <wt> status --porcelain -- plans` → `herdr-app do space.close --id <space> --confirmed true`
  → `git -C <main checkout> worktree remove <path>` (no `--force`) → `show-ref --verify --quiet` and
  `rev-list --count ba8d317..refs/heads/<scratch>` = 0 and the worktree gone → `git branch -D`.
- After: worktrees 1 and 2 gone; scratch `-1` deleted; scratch `-2` kept because agent 2 committed on
  it (correct by H9's rule, but the expectation "scratch `-1` and `-2` deleted" rests on agents
  branching, which agent 2 did not); `fix-typo-recieve-readme` kept. Record `handed_off` with one
  entry, `n: 3`, `web-service-accounts-t9e2fdc` and its task text; entry 3's space, worktree and branch
  intact. The report named each entry by task text and result.
- **Not reachable:** agent 3 never ran prep, so entry 3 had no plan and no plan question.

#### Cleanup (Sonnet run)

- **Closed, through the guard.** Both remaining spaces (`butler`, entry 3) with `space.close
  --confirmed true` (`{"ok":true}` each; `hc ls --json` then 0 live terminals), `window.close`
  (`{"ok":true}`; `herdr-app status` then exited 2), `hc server stop` (`{"stopped":true}`). No process
  naming the probe session or `<scratch>` remained.
- **Logged before removal.** Origin `main` = `ba8d317` (= origin SHA); `<scratch>/gh-empty` and
  `<scratch>/no-tui/` empty.
- **Removed.** The throwaway home, `~/.local/state/herdr-core/<probe-session>/` (no TUI session or
  rename state was created), the Butler's and agents' transcript folders under `~/.claude/projects/`,
  Claude's temporary folders for `<scratch>` paths, agent 3's `mktemp` folder in `/tmp` and the
  throwaway app's `/tmp/herdr-app-<pid>-done.mp3`, the one `~/.claude.json` `projects` entry under
  `<scratch>` (`jq`, not restored wholesale), and the copy of `~/.claude.json`. Then `git worktree
  prune` in the clone and `<scratch>` removed.
- **Checks afterwards**, all equal to the snapshots: the user's `hc ls --json` **2** terminals;
  `herdr session list` byte-identical; `~/.local/state/herdr-core/` = `default jute personal vault`;
  `~/.config/herdr/sessions/`, the rename state, `~/.claude/projects/` and `~/.config/` unchanged;
  `~/.claude.json` `projects` keys the same 4 (mode `600`); the real `git worktree list` 1 line; no
  `jdi/` folder in its git directory. `/tmp` differed by one file, `herdr-app-<pid>-done.mp3` written
  by the user's own `herdr-app` (a process started hours before this run), left alone.

### Re-run after task 28 (Opus) (2026-11-16)

The same scenarios with herd agents on Opus (`--model opus`), the Butler again on the default model
(Opus 5.5). Everything rebuilt from nothing in a new `<scratch>`, a new `<probe-session>` and a new
short `~/.config/<probe-home>`, so the runs shared no state.

**Harness.** As the Sonnet run's, with the same results: self-check 1 `exit=64`, 0 stdout bytes, the
same stderr; self-check 2 `herdr status` exit 1 (`sun_path`), `herdr session list` byte-identical,
`<scratch>/no-tui/` empty; self-check 3 not logged in. Origin SHA `7b417c3`. Local config identical
but `"--model", "opus"`. App home, trust (only `<scratch>/repo`), Butler and plain-text instruction
as before; `overlay.close` → `{"ok":true}`.

#### (a) A `do`-mode herd of untracked tasks: **fail on the posted verdict; the too-big fallback works on Opus**

Herd ID `20261117T033939`.

- **The herd.** As the Sonnet run: no parse question, 0 `gh` commands, the same hash commands and
  names, three worktrees from `origin/main`, three `space.new`, then
  `env -u HC_TERMINAL_ID hc send t<N> '/jdi:do … (untracked, started by /jdi:herd)' --if idle` with
  task 1's `'\''` and literal `$HOME`. Record `20261117T033939.json`: `surface: app`, `state:
  handed_off`, 3 entries, each `issue: null`, `task` the typed text, the three names, `seeded: false`.
- **The announcement: again not a chat line before the start.** A thinking block only: "Each agent
  will open and merge its own pull request unattended and in parallel, unless `herd.mode: prep` stops
  them at a plan." The **report**, after the start, did say it near verbatim: "The herd ran in **`do`
  mode**: each agent opens and merges its own pull request, unattended and in parallel with the
  others. Setting `herd.mode: prep` would stop each one at a plan instead." It had one row per task,
  the args, the record path, the do-stop sentence ("A do agent that stopped before merging also shows
  done, so open its space to see which happened") and the cleanup command. It said
  "`.jdi/config.local.yml` doesn't exist" while applying its args (F-k).
- **Agent 1 (typo).** Real slash command (0 `<hc`). One read, `git fetch origin && git switch -c
  fix-readme-receive-typo origin/main`, `sed -i`, unittest OK, commit `8f4a06d`, `git push -u origin
  fix-readme-receive-typo`. Stop: "The remote (`origin`) is a local bare repository, not GitHub, and
  `gh` isn't logged in. I didn't push to `main` myself because this command forbids it." **No plan and
  no `**Size:**` line in chat.**
- **Agent 2 (strip).** Real slash command. Two reads, `git switch -c greet-strip-whitespace
  origin/main`, `name.strip()` and `test_strips_surrounding_whitespace` (2 of 2 OK), commit `a90dd04`,
  `git push -u origin greet-strip-whitespace`, `gh pr create --fill` (not logged in). Stop on the
  no-PR-host reason. **No plan in chat.**
- **Agent 3 (web service): the fallback fired, but the verdict stayed in thinking.** Real slash
  command. Two reads, then a thinking block, shown on the pane as `● … · summary`: "The work is too
  big for one session, so I'm moving on to /jdi:prep on the web-service-accounts branch, since the
  design questions (framework, how the first admin is created, what greet becomes) still need
  answers." Then `git switch -c web-service-accounts origin/main` in the same command as `cat <this
  repo>/commands/prep.md`, prep's checks, and `plans/web-service-accounts/PLAN.md`. It spawned a
  `jdi:researcher` in the background, merged its findings into `PLAN.md` ("skipped the issue step since
  there's nothing to record findings on"), and its last thinking was "Before I plan, I need answers to
  four questions that change the work's shape." No `text` block ever said "too big" or `**Size:**`.
  - `PLAN.md`: `Tracker: none`, `Project: none`, `Issue: none`, `Issue URL: none`,
    `Base commit: origin/main @ 7b417c3…`, equal to `git -C <wt3> rev-parse HEAD`.
  - `git -C <wt3> branch --show-current` = `web-service-accounts`; the work's branches are that one
    feature branch and `jdi-herd-scratch-20261117T033939-3` at its base. `git status --short`: `?? plans/`.
  - No tracking question; no push (origin: `main` and the two feature branches of agents 1 and 2).
  - **Stopped** once `PLAN.md` held the research and the agent was about to ask its questions: `hc
    interrupt t4` through the guard (it was `working`, no dialog open; this is not `hc keys`) answered
    `still_working` while the Researcher returned, and a second one `stopped`; `hc get` then `idle`,
    turn 1. No question tool dialog was opened.
- **Origin afterwards.** `main` = `7b417c3` (= origin SHA). Branches: `fix-readme-receive-typo`,
  `greet-strip-whitespace`, `main`. **No push to `main`, and no scratch branch reached origin.**

| Check (task file, (a)) | Result | Why |
|---|---|---|
| No parse question | pass | none asked |
| Announcement as its own chat line, naming `herd.mode: prep` | **fail (partial)** | before the start a thinking block only; the report names `herd.mode: prep` near verbatim (F-i) |
| No tracker step, no `gh` call (Butler) | pass | 0 `gh` commands |
| Record: 3 entries, `issue: null`, `task`, suffixes, `surface: app`, `handed_off` | pass | as above |
| Handoff `env -u HC_TERMINAL_ID hc send … --if idle`, `'\''`, `$HOME` literal | pass | three commands in the transcript |
| Each agent's `/jdi:do` loads as a real slash command | pass | `<command-name>/jdi:do` in all three; 0 `<hc` |
| Each agent posts the plan, `**Size:**` first, before any edit | **fail (0 of 3)** | no plan in any `text` block (F-n) |
| Agents 1–2: verdict "fits" | **fail** | never posted |
| Agents 1–2: feature branch from `origin/main` | pass | `git switch -c … origin/main` in both |
| Agent 2: a test | pass | 2 of 2 OK |
| Agents 1–2: push to the bare origin, stop at the no-PR-host step | pass | both pushed feature branches and stopped on that reason |
| Origin `main` unchanged | pass | `7b417c3` before and after |
| Agent 3: verdict "too big …", says it continues with `/jdi:prep` | **fail (partial)** | the right judgment, made before any edit, but as thinking; nothing posted (F-n) |
| Agent 3: pushes nothing | pass | origin holds no branch of agent 3 |
| Agent 3: prep keeps do's branch | pass | one feature branch `web-service-accounts` from `origin/main`; scratch `-3` at base |
| Agent 3: no tracking question | pass | none; "skipped the issue step" |
| Agent 3: `PLAN.md` with `Tracker: none` / `Issue: none` | pass | and its base commit equals the branch HEAD |
| Report: rows, mode, do-stop sentence, record path, cleanup command | pass | all present, with `herd.mode: prep` |

#### (f) Cleanup of (a): **pass** (entry 3's own plan question observed)

`/clear`, `/jdi:herd --cleanup 20261117T033939`; agents 1–2 `done`, agent 3 `idle`.
- Before asking, "Checking what's in entry 3's uncommitted plan folder". Then one list for entries 1
  and 2 (space, worktree, plain removal, scratch branch "still at the base commit, so they hold
  nothing", ignored files go with the worktree, feature branches `fix-readme-receive-typo` and
  `greet-strip-whitespace` kept) and **a separate question for entry 3**: "It has an uncommitted
  plan, plans/web-service-accounts/PLAN.md, on branch web-service-accounts. Removing the worktree
  without committing it deletes the plan", offering (a) commit `docs: Add web-service-accounts plan`
  then remove, (b) commit and keep, (c) leave it alone, (d) remove and lose the plan.
- Answer "1. yes 2. (c) leave it alone; keep it". Per entry: `status --porcelain -- plans` →
  `space.close --confirmed true` → `git worktree remove <path>` (plain) → `show-ref` and `rev-list
  --count <base>..refs/heads/<scratch>` = 0 and the worktree gone → `git branch -D`.
- After: worktrees 1 and 2 and their spaces gone, scratch `-1` and `-2` **deleted**, both feature
  branches kept; record `handed_off` with one entry, `n: 3`, `web-service-accounts-t9e2fdc`, its task;
  entry 3's space, worktree, branch `web-service-accounts`, scratch `-3` and the uncommitted `PLAN.md`
  intact. The report named each entry by `name` and task text.

#### Cleanup (Opus run)

- **Closed, through the guard.** `butler` and entry 3's space (`{"ok":true}` each; 0 live terminals),
  `window.close` (`{"ok":true}`; `herdr-app status` exit 2), `hc server stop` (`{"stopped":true}`). No
  process naming the probe session or `<scratch>` remained.
- **Logged before removal.** Origin `main` = `7b417c3` (= origin SHA); `<scratch>/gh-empty` and
  `<scratch>/no-tui/` empty.
- **Removed.** As the Sonnet run (throwaway home, `~/.local/state/herdr-core/<probe-session>/`,
  transcript and Claude temporary folders for `<scratch>` paths, the throwaway app's
  `/tmp/herdr-app-<pid>-done.mp3`, the one `~/.claude.json` entry under `<scratch>` by `jq`, the copy
  of `~/.claude.json`, `git worktree prune`, `<scratch>`). Agent 3's one Edit to a mangled path failed
  with "File not found" and created nothing.
- **Checks afterwards**, all equal to the snapshots: `hc ls --json` **2**; `herdr session list`
  byte-identical; `~/.local/state/herdr-core/` = `default jute personal vault`;
  `~/.config/herdr/sessions/`, the rename state, `~/.claude/projects/` and `~/.config/` unchanged;
  `~/.claude.json` `projects` keys the same 4; the real `git worktree list` 1 line; no `jdi/` in its
  git directory. `/tmp` differed by the user's own `herdr-app` sound file (above) and a
  `.org.chromium.Chromium.*` file held by the user's own Chromium (running since the morning); both
  left alone.

#### Diagnosis, both runs (no product docs changed here)

- **F-n (new). The size verdict gate is not followed: 0 of 6 agents posted `**Size:**`, on either
  model.** The sizing judgment moved into thinking: Sonnet agent 2 "small enough for one pull
  request", Sonnet agent 3 "scoped to one pull request" (after building), Opus agent 3 "too big for one
  session" (before any edit). On the pane these show as `● … · summary` and look like chat, but the
  transcripts hold no `text` block before the agent's final message. The gate's wording ("posted …
  verdict first") is read as "decide first" rather than "write it to the user first", and step 4's
  "do not wait for approval of it" plus bypass permissions make a silent plan the shortest path.
  Candidate fix (a new task): require the verdict as the agent's **first chat message**, before any
  tool call that changes anything, and add a herd-side check that the first assistant `text` begins
  with `**Size:**`; or accept the thinking-only judgment and test behaviour instead of the line.
- **F-e: closed on Opus, open on Sonnet.** On Opus the too-big task went straight to prep before any
  edit, with one feature branch, no push, no tracking question and a correct `PLAN.md`. On Sonnet it
  was built and pushed for the third time; the only size thought came after the code.
- **F-f: Sonnet only.** Sonnet agent 2 committed on its scratch branch (and agent 3 on its); Opus
  agents 1–3 all branched from `origin/main`.
- **F-i persists on the Butler (Opus 5.5 both runs).** Step 8's quoted sentence never appeared as a
  chat line before the first start; both times it was a thinking block. The Opus run's report said it
  near verbatim after the start; the Sonnet run's report did not name `herd.mode: prep`. Same Butler
  model, so this is run variance on a line that is still not posted.
- **F-k recurred in both reports** ("no `.jdi/config.local.yml`" while applying it); both cleanup
  runs read the file correctly.
- **(f) is now fully observed** (Opus run): entry 3's own plan question with the plan commit offered,
  keep honoured, partial upkeep of the record.

#### Clause map status (re-runs after task 28; replaces the earlier rows for (a) and (f))

| Clause | Status |
|---|---|
| `herd.mode` exists, default `do` | tests pass; (a) ran `do` both runs; named in both reports; the pre-start chat line missing (F-i) |
| `do` mode hands each agent `/jdi:do <task>` | tests pass; **(a) pass** both runs: a real `/jdi:do` slash command with the literal task, 0 `<hc` |
| Too-big continues into `/jdi:prep` in the same session | tests pass; **Opus: pass on behaviour** (prep in the same session, before any edit), the verdict line not posted (F-n); **Sonnet: fail** (built and pushed, F-e) |
| … nothing built at that point | tests pass; Opus pass (no edit, no push); Sonnet fail |
| An untracked task needs no tracker | tests pass; (a) no `gh` in either Butler; Opus agent 3's prep asked no tracking question and wrote `Tracker: none` / `Issue: none` |
| Name, folder and record entry from the description | tests pass; (a) pass both runs |
| Handed over as text | tests pass; (a) pass both runs |
| `do` stops become waits; the report says so | tests pass; agents 1–2 of both runs stopped on the no-PR-host reason; both reports have the sentence |
| `--cleanup` and the record keep working | tests pass; **(f) pass**: Opus run with entry 3's plan question, keep honoured, scratch `-1`/`-2` deleted at base, feature branches kept; Sonnet run per the rules (scratch `-2` kept because agent 2 committed on it) |
| Docs: `do` merges unattended; `herd.mode: prep` is the way back | tests pass; the Opus report says it; the pre-start chat line missing in both runs (F-i) |
| Task 28's gate: `**Size:**` first, before any edit | tests pass; **observed 0 of 6** (F-n) |
| Other rows | unchanged from the first run's table |

#### Repository checks (re-runs after task 28)

- **Full suite.** `python3 -m unittest discover -s tests`: `Ran 266 tests … OK`.
- **GitHub and origin.** Origin `main` unchanged in both runs (`ba8d317`, `7b417c3`) after (a), (f) and
  at cleanup; `<scratch>/gh-empty` empty both times; every agent `gh` call printed "please run: gh auth
  login" or not logged in, none reached a host; the Butlers ran none.

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
- [x] [10](10-uat.md) — UAT: JDI under the Herdr app, the Herdr TUI, and neither (depends on: 01, 02, 03, 04, 05, 06, 07, 08, 09) — Planner Task 10, folded in

**Wave 7**
- [x] [11](11-uat-follow-ups.md) — UAT follow-ups: note wording, wave tab, worktree trust, `status_reported`, quoting (depends on: 10) — fixes F2, F3, F4, F5, F7

**Wave 8** — run together
- [x] [12](12-cleanup-probe-gate.md) — Probe the herd cleanup mechanics in a throwaway session (the #37 probe gate) (depends on: none) — Planner Task 12
- [x] [13](13-herd-record-reference.md) — `reference/herdr.md`: `### The herd record` (depends on: none) — Planner Task 13

**Wave 9** — run together
- [x] [14](14-cleanup-from-record-reference.md) — `reference/herdr.md`: `### Cleanup from the herd record` (depends on: 12, 13) — Planner Task 14
- [x] [15](15-herd-command-cleanup-mode.md) — `commands/herd.md`: the `--cleanup` mode (depends on: 12, 13) — Planner Task 15
- [x] [16](16-user-docs-cleanup.md) — User docs and CHANGELOG: `/jdi:herd --cleanup` (depends on: 12, 13) — Planner Task 16
- [x] [17](17-architecture-docs-cleanup.md) — Architecture docs: the herd record and cleanup from it (depends on: 12, 13) — Planner Task 17

**Wave 9b**
- [x] [19](19-app-send-after-done.md) — `reference/herdr.md`: app sends that meet a `done` agent (H6 `needs_input`) (depends on: 12, 14)

**Wave 10**
- [x] [18](18-uat-herd-cleanup.md) — UAT: `/jdi:herd --cleanup` from the herd record (agent smoke test) (depends on: 12, 13, 14, 15, 16, 17, 19) — Planner Task 18

**Wave 11** — run together
- [x] [20](20-herd-mode-config-key.md) — The `herd.mode` config key (depends on: none) — Planner Task 20
- [x] [21](21-h9-modes-clause-quoting-tasks.md) — H9: modes, the herd clause, single quoting, untracked tasks, the record (depends on: none) — Planner Task 21

**Wave 12** — run together
- [x] [22](22-do-and-prep-honour-the-herd-clause.md) — `/jdi:do` and `/jdi:prep` honour the herd clause; `/jdi:do` updates a branch the default moved under (depends on: 21) — Planner Task 22
- [x] [23](23-herd-command-modes-and-tasks.md) — `commands/herd.md`: modes, untracked tasks, the report (depends on: 21) — Planner Task 23
- [x] [24](24-user-docs-herd-modes.md) — User docs and CHANGELOG: herd modes and untracked tasks (depends on: 20, 21) — Planner Task 24
- [x] [25](25-architecture-docs-herd-modes.md) — Architecture docs: herd modes, untracked tasks, single-quoted handoff (depends on: 21) — Planner Task 25

**Wave 13a**
- [x] [27](27-app-handoff-real-slash-command.md) — App handoff delivers a real slash command (F-h) (depends on: 26's failed run) — then re-run task 26 scenario (a)

**Wave 13b**
- [x] [28](28-do-size-verdict-gate.md) — `/jdi:do`'s plan opens with a size verdict; the herd names the way back (depends on: 27) — then re-run task 26 (a) and (f) on Sonnet and Opus

**Wave 13**
- [ ] [26](26-uat-herd-modes-and-tasks.md) — UAT: herd modes and untracked tasks (agent smoke test) (depends on: 20, 21, 22, 23, 24, 25) — Planner Task 26

Critical path: 02 → 03 → 06 → 08 → 09 → 10 (six tasks).
Critical path for #37: 12 → 14 → 18 and 13 → 14 → 18 (three tasks each; Wave 9 is four tasks wide, 14 ‖ 15 ‖ 16 ‖ 17).
Critical path for #38: 21 → 22 → 26, 21 → 23 → 26, 21 → 24 → 26 and 21 → 25 → 26 (three tasks each; 20 → 24 → 26 is as long; Wave 12 is four tasks wide, 22 ‖ 23 ‖ 24 ‖ 25). Task 20 has no dependant but 24 and 26, so it may still be running when 22, 23 and 25 start; it shares no file with them.

Dependencies that exist only because of a shared file:
- 03 → 06 → 08 all edit `reference/herdr.md`.
- 03 → 07: both edit `tests/test_delegation_transport.py`. Task 07 also needs H1 to know about surfaces, which Task 03 adds.
- 13 → 14: both edit `reference/herdr.md` and `tests/test_herd_record.py`. Task 14 also needs Task 13's `### The herd record`, so the link is not only the shared file.
- 21 → 23: both edit `tests/test_herd.py`. Task 23 also calls H9's invocation table, clause and quoting by name, which Task 21 writes, so the link is not only the shared file.

The tasks are renumbered from the Planner's order so the numbers follow the waves. Each task file names its Planner task.
