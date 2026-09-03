status: done
# 04 — Resolve the three `reference/testing.md` collisions

Depends on: 03

## Why
`reference/testing.md`'s TS2 discipline was written for one agent working alone, and read literally
it now disagrees with P2: TS2 says a task is not complete at red, and a paired turn legitimately
ends at a captured red because that red *is* the handoff. Left unresolved, the two files describe
two different truths about the same repository, and the single-agent path must not be the one that
changes to make room for the new one.

## Description
Edit `reference/testing.md` only, and make every edit additive and scoped to P2, so the
single-agent reading is unchanged:

- **TS2 rule 7** ("a task is not complete at red") stays verbatim. Add a scoped paragraph: under
  P2 the completion unit is the exchange, and a paired turn legitimately ends at a captured red
  because that red is the handoff. Nobody stops at red; what changes is *who* finishes it.
- **TS2 step 1** (one test per task) stays. Add that under P2 the granularity is a list, derived
  from the plan's Verification clauses and Testing Strategy items — the same two named sources P2
  already uses — with the tracing rule: an item added mid-task without tracing to one of those
  becomes a `next-test` parked note. The plan stays the authority; the list refines it.
- **TS2 steps 3-4** gain a note that under P2 the compulsory-reproduction step happens twice, and
  the doubling is the anti-rubber-stamp mechanism. The closing "the Butler does not reproduce red"
  paragraph gains one sentence: a pair does it for free, because the receiver must run the test
  before it may implement.

## Files
- `reference/testing.md`

## Verification
- **Nothing in this repository's test suite observes command or role body prose, and this task is
  entirely prose — the suite run below is a regression guard on structure, not evidence the added
  text is correct.** `python3 -m unittest discover -s tests -v` — expect `Ran 17 tests ... OK`,
  unchanged from task 03, because no enumeration or schema check reads inside `testing.md`'s body.
- **Under TS2 this task produces the announced skip — no testable behaviour — and the skip is the
  right answer.** Do not answer it with a fabricated test: asserting that `reference/testing.md`
  contains the word "exchange" would give a green suite and a red transcript that prove nothing
  while looking exactly like proof, which is the worst outcome `reference/testing.md` itself names.
- `git diff -- reference/testing.md` — expect every line of the three quoted originals (TS2 rule 7,
  step 1, and steps 3-4's closing paragraph) present byte-for-byte, with only new paragraphs and
  sentences added around them. A diff that removes or reorders any of the three original passages
  is wrong regardless of what the suite says.
