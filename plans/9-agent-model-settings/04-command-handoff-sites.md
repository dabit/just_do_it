status: done
# 04 — The command hand-off sites

Depends on: 03

**Kept as one task, not split**, despite being twenty-five separate one-line edits across eleven
files: every edit is the same mechanical operation (delete a tier clause, touch nothing else), one
grep verifies all of them at once, and there is no independent review, revert, or test boundary
between "half the command files" and "all of them" — splitting it would produce busywork commits
with no added checkpoint value. This is the batch the plan itself names as the one plausible split
candidate; it is kept whole because the risk it carries (an inconsistent half-edit) is exactly what
the single verifying grep catches in one place, not what smaller commits would catch better.

## Why
Eleven command files still say "Delegates to: X (tier)" and "at the **X** tier" in their hand-off
sentences, describing a lookup that task 02 already recast away from tier vocabulary. Left as is,
these sites would keep pointing a reader at a concept `reference/delegation.md` no longer defines.

## Description
The lowest-risk form is **pure deletion of the tier clause**, not rewording — fewer decisions, fewer
ways to be inconsistent across files, and `reference/delegation.md` is already named at almost every
site.

1. **Eleven "Delegates to" header lines** — drop the parenthesised tier: `commands/research.md:8`,
   `reresearch.md:8`, `feedback.md:8`, `prep.md:9`, `execute.md:8`, `yolo.md:8`, `next.md:8`,
   `split.md:8`, `replan.md:8`, `plan.md:8`, `pr.md:9`. E.g. `**Delegates to: Planner** (deep).` →
   `**Delegates to: Planner**.`; `commands/prep.md:9` → `**Delegates to: Researcher**, **Planner**,
   **Splitter**.`
2. **Fourteen "at the **X** tier" hand-off sentences** — delete the clause and nothing else:
   `commands/research.md:34,57`, `feedback.md:31`, `prep.md:104,120,136,156`, `execute.md:61`,
   `yolo.md:77`, `next.md:53`, `split.md:57`, `plan.md:64`, `pr.md:43,81`. Read each sentence after
   the deletion — three need a word adjusted to stay grammatical:
   - `research.md:57` — "again at the **deep** tier to explore" → "again to explore"
   - `prep.md:156` — "delegate to the **Splitter** at the **standard** tier. State" → "delegate to
     the **Splitter**. State"
   - `prep.md:120` — same shape as `:156`, adjust the same way.
3. **`commands/prep.md:23`** — the literal config-block list: `Everything below refers to
   \`tracker\`, \`split\`, \`plans\`, \`docs\`, and \`consumers\` from it.` → add `models` and
   `harnesses`. `/jdi:prep` delegates to three roles (steps 8, 13, 16), so it genuinely reads both
   blocks — the opposite call from `tdd`, which was deliberately omitted there because prep never
   resolves that key.
4. **`commands/status.md` — deliberately excluded.** It loads the config and never names a key
   (`:8` says "No delegation."). Per `docs/config-key-lifecycle.md:140-142`, a command joins the set
   when the key changes what it *does*, not when it merely reads the config. Make no edit to this
   file; state the exclusion and its reason in the commit body.

No test changes in this task — nothing in the suite reads command body prose (confirmed in the
Testing Strategy: `tests/test_enumerations.py` reads README and `reference/delegation.md`, not
`commands/*.md`).

## Files
- `commands/research.md`, `reresearch.md`, `feedback.md`, `prep.md`, `execute.md`, `yolo.md`,
  `next.md`, `split.md`, `replan.md`, `plan.md`, `pr.md`

## Verification
- `python3 -m unittest discover -s tests -v` — expect **unchanged from task 03: at least 51 tests,
  OK**, 0 failures, 0 errors. This task touches no test file and no file the suite reads; the count
  should not move at all. If it does, an edit landed somewhere the suite parses.
- `grep -riE '\btiers?\b' commands/research.md commands/reresearch.md commands/feedback.md commands/prep.md commands/execute.md commands/yolo.md commands/next.md commands/split.md commands/replan.md commands/plan.md commands/pr.md`
  — expect **no output**, naming the eleven files by hand rather than globbing `commands/*.md`.
  `commands/help.md:2,115` and `commands/init.md:13,102,106` still say "tier" at this point — they
  are task 05's sites, not this task's — so a bare `grep -riE '\btiers?\b' commands/*.md` would show
  hits and look like a failure here. `commands/status.md` should show no hits either way (it never
  had any). Expect the plan's named false positives to be untouched and irrelevant here: "data
  models" at `commands/research.md:58` does not match `\btiers?\b`.
- Control, confirming the residual sites are exactly where expected and not yet fixed:
  `grep -riE '\btiers?\b' commands/help.md commands/init.md` — expect hits, closed in task 05.
- `grep -n "Delegates to" commands/*.md` — read each of the eleven lines and confirm none still has
  a trailing parenthesised tier.
- Read `commands/research.md:57`, `commands/prep.md:120`, `commands/prep.md:156` specifically —
  confirm each reads as a grammatical sentence after the deletion, not a dangling clause.
