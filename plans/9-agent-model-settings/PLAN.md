# Configure each agent's model in settings, not in the agent frontmatter

- Tracker: GitHub Issues
- Project: feature development
- Issue: 9
- Issue URL: https://github.com/dabit/just_do_it/issues/9
- Created: 2026-09-20
- Base commit: origin/main @ 815dfaeb1f67f1a142c9e04e2ca0c65459484c7f
- Summary: Replace the three-tier `models:` block and the hardcoded `model:` frontmatter in `agents/*.md` with a per-role mapping in `.jdi/config.yml` carrying both `model:` and `harness:`, making settings the single place a role's model — and the agent CLI it runs in — is named.
- Started: 2026-09-20
- TDD: on — proven 2026-09-20 with `python3 -m unittest discover -s tests -v`

## References

- `reference/config.md` — `models:` and `harnesses:` schema, defaults, invariants, example mappings
- `reference/delegation.md` — roles table, "what each role wants from a model", the ladder, the authorization paragraph
- `jdi.config.example.yml`
- `.jdi/config.yml` — the dogfood
- `agents/researcher.md`, `agents/planner.md`, `agents/executor.md`, `agents/feedbacker.md`, `agents/splitter.md`, `agents/synthesizer.md`, `agents/pr-writer.md`
- `roles/butler.md`
- `bin/sync-opencode.sh`
- `commands/research.md`, `commands/reresearch.md`, `commands/feedback.md`, `commands/prep.md`, `commands/execute.md`, `commands/yolo.md`, `commands/next.md`, `commands/split.md`, `commands/replan.md`, `commands/plan.md`, `commands/pr.md`
- `commands/init.md`, `commands/help.md`
- `commands/status.md` — considered, excluded
- `README.md`
- `AGENTS.md`
- `docs/harness-adapter-architecture.md`
- `docs/config-key-lifecycle.md`
- `skills/run/SKILL.md` — considered, unchanged
- `CHANGELOG.md`
- `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json`
- `tests/test_config_schema.py`, `tests/test_frontmatter.py`, `tests/test_opencode_sync.py`, `tests/test_codex_plugin.py`, `tests/test_enumerations.py`, `tests/test_versions.py`, `tests/jdi_files.py`
- `plans/1-tdd-configuration/PLAN.md` — 8-batch precedent, dogfood-at-release precedent (deviated from here)
- `plans/7-codex-skill-model/PLAN.md` — capability-based delegation prose, `UNVERIFIED — Issue #<n>` idiom
- `origin/herd-command:reference/config.md`, `origin/herd-command:commands/herd.md` — PR #5, open and unmerged, not edited here

## Decisions

- **Per-role keys replaced the three tiers outright.** `models.<role>` (seven entries, one per
  `agents/*.md` stem) carries both `model:` and `harness:`. `models.butler` is deliberately
  omitted — the Butler is the session already running and no harness lets a config file change a
  session already in flight.
- **The dogfood moved from the release batch into batch 01**, ahead of the frontmatter deletion,
  so the window in which this repo would silently run on the session model — because
  `.jdi/config.yml` had no `models:` block yet but the frontmatter had already been deleted — never
  opened.
- **The dogfood uses Claude Code aliases (`opus`/`sonnet`), not full identifiers**, because Claude
  Code's own Agent tool takes `model` as an enum (`sonnet | opus | haiku | fable`) and cannot accept
  a free-form identifier like `claude-opus-5` at spawn time. Writing full identifiers would have
  regressed the primary harness on day one.
- **Resolution is exec-first, Herdr second.** Prefer each CLI's own non-interactive mode
  (`codex exec -m … -o <file>`, `opencode run -m … --agent jdi-<role> --format json`,
  `claude -p --model … --output-format json`) and read the report from a file. Herdr is used only
  when a kind has no exec mode JDI knows, driven by `herdr pane split` → `herdr pane run` →
  `herdr pane wait-output` → `herdr pane close` — **never `herdr agent start`**, because
  `herdr agent read` is a terminal scrape in every mode and cannot recover a long report lost to the
  alternate screen.
- **A new top-level `harnesses:` block**, keyed by CLI kind, rather than reading PR #5's `herd:`
  block on the still-unmerged `herd-command` branch. This ships independently; PR #5 is expected to
  rebase onto it afterwards, moving `herd.args`/`herd.env` into `harnesses:`.
