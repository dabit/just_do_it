status: done
# 06 — `reference/herdr.md`: app variants of H2–H8 and waves

Depends on: 03

## Why
Role delegation and waves have to run on the Herdr app through the same named operations they use on the TUI. The rules for an app worker are:
- its kind is resolved to an absolute path, and an agent that never reaches `status: idle` at readiness is rejected (D7, amended);
- it starts with `pane.split --argv` beside the Butler, direction always `right`, with env as an argv prefix;
- it is addressed by terminal ID and a `jdi.agent` label;
- it is waited on with `hc` in seconds, and never sent keys;
- it is closed with `pane.close` or `tab.close`.

The TUI text moves under its own subheadings, unchanged. Rests on: D-struct, D3, D4, D5, D7, D8, D10, P1, P2, P3, P8, P9, P10.

## Description
Planner's Task 4. **Before starting, read `## Probe log` in PLAN.md.** The gate settles three
VERIFY-AT-EXECUTION points here:
- P2: whether the `sh -c 'cd -- …'` wrapper is needed and keeps status reporting. See A14 and A6.
  If the wrapper breaks status, R2's fallback applies: single workers use `tab.new --folder`, and
  D4 is amended.
- P3: whether `pane.split` moves focus (A13). If it does, H4 step 1's command ends with
  `&& herdr-app do pane.focus --pane <butler pane>`. Otherwise nothing is added.
- The "already gone" error JSON (A7), the `tab.new` output (A1), and whether each kind reports
  status (A2, A3).

Where the gate amended a decision, the amendment wins over this file, and its tests change with it.
Say so in your report.

**Structure rule.** For H2, H4, H5, H6 and H8, move the existing TUI text unchanged under a new
`### H<n> on the TUI` heading. Put it first, followed by `### H<n> on the app`. Text shared by both
stays above the two subheadings.
- H3 gets only `### H3 on the app`; its TUI text stays where it is.
- The existing `### H4b - Start an agent in a given pane` heading stays as it is, because
  `commands/herd.md` cites **H4b**. It may sit between `### H4 on the TUI` and `### H4 on the app`.
- The new `#### H4b on the app` goes inside `### H4 on the app`.
- H7 is shared and unchanged.
- Write no em dash (`test_no_em_dash`).
- Inside an indented fence, no line starts with `#` at column 0.
- Every pinned phrase must survive verbatim:
  - "Herdr's `kinds:` line lists the kinds it supports", and "lists the kinds Herdr supports" (H2);
  - the H3 manifest table row
    ``| `manifest.json` | the Butler | in H4, after the pane split and before `agent start`; never edited afterward |``;
  - `herdr pane split --current` and `**Write the run files.**`, in that order, in H4 TUI step 1;
  - the TUI H5 table rows.

TDD is on: write the tests first and watch them fail.

### 1. Tests first, in `tests/test_herdr_operations.py`
**Add these to `HEADINGS`:** `### H2 on the TUI`, `### H2 on the app`, `### H3 on the app`,
`### H4 on the TUI`, `### H4 on the app`, `#### H4b on the app`, `### H5 on the TUI`,
`### H5 on the app`, `### H6 on the TUI`, `### H6 on the app`, `### H8 on the TUI`,
`### H8 on the app`, `### Waves on the app`.

**New methods.** Each uses `assertSectionContains(<heading>, …)` unless the bullet says otherwise.
- `test_h2_app`, on `### H2 on the app`: "`command -v <kind>`", "absolute path",
  "no kinds list", "not ready", "`--no-daemon`",
  "`harnesses.codex.args`".
- `test_h3_app`, on `### H3 on the app`: "`hc ls --json --label jdi.agent=<name>`",
  "`herdr-app ls`", `"surface"`, `"space_id"`, `"terminal_id"`.
