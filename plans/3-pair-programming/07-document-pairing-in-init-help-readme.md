status: done
# 07 — Document pairing in init, help, and the README

Depends on: 05

## Why
Everything pairing needs to run now exists; this task is what lets a human discover it. Without it,
`/jdi:pair` and the `pair` config key are real but invisible to anyone who has not read the plan.

## Description
- **`commands/init.md`**: frontmatter gains the pairing question. A **new step 6**, renumbering the
  existing steps 6-12 to 7-13, follows init's own precedent that a question that cannot be
  meaningfully answered is not asked: **skip it entirely when `herdr` is not on `PATH`**, saying
  once that `/jdi:pair` asks inline when it is needed. Where `herdr` is present: explain there is no
  on/off switch, propose kinds that clear all three P1 layers, say the value is prose. After
  renumbering, `grep -n 'step [0-9]'` the file and fix every back-reference to a step number.
- **`commands/help.md`**: three edits, matching `docs/config-key-lifecycle.md`'s floor for a new
  key. The closing config-state line gains the pair block, phrased as what it *names* (which two
  agents) rather than on/off. The `/jdi:init` row in the command table — which already lists what
  init asks about — gains pairing alongside tracker, split pieces, TDD, plan store, and docs folder,
  since `/jdi:init` now asks about it too. A new `###` subsection explains the mode and states the
  quality claim plainly: every red is re-run by the agent that did not write it, because it cannot
  implement until it has.
- **`README.md`**: both enumerations of init's questions (the comment on the `/jdi:init` snippet,
  and the prose immediately below it) gain pairing. A new `### Pair programming` section states one
  honest cost sentence — Arisholm et al. found the overall correctness gain **not significant** for
  ~84% more effort — so `/jdi:pair` is documented as a deliberate choice for hard tasks, not a
  default. README's role counts and its "two testing operations (TS1-TS2)" row are unchanged;
  pairing is not a testing operation.

**A known, deliberate deferral, not a gap in this task**: `docs/config-key-lifecycle.md`'s own
`file:line` citations into `commands/init.md` go stale again the moment this task renumbers its
steps. That staleness was already recorded as deferred to a single dedicated pass when the TDD
plan first caused it; this task does not re-chase it, for the same reason — a citation refresh is
a different piece of work from a behaviour change, and half-doing it twice is worse than deferring
it once.

## Files
- `commands/init.md`
- `commands/help.md`
- `README.md`

## Verification
- **This task is entirely user-facing prose; nothing in the suite reads command or role body
  text.** `python3 -m unittest discover -s tests -v` — expect `Ran 17 tests ... OK`, a regression
  guard on structure (frontmatter, the enumerations from tasks 01, 03, and 05), not proof the new
  prose is correct or well-placed.
- **Under TS2 this task produces the announced skip — no testable behaviour — and the skip is the
  right answer.** Do not answer it with a fabricated test: asserting that `README.md` contains the
  word "pairing" would give a green suite and a red transcript that prove nothing while looking
  exactly like proof.
- `grep -n 'step [0-9]' commands/init.md` — expect every back-reference (e.g. "propose whatever
  step 2 found") to point at its correct, renumbered target, and no reference to a step number that
  no longer holds the content it once did.
- PR review of the `README.md`, `commands/help.md`, and `commands/init.md` diffs is the actual
  proof this step exists for — this task's own UAT coverage is limited to what group A can drive
  non-interactively (see task 09); whether the question is asked in the right words, at the right
  time, is deferred there.