- **The authorization correction lands in both documents as one change.**
  `reference/delegation.md` and `docs/harness-adapter-architecture.md` both said a spawned CLI
  "stays inside" / "inherits" this session's sandbox and approval policy — false once a role's
  harness can be a different CLI process. Both were corrected to the same invariant: an in-harness
  subagent and an inline adoption inherit this session's sandbox and approval policy; a separately
  spawned CLI does not — it resolves its own from its own configuration, and JDI composes no
  authority-affecting flag and translates none between kinds.
- **`skills/run/SKILL.md` and `docs/harness-adapter-architecture.md`'s dispatcher guarantee list
  (its "preserves the active environment's authorization and sandbox boundaries" line) were
  considered and deliberately left unchanged.** Both describe the in-session dispatcher, not a
  spawned CLI, and remain true as written — JDI still grants nothing; a spawned CLI's authority
  comes from its own configuration and from flags the user wrote.
- **`commands/status.md` considered and excluded.** It loads the config but never names a key
  ("No delegation."); a command joins the config-consuming set only when a key changes what it
  *does*, not when it merely reads the file.
- **1.0.5 shipped as a patch bump despite removing a key**, stated deliberately in the CHANGELOG
  rather than left to convention — matching the only observed precedent (two prior full features
  shipped as patches).

## Plan gaps caught during execution

- The plan's `^tools:` control said seven hits; it is six — `agents/executor.md` never had a
  `tools:` key (verified against base commit `815dfae`).
- T-E's reach was overstated in the plan: it guards a tidied `AGENT_DROP` **and** a role file
  reacquiring `model:`, not the drop-set alone — with the source frontmatter now clean, tidying the
  set by itself would still leave T-E green.
- The plan's reviewer grep `grep -rn "sandbox, approval"` misses
  `docs/harness-adapter-architecture.md`, which says "sandbox **and** approval".
- `grep -l "A separately spawned CLI does not"` could not match `reference/delegation.md` — the
  sentence wrapped mid-phrase, so the plan's own verification grep could not match the file it was
  checking. The paragraph was reflowed (whitespace only; content verified identical).
- The citation sweep into `reference/config.md` ran eight sites wider than the plan catalogued, all
  self-caused rot from batches 03–05; every corrected citation was verified by opening its target.
- The release commit found `docs/config-key-lifecycle.md` still saying all three manifests were
  `1.0.4`, plus five CHANGELOG citations that moved when the new entry was inserted — fixed in the
  same commit that caused it.
- `commands/research.md` gained `models`/`harnesses` in its literal config-block list — the plan
  scoped that step to `commands/prep.md` alone, but `research.md` delegates too and genuinely reads
  both blocks.
- `/jdi:init` was made to *rewrite* a pre-1.0.5 `deep`/`standard`/`fast` block rather than
  preserve it, folded in during batch 05 though the plan's step never asked for it. The general
  keep-every-value-the-user-does-not-change rule would otherwise have silently retained a block
  nothing reads — the exact silent regression the ladder's old-shape rung exists to prevent.
- The plan predicted three grammar sites needing more than deletion, in `research.md` and
  `prep.md`. Execution found the actual sites were `prep.md` and `plan.md` instead, where the tier
  clause opened a wrapped line and deleting it would have left a line starting with punctuation.
- An earlier draft had the vocabulary guard (T-H) written red across batches 02–06 as a progress
  meter; withdrawn, because `tdd.enabled: true` puts tests and implementation in one commit and
  `/jdi:yolo` halts on the first failing task — a deliberately-red commit would have stopped the
  run at batch 03. T-H was written in batch 06, the batch that makes it green immediately.
- An earlier draft proposed the README heading "Roles and tiers, not agents and models" →
  "not agents and tiers", which contains the very word the vocabulary guard bans repo-wide;
  withdrawn before it shipped.

## Outcome

### Shipped

| Batch | Commit |
|---|---|
| Plan approved | `bae1272` |
| 01 — config schema, `harnesses:` block, worked example, dogfood | `afd35c1` |
| 02 — `reference/delegation.md`: ladder, authorization correction, recast | `e6f4465` |
| 03 — frontmatter `model:` lines removed | `0935e15` |
| 03 record correction (tools: control, T-E scope) | `4c42bd5` |
| 04 — command hand-off sites (25 edits, 11 files) | `b5837f1` |
| 05 — init/help/README/AGENTS.md, nine-file floor | `033f0d3` |
| 06 — architecture docs, citation sweep, vocabulary guard (T-H) green | `531fa1c` |
| 07 — release 1.0.5 (version bump, CHANGELOG, dogfood re-verified) | `3246653` |