- `test_h4_app_spawn_line_and_split_are_one_command`. Copy the harness of the existing
  `test_h4_spawn_line_and_pane_split_are_one_command` exactly, with three changes:
  - scope it to `self.section_lines("### H4 on the app")`, which is
    `jdi_files.section(self.text, "### H4 on the app")`;
  - assert that the first line starting `1. ` starts with `1. **Print the spawn line.**`;
  - match, inside step 1's first fenced block, one line that contains both
    `printf '%s\n' "JDI spawn` and
    `&& herdr-app do pane.split --pane <butler pane> --direction right --argv`.

  The template can express all of this: it already returns the section's lines and slices step 1
  between `1. ` and `2. `.
- `test_h4_app_order`, on `self.section_text("### H4 on the app")`. These markers appear with
  strictly increasing `index`: `pane.split`, then `hc label <terminal> jdi.agent=<agent name>`,
  then `**Write the run files.**`, then `hc wait <terminal> --timeout 120`.
- `test_h4_app_argv`, on `### H4 on the app`: `cd -- "$1"`, `env KEY=VALUE`,
  "Expand every path".
- `test_h4b_app`, on `#### H4b on the app`: `hc label`, `hc wait <terminal> --timeout 120`.
- `test_h5_app`, on `### H5 on the app`:
  - contains `hc send <terminal> "<short prompt>" --if idle --wait --timeout 300`, "`--if idle`",
    `hc wait <terminal> --timeout 300`, and "seconds, not milliseconds";
  - every one of these row prefixes starts some line of `self.section_lines("### H5 on the app")`:
    ``| `working` ``, ``| `blocked` ``, ``| `idle` or `done` |``,
    ``| `idle` or `done` with no `result.json` ``, ``| `error` ``, `| no status`,
    `| overall timeout`, `| refused as blocked`, ``| `not_started` ``,
    ``| `reason: message` ``, `| finished`.

  Use the same `any(line.startswith(row) …)` loop as `test_h5_prompt_and_wait`. These prefixes are
  the contract between this test and the table this task writes, and are exact.
- `test_h6_app`, on `### H6 on the app`: "never `hc keys`", "never `hc send --force`",
  "never `hc interrupt`", `hc read <terminal> --lines 80`,
  `herdr-app do agent.focus --terminal <terminal>`.
- `test_h8_app`, on `### H8 on the app`: `herdr-app do pane.close --pane <pane_id>`,
  `herdr-app do tab.close --id <tab_id> --confirmed true`, "already gone".
- `test_waves_app`, on `### Waves on the app`: `herdr-app do tab.new --name jdi-wave-<first run id>`,
  `--focus false`, `hc wait <terminal> --timeout 30`.

### 2. `reference/herdr.md`

**H2.**
- The model-flag table stays shared.
- `### H2 on the app` says:
  - there is no kinds list and no integration status;
  - the kind's only check is `command -v <kind>` in the Butler's shell, and the **absolute path**
    it prints goes into the argv, because terminals get the core's env, not the Butler's PATH;
  - a non-absolute answer, such as an alias or a function, fails H2 on the app with that reason
    (P1).
- Say that a kind is only usable on the app if it reports a status: the readiness wait (H4 step 5)
  treats an agent that never reaches `status: idle` as "not ready" and types nothing (D7, amended
  after the probe gate: trust and hook-review dialogs report no status).
- Add a Codex note: under hc, Codex needs `--no-daemon`, and the user puts it in
  `harnesses.codex.args`. JDI adds nothing, but notes once when it is missing (D8, universal
  rule 9).

**`### H3 on the app`.**
- The collision check is `hc ls --json --label jdi.agent=<name>`.
- The space and tab IDs come from the labels in `hc get "$HC_TERMINAL_ID" --json`.
- The Butler pane is the `herdr-app ls` entry whose `terminal` equals `$HC_TERMINAL_ID` (A16).
- On the app, the manifest's `"herdr"` object is the one below, verbatim (Appendix A3):
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
- Add `"surface": "tui",` as the first field of the TUI manifest's `"herdr"` object (P8). This is
  additive, and `"schema"` stays `1`.
- Add one sentence: on the app the split starts the agent, so the manifest is written after the
  split and before the short prompt. The pinned H3 table row stays unchanged.

