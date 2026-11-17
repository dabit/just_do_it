status: done
# 27 — App handoff delivers a real slash command (F-h)

Depends on: 26 (its failed run and `## UAT log (#38)`)

## Why
UAT #38 scenario (a) failed (`## UAT log (#38)`, F-e to F-h). On the Herdr app the herd's Butler runs inside an app terminal, and `hc send` from there wraps the text as `<hc from="t1">/jdi:do …</hc>` (`hc --skill`: "Reports arrive tagged"). Claude does not treat a tagged message as a slash command, so `/jdi:do` (and in #37, `/jdi:prep`) was probably never loaded: no ten-line plan (F-g), no size check and fallback (F-e), work on the scratch branch (F-f). The TUI's `herdr agent prompt` delivered a real slash command (scenario (g)). hc's global `notes = false` would drop the tags, but that is the user's herdr-core config: JDI changes no Herdr setting (universal rule 2) and never sets session or home variables.

## Description
TDD is on: test first (red on its own assertion), then the fix.

1. **Probe** through the #38 guard (throwaway session and SHORT home; nonexistent `HERDR_SOCKET_PATH`; GitHub cut off; pre-trust only the scratch repo; cheap `--model haiku` agents; never `hc keys`), from inside a throwaway app terminal acting as the Butler, against an idle Claude agent started like a herd agent. Record as R7 under `## Probe log (#37)`:
   - (i) `hc send <t> '/jdi:help' --if idle` from the Butler terminal: is it tagged, and does the agent run it as a slash command?
   - (ii) the same with the Butler's terminal identity dropped for that one command only (`env -u HC_TERMINAL_ID hc send …`): untagged? still reaches the throwaway core (not another session)? `--if idle` still enforced (refused for `done`/no status)?
   - (iii) the work given at launch instead: the agent's argv carries the invocation as its first prompt (e.g. `claude '<invocation>'` via `space.new --argv`): run as a slash command? what happens when a trust dialog is up first (held until answered, or lost)?
   - Any other untagged path the `hc`/`herdr-app` help documents.
2. **Pick the smallest path that delivers a real slash command, keeps amended D6 (never type into a dialog: idle-only, `--if idle`) and changes no Herdr setting.** Prefer (ii) if it holds; else (iii) for kinds whose CLI takes a first prompt, with a per-kind rule. State the evidence.
3. **Fix `reference/herdr.md`:** H9 on the app's handoff, and H5 on the app's first prompt and H6's answer if they have the same problem (they also send from the Butler's terminal: check whether a tagged prompt still reaches a delegated worker correctly, or fix them too). Keep every pinned phrase unless a test is deliberately changed.
4. **Note** in the UAT log that #37's UAT (a) "handoff by `hc send`" only showed the text was sent, not that the command loaded.

## Files
- `reference/herdr.md`
- `tests/test_herd.py` and/or `tests/test_herdr_operations.py` (whichever pins the changed sections)
- `docs/herdr-surfaces-architecture.md` (the H9 hand-off row and the R-notes, if the chosen path changes them)
- `tests/test_herdr_surfaces_doc.py` (only if the doc row's pinned text changes)
- `plans/36-herdr-app-support/PLAN.md` (R7 under `## Probe log (#37)` only)

## Verification
1. New test(s) pin the chosen delivery rule in the changed section(s); red on its own assertion before the edit, green after.
2. Existing H5/H6/H9 app tests still pass (`--if idle`, "never `hc keys`", "never `hc send --force`").
3. `python3 -m unittest discover -s tests -v` passes.
4. Probe cleanup verified (user's `hc ls --json` count, `~/.local/state/herdr-core/` = default, jute, personal, vault, `herdr session list`, real `git worktree list`, `~/.claude.json` project keys unchanged; no throwaway home or scratch).
5. Then task 26 is re-run for scenario (a) (and (f)'s entry-3 plan question if (a) now reaches prep).
