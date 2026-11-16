status: done
# 11 — UAT follow-ups: note wording, wave tab, worktree trust, `status_reported`, quoting

Depends on: 10

## Why
The UAT (task 10, `## UAT log` in PLAN.md) found five places where the docs and the observed app disagree, or where the wording let a Butler go off-pattern. The user chose to fix all five before the PR (2026-11-16): F2, F3, F4, F5 and F7. F1 (a Sonnet Butler skipping Herdr for `opencode run`) is model adherence, not a doc error, and F6 is harmless; both stay recorded in the UAT log only.

## Description
Read `## UAT log` in PLAN.md first (findings F1–F7 and scenarios (e), (g), (c), (c4), (b)). TDD is on: for each fix, pin the new wording in a test first, watch it fail on its own assertion, then edit the docs.

1. **F5: the step-0 note and "silent".** Scenario (e): with `herdr.surface: tui` pinned inside the app under `delegation.transport: auto`, the Butler fell back to `native` correctly but narrated H1 and mentioned Herdr in its summary. Scenarios (e)/(g) under `herdr`: the one-time note did not follow the `## When a step fails` pattern or name the surface.
   - In `reference/herdr.md` (H1's shared intro and/or `### Choosing the surface`): state that "silent" under `auto` means the run never mentions Herdr or H1 at all, **summaries included**, and that a pinned surface whose checks fail under `auto` is silent too.
   - Quote the exact one-time note shape from `## When a step fails` (it already names "Herdr (<surface>)") where H1 tells the Butler to announce, so the Butler copies it instead of paraphrasing.
   - Only touch the nine step-0 command sites if the fix cannot live in `reference/herdr.md`; if you do, keep the wording identical at every site and keep `tests/test_step_zero_transport.py` green.
2. **F3: the app's wave tab closes itself.** Observed in (b): once a wave tab's last pane closes, the tab closes with it. Fix the text in `### Waves on the app` / `### H8 on the app` that says the tab "does not close itself": H8 still closes it, and the "no tab" error JSON (A7 shape, stdout, exit 1) is the expected, harmless result when it is already gone. Mirror the fix in `docs/herdr-surfaces-architecture.md`.
3. **F4: worktree trust is inherited.** Observed in (c) and (c4): a linked worktree takes Claude's folder trust from its main checkout, so no trust dialog appeared in (c); it appeared only when the main checkout was untrusted (c4). Fix `### H9 on the app` (and anything in `commands/herd.md`, `docs/herdr-surfaces-architecture.md`, `CHANGELOG.md` 1.0.11) that says a new worktree *always* shows the dialog: it *can* (an untrusted main checkout, or a CLI that doesn't inherit trust), and the amended D7 handling (blocked at startup, nothing typed, space left open) stays as is.
4. **F2: `status_reported`.** The app manifest's `status_reported` is written in H4 step 4, before the readiness wait, so it is always `false`. Redefine it in `### H3 on the app` / `### H4 on the app` (and the architecture doc) so it is meaningful: record it when the readiness wait returns (update the manifest after step 5), or drop the field. Pick the smaller correct change and say which in your report.
5. **F7: quoting the herd space name.** In (c) the space name was double-quoted. `### H9 on the app` must make the single-quote rule hard to miss: add a literal example line using single quotes, and say why (A17: `'`, `$` and backticks arrive literally only when single-quoted; a `'` inside becomes `'\''`).

## Files
- `reference/herdr.md`
- `tests/test_herdr_operations.py`
- `tests/test_herd.py`
- `docs/herdr-surfaces-architecture.md`
- `tests/test_herdr_surfaces_doc.py` (only if the doc fix needs pinning)
- `CHANGELOG.md` (1.0.11 entry, F4 wording only)
- `commands/herd.md` (only if it repeats the "always a dialog" claim)
- `commands/{prep,research,plan,split,feedback,pr,execute,next,yolo}.md` and `tests/test_step_zero_transport.py` (only if F5 cannot live in `reference/herdr.md`)

## Verification
1. Each new test fails on its own assertion before the doc edit and passes after (TS2 red and green).
2. `python3 -m unittest discover -s tests -v` passes.
3. `grep -n "does not close itself" reference/herdr.md docs/herdr-surfaces-architecture.md` finds nothing.
4. `HerdrConfinementTest` passes; `reference/herdr.md` has no em dash and no personal values.
5. Re-walking (e) and (g) is deferred with (u1)/(u2) to PR review (user decision 2026-11-16); say so in the report.