**`### H4 on the app`** (D4, D10, P2, P3):
1. **`1. **Print the spawn line.**`** The spawn line and the split are one shell command on one
   physical line (Appendix A2):
   ```text
   printf '%s\n' "JDI spawn <run-id>: <Role> on <kind> (<model | CLI default>) - args: <verbatim | none> - env keys: <keys | none> - run dir: <path> - agent: <agent name>" && herdr-app do pane.split --pane <butler pane> --direction right --argv '<argv JSON>'
   ```
   The split worker's `<argv JSON>` is below. The `"env", "KEY=VALUE", …` elements appear only when
   `harnesses.<kind>.env` is non-empty. Elements are JSON-escaped, and the array is single-quoted
   with `'` written as `'\''`.
   ```text
   ["sh", "-c", "cd -- \"$1\" && shift && exec \"$@\"", "jdi-worker", "<worktree root>", "env", "KEY=VALUE", "<absolute path of kind>", "<model flag>", "<model>", "<args...>"]
   ```
   **What in these two fences is exact:**
   - each is one physical line;
   - the first contains `printf '%s\n' "JDI spawn` and
     `&& herdr-app do pane.split --pane <butler pane> --direction right --argv`;
   - the spawn-line text is the TUI H4 spawn line's text;
   - the argv starts with the `sh -c 'cd -- "$1" && shift && exec "$@"' jdi-worker <worktree root>` wrapper.

   The angle-bracket placeholders and `<args...>` are illustrative. The prose must say
   "Expand every path" (D3: `~` and variables expanded before they enter the argv) and name
   `env KEY=VALUE`.
2. Read `.pane` and `.terminal` from the split's JSON. That JSON is the **last line of the
   command's stdout**; the spawn line is the first. hc and herdr-app report errors as JSON on
   **stderr**. If A13 showed that the split moves focus, restore it in the same command (P3).
