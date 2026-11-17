status: done
# 29 — Size gate judged by behaviour; model note for `do`-mode herds

Depends on: 28 (and the two re-runs in `## UAT log (#38)`)

## Why
Re-runs after task 28 (`## UAT log (#38)`): with herd agents on Opus the too-big task was judged before any edit and fell back to `/jdi:prep`, but only in the agent's thinking; no agent on either model posted the `**Size:**` verdict in chat. Sonnet agents built the too-big task in all three runs and once worked on the herd's scratch branch. The herd's Butler never posted step 8's quoted announcement before the start; its final report names the mode and `herd.mode: prep`.

User decisions (2026-11-16):
- **Behaviour is enough.** Passing is: a too-big task falls back to `/jdi:prep` before any edit, a small one ships. `/jdi:do`'s gate becomes "decide the size before any edit"; posting the verdict in chat is no longer required.
- **Document a model recommendation.** `do`-mode herds need a model that follows `/jdi:do`'s gate: Opus observed working, Sonnet observed skipping it; `herd.mode: prep` for cheaper models. No enforcement.
- **Announcement: keep step 8 as is, accept report-only.** Record the gap; no change to `commands/herd.md` step 8.

## Description
TDD is on: change the pinning tests deliberately first (say which and why), see them red against the current text, then edit.

1. **`commands/do.md` step 4:** the gate is the decision, not the post: the size is decided before any edit (still before anything is changed beyond step 2's branch and the issue move); the verdict is the plan's first field when the plan is shown, but nothing requires posting it before acting. Keep the two verdict forms, step 5's pointer to "the step-4 size verdict", and the herd fallback. Reword the title ("posted before any edit") and the **This plan is a gate.** paragraph accordingly.
2. **Model note** (no enforcement, no model-name logic): one sentence each in `reference/config.md`'s `herd.mode` Notes bullet, the README herd paragraph, and the CHANGELOG 1.0.13 `herd.mode` bullet: `do` mode relies on each agent judging size before it builds; in testing, Opus herd agents did and Sonnet agents built an oversized task instead, so pick the herd agents' model accordingly, or use `herd.mode: prep`. Keep confinement (no Herdr command names in `reference/config.md`).

## Files
- `commands/do.md`
- `tests/test_herd_handoff.py`
- `tests/test_structural_checks.py` (only if it pins the "posted" wording)
- `reference/config.md`
- `tests/test_config_schema.py` (only if the Notes bullet's pinned text changes)
- `README.md`
- `CHANGELOG.md`
- `tests/test_transport_docs.py` (only if a pinned fragment changes)

## Verification
1. Changed/new tests pin: step 4 says the size is decided before any edit, and no longer requires posting before acting; the model note appears in config Notes, README herd paragraph and CHANGELOG bullet. Red before the edit, green after.
2. `python3 -m unittest discover -s tests -v` passes; `HerdrConfinementTest` passes.
3. No UAT re-run: the Opus re-run already shows the behaviour this wording accepts.
