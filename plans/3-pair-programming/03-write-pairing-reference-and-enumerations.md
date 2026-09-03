status: pending
# 03 — Write `reference/pairing.md`, and both reference-file enumerations

Depends on: 02

## Why
Pairing needs a single, named definition of what proving a pair can run means, what one exchange
between two agents looks like, and who drives a turn — one file both paired agents can be handed an
absolute path to and read directly, since `commands/pair.md` is written to the orchestrator and
describes work the panes themselves must never perform. Landing it now, with the two
hand-maintained lists that must name any new reference file, is what keeps it discoverable rather
than an orphaned file nothing points at.

## Description
Add `reference/pairing.md`, a new reference file using the `P` prefix (`P1`-`P3`), matching the
shape `reference/testing.md` established: a preamble naming the prefix and who consumes the file, a
who/when table, a universal-rules block, and a numbered ladder.

The preamble must say two things other reference files do not need to: that it names the external
`herdr` CLI in its body deliberately, checked and degraded from at P1 exactly as the tracker files
treat an MCP integration; and that **both paired agents read this file by absolute path**, which is
the reason the protocol lives here rather than in `commands/pair.md`.

Three operations:
- **P1 — prove the pair can run.** The Butler, once per `/jdi:pair` run, before the first exchange.
  An eight-rung degradation ladder, first rung that applies, announced, degrade down only: the
  `TDD:` line must already read `on` (never trigger TS1 from here); `HERDR_ENV` must be `1`;
  `pair.agents` empty means *ask, do not degrade* — show the exact YAML, name the path, get explicit
  confirmation, append only the `pair:` block; the three-layer kind check (binary-supported,
  installed-and-current, resolvable on `PATH`), named against the environment it was measured in;
  bring the panes up (`pane layout`, `pane split --no-focus`, `agent start`), never persisting an
  agent name; record which lifecycle source (`agent explain --verbose`) each pane's state comes
  from; designate the shared report directory, absolute, outside the working tree, asking before
  reusing an earlier run's files; write the `- Pair:` line, once, alongside `- Started:`.
- **P2 — the exchange.** The two paired agents, every turn once P1 said `on`. A turn is
  reproduce-red, make-it-pass, refactor, write-the-next-failing-test, hand off; the completion unit
  is the **exchange**, not the turn. The test list is derived from the plan's Verification clauses
  and Testing Strategy items, never invented. The five-part handoff (failing test; red transcript;
  test-list delta; parked-notes ledger or "nothing parked"; a read receipt naming one concrete
  thing, with the first-turn exception stated) — all five or it is returned. Compulsory
  re-reproduction before implementing. Disagreement is expressed as a test or a stated rejection,
  never silent workaround or edit. Turn-back cap: two consecutive stop the run. Single writer: only
  the turn-holder touches files or the index.
- **P3 — drive a turn.** The Butler, every turn: never prompt an agent not observed at `idle`,
  `done` or `blocked`; treat `idle`/`done` as one condition; `unknown` is never "turn over"; prompts
  carry resolved absolute paths; the report file is the turn-over signal, Herdr state is only the
  wake-up; a structural (not substantive) check on the five headings before relaying; `agent_blocked`
  stops and asks the user, never answers the dialog; escalate on two turn-backs, six exchanges, or a
  blocked pane, handing over both positions without breaking the tie.

Then, in the same task: a `reference/pairing.md` row in `README.md`'s "How it is put together"
table, and a mention added to `AGENTS.md`'s "**Reference files.**" paragraph. `README.md`'s "two
testing operations (TS1-TS2)" row stays unchanged — pairing is not a third testing operation.

## Files
- `reference/pairing.md` (new)
- `README.md`
- `AGENTS.md`

## Verification
- `python3 -m unittest discover -s tests -v` — expect `Ran 17 tests ... OK`. No new test: the
  existing `ReferenceFileEnumerationTest` in `tests/test_enumerations.py` already checks both
  directions (every `reference/*.md` file is named in both documents, and neither document names a
  file that does not exist), so it fails naming `reference/pairing.md` if either enumeration is
  skipped, and passes once both are done.
- If `reference/pairing.md` is created alone, before the `README.md` and `AGENTS.md` edits: expect
  both of `ReferenceFileEnumerationTest`'s subTests (README, AGENTS.md) to fail, each naming
  `reference/pairing.md` as missing from that document's enumeration. Once both documents name it,
  the suite returns to `Ran 17 tests ... OK`.
