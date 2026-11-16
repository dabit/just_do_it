status: done
# 09 — Release 1.0.11: version bump and CHANGELOG

Depends on: 01, 02, 03, 04, 05, 06, 07, 08

## Why
`claude plugin update` compares versions, not content, so the change ships only with a version bump. The CHANGELOG has to tell users already inside the Herdr app that `auto` and `herdr` now act there instead of staying silent, and how to keep the old behaviour. Rests on: P12, D1, D-wt, D8.

## Description
Planner's Task 9. It comes after Tasks 01–08, as the Planner ordered, so the release note describes
what landed, including any amendment the probe gate (Task 02) made.

**Version.** Set the version to **1.0.11** in all three JSON authorities (P12):
- `.claude-plugin/plugin.json`, the `"version"` field (line 3);
- `.codex-plugin/plugin.json`, the `"version"` field (line 3);
- `.claude-plugin/marketplace.json`, the plugin entry's `"version"` (line 10).

**`CHANGELOG.md`.** Add a new top entry `## 1.0.11`, above `## 1.0.10`, with the headline
**"JDI drives the Herdr app as well as the Herdr TUI."** in bold, matching 1.0.10's style.

Bullets:
- `herdr.surface` (`auto | app | tui`) and its default `auto`. With no key, nothing changes for TUI
  users. On and off stays `delegation.transport`.
- **A bold bullet for users already in the Herdr app** (risk R4). Under `delegation.transport: auto`
  or `herdr`, roles on another CLI now get app panes, and `/jdi:herd` now works instead of stopping
  at its first check. To keep the old behaviour, set `delegation.transport: native` or
  `herdr.surface: tui`.
- App worktrees follow the app dialog's layout, `<worktrees.directory>/<repo>/<name>`, so herd
  spaces nest under their repository like dialog-made ones.
- JDI never sets session or home variables. It works with or without a named session.
- Codex users on the app add `--no-daemon` to `harnesses.codex.args`. JDI notes once when it is
  missing.

Reflect any probe-log amendment that changes user-visible behaviour, for example R2's `tab.new`
fallback for single workers.

**Commit message**, which the Butler uses when marking this task done:
`feat: Support the Herdr app alongside the TUI (1.0.11)`. The body names what was deliberately
left out:
- `/jdi:status`;
- `hc run` workers;
- Windows verification;
- a shipped worktree script.

**R9.** `origin/main` has its own 1.0.10–1.0.12. Whoever rebases #31 and this PR must renumber both.
Say so in your report; it is not this task's to fix.

**TDD: there is no red-first step for this task.** The existing `VersionTest` already passes, and
stays passing as long as the three JSON files and the CHANGELOG move together. The tests-bite check
below stands in for it.

## Files
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `CHANGELOG.md`

## Verification
1. **The test bites.** Bump only `.claude-plugin/plugin.json` to 1.0.11, then run
   `python3 -m unittest discover -s tests -p 'test_versions.py' -v`. Expected: two failures,
   `test_claude_codex_and_marketplace_versions_match` and
   `test_the_changelog_leads_with_the_shipped_version`.
2. **Green.** Bump the other two JSON files and add the CHANGELOG entry, then run the same command.
   Expected: every test passes.
3. **One version everywhere.** Run
   `grep -n '"version"' .claude-plugin/plugin.json .codex-plugin/plugin.json .claude-plugin/marketplace.json && sed -n 3p CHANGELOG.md`.
   Expected: three `"version": "1.0.11"` lines, and `## 1.0.11`.
4. **Full suite.** Run `python3 -m unittest discover -s tests -v`. Expected: every test passes. Every
   other task is done by now, so any failure is real and blocks this task.
