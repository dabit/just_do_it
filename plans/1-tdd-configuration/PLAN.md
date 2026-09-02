# Add a TDD configuration

- Tracker: github
- Project: feature development
- Issue: #1
- Issue URL: https://github.com/dabit/just_do_it/issues/1
- Created: 2026-09-02
- Started: 2026-09-02
- Base commit: main @ a6823a921731d6fed62cff34afde988c1dc763a8
- Summary: A configurable TDD mode that has the Executor write failing tests before implementation, only when explicitly enabled and a viable test suite exists.

## References

- `docs/config-key-lifecycle.md` — architecture doc: resolution order, mandatory file set,
  degradation idiom, release mechanics
- `reference/config.md` — the `tdd:` schema block, defaults rows, `## Notes` invariants
- `jdi.config.example.yml` — the example block
- `reference/testing.md` — the TS1/TS2 ladder
- `reference/plan-store.md` — documents the `TDD:` metadata line
- `reference/tracker.md` — the degradation-ladder idiom this change matches
- `commands/init.md`, `commands/help.md`, `README.md` — user-facing surface
- `commands/execute.md`, `commands/next.md`, `commands/yolo.md` — the nine hand-off/verification
  sites
- `agents/executor.md`, `roles/butler.md`, `agents/planner.md` — role responsibilities
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `CHANGELOG.md` — release
- `tests/` — the repository's first automated test suite

## Decisions

- **`test_instructions` is free-form prose an agent reads and translates, never a string to
  exec.** Empty means "work it out from the repo" — a literal command is usually not runnable as
  typed. The key: `tdd: { enabled: false, test_instructions: "" }`.
- **Two named operations in `reference/testing.md`**, prefixed `TS` to avoid colliding with
  `tracker.md`'s `T1`-`T8`: **TS1** — prove the test suite runs, once per plan, by the Butler,
  recorded in `PLAN.md`. **TS2** — write the failing test first, the Executor's per-task
  discipline. TS1's core rule: **read the tally, not the exit code** — `python3 -m unittest`
  exits `5` on "Ran 0 tests", and a suite with a genuine pre-existing failure exits non-zero while
  still proving the runner works.
- **The `TDD:` metadata line** is written once and **never rewritten** for that plan — flipping
  `.jdi/config.yml` mid-plan changes nothing until the next plan. **No line is written when
  `tdd.enabled` is not `true`**: only an ON-but-degraded run writes `off` and announces. This
  plan's own execution carries no line at all — rung 1 (off) applied before the key existed, and
  dogfooding it on later (task 07) does not add one retroactively.
- **"No line means no TDD, for every command, always."** A plan predating the key and a plan whose
  TS1 resolved to off are indistinguishable by design, so absence must never be treated as an
  invitation to (re-)detect — this is what keeps `/jdi:next`, `/jdi:execute`, and `/jdi:yolo` from
  disagreeing about the same plan.
- **"Silent when off" is scoped to execution time, not to all mention** — `/jdi:help` reports
  whether TDD is on and `/jdi:init` asks about it; no command *running a plan* speaks about TDD.
  `/jdi:init`'s trial run is deliberately not TS1: TS1 must have exactly one site that writes the
  `TDD:` line.
- **The Butler performs TS1 and hands the Executor a resolved decision; the Executor never reads
  `.jdi/config.yml`.** A role receives exactly the inputs its "What it receives" section lists.
- **Tests and implementation land in the same commit.** TDD changes the order the Executor writes
  them, not the history — preserving yolo's bisect promise and `split.pieces`'s "identical in all
  three modes" invariant.
- **The Executor must report red-run evidence** (exact command, failing output captured before the
  implementation existed, the assertion line proving it failed for the intended reason) — without
  it, "tests first" collapses into "tests in the same commit", true of every task regardless of
  TDD.
- **The Butler does not reproduce red**: the no-`git stash` rule makes reconstructing a pre-change
  tree expensive on purpose. The Butler verifies the tests are in the diff and green now, and
  reads the Executor's captured red rather than re-running it.
- **A three-way skip judgement, not two**: docs/config get an announced skip; a task touching
  executable code that the plan names no test for is a *gap in the plan*. The Planner's existing
  testing-strategy bullet was extended, not given a new one, to attribute each test to the step it
  proves and name any step no test can observe.
