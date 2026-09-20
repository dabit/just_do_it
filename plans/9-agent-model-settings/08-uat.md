status: pending
# 08 — UAT

Depends on: 07

## Why
Almost everything this change ships is prose an agent reads and acts on — a twelve-rung degradation
ladder, an exec-first/Herdr-second resolution order, an authorization boundary. The test suite
checks only structure (a key path exists, a heading exists, a word is absent); it cannot prove the
ladder is followed, that the first applicable rung wins, that an announcement actually happens, or
that a pane is actually closed. This task is where the change is actually verified, and where every
clause of issue #9's acceptance criteria gets tied to the evidence that proves it — or is named as
unproven.

## Description
Run all fifteen scenarios below against a real harness (this machine has `codex`, `opencode`,
`gemini`, `herdr`, and `claude` on `PATH`; `qwen` is not installed; `~/.config/opencode/agent/
jdi-*.md` exists for all seven roles; `gemini` is installed with no JDI). For each, record the
composed command (or announcement) verbatim, not just pass/fail — several scenarios exist
specifically to check *which* command was composed, not merely that something ran.

### Scenarios

**Positive — the exec path end to end, both installed kinds, plus the reverse direction:**

1. **Codex exec.** Scratch repo, `.jdi/config.yml` with `models.researcher: {model:
   gpt-5.1-codex-max, harness: codex}` and `harnesses.codex.args: ["--sandbox",
   "workspace-write"]`. Run `/jdi:research`. Confirm: the composed command uses `codex exec -m …
   -o <file>`; the args are printed back **before** the spawn and appear verbatim, unmerged; the
   report comes back from the file, not a terminal scrape; no pane was created.
