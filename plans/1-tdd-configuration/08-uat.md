status: pending
# 08 — UAT: prove the TDD-on path and the off-by-default regression guard

Depends on: 07

## Why
Every behavioural claim in this plan is a markdown instruction to an agent — no unit test can
assert that a Butler followed TS1's rung 4 rather than trusting an exit code, or that yolo didn't
stop on an expected red. This task is the only proof of the TDD-on path, and the only place every
clause of the issue's acceptance criteria gets checked against something observable.

## Description

### How this repo actually runs its own commands (read before starting)

This plugin is installed in this environment as a **directory-source** marketplace pointing
straight at this working tree (`~/.claude/plugins/known_marketplaces.json` registers `just-do-it`
with `"source": "directory", "path": "/home/dabit/git/just_do_it"`, no cached copy in between).
That means `/jdi:execute`, `/jdi:next`, and `/jdi:yolo` invoked in this repository read the command
files **live from the working tree**, not from a stale installed copy — confirmed by diffing this
session's actual `/jdi:init` behaviour against `commands/init.md:2` in the tree. **Use the native
`/jdi:execute` / `/jdi:next` / `/jdi:yolo` invocations as the primary UAT path in this environment.**

This is an environment-specific fact, not a universal one. On a machine where JDI is installed from
a marketplace that caches a versioned copy (the normal case for an end user, per
`README.md:151-162`), the installed copy would lag the working tree until a `claude plugin update`.
Keep the manual invocation from `AGENTS.md:9-16` — *"Read
`/home/dabit/git/just_do_it/commands/execute.md` and follow it"* — documented as the fallback for
that situation, and as the mechanism `AGENTS.md` exists to guarantee on a harness with no plugin
loader at all.

**New risk this implies, worth stating explicitly to whoever runs UAT:** because this plan edits
its own runtime, the behaviour observed by a scenario run *after* task 05 lands (which rewrites
`execute.md`/`next.md`/`yolo.md`) differs from a scenario run before it — and the same is true past
task 03 (`reference/testing.md`) and task 04 (`agents/executor.md`). A surprising result may be the
feature correctly taking effect mid-plan, not a bug. **Before recording any scenario's result, note
which tasks are already committed.** Run UAT after task 07 (all tasks committed) for the cleanest
read; if run earlier for spot-checking, expect partial behaviour and say so.

**Setup note:** scenarios 4, 5, 6, and 8 need a task with genuine testable, executable-code
behaviour to exercise TS2's red/green cycle. This repository is almost entirely markdown, so those
four scenarios are best run against a small scratch repo with a trivial Python (or similar)
function and a plan/task naming it — not against this repository's own plan history. Scenarios 1,
2, 3, 7, and 9 can be run directly against this plan's own execution or a minimal second plan here.

### Scenarios

Carried verbatim from `PLAN.md`'s `## Testing Strategy`:

1. **TDD off is silent (the regression guard).** `tdd` absent; run the first-task check. Expect no
   `TDD:` line, no mention of TDD anywhere, a diff identical in shape to today's. This is the
   "every existing repo behaves exactly as it does now" claim.
2. **TS1 proves the runner.** `enabled: true` here. Expect the derived invocation announced,
   output containing a `Ran N tests` tally, and the `- TDD: on — proven …` line written after
   `- Started:`.
3. **TS1 degrades out loud.** Set `test_instructions` to name an unreachable environment. Expect
   the attempt described, the failure shown, `- TDD: off — <reason>` written, the plan proceeding
   normally, and TDD **not** silently re-enabled by the presence of `tests/`.
4. **The red run is real and reported.** Give the Executor a task with genuine testable behaviour.
   Expect a `FAIL:` line naming the new assertion, then the same command green. Verify the red
   names the assertion, not an ImportError — that is the whole point.
5. **Yolo does not stop on the expected red.** Two-task plan, first task testable. Expect the loop
   to continue past the red-containing report, with the Butler's own run reported as pass/fail.