3. `hc label <terminal> jdi.agent=<agent name>` (D5).
4. **Write the run files.** Write `manifest.json` (A3 object) and `prompt.md`.
5. `hc wait <terminal> --timeout 120`. Then branch on the result:
   - `idle`: go to H5.
   - `blocked`: go to H6 with the prompt unsent.
   - finished, not found, or a JSON error: H8, then rung 8.
   - anything else, including a check-in timeout with no `status` (an open trust or hook-review
     dialog, or a kind that reports none): not ready (D7). Type nothing, say why (the dialog, if
     any, is the user's to answer), then H8 and rung 8.

**`#### H4b on the app`.** The `hc label` call and the `hc wait <terminal> --timeout 120` readiness
wait, for a terminal the caller created. The outcomes are the same as H4's.

**`### H5 on the app`.**
- Send only after H4's readiness wait reported `status: idle`, with
  `hc send <terminal> "<short prompt>" --if idle --wait --timeout 300` (D6, amended: the app then
  refuses to type into anything not idle), then loop
  `hc wait <terminal> --timeout 300` under the 2700 s overall deadline. Where the shell tool caps
  lower, use its cap minus 30 s.
- Say "seconds, not milliseconds".
- Classify from hc's JSON, on stdout and stderr. The exit code only confirms.
- Note that `hc send` waits up to 60 s for a person's unfinished draft.
- The table has these rows, each starting with its prefix from the test:
  - `working` or `reason: timeout`;
  - `blocked`;
  - `idle` or `done` (settled; "not proof"; go to H7);
  - `idle` or `done` with no `result.json`;
  - `error` (inspect; never a success);
  - no status (mid-run only; readiness already rejected kinds that never report one): with P10,
    every check-in also checks for `result.json`, and goes to H7 if it exists;
  - overall timeout;
  - refused as blocked (exit 9);
  - `not_started` (do not resend; read first);
  - `reason: message` (not a worker state; wait again);
  - finished (11), not found (3), or a JSON error: a transport failure.

**`### H6 on the app`.**
- Inspect with `hc get <terminal> --json`, whose `status.kind` is one of permission, question or
  auth, and with `hc read <terminal> --lines 80`. The read shows the screen only while the worker
  is blocked or working.
- Focus with `herdr-app do agent.focus --terminal <terminal>`, and only on a yes from the user.
- Answer `needs_input` with `hc send <terminal> "<answer>" --if idle --wait --timeout 300`.
- Never `hc keys`, never `hc send --force`, never `hc interrupt`, even where the hc manual suggests
  `hc keys` for a trust dialog (P9, universal rule 7).

**`### H8 on the app`.**
- `outcome.json` is shared.
- Close with `herdr-app do pane.close --pane <pane_id>`. A split whose program exited is "already
  gone", and the A7 error JSON is expected.
- For a wave, also run `herdr-app do tab.close --id <tab_id> --confirmed true`.
- Close only through `pane.close`, `tab.close` or `space.close`. Never `hc kill`, `hc rm`,
  `hc keys`, `hc interrupt` or `hc send --force` (P9).

**`### Waves on the app`** (D4), inside `## Waves`:
- The first worker is started with this command on one physical line (Appendix A2):
  ```text
  printf '%s\n' "<its JDI spawn line>" && herdr-app do tab.new --name jdi-wave-<first run id> --space <space_id> --folder <worktree root> --argv '<argv JSON without the sh wrapper>' --focus false
  ```
  It uses `--folder` and no wrapper. Its terminal runs in an interactive shell that stays live
  after the agent exits, so H8 must close it.
- Later workers use `pane.split --pane <a live worker pane in the wave tab>` with the wrapper. If no
  worker pane is live, open a new wave tab.
- Wait on each worker with `hc wait <terminal> --timeout 30`, or with `hc get`.
- The cap of 4 and the other wave rules are shared.

**`## Why the agent surface, not pane run`.** Add one paragraph: on the app, states come from the
program, via OSC 7501, through hc. The reason is the same.

## Files
- `tests/test_herdr_operations.py`
- `reference/herdr.md`

## Verification
1. **Red first.** Run `python3 -m unittest discover -s tests -p 'test_herdr_operations.py' -v`
   before editing `reference/herdr.md`. Expected: the 13 new heading subtests and the 10 new
   methods fail, and every pre-existing test passes.
2. **Green.** Run the same command after the edits. Expected: every test passes, including the
   untouched TUI tests:
   - `test_h2_kind`, `test_h3_prepare`, `test_h4_start`;
   - `test_h4_opens_with_the_spawn_line`, `test_h4_spawn_line_and_pane_split_are_one_command`
     (step 1 of `## H4` is still the TUI's);
   - `test_manifest_is_written_after_the_pane_exists`, `test_h5_prompt_and_wait`, `test_waves`;
   - `test_h6_blocked`, `test_h8_close`, `test_wave_tab_close_may_find_the_tab_gone`;
   - `test_result_channel_rules`, `test_no_em_dash`.
3. **The tests bite.** Edit `### H4 on the app` in `reference/herdr.md`, the text that defines the
   app spawn, in two ways and run the module after each:
   - Move step 3 (`hc label …`) above step 1's fence. Expected: `test_h4_app_order` fails.
   - Split step 1's fenced line into two lines at `&&`. Expected:
     `test_h4_app_spawn_line_and_split_are_one_command` fails.

   Restore the original text, and confirm with `git diff -- reference/herdr.md`.
4. **The TUI text did not change.** Run
   `git diff -U0 -- reference/herdr.md | grep -E '^-[^-]'`. Expected: no removed line that carried
   a TUI command (`herdr …`) or a pinned phrase. Removed lines may only be whitespace or heading
   moves; explain each one in the report.
5. **Confinement still holds.** Run
   `python3 -m unittest discover -s tests -p 'test_delegation_transport.py' -k HerdrConfinementTest -v`.
   Expected: every test passes. `reference/herdr.md` is exempt, and this task touches no other
   confined file. The `-k` filter matters: Task 07 edits `TransportSelectionTest` in the same
   module and may run at the same time.
6. **Full suite.** Run `python3 -m unittest discover -s tests -v`. Expected: every test passes, with
   one exception: failures in a test module owned by a task running at the same time. Task 07 owns
   `tests/test_step_zero_transport.py` and `tests/test_delegation_transport.py`. Tasks 04 and 05
   may still be running if they started late.
