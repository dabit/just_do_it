status: pending
# 03 — The frontmatter comes out

Depends on: 02

The functionally load-bearing dependency for this task is **task 01, not task 02**: task 01 wrote
the per-role `models:` block into `.jdi/config.yml`, reproducing exactly what each role's
frontmatter gives it today. This task cannot land before that, or JDI regresses on itself between
these two commits — every deep role in this repo would silently drop to whatever model the session
happens to already be running, invisibly, on this branch. (The immediate predecessor in the task
sequence is 02, which this task also depends on for the sequencing chain, but the correctness
argument is with 01.)

## Why
Two places currently name a role's model and they disagree about which one is in charge. This task
removes the frontmatter side, which is what actually reached Claude Code today, so that
`.jdi/config.yml` becomes the only place a role's model is named — the acceptance criterion the
whole change is named for.

## Description
1. **Delete the seven `model:` frontmatter lines**: `agents/researcher.md:18`,
   `agents/planner.md:18`, `agents/executor.md:17`, `agents/feedbacker.md:18`,
   `agents/splitter.md:17`, `agents/synthesizer.md:16`, `agents/pr-writer.md:17`. Change nothing
   else in these files — `tools:` and every other frontmatter key stay. After task 01, every one of
   these models comes from `.jdi/config.yml`'s dogfood block, so this is behaviour-neutral in this
   repo under Claude Code.
2. **`roles/butler.md:3`** — `**Tier: fast — but the Butler is never spawned.**` →
   `**The Butler is never spawned.**` The Butler has no model key and never will (there is no
   `models.butler`), and the vocabulary guard forbids the word "tier".
3. **`bin/sync-opencode.sh:78-81`** — reword the comment only. It currently reads "JDI's tiers live
   in prose and in .jdi/config.yml, not in this frontmatter", naming a concept that no longer
   exists. **Keep `AGENT_DROP = {"model", "tools"}` unchanged** — with no `model:` left to strip
   this is a no-op, but it stays as a guard against a role file reacquiring the key, and removing
   it would be an unrelated behaviour change to the adapter. New comment: models are resolved from
   `.jdi/config.yml` by the Butler and never appear in a role file's frontmatter; `model` stays in
   the drop set as a guard.

**Tests, same commit.**
- **T-D**, in `tests/test_frontmatter.py`: reusing `jdi_files.split_frontmatter` exactly as the
  existing `description:` check does (`:34-84`), assert for each `agents/*.md` file that no
  frontmatter line starts with `model:`. Red today (all seven carry it), green after step 1. Note
  in the test's failure message the asymmetry worth stating: nothing in the suite ever asserted
  `model:` was *present*, which is exactly why the two-place arrangement drifted for four releases.
- **T-E**, in `tests/test_opencode_sync.py`: assert no file under the synced `agent/` directory
  contains a frontmatter `model:` line. This is a **characterization test, not red-first** — it
  passes today because `bin/sync-opencode.sh:81`'s `AGENT_DROP` already strips `model` before
  writing. Add it anyway: it pins the drop as *intentional* once the source files no longer carry
  the key, so a later contributor tidying `AGENT_DROP` down to `{"tools"}` gets a failing test that
  explains why `model` stays as a guard.

## Files
- `agents/researcher.md`, `agents/planner.md`, `agents/executor.md`, `agents/feedbacker.md`,
  `agents/splitter.md`, `agents/synthesizer.md`, `agents/pr-writer.md`
- `roles/butler.md`
- `bin/sync-opencode.sh`
- `tests/test_frontmatter.py`
- `tests/test_opencode_sync.py`

## Verification
- `python3 -m unittest discover -s tests -v` — expect **at least 51 tests, OK**, 0 failures, 0
  errors (49 from task 02, plus T-D and T-E). If the count is lower, one of the two new tests did
  not get added; if it errors instead of failing red-then-green, check `split_frontmatter` usage.
- `grep -rn "^model:" agents/*.md` — expect **no output**. Control: `grep -rn "^tools:" agents/*.md`
  — expect **seven hits**, one per file, proving the deletion was scoped to `model:` only and did
  not touch adjacent frontmatter keys.
- `grep -ciE '\btiers?\b' roles/butler.md` — expect `0`. (Case-insensitive matters: the line being
  deleted is `**Tier: fast …**`, capital T — a case-sensitive `grep -c tier` would read `0` even
  before the edit and tell you nothing.)
- `grep -n "AGENT_DROP" bin/sync-opencode.sh` — confirm the set is still exactly
  `{"model", "tools"}` and the surrounding comment no longer says "tiers".