6. **Yolo still stops on a real red (the safety guard).** Same plan, implementation broken so the
   Butler's own run fails. Expect an immediate stop. Scenario 5 without 6 proves nothing.
7. **The announced skip.** A markdown-only task. Expect the skip announced and **no fabricated
   test** in the diff.
8. **Missing red evidence is caught.** A report with tests in the diff but no red run on a task
   touching executable code. Expect yolo to stop and execute to lead with it.
9. **The line is not rewritten.** Flip `tdd.enabled` mid-plan, run `/jdi:next`. Expect the existing
   line honoured unchanged.
9b. **A plan that started off stays off.** Start a plan with `tdd.enabled: false` — so no `TDD:`
   line is written at all — then flip it to `true` and run `/jdi:next`. Expect TDD to stay **off**
   and silent: no TS1 run, no line written, no mention of TDD. Then resume `/jdi:yolo` on the same
   plan and expect the same. *This is the pair to scenario 9: 9 proves an existing line is
   honoured, 9b proves an absent one is not an invitation to re-detect. Without 9b, a mid-plan
   config flip could silently turn TDD on through `/jdi:next`, and `/jdi:next` and `/jdi:execute`
   would disagree on the same plan.*

**Scenarios 1, 6, and 7 must not be dropped under time pressure.** They are the three places this
change could silently damage something that already works today: existing repos with no `tdd` key
(1), yolo's safety stop when a change genuinely breaks something (6), and the promise that TDD
never fabricates a test where none was warranted (7).

### Acceptance-criteria mapping

| # | Acceptance criterion | Proven by |
|---|---|---|
| 1 | `.jdi/config.yml` accepts a TDD setting, documented in `reference/config.md` and shown in `jdi.config.example.yml` | Automated, observable on merge: task 02's `test_config_schema` suite run. Exercised live by scenarios 2 and 3, which read the key from `.jdi/config.yml`. |
| 2 | The setting is off by default, so every existing repo behaves exactly as it does now | Scenario 1. |
| 3 | When enabled AND a viable test suite is detected, the Executor writes failing tests before the implementation, then makes them pass | Scenarios 2 (detection) and 4 (the red/green cycle itself). |
| 4 | When enabled but NO viable test suite is detected, JDI says so out loud and falls back rather than inventing a test harness | Scenario 3. |
| 5 | `/jdi:init` asks about the setting | **Not exercised by any of the nine scenarios — none of them run `/jdi:init`.** What proves the mechanism instead, on merge: task 06's regression check (`test_frontmatter` passing on the edited `init.md`) plus a direct read of the new step 5 and the `grep -n "step [0-9]" commands/init.md` renumber check performed in task 06. Full behavioural proof (does the question actually get asked, in the right words, with the right default) is deferred to the first live `/jdi:init` run in a repository with no existing `.jdi/config.yml` — pick this up either the next time `/jdi:init` is run fresh anywhere, or as a dedicated scratch-repo check before this plan is considered fully proven end-to-end. |
| 6 | The README documents it | **Not exercised by any of the nine scenarios — none of them read `README.md`.** What proves the mechanism instead: task 06's `grep -n "TDD|tdd" commands/help.md README.md` check that both enumerations and the new section exist, and human review of the `README.md` diff during code review of task 06 — this is documentation-only, so PR review of that diff is the proof, and no further deferral is needed beyond it. |

## Files
None (verification-only task; no production files are edited here).

## Verification
Run the nine scenarios above, in the setup described, and confirm each expected outcome. Then
confirm the acceptance-criteria table: for row 1, `python3 -m unittest discover -s tests -v` (via
task 02's `test_config_schema` module) is `OK`; for rows 5 and 6, confirm the deferral is recorded
here rather than silently assumed covered. Do not add a tenth scenario to make rows 5 or 6 look
exercised — name the gap, as this task does, rather than implying coverage that does not exist.
