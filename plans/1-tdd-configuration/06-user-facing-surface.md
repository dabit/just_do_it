status: pending
# 06 — Document TDD in init, help, and README

Depends on: 02, 03

## Why
Two of the issue's acceptance criteria live here: `/jdi:init` must ask about the setting, and the
README must document it. Both are user-facing text about the same key and the same ladder, edited
across three files whose enumerations already restate each other's wording (`init.md`'s question is
listed a second time in `help.md`'s init row and a third time in both of README's enumerations), so
they land together.

## Description
**`commands/init.md`** — the frontmatter `description:` (`:2`) gains the TDD question. A new step 5
goes in after the `split.pieces` question (`:41-55`), renumbering 5→6 through 11→12 (the
back-reference at `:70` points at step 2, which does not move — grep `step [0-9]` afterward
anyway). The question follows `init.md:37-39`'s precedent — prove the capability, do not record an
aspiration: ask whether the Executor should write tests first (default `false`, and say that off
means nothing changes); on a yes, propose `test_instructions` from what step 2 already found,
saying plainly that the value is prose a later agent reads (so "run `bin/rails test` inside the
devcontainer" is a *better* answer than a bare command); then try it once, scoped small, and say
whether the suite actually ran. If it did not, say so and record the setting anyway — JDI re-checks
per plan and degrades out loud. Unlike `split.pieces`, this question is never skipped: TDD does not
depend on a tracker.

**`commands/help.md` — six edits.** The closing config-state line (`:9-12`) gains whether TDD is
on; the `/jdi:init` row (`:25`) gains TDD; a new `###` subsection after "What the pieces become"
(`:82-89`); and the rows for `/jdi:execute` (`:31`), `/jdi:next` (`:33`) and `/jdi:yolo` (`:34`) —
yolo's clause matters most: an expected red inside a TDD task is not a failure and does not stop
it.

**`README.md` — two enumerations plus a section.** `:167` (the snippet comment) and `:174` (the
prose) both list init's questions and both gain TDD; then a `### Test-first execution` section
after "What a split piece becomes" (`:179-193`).

## Files
- `commands/init.md`
- `commands/help.md`
- `README.md`

## Verification
1. `python3 -m unittest discover -s tests -v` — expect `OK`. `test_frontmatter.py` confirms
   `commands/init.md`'s edited `description:` is still well-formed and non-empty; nothing in the
   suite checks the prose content of `help.md`, `README.md`, or the rest of `init.md`'s body, so
   this run is a regression guard, not proof the question or the documentation is correct.
2. `grep -n "step [0-9]" commands/init.md` — expect every reference to read the *renumbered* step
   it now points at (the `:70` back-reference still names step 2, which did not move).
3. `grep -rln "step [0-9]" commands/ | xargs grep -l "jdi:init\|init.md"` — expect no other command
   file references `init.md`'s steps by number (the architecture doc notes none currently do; this
   confirms that claim still held after the renumber).
4. `grep -n "TDD\|tdd" commands/help.md README.md` — expect a hit at each of the six `help.md`
   sites and both README enumerations plus the new `### Test-first execution` section heading.