2. **OpenCode exec.** `models.splitter: {model: <provider/model>, harness: opencode}`. Run
   `/jdi:split`. Confirm `opencode run -m … --agent jdi-splitter --format json` and that the role's
   own instructions were used. **The `--agent jdi-splitter` claim is unverified going in** — the
   synced agents carry `mode: subagent` (`bin/sync-opencode.sh:144`), and whether `opencode run
   --agent` resolves a subagent-mode agent has not been tested on this branch. If it is accepted,
   record the command and move on. If it is rejected, that is rung 5 firing correctly and the
   contingency is the inline path (pass `agents/splitter.md`'s text in the prompt) — record
   whichever happened. **Either outcome is a pass for the degradation ladder; only acceptance is a
   pass for the specific `--agent` claim.** Do not conflate the two in the writeup.
2b. **Claude exec, from a non-Claude session.** Run JDI under Codex or OpenCode with
   `models.planner: {model: opus, harness: claude}`. Confirm the composed command is `claude -p
   --model opus --output-format json`, the report is parsed from the JSON result rather than
   scraped, and the Planner phase runs. This is the direction issue #9's AC4 names explicitly
   (`claude -p`) and the one scenarios 1 and 2 do not cover — without it, "codex, opencode, claude"
   is only ever two of three.

**Negative — the rungs that are genuinely reachable here:**

3. **Rung 3, CLI absent from `PATH`.** `models.planner.harness: qwen` (not installed). Confirm
   exactly one announcement naming what was configured and what is running instead; **nothing is
   spawned**; the Planner phase still runs at the floor.
4. **Rung 4, no exec mode JDI knows.** `models.planner.harness: gemini` (on `PATH`, but JDI knows
   no exec invocation for it). Confirm the announcement names the reason correctly — *no exec mode*,
   not *not installed* — and that the ladder then considers Herdr before the floor.
5. **Rung 5, instructions unresolvable.** `models.splitter.harness: opencode` with
   `OPENCODE_CONFIG_DIR` pointed at an empty directory via `harnesses.opencode.env`, so `--agent
   jdi-splitter` cannot resolve. Confirm the ladder either inlines the role file or announces rung 5
   and floors — and that it **never** derives or searches for a plugin path.
6. **Rung 10, the model this harness cannot express.** Inside Claude Code, `models.planner: {model:
   claude-opus-5}` with **no** `harness:`. Claude Code's Agent tool takes `model` as an enum, so
   this cannot be passed at spawn time. Confirm an **announcement**, not a silent drop, and that the
   Planner runs on the harness default. **This scenario is not deferrable.** It is the regression the
   whole change exists to close, it is a certainty by schema rather than a hypothesis (verified
   at PLAN.md's "Verified harness capability" section: Claude Code's Agent tool `model` parameter is
   an enum), and it must be exercised live, not waved through on the strength of the schema alone.
7. **Rungs 6–9 and pane hygiene.** Force the Herdr transport (a kind with no exec mode, Herdr
   present). Interrupt it mid-run so it never reports usably. Repeat for **three consecutive failed
   attempts** — the three-attempt form is the point, not one attempt. Confirm: one announcement per
   attempt; the phase still runs at the floor; and `herdr pane list` shows **no leaked pane** after
   all three. A leak of one pane per attempt, visible only after several attempts, is the failure
   this scenario is guarding against — a single attempt would not catch it.

**Compatibility and silence:**

8. **Old-shape `models:` block.** Scratch repo with `models: {deep: claude-opus-5, standard:
   claude-sonnet-5, fast: claude-haiku-4-5}`. Run `/jdi:plan`. Confirm exactly one announcement that
   the block is the pre-1.0.5 shape and is not read, that `reference/config.md` is named, and that
   the workflow proceeds on the session's model. Nothing breaks and nothing is silently
   reinterpreted.
9. **No `models:` block at all.** Scratch repo with a 1.0.4-era config. Run `/jdi:plan`. Confirm
   **complete silence** on models — a run here must be indistinguishable from a 1.0.4 run.
10. **The dogfood.** In this repository, under Claude Code, run `/jdi:plan`. Confirm the Planner is
    spawned on `opus` resolved from `.jdi/config.yml` (task 01's dogfood block), and that **nothing
    is announced** — rung 1/2, the silent path. Then run the same under Codex or OpenCode and
    confirm the single announcement that the alias cannot be expressed, and that the phase still
    runs.
11. **`/jdi:init` read-through.** Scratch repo with no `.jdi/config.yml`. Run `/jdi:init`. Confirm
    step 8 asks per role, says it is optional, and asks the `harnesses` follow-up **only** when a
    role was given a different harness. Confirm the written file matches the schema. Do not
    substitute a diff review for this run — init's question wording is genuinely unverifiable
    without it.
12. **`/jdi:help` read-through.** Confirm the table has no `Tier` column, the `### Roles and
    models` section reads correctly, and the closing line names which roles have a model
    configured.
13. **OpenCode sync end to end.** `bin/sync-opencode.sh --global` into a temp
    `OPENCODE_CONFIG_DIR`; confirm no synced agent carries `model:`, then run `/jdi-plan` against
    the synced copy and confirm the workflow still runs.
14. **Acceptance-criteria sweep.** This scenario *is* the AC-mapping table below — running it means
    walking that table and confirming each row's cited scenario or test actually produced the
    evidence it claims.

### Acceptance criteria mapping

Mapped against the **live issue text** (`gh issue view 9`), not the earlier PLAN.md wording — AC4 in
particular was revised after the plan was written.

| AC | Clause | Proven by | Notes |
|---|---|---|---|
| 1 | No file under `agents/` carries a `model:` key | T-D (`tests/test_frontmatter.py`, task 03) | Structural, whole-repo; scenario 13 additionally confirms the synced OpenCode copies |
| 2 | `.jdi/config.yml` accepts a per-role mapping with `model:`/`harness:`; `reference/config.md` documents schema, defaults, invariants | T-A, T-B, T-C (task 01) | Scenario 11 confirms `/jdi:init` writes a file matching the schema; the *invariants read well to a human* is not test-provable — reviewer judgment only |
| 3 | Every delegatable role can be named. **Unset is silent** (no entry, no `harness:`, or no `models:` block at all — runs in this session's harness on the session's own model, saying nothing); **announcement is for degradation only** | Scenario 9 (no block — must be indistinguishable from a 1.0.4 run), scenario 10 (dogfood — silent), and every announcing scenario 3–7, 11 as the contrast | **Resolved by the Butler — the earlier tension is closed.** The issue's original "announced once" wording for the unset case was written before the ladder existed and was wrong; AC 3 now states the silent reading explicitly. The rule it follows is `docs/config-key-lifecycle.md:230-240` and its precedent `commands/split.md:96-97` ("Say nothing; there is nothing to skip"): a feature that is **off** produces no notice, because nothing was skipped, while a configured value that could not be honoured is announced exactly once. Treat any announcement at all in scenario 9 as a **failure**, not as harmless extra chatter — polluting every default-configuration run with notices about features nobody enabled is the specific failure that rule exists to prevent. |
| 4 | `harness:` honoured **exec-first** (`codex exec`, `opencode run`, `claude -p`), Herdr **second** via `herdr pane run` (not `herdr agent start`) | Scenarios 1, 2, 2b (exec-first, all three CLIs), 7 (Herdr second, `herdr pane run`, pane hygiene) | Scenario 2's `--agent` sub-claim is unverified — see its own note. Nothing exercises `herdr agent start` being *avoided*; T-F's pin of `"herdr pane close"` and the ladder's Herdr-rung prose are the structural check that the wrong primitive was never named |
| 5 | A written, ordered degradation ladder covers every harness-dimension failure (no `harness:`, no herdr binary, no server, uninstalled kind, no pane, agent never reports), degrading **down only**, announced | T-F (task 02) pins the ladder's structure, ordering, and floor sentence | Live: scenario 3 (uninstalled kind), 4 (no exec mode, considers Herdr), 5 (unresolvable instructions), 7 (no pane / never-reports rungs, pane hygiene). **Not exercised live: rung 6, "Herdr wanted but not detected" (no binary, no `HERDR_ENV`, no server answering).** Herdr is installed and running on this machine for every other scenario's setup; nothing in this list forces its absence. Mechanism is proven by T-F's pins of the rung's text, not by a live run. Deferred: pick up in a follow-up UAT pass with `HERDR_ENV` unset or `herdr` removed from `PATH`, or as a fast-follow issue if this gap matters before merge |
| 6 | Authorization boundary stated explicitly: a spawned agent does not inherit this session's approval policy; JDI composes no permission flag | T-F's rewritten fragments (`"A separately spawned CLI does not"`, `"JDI composes no authority-affecting flag and translates none between kinds"`), the 3-site `grep -n "sandbox"` control (task 02 and task 06 verification) | Scenario 1 additionally confirms in practice that `harnesses.codex.args` is printed back verbatim before the spawn, unmerged |
| 7 | Documentation no longer tells a reader a model name belongs in frontmatter — `delegation.md`, `README.md`, `help.md`, `config-key-lifecycle.md` all agree | T-H (task 06, whole-repo word scan), T-G (README heading rewrite) | Scenario 12 confirms `/jdi:help` reads correctly. **`docs/config-key-lifecycle.md` §5's actual rewritten *content* (not just its heading stability, which `tests/test_versions.py` pins) is reviewer-verified only** — no test reads what §5 says, only that its headings didn't move |
| 8 | A repo with no `models:` block still runs every command end to end; CHANGELOG states plainly what changes | Scenario 9 (full silent run) | Scenario 9 as written runs `/jdi:plan` only, not literally every JDI command. "Every command end to end" is inferred, not directly exercised: every delegation in the workflow shares the one degradation ladder written in task 02, so a silent run of one delegating command is evidence the ladder's silent rung behaves generally, not proof that all eleven commands were run. The CHANGELOG's specific wording (task 07) is **reviewer-verified only** — no test reads `CHANGELOG.md`'s content |
| 9 | `bin/sync-opencode.sh` still produces valid OpenCode agent files; full suite passes | T-E (characterization, task 03), scenario 13 | Full suite green is the final-state check, confirmed at task 07 and again here |
| 10 | Release ships with matching versions in the three JSON files and a CHANGELOG entry | Task 07's version grep across `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json` | Entry's presence and shape reviewer-verified; no test reads the CHANGELOG |

One clause is named above as **not provable by anything in this plan, mechanism or live run,
before merge**: the live exercise of ladder rung 6, "Herdr wanted but not detected" (AC 5). Herdr is
installed and running on this machine for every other scenario's setup, so nothing here forces its
absence; the rung's text is pinned by T-F but never executed. State it as a gap rather than marking
it pass, and pick it up either in a follow-up pass with `HERDR_ENV` unset and `herdr` off `PATH`, or
as a fast-follow issue.

AC 3's earlier "announced once" tension is **closed**, not carried: the issue text was corrected to
state that unset is silent. See its row above.

## Files
None — this task runs the shipped change against scratch repos and this repository; it produces no
diff of its own beyond the UAT record (a scratch note, or comments on the pull request, per however
this plan's `split.pieces`/tracker mode records UAT evidence — this plan's `split.pieces` is
`commits`, so nothing is mirrored to a tracker; keep the record in the PR description or the
condensed plan, not in a new file under this plan folder).

## Verification
- `python3 -m unittest discover -s tests -v` — expect the final suite state from task 07 (at least
  52 tests, OK), 0 failures, 0 errors, run once more here as the last check before the change is
  considered done.
- Each of the fifteen scenarios above run to completion, with its **expected outcome recorded
  against what actually happened** — not just "pass," since several scenarios (2, 6, 7) are
  specifically about *which* command or announcement occurred, and a superficial pass would miss a
  wrong-but-plausible one.
- Scenario 6 run and recorded — **do not defer it**.
- Scenario 7 run for **three consecutive failed attempts**, with `herdr pane list` checked after all
  three, not after the first.
- The acceptance-criteria table above walked row by row, with AC3's and AC5's flagged gaps carried
  forward into the PR description or condensed plan rather than silently dropped.
