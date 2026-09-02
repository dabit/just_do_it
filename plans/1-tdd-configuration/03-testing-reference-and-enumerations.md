status: pending
# 03 — Write the shared TS1/TS2 ladder and update both reference-file enumerations

Depends on: 01

## Why
Six command sites (in task 05) all need to perform the same two operations — "prove the test suite
runs" and "write the failing test first" — without repeating the full ladder six times. This task
gives those operations a single home, named so no reader confuses them with `reference/tracker.md`'s
`T1`–`T8`, and updates the two hand-maintained lists of reference files so the new one doesn't
quietly go undocumented the way the architecture doc warns is easy to do.

## Description
Create `reference/testing.md` with two named operations, prefixed `TS`:

**TS1 — Prove the test suite runs.** Resolved once per plan, before the first task, by the Butler.
Preamble: capability is proven, not assumed — a `spec/` folder, a `tests/` folder, or a manifest
dependency is not evidence.
1. `tdd.enabled` is not `true` → off. Say nothing. Write no `TDD:` line. Stop.
2. Derive the invocation — from `test_instructions` as prose, or from the repo when empty. Say
   which invocation was derived and where it came from.
3. Run it, scoped as narrowly as the runner allows.
4. Read the output, not the exit code. Proof is a printed test-result tally, even "zero tests" in a
   repo that has none yet. The exit code is not the signal — `python3 -m unittest` exits `5` on
   "Ran 0 tests" (verified on 3.14.7), and a suite with a genuine pre-existing failure exits
   non-zero while still proving the runner works. Not proof: command not found, missing
   interpreter, dependency-resolution error, config parse error, unreachable container, timeout, an
   interactive prompt — nothing ran.
5. Proven → write `- TDD: on — proven <date> with \`<command>\`` after `- Started:`.
6. Disproven → off, announced with the command tried and the output showing why. Write
   `- TDD: off — …`.
7. Ambiguous → ask the user once (give the invocation, run without TDD, or stop). The Butler asks,
   never the Executor. With no user to ask, degrade to off and say so.

Anything unparseable in an existing `TDD:` line is treated as absent — off, silent.

**TS2 — Write the failing test first.** By the Executor, per task, only when the line says `on`.
1. Judge whether the task has testable behaviour, from the plan's `## Testing Strategy` and the
   task's own Verification. If the plan names none and the Files list is docs/prose/config,
   announce the skip and implement normally — never fabricate a test. If the plan names none but
   the task touches executable code, say that too; it is a gap in the plan.
2. Write the test, and only the test.
3. Run it and capture the red — exact command and output.
4. Confirm it failed for the right reason (the new expectation, not a syntax/import/collection
   error).
5. Write the implementation.
6. Re-run the same command and capture the green.
7. Return both — a task is not complete at red.

Close the file by stating why the Butler does not reproduce red: `agents/executor.md:80-88`
forbids `git stash` and makes reconstructing a pre-change tree expensive; the Butler instead
verifies the tests are in the diff and green now, and reads the captured red evidence.

Update `reference/plan-store.md` — after `:17-19` (the `Ticket:` precedent), document the `TDD:`
line: its absence means TDD was never enabled for that plan, and every command reads the line
rather than re-detecting.

Update both hand-maintained enumerations:
- `README.md:218-228` (the "How it is put together" table) — gains a `reference/testing.md` row.
- `AGENTS.md:46-47` — currently names four reference files; must name five.

## Files
- `reference/testing.md` (new)
- `reference/plan-store.md`
- `README.md`
- `AGENTS.md`

### Carried over from task 02

Task 02 deliberately left the `tdd:` schema block in `reference/config.md` **without** the
cross-reference that `split:` carries (`# See reference/tracker.md, T7/T8.`), because
`reference/testing.md` did not exist at that commit and a citation to a missing file is exactly the
dangling reference this repo's docs warn against. **Add it now**, mirroring `split:`'s form:
`# See reference/testing.md, TS1/TS2.` at the end of the `tdd:` block.

For the same reason task 02 made no mention of the `TDD:` `PLAN.md` metadata line. This task defines
it (in TS1) and documents it in `reference/plan-store.md`.

## Verification
1. `python3 -m unittest discover -s tests -v` — expect `OK`. The discriminating module is
   `tests/test_enumerations.py`. Its falsifiability control:
   `test_reference_files_are_enumerated_in_readme_and_agents_md` fails, naming `testing.md` and
   which document is missing it, if either enumeration is skipped. A green run here is evidence
   both enumerations were updated together, not that the new file merely exists.
2. `grep -n "testing.md" README.md AGENTS.md` — expect one match in each file.
3. `grep -n "^## TS1\|^## TS2" reference/testing.md` — expect both headings present.
