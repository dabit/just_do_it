status: done
# 08 — Release 1.0.4, and dogfood

Depends on: 06, 07

## Why
This is the shipping step: the two version files, the changelog entry, and the commit that make
the previous seven tasks reach an installed copy. Dogfooding pairing in this repo's own config is
what exercises the ladder's real behaviour on a real machine, rather than leaving it only ever
described in prose.

## Description
- Bump `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` to **1.0.4**, matching.
- Add a `## 1.0.4` entry to `CHANGELOG.md`, newest-first, following `docs/config-key-lifecycle.md`'s
  shape: a bold one-line headline stating the user-visible outcome; the **first bullet says what
  happens to a repo that does not set the `pair` key** — nothing, and `/jdi:pair` is never invoked
  unless a user types it, so `/jdi:yolo` never pairs; every key, mode, and command named in
  backticks; a closing statement of what was deliberately left out of scope
  (`commands/prep.md`'s config-block list, `commands/status.md`, `agents/planner.md`,
  `bin/sync-opencode.sh`, `CHANGELOG.md`'s own 1.0.0 entry — none of these were touched, and each
  has a stated reason in `PLAN.md`'s Decisions).
- Commit subject: `feat: Pair two agents through a plan (1.0.4)`.
- **Dogfood**: add a `pair:` block to this repository's own `.jdi/config.yml` (already tracked in
  this repo), naming two agent kinds that clear all three of `reference/pairing.md`'s P1 layers on
  this machine. Note in the same edit that this is a claim about one machine, and a contributor
  lacking one of the named kinds gets P1 rung 4's announced degradation — designed behaviour, not a
  defect, and the path this dogfooding most needs to exercise.

## Files
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `CHANGELOG.md`
- `.jdi/config.yml`

## Verification
- `python3 -m unittest discover -s tests -v` — expect `Ran 17 tests ... OK`.
- Bump one version file alone (before the other, and before `CHANGELOG.md`) — expect
  `VersionTest.test_plugin_and_marketplace_versions_match` to fail, naming the two mismatched
  version strings, and/or `test_the_changelog_leads_with_the_shipped_version` to fail naming
  `CHANGELOG.md`'s still-old `## 1.0.3` heading against the new plugin version. Once all three
  (`plugin.json`, `marketplace.json`, `CHANGELOG.md`) agree — expect `Ran 17 tests ... OK`.
- `git diff -- .claude-plugin/plugin.json .claude-plugin/marketplace.json` — expect both show
  `1.0.3` → `1.0.4`, nothing else changed.
