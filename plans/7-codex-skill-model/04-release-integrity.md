status: pending
# 04 — Release the adapter with synchronized metadata

Depends on: 01, 02, 03

## Why
The installed adapter is a public behavior change, and cached plugin updates only ship it when all
version authorities advance together. Contributor guidance and release notes must also stop
describing a two-manifest, Claude-only package.

## Description
Advance `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, the Codex manifest, and the
newest CHANGELOG heading together. Against the recorded `1.0.3` base the target is `1.0.4`; if main
has claimed that number before execution, select the next patch and use it everywhere. Make the
marketplace description harness-neutral.

Add a newest-first CHANGELOG entry covering Codex-native `jdi:run` discovery and invocation, safe
dispatch and installed-root resolution, all-occurrence argument replacement, capability-based Codex
delegation, and unchanged Claude/OpenCode interfaces. Update `docs/config-key-lifecycle.md` and test
comments/messages so release invariants, counts, tables, prose, checklists, and JSON-edit counts
include `.codex-plugin/plugin.json`.

**TDD:** This task has testable release invariants. If TS1 records `TDD: on`, revise/add these exact
tests before changing metadata or prose. Capture the expected failures from the old two-manifest
release guidance and Claude-only marketplace description, then complete the release edits in this
same task and commit. Version-equality controls may remain green before the bump because task 01
seeded the Codex manifest from the current release; they must remain green after all authorities
advance:

- `VersionTest.test_claude_codex_and_marketplace_versions_match`
- `VersionTest.test_the_changelog_leads_with_the_shipped_version`
- `ReleaseMetadataTest.test_marketplace_description_is_harness_neutral`
- `ReleaseDocumentationTest.test_release_mechanics_names_all_version_authorities`
- `ReleaseDocumentationTest.test_release_counts_and_checklist_include_the_codex_manifest`

If TS1 records `off` or no `TDD:` line, do not claim a red-first run; add and run the same tests
normally.

## Files
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.codex-plugin/plugin.json`
- `CHANGELOG.md`
- `docs/config-key-lifecycle.md`
- `tests/jdi_files.py`
- `tests/test_versions.py`

## Verification
1. Run `python3 -m unittest discover -s tests -p 'test_versions.py' -v`. Expected: all five listed
   tests pass; Claude, Codex, marketplace, and newest CHANGELOG versions are identical, and on the
   recorded base all report `1.0.4`.
2. Run `python3 -m unittest discover -s tests -v`. Expected: the complete suite passes with the
   released metadata and all prior adapter, guidance, documentation, and OpenCode controls intact.
3. Run `claude plugin validate .`. Expected: successful validation of the additive Codex package
   without breaking Claude's plugin package.
4. Inspect the three JSON version values and newest CHANGELOG heading. Expected: exactly one chosen
   release number appears in all four authorities; no `1.0.4` expectation is retained if execution
   had to reconcile to a later patch.
5. Inspect `docs/config-key-lifecycle.md` for the release file/count statements and checklist.
   Expected: none says a release has only two JSON edits or omits `.codex-plugin/plugin.json` from
   the version authorities.
6. Run `git diff --check`. Expected: no whitespace errors.
