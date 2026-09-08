status: done
# 05 — UAT the installed adapter across harnesses

Depends on: 01, 02, 03, 04

## Why
Structural tests cannot prove Codex's installed-cache discovery, completion UI, model compliance,
or real delegation behavior. This task qualifies the released snapshot from isolated environments
and proves the existing Claude and OpenCode entry points still work.

## Description
Run every scenario below against the completed release and retain commands, relevant transcript
excerpts, versions, and outcomes in the task/PR evidence. Use disposable repositories and isolated
harness homes so an older standalone `$jdi` skill, cached JDI plugin, or working-tree command file
cannot create a false positive. Do not edit implementation in UAT; a failed criterion reopens its
own implementation task.

**TDD:** UAT-only; no new automated test applies. This task runs the already-written suite and live
harness scenarios, so inventing another red-first test would not prove installed-runtime behavior.

### Scenario 1 — Clean Codex install, snapshot, discovery, and completion

1. Record `codex --version`; the researched target is 0.151.0. Create a temporary marketplace
   snapshot from the completed commit and an isolated Codex home/config with no copied plugin cache
   or standalone JDI skill. Authenticate that isolated home as needed.
2. In that isolated environment, run the README's unchanged `codex plugin marketplace add
   <snapshot>` and `codex plugin add jdi@just-do-it`, then `codex plugin list`.
3. Locate and inspect the installed cached snapshot rather than the source checkout. Confirm it
   contains `.codex-plugin/plugin.json`, `skills/run/SKILL.md`, all 16 `commands/*.md`,
   `roles/butler.md`, all seven `agents/*.md`, and all `reference/*.md` files.
4. Start a **fresh** Codex session. Open `/skills`, type `$`, then type `$jdi:run` without submitting.

Expected: installation succeeds; the cached snapshot is complete; `/skills` lists exactly the
qualified JDI skill `jdi:run`; `$` completion offers `$jdi:run`; no standalone `$jdi` or per-command
JDI skill is required. If the runtime is not 0.151.0, record the actual version and treat observed
discovery—not the source-level assumption—as authoritative for this release.

### Scenario 2 — Empty and explicit canonical help

1. In fresh sessions from scenario 1, submit `$jdi:run` and `$jdi:run help`.
2. Compare both outputs with the installed snapshot's `commands/help.md`, including its command
   table and repository-configuration closing line.

Expected: both invocations dispatch canonical help with an empty payload; neither reports a missing
command, chooses a different workflow, or prints a copied/reinterpreted help implementation.

### Scenario 3 — Argument preservation and multiple placeholder replacement

1. Create a disposable git repository with a disposable local `origin`, one initial commit, and JDI
   configured with `tracker.name: none`. From that repository, submit `$jdi:run prep 4`, answer only
   genuinely required prompts, and stop after prep has produced its plan/tasks.
2. Inspect the resulting plan and transcript for the received task description.
3. Add an **older** matching plan and a **newer** unrelated plan. Submit
   `$jdi:run feedback <matching-plan-name>`; `commands/feedback.md` is the non-vacuous command whose
   original body contains two `$ARGUMENTS` placeholders.
4. In another disposable invocation, pass repeated spaces, punctuation, and a literal
   `$ARGUMENTS` in the payload. Record the command-visible payload before judging downstream prose.

Expected: `prep` receives exactly `4`, not empty input or a reconstructed argument list; feedback
uses the named older plan in both argument-dependent steps rather than falling back to the newer
plan; every original placeholder is replaced; a literal placeholder introduced by the payload is
not replaced recursively; and the remainder is not quote-parsed, expanded, path-resolved, or
whitespace-normalized by the dispatcher.

### Scenario 4 — Unknown and path-like input fails closed

1. In a disposable repo, record `git status --porcelain=v1`, the plan tree, and relevant file
   checksums. Invoke `$jdi:run UNKNOWN`, `$jdi:run ../help`, `$jdi:run /tmp/help`, and
   `$jdi:run commands/help.md`, recording each transcript.
2. Repeat the state/checksum probes.

Expected: every token is rejected case-sensitively with the supported 16-command list before any
command path/read or workflow action; none defaults to help; repository and plan state are
unchanged. The structural pre-path test is the proof of instruction ordering when the host exposes
no file-read trace; the live no-mutation control proves the user-visible failure mode.

### Scenario 5 — Installed-root isolation

1. From a separate scratch repository, create a decoy `commands/help.md`, `roles/butler.md`, and
   `reference/` content with unmistakable text. Submit `$jdi:run help` from that repository.
2. Confirm any plans and git operations target the scratch repository while all support-file content
   comes from the installed snapshot.
3. In a throwaway copy of the installed snapshot, remove one required installed reference and run a
   command that needs it while another JDI checkout remains visible elsewhere on disk.

Expected: canonical installed help wins over every decoy; support paths never follow the process
working directory, marketplace checkout, `${CLAUDE_PLUGIN_ROOT}`, or an ancestor search; the missing
installed file produces a diagnostic rather than falling back; user-repository mutations, when a
valid workflow calls for them, remain in the scratch repository.

### Scenario 6 — Enabled subagent and disabled-subagent fallback

1. With Codex subagents enabled, run a delegating command such as `$jdi:run feedback <plan>`.
   Observe the child execution and, where the runtime exposes it, inspect the role instructions and
   handoff inputs.
2. Confirm an unregistered JDI role is represented by a suitable generic subagent loaded from the
   installed `agents/feedbacker.md`, receives only the role's declared inputs, and remains inside
   the active sandbox/approval boundaries.
3. Set `agents.enabled = false`, start a fresh session, and repeat. Observe the second-session rung
   if actually available; otherwise require the announced inline-role switch and return to Butler
   voice.

Expected: the enabled run delegates instead of making a blanket no-subagents assumption; the
disabled run does not skip the phase and visibly uses the documented fallback ladder; neither run
widens authorization. If Codex does not expose the complete child prompt, exact input minimality is
**not observable on merge**: record it as unverified in the PR/UAT evidence, cite
`DelegationGuidanceTest.test_unregistered_role_uses_installed_definition_and_declared_inputs` as
mechanism proof only, and pick it up in the next Codex release-qualification run that provides
subagent tracing. Do not report that clause as live-passed.

### Scenario 7 — Claude Code regression

1. Install/update the completed snapshot in an isolated or disposable Claude configuration and run
   `claude plugin validate .` from the source checkout.
2. Start a fresh Claude session, run `/jdi:help`, and inspect registered agents.
3. Confirm the additive root skill does not shadow or replace `/jdi:<command>`.

Expected: validation succeeds; `/jdi:help` follows canonical help; all seven named JDI agents remain
registered; existing `/jdi:<command>` behavior remains available even if the additive `jdi:run`
skill is also visible.

### Scenario 8 — OpenCode regression

1. Run `python3 -m unittest discover -s tests -p 'test_opencode_sync.py' -v`.
2. Create empty temporary global and project destinations. Run
   `OPENCODE_CONFIG_DIR=<global> bin/sync-opencode.sh --global` and
   `bin/sync-opencode.sh --project <project>`.
3. Start OpenCode against the temporary global sync and run `/jdi-help`; repeat against project
   mode. Scan project output for the source checkout's absolute path.

Expected: tests and both syncs pass; each has 16 `jdi-*` commands and seven `jdi-*` agents;
`/jdi-help` works; project mode includes portable copied roles/references and no absolute checkout
path; global mode retains its intentional checkout path; neither mode copies Codex packaging.

### Scenario 9 — README and manual-adapter correctness

1. Follow the README's Codex steps from install through fresh-session `/skills`, `$` completion,
   `$jdi:run`, `$jdi:run help`, `$jdi:run prep 4`, `$jdi:run yolo`, and `$jdi:run pr`. Confirm its
   machine-wide scope, cached-refresh, and capability-based delegation statements match observation.
2. Confirm the same README still gives working Claude `/jdi:help` and OpenCode `/jdi-help` examples
   and does not claim Codex registers `commands/*.md` as custom slash commands.
3. Follow `AGENTS.md` manually with `commands/help.md` (zero placeholders), `commands/prep.md` (one),
   and `commands/feedback.md` (multiple), using literal one-pass substitution.

Expected: a reader can discover and run only the supported public Codex interface without hidden
knowledge; all listed examples are accurate; the other harness examples remain accurate; manual
zero/one/multiple-placeholder invocation agrees with the dispatcher contract.

### Acceptance mapping and honest limits

| Reconciled acceptance clause | Proof in this task |
|---|---|
| Clean install exposes `jdi:run` | Scenario 1 installed snapshot plus fresh `/skills` |
| Typing `$jdi:run` offers completion | Scenario 1 `$` completion |
| Empty and explicit help run canonical help | Scenario 2 |
| `prep 4` preserves `4` | Scenario 3 |
| Multiple placeholders and opaque payload are handled once | Scenario 3 plus dispatcher structural tests |
| Unknown and path-like tokens fail before mutation/path use | Scenario 4 plus pre-path structural test |
| Installed-root and user-repository roots stay isolated | Scenario 5 |
| Enabled subagents run and disabled subagents fall back | Scenario 6 |
| Claude Code does not regress | Scenario 7 plus `claude plugin validate .` |
| OpenCode does not regress | Scenario 8 plus temporary sync tests |
| README matches supported behavior | Scenario 9 plus README structural tests |
| Manual invocation handles zero, one, and multiple placeholders | Scenario 9 |

Byte-for-byte payload handling, pre-read ordering, and hidden child-prompt contents may not be fully
visible in a natural-language TUI. Their structural tests prove the shipped instructions, not model
compliance. Any clause lacking runtime observability must remain explicitly unverified in the PR's
UAT record and be repeated in the next release-qualification run on a host exposing the needed
trace; it must not be silently upgraded to passed.

## Results

Agent-run smoke test on 2026-09-08:

- **PASS:** Codex CLI 0.151.0 installed `jdi@just-do-it` 1.0.4 into an isolated home. The cached
  snapshot contained the native manifest, `skills/run/SKILL.md`, all 16 commands, all seven agents,
  the Butler, and all five reference files.
- **PASS:** OpenCode 1.18.25 global and project syncs retained 16 commands and seven agents,
  project-mode paths remained portable, Codex packaging was not copied, and `/jdi-help` produced
  canonical help in both modes.
- **PASS:** Manual zero/one/multiple-placeholder substitution preserved introduced literal
  `$ARGUMENTS` text under the global, literal, single-pass rule.
- **PASS:** `python3 -m unittest discover -s tests -v` ran 47 tests successfully;
  `claude plugin validate .` and `git diff --check` also passed.
- **UNVERIFIED:** Fresh Codex `/skills`, `$` completion, help, prep, rejection, root-isolation, and
  delegation behavior could not run because the isolated home was unauthenticated; non-interactive
  attempts stopped at HTTP 401 before model dispatch.
- **UNVERIFIED:** Claude `/jdi:help` could not execute in the isolated unauthenticated configuration.
  Plugin installation succeeded and reported 17 skills (16 commands plus additive `run`) and seven
  agents, proving package inventory but not live command behavior.
- **UNVERIFIED:** Exact hidden child inputs, byte-for-byte payload receipt, and pre-read ordering
  were not observable. Structural tests are mechanism evidence only, not a live pass.

No implementation failure was observed. The unverified clauses must be repeated during PR user
acceptance from authenticated Codex and Claude sessions.

## Files
- No implementation files
- UAT evidence recorded in the task completion report and PR summary

## Verification
1. Run `python3 -m unittest discover -s tests -v`. Expected: every structural, documentation,
   version, and cross-harness regression test passes before live UAT begins.
2. Run `claude plugin validate .`. Expected: validation succeeds.
3. Run scenarios 1–9 and complete the acceptance mapping. Expected: every observable clause passes
   with retained evidence; every host-hidden clause is named unverified with the mechanism test and
   next release-qualification pickup recorded exactly as above.
4. Run `git diff --check`. Expected: no whitespace errors and no UAT-time implementation changes.