All nine commits are on this branch per `git log origin/main..HEAD` in this session; push/merge
state is otherwise unverified here.

### Deferred

- **`08-uat.md` — UAT did not run.** The user chose explicitly to skip it and open the pull
  request instead. No commit exists for it. Full procedure carried below under Remaining work; no
  follow-up issue has been filed for it.
- **Herdr rung 6 ("wanted but not detected") is not exercisable on the development machine** —
  Herdr is installed and running for every other scenario's setup. Pinned by
  `tests/test_codex_plugin.py` only, never executed live. No follow-up issue filed; see Remaining
  work, AC 5.
- Deliberately out of scope, not deferred (decisions, not gaps): `models.butler`,
  `harnesses.<kind>.jdi_root` (no kind needs it today; the trigger to revive it is a kind that can
  take role instructions only as a file path), `commands/status.md`, `skills/run/SKILL.md`, and
  PR #5's `herd:` block (independent, expected to rebase onto `harnesses:` afterwards).

## Test result

Baseline **47 tests, OK**. Final suite, verified in this session:
`python3 -m unittest discover -s tests -v` → **54 tests, OK**, 0 failures, 0 errors. The suite
checks structure only (key paths, headings, literal substrings, an absent word) — **no test
observes command or role body prose**. Behavioural proof was left to UAT, which did not run (see
Deferred and Remaining work).

## Risk note

- **The silent drop to the session model — the regression this whole change exists to close — is
  UNVERIFIED live.** Deleting `agents/*.md`'s `model:` removed the one mechanism that actually
  reached Claude Code before; the ladder's rung 10 is detectable before the spawn from the harness's
  own schema, and the floor sentence and announcement rules are pinned by test. But the one scenario
  written specifically to exercise this live — UAT scenario 7 — was explicitly marked
  "not deferrable" and **was not run**, because UAT as a whole was skipped. Detection signal if this
  regresses: a role silently running on the session's own model with no announcement, in a repo
  whose config names a model the harness cannot express. Remedy: run UAT scenario 7 (see Remaining
  work) before relying on this in a harness other than Claude Code.
- **An accepted, visible UX change on this repo, ships as designed.** The dogfood writes Claude
  Code aliases into `.jdi/config.yml`. Under Claude Code that is exact parity with before. Under
  Codex or OpenCode, every JDI-on-JDI delegation now emits a rung-10 announcement that did not exist
  before — correct behaviour, since the alias genuinely cannot be expressed there, but it will look
  like a bug to whoever sees it first. Detection signal: a bug report about a new "cannot express
  model" announcement on this repo under Codex/OpenCode. Remedy if the noise proves intolerable: a
  `harnesses:`-aware per-kind model in a later change, not silence.
- **An existing user's pre-1.0.5 `models:` block (`deep`/`standard`/`fast`) is handled by a
  detect-and-say-once sentence, not by interpretation** — JDI never invents a mapping the user did
  not write. This is proven only by reading the prose — no test pins the old-shape detection
  sentence itself; UAT scenario 9, which would have exercised it live, did not run.
- **Prose correctness is unverifiable by the test suite** for the whole change — the ladder, the
  exec-first/Herdr-second resolution, and the authorization boundary are markdown instructions to an
  agent. The suite is a regression guard on structure only. With UAT skipped, this remains true for
  every scenario, not only scenario 7.

## Remaining work

**UAT did not run.** The user chose explicitly to skip it and open the pull request. This section
is the only remaining record of the procedure and is carried in full so it can actually be executed
later — it is exempt from this document's compression target.

Run all fifteen scenarios below against a real harness. Machine state this plan was verified
against: `codex`, `opencode`, `gemini`, `herdr`, and `claude` on `PATH`; `qwen` **not** installed;
`~/.config/opencode/agent/jdi-*.md` exists for all seven roles; `gemini` is installed with no JDI.
For each scenario, record the composed command (or announcement) verbatim, not just pass/fail —
several scenarios exist specifically to check *which* command was composed.

### Scenarios

**Positive — the exec path end to end, both installed kinds, plus the reverse direction:**

1. **Codex exec.** Scratch repo, `.jdi/config.yml` with
   `models.researcher: {model: gpt-5.1-codex-max, harness: codex}` and
   `harnesses.codex.args: ["--sandbox", "workspace-write"]`. Run `/jdi:research`. Confirm: the
   composed command uses `codex exec -m … -o <file>`; the args are printed back **before** the
   spawn and appear verbatim, unmerged; the report comes back from the file, not a terminal scrape;
   no pane was created.