- **The repo gained its own test suite** (python3 stdlib `unittest`, no third-party dep —
  `bin/sync-opencode.sh` already hard-depends on `python3`; pyyaml rejected since a
  `skipUnless(HAS_YAML)` guard would silently vanish the suite's most valuable assertion on a
  contributor's machine) so the TDD-on path is provable here rather than only in theory — chosen
  over deferring proof to a scratch repo. It parses no YAML: it extracts key *paths* from the
  plain two-space-indented subset both config files are hand-written in.

## Plan gaps caught during execution

- **The `/jdi:next` lazy-detect that would have contradicted the never-rewritten invariant** —
  caught before implementation: an absence-triggered TS1 in `/jdi:next` would let a mid-plan
  config flip turn TDD on there while `/jdi:execute` disagreed. Fix: `/jdi:next` reads the `TDD:`
  line and never runs TS1.
- **The yolo/execute pre-loop gate could still flip TDD on mid-plan**, found by UAT, fixed in
  `b755ec5`. The gate asked whether every task was still unchecked, but `/jdi:execute` leaves
  ticking to `/jdi:done`, so that stays true after a task was already run with TDD off — a
  subsequent config flip plus `/jdi:yolo` re-fired TS1. Both sites now gate on **absence of a
  `- Started:` line** instead, and yolo writes `Started:` itself, as execute already did.
- **TS1 rung 4 accepted an import error as proof**, found by UAT, fixed in `b755ec5`: the "not
  proof" list omitted a failed import, and `python3 -m unittest` answers a bad module path with
  `ModuleNotFoundError`, `Ran 1 test`, `FAILED (errors=1)` — a tally alongside a non-proof. TS2
  step 4 already excluded this case; the exclusion now appears at both ends.
- **Rung 3 (scoped probe) and rung 5 (record the exact command) disagreed**, found by UAT, fixed
  in `b755ec5`: recording the narrowed probe would have hidden a red raised outside that slice.
  Rung 5 now records the invocation unscoped, matching the file's own example.
- **The first-task check's steps were ordered a/b/c but step c said "do this before b's commit
  runs"**, found by UAT, fixed in `b755ec5`: TS1 is now step b, the approval commit step c.
- **The synthesizer dropped the `TDD:` line at PR time**, found during task 07's own pre-commit
  sweep, fixed in `9f61c35`: since absence means "never enabled," dropping the line silently at
  PR time would assert something false in the copy that outlives the branch.
- **`commands/yolo.md` anchored the `TDD:` line "immediately after `- Started:`"**, but only
  `/jdi:execute` writes `- Started:` — a plan taken straight from `/jdi:prep` to `/jdi:yolo` has no
  anchor. Fixed in `9f61c35`, loosened again to "alongside" in `b755ec5` once TS1 moved to run
  before the commit that writes `Started:`.
- **Self-caused citation rot, fixed in the task that caused it**: `reference/testing.md`'s
  citation into the no-stash rule (task 04); `docs/config-key-lifecycle.md`'s citations into the
  renumbered `init.md` (task 06).
- **Compound findings**: task 01 added a `.gitignore` the repo never had (else `__pycache__` lands
  in a commit); `reference/config.md`/the example originally said the *Executor* derives the test
  invocation, contradicting "the Executor never reads `.jdi/config.yml`" — fixed in task 03;
  `README.md`'s yolo snippet was an unlisted third "stopping on failure" site (task 06).

## Outcome

### Shipped

| Batch | Commit(s) |
|---|---|
| Plan approved | `8b99646` |
| 01 — test suite | `ea81473` |
| 02 — config schema and example | `c0b3986`, `71ff175` |
| 03 — `reference/testing.md`, enumerations | `c3bba74` |
| 04 — Executor and Planner roles | `a9a4923` |
| 05 — execute/next/yolo hand-off sites | `ced4c2b` |
| 06 — init/help/README documentation | `272f51d` |
| 07 — version bump, changelog, dogfood (1.0.3) | `9f61c35` |
| 08 — UAT, 4 defects found and fixed | `b755ec5` |

All ten commits are on this branch, ahead of `origin/main` per `git log origin/main..HEAD` in this
session; push/merge state is otherwise unverified here.

### Deferred

- `docs/config-key-lifecycle.md`'s stale `file:line` citations (see Remaining work).
- Full behavioural proof of acceptance criteria 5 and 6 (see Remaining work).

## Test result

15 stdlib `unittest` tests, green: `python3 -m unittest discover -s tests -v` reports `OK`. No
third-party dependency. Covers frontmatter well-formedness, config schema/example/defaults
agreement, hand-maintained enumeration consistency, and version agreement across
`plugin.json`/`marketplace.json`/`CHANGELOG.md`. **No test observes command or role body prose** —
every behavioural claim here (TS1's rung 4, the Executor's red/green discipline, yolo not stopping
on an expected red) is a markdown instruction to an agent, so the suite is a regression guard on
structure only, not behaviour. Behavioural proof is UAT (below).

## Risk note

- **Dogfooding turns TDD on for most future tasks here, and most are markdown**, so the
  "no testable behaviour" skip will fire often. Signal: a contributor reading the repeated skip as
  "TDD does nothing here." Remedy if noise outweighs signal: `enabled: false` here, prove the mode
  in a scratch repo instead — not weakening the announcement.
- **"Failed for the right reason" is the Executor judging its own work** — a trivially-true test
  that fails trivially is undetectable by design. The rejected remedy is the Butler reproducing
  red, which the no-`git stash` rule makes expensive on purpose.
- **Yolo's scoping sentence is the highest-consequence edit**: if the Executor's red leaks into the
  channel the Butler's own run reports on, the safety stop weakens invisibly. UAT scenario 6 is
  the detector.
- **`test_instructions` is a translation surface**: a wrong-but-runnable command would pass TS1 and
  produce meaningless red runs for a whole plan. Mitigation: TS1 announces the derived invocation
  once, so a human can correct it.
- **The key-path extractor is not a YAML parser** — it handles only the plain two-space-indented
  subset both files are hand-written in, and would misread flow mappings, multi-line scalars, or
  tabs; it fails loudly, not quietly.
- The drift grep for all nine command sites: `grep -rn "TS1\|TS2\|TDD" commands/`.

## Remaining work

**UAT was run by an agent, not a user** — a smoke test, not user acceptance. All nine scenarios
(off-by-default silence, TS1 proving/degrading, real red/green, yolo continuing past an expected
red, yolo still stopping on a real red, the announced skip, missing-evidence detection, the line
not rewritten mid-plan, a plan that started off staying off) ran and passed. Running them surfaced
four defects that reading the files had not (listed under Plan gaps), all fixed in `b755ec5`.

**Acceptance criteria 5 (`/jdi:init` asks about the setting) and 6 (the README documents it) were
NOT OBSERVED by any scenario** — none of the nine run `/jdi:init` or read `README.md`. What
stopped exercise: `/jdi:init` is interactive, and the manual fallback would mean the agent writing
the question and then judging its own wording, which proves nothing. Both were verified by
**reading the files only**:
- Criterion 5's substitute: `commands/init.md`'s new step 5 exists, and the renumbering of the
  steps after it is intact.
- Criterion 6's substitute: the `README.md` and `commands/help.md` enumeration sites exist. PR
  review of the `README.md` diff is the proof for the documentation criterion — no further
  deferral beyond that review.

Both remain genuinely unverified in the sense that matters (does the question actually get asked,
in the right words, with the right default) until a live `/jdi:init` run against a repo with no
existing `.jdi/config.yml`, or a dedicated scratch-repo check.

**`docs/config-key-lifecycle.md`'s `file:line` citations into `reference/config.md`, `README.md`,
and the command files went stale** as tasks 02-06 edited those files. Deliberately deferred to a
single dedicated pass rather than chased piecemeal — a citation refresh, not a behaviour change.

**Deliberately out of scope, with reasons** (decided and recorded, not gaps):
- `commands/prep.md`'s config-block list omits `tdd` — prep never resolves TS1.
- `roles/butler.md` stays silent on TS1, matching its existing silence on `T7`/`T8` — keys land in
  command files, not the orchestrator role.
- `commands/status.md` excludes it, matching the `split.pieces` precedent.
- No CI workflow — the repo has no `.github/` at all; a ~15-line workflow would close this but is
  a separate issue, not scope creep here.
