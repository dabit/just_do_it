status: done
# 28 — `/jdi:do`'s plan opens with a size verdict; the herd names the way back

Depends on: 27 (and the re-run log in `## UAT log (#38)`)

## Why
Two UAT runs of #38 scenario (a) (`## UAT log (#38)`, first run and *Re-run after task 27*): every herd `/jdi:do` agent (four, on Sonnet) skipped step 4's ten-line plan and never judged size, so the too-big task was built and pushed instead of continuing with `/jdi:prep`, even with `do.md` loaded. The size judgment lives only in step 5's stop list, and the plan's **Stops** field is the only thing that points at it; an agent that skips the plan skips the judgment. Separately, the herd's mode announcement (herd step 8, M5) never named `herd.mode: prep` as the way back. User decision (2026-11-16): make the plan a required gate whose first line is a size verdict, applying to standalone `/jdi:do` too, then re-run (a) and (f) with herd agents on Sonnet and on Opus.

## Description
TDD is on: test first (red on its own assertion), then the edit.

1. **`commands/do.md` step 4 becomes a gate.** Its first field, posted before any edit, is a size verdict, exactly one of: `**Size:** fits one pull request` or `**Size:** too big for one session — <why>` (pick the exact wording; keep it greppable, and use an ASCII separator if the file avoids em dashes). Say plainly: no file is edited, no branch is pushed, and no tool that changes anything runs before the plan, verdict first, is posted, in a standalone run and under a herd alike. A "too big" verdict is step 5's *too big* stop: under a herd (the clause), continue with `/jdi:prep` as step 5 already says; standalone, hand back as it already does. Keep the other fields and the 60-word limit; renumber nothing. Update anything that pins "Four fields" (e.g. `DoPlanShapeTest` in `tests/test_structural_checks.py`) deliberately, and say so.
2. **Step 5's *too big* bullet** points back at the verdict ("the step-4 size verdict"), so the two cannot drift.
3. **`commands/herd.md` step 8** quotes the announcement it must say, naming `herd.mode: prep` as the way back (in `do` mode: each agent opens and merges its own pull request, unattended and in parallel; `herd.mode: prep` stops each at a plan instead). Keep confinement (no Herdr command names).
4. **Docs:** the CHANGELOG 1.0.13 `/jdi:do` or herd bullet mentions the size verdict in one clause; README only if it describes do's plan fields.

## Files
- `commands/do.md`
- `commands/herd.md`
- `tests/test_herd_handoff.py`
- `tests/test_herd.py`
- `tests/test_structural_checks.py` (only if it pins the plan's field count)
- `CHANGELOG.md`
- `tests/test_transport_docs.py` (only if the CHANGELOG bullet is pinned there)

## Verification
1. New tests pin: the verdict as step 4's first field with both exact forms; "before any edit" (the gate wording); step 5's pointer to the step-4 verdict; herd step 8's quoted announcement containing `herd.mode: prep`. Each red on its own assertion before the edit, green after.
2. `DoPlanShapeTest` and the other do/prep/herd tests pass (changed deliberately where they pinned four fields).
3. `HerdrConfinementTest` passes; `python3 -m unittest discover -s tests -v` passes.
4. Then re-run task 26 scenarios (a) and (f) twice, herd agents on Sonnet and on Opus (Butler on the default model), recorded as a second re-run in `## UAT log (#38)`.
