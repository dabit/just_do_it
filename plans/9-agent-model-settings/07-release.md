status: done
# 07 — Release 1.0.5

Depends on: 06

## Why
This change removes a config key (`models.deep`/`.standard`/`.fast`) and adds two new ones
(`models.<role>`, `harnesses.<kind>`), and `docs/config-key-lifecycle.md:338-340` requires a key
**removal** to be stated deliberately in the CHANGELOG rather than inferred from convention. This
task bumps the three version authorities and writes that entry.

## Description
1. **Version to `1.0.5`** in all three JSON authorities, which must match: `.claude-plugin/
   plugin.json:3`, `.codex-plugin/plugin.json:3`, `.claude-plugin/marketplace.json:10`. Patch bump,
   per the only observed convention (`docs/config-key-lifecycle.md:334-337`: `c48137c` → 1.0.1 and
   `c83963b` → 1.0.2 were both full features shipped as patches).
2. **`CHANGELOG.md` — a new `## 1.0.5` entry at the top**, newest-first, in the shape at
   `docs/config-key-lifecycle.md:342-355`: a bold one-line headline naming the user-visible outcome,
   then bullets with bold lead-ins, every key and command in backticks. The entry must carry all of:
   - **The three tier keys are gone.** Name `models.deep`, `models.standard`, and `models.fast`
     explicitly — they are no longer read.
   - **What happens to a repo with the old shape.** A `models:` block keyed by
     `deep`/`standard`/`fast` names no role, so nothing in it is read; JDI says so once and runs
     every role on the session's own model. Nothing breaks and nothing is silently reinterpreted.
   - **What happens to a repo with no `models:` block at all.** Exactly what happened before: every
     role runs on the session's own model, silently, because nothing was skipped.
   - **No file under `agents/` carries a `model:` key any more**; settings are the single place a
     role's model is named.
   - **New `harnesses:` block**, and `models.<role>.harness` naming a key in it.
   - **Degrades down, never up** — a bold lead-in bullet, matching `CHANGELOG.md:90`'s precedent.
   - **The authorization correction**, stated as a documentation fix: a user reading the old
     sentence would have believed a spawned CLI inherited this session's approval policy.
   - **Leave `CHANGELOG.md:127-128` alone.** It is a historical 1.0.0 note describing what 1.0.0
     shipped; rewriting history is not a release note.
3. **Re-verify the dogfood** written in task 01 against the final schema, rather than writing it
   here — read `.jdi/config.yml`'s `models:` block and confirm every key still parses against
   `reference/config.md`'s schema as it stands after tasks 01–06 (no key drifted during the prose
   tasks).
4. **Commit subject** `feat: Configure each role's model in settings (1.0.5)` — sentence case,
   imperative, version in parentheses (`docs/config-key-lifecycle.md:357-362`). The body opens with
   the problem in the past tense, describes the change, bullets the mechanics, and closes with
   **what was deliberately left out of scope**: `commands/status.md`, `models.butler`,
   `harnesses.<kind>.jdi_root`, `skills/run/SKILL.md`, and PR #5's `herd:` block.

No test changes in this task — nothing in the suite reads `CHANGELOG.md`'s content or the JSON
manifests' version strings beyond `tests/test_versions.py`'s existing checks (which name the
authorities, not their current value).

## Files
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `CHANGELOG.md`

## Verification
- `python3 -m unittest discover -s tests -v` — expect **unchanged from task 06: at least 52 tests,
  OK**, 0 failures, 0 errors.
- `grep -n '"version"' .claude-plugin/plugin.json .codex-plugin/plugin.json` and
  `grep -n '"version"' .claude-plugin/marketplace.json` — expect all three to read `1.0.5`, matching
  exactly.
- `head -20 CHANGELOG.md` — confirm the new `## 1.0.5` heading is above `## 1.0.4`, and that every
  bullet listed in step 2 above is present with the named keys and commands in backticks.
- `git diff HEAD -- CHANGELOG.md | grep -c '^-[^-]'` — expect `0`. This commit only inserts a new
  `## 1.0.5` section at the top; no existing line, including the historical 1.0.0 note at
  `:127-128`, should be removed or altered. A non-zero count means something pre-existing was
  touched — read the diff and confirm it was not the 1.0.0 note.
- `cat .jdi/config.yml` — confirm the `models:` block from task 01 is unchanged and still validates
  against `reference/config.md`'s schema (same seven roles, same two keys each, no `harness:` set).