2. **OpenCode exec.** `models.splitter: {model: <provider/model>, harness: opencode}`. Run
   `/jdi:split`. Confirm `opencode run -m … --agent jdi-splitter --format json` and that the role's
   own instructions were used. **This scenario's `--agent jdi-splitter` claim is unverified going
   in** — the synced agents carry `mode: subagent`, and whether `opencode run --agent` resolves a
   subagent-mode agent has not been tested on this branch. If accepted, record the command. If
   rejected, that is rung 5 firing correctly and the contingency is the inline path (pass
   `agents/splitter.md`'s text in the prompt) — record whichever happened. **Either outcome is a
   pass for the degradation ladder; only acceptance is a pass for the `--agent` claim itself.** Do
   not conflate the two in the writeup.
3. **Claude exec, from a non-Claude session** (scenario 2b in the original split). Run JDI under
   Codex or OpenCode with `models.planner: {model: opus, harness: claude}`. Confirm the composed
   command is `claude -p --model opus --output-format json`, the report is parsed from the JSON
   result rather than scraped, and the Planner phase runs. This is the direction issue #9's AC 4
   names explicitly and the one the two scenarios above do not cover.

**Negative — the rungs that are genuinely reachable here:**

4. **Rung 3, CLI absent from `PATH`.** `models.planner.harness: qwen` (not installed). Confirm
   exactly one announcement naming what was configured and what is running instead; **nothing is
   spawned**; the Planner phase still runs at the floor.
5. **Rung 4, no exec mode JDI knows.** `models.planner.harness: gemini` (on `PATH`, no known exec
   invocation). Confirm the announcement names the reason correctly — *no exec mode*, not
   *not installed* — and that the ladder then considers Herdr before the floor.
6. **Rung 5, instructions unresolvable.** `models.splitter.harness: opencode` with
   `OPENCODE_CONFIG_DIR` pointed at an empty directory via `harnesses.opencode.env`, so
   `--agent jdi-splitter` cannot resolve. Confirm the ladder either inlines the role file or
   announces rung 5 and floors — and that it **never** derives or searches for a plugin path.
7. **Rung 10, the model this harness cannot express. NOT DEFERRABLE.** Inside Claude Code,
   `models.planner: {model: claude-opus-5}` with **no** `harness:`. Claude Code's Agent tool takes
   `model` as an enum, so this cannot be passed at spawn time. Confirm an **announcement**, not a
   silent drop, and that the Planner runs on the harness default. This is the regression the whole
   change exists to close, it is a certainty by schema rather than a hypothesis, and it must be
   exercised live — not waved through on the strength of the schema alone.
8. **Rungs 6–9 and pane hygiene — three consecutive failed attempts, not one.** Force the Herdr
   transport (a kind with no exec mode, Herdr present). Interrupt it mid-run so it never reports
   usably, three times in a row. Confirm: one announcement per attempt; the phase still runs at the
   floor each time; and `herdr pane list` shows **no leaked pane** after all three. A leak of one
   pane per attempt, visible only after several attempts, is what this scenario guards against — a
   single attempt would not catch it.

**Compatibility and silence:**

9. **Old-shape `models:` block.** Scratch repo with
   `models: {deep: claude-opus-5, standard: claude-sonnet-5, fast: claude-haiku-4-5}`. Run
   `/jdi:plan`. Confirm exactly one announcement that the block is the pre-1.0.5 shape and is not
   read, that `reference/config.md` is named, and that the workflow proceeds on the session's model.
   Nothing breaks and nothing is silently reinterpreted.
10. **No `models:` block at all.** Scratch repo with a 1.0.4-era config. Run `/jdi:plan`. Confirm
    **complete silence** on models — a run here must be indistinguishable from a 1.0.4 run. Any
    announcement at all here is a **failure**, not harmless extra chatter.
11. **The dogfood.** In this repository, under Claude Code, run `/jdi:plan`. Confirm the Planner is
    spawned on `opus` resolved from `.jdi/config.yml`, and that **nothing is announced** (the silent
    path). Then run the same under Codex or OpenCode and confirm the single announcement that the
    alias cannot be expressed, and that the phase still runs.
12. **`/jdi:init` read-through.** Scratch repo with no `.jdi/config.yml`. Run `/jdi:init`. Confirm
    step 8 asks per role, says it is optional, and asks the `harnesses` follow-up **only** when a
    role was given a different harness. Confirm the written file matches the schema. Do not
    substitute a diff review — init's question wording is genuinely unverifiable without this run.
13. **`/jdi:help` read-through.** Confirm the table has no `Tier` column, the `### Roles and models`
    section reads correctly, and the closing line names which roles have a model configured.
14. **OpenCode sync end to end.** `bin/sync-opencode.sh --global` into a temp
    `OPENCODE_CONFIG_DIR`; confirm no synced agent carries `model:`, then run `/jdi-plan` against
    the synced copy and confirm the workflow still runs.
15. **Acceptance-criteria sweep.** Walk the table below row by row and confirm each cited scenario
    or test actually produced the evidence it claims.

### Acceptance-criteria mapping (against the live issue #9 text, not the earlier plan wording)

| AC | Clause | Proven by | Notes |
|---|---|---|---|
| 1 | No file under `agents/` carries a `model:` key | T-D (`tests/test_frontmatter.py`) | Structural, whole-repo; scenario 14 additionally confirms synced OpenCode copies |
| 2 | `.jdi/config.yml` accepts a per-role mapping with `model:`/`harness:`; `reference/config.md` documents schema, defaults, invariants | T-A, T-B, T-C (`tests/test_config_schema.py`) | Scenario 12 confirms `/jdi:init` writes a matching file; whether the invariants read well to a human is reviewer judgment only |
| 3 | Every delegatable role can be named. **Unset is silent**; **announcement is for degradation only** | Scenario 10 (no block, must be silent), scenario 11 (dogfood, silent), scenarios 4–8 and 12 as the contrast | The issue's original "announced once" wording for the unset case predated the ladder and was corrected — AC 3 now states the silent reading explicitly. This tension is **closed**, not carried |
| 4 | `harness:` honoured **exec-first** (`codex exec`, `opencode run`, `claude -p`), Herdr **second** via `herdr pane run` (never `herdr agent start`) | Scenarios 1, 2, 3 (exec-first, all three CLIs), 8 (Herdr second, pane hygiene) | Scenario 2's `--agent` sub-claim is unverified — see its own note. Nothing exercises `herdr agent start` being *avoided* live; T-F's pin of `"herdr pane close"` and the ladder's prose are the structural check |
| 5 | A written, ordered degradation ladder covers every harness-dimension failure, degrading down only, announced | T-F pins structure, ordering, floor sentence | Live: scenarios 4, 5, 6, 8. **Not exercised live: rung 6, "Herdr wanted but not detected"** — Herdr is installed and running for every other scenario's setup here. Mechanism proven only by T-F's text pin. Pick up in a follow-up UAT pass with `HERDR_ENV` unset or `herdr` off `PATH`, or as a fast-follow issue — none filed |
| 6 | Authorization boundary stated explicitly: a spawned agent does not inherit this session's approval policy; JDI composes no permission flag | T-F's rewritten fragments, the 3-site `grep -n "sandbox"` control | Scenario 1 additionally confirms in practice that `harnesses.codex.args` is printed back verbatim before the spawn |
| 7 | Documentation no longer tells a reader a model name belongs in frontmatter | T-H (whole-repo word scan), T-G (README heading rewrite) | Scenario 13 confirms `/jdi:help` reads correctly. **`docs/config-key-lifecycle.md` §5's rewritten *content* is reviewer-verified only** — no test reads what §5 says, only that its section headings didn't move |
| 8 | A repo with no `models:` block still runs every command end to end; CHANGELOG states plainly what changes | Scenario 10 | Scenario 10 as written runs `/jdi:plan` only, not literally every command — inferred, not directly exercised, since every delegation shares one ladder. **The CHANGELOG's specific wording is reviewer-verified only** — no test reads its content |
| 9 | `bin/sync-opencode.sh` still produces valid OpenCode agent files; full suite passes | T-E (characterization), scenario 14 | Full suite green confirmed in this session (54 tests, OK) |
| 10 | Release ships with matching versions in the three JSON files and a CHANGELOG entry | `tests/test_versions.py` (the three manifests match); version grep run in this session confirms all three read `1.0.5` | Entry's presence and shape reviewer-verified; no test reads the CHANGELOG |

**Reviewer-verified-only clauses (no test reads them):** `docs/config-key-lifecycle.md` §5's
rewritten prose; the CHANGELOG's specific wording; the four-site `/jdi:init` question enumeration
(`commands/init.md`, `commands/help.md`, `README.md`'s two sites).

**AC 5's rung 6 ("Herdr wanted but not detected") is pinned-by-test-only, not passed** — it is not
exercisable on the development machine, where Herdr is installed and running for every other
scenario's setup. Record it as such; do not mark it passed.
