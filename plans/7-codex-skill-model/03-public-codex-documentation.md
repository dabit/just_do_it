status: pending
# 03 — Document the supported Codex interface

Depends on: 01

## Why
Users currently receive incorrect Codex discovery, invocation, and delegation instructions. The
README must teach the one supported `$jdi:run` interface without rewriting the still-valid Claude
and OpenCode interfaces.

## Description
Update the harness table, Codex installation/verification section, update guidance, usage examples,
delegation explanation, release-version explanation, and repository structure in `README.md`.
Retain the existing Codex marketplace/plugin install commands and machine-wide cached-snapshot
semantics, require install/refresh followed by a fresh session, and teach `/skills` plus `$`
completion of `jdi:run`.

State that `commands/*.md` remain canonical files rather than arbitrary Codex custom slash commands.
Show `$jdi:run`, `$jdi:run help`, `$jdi:run prep 4`, `$jdi:run yolo`, and `$jdi:run pr`; do not
advertise bare `$jdi`, one skill per command, or `/` command discovery for Codex. Preserve Claude
`/jdi:help`, OpenCode `/jdi-help`, and their command examples. Replace the blanket Codex no-subagent
claim with capability-based delegation and its announced fallback, and list both new Codex package
paths in the structure table.

**TDD:** This task has structurally testable documentation behavior. If TS1 records `TDD: on`, add
these exact tests to `tests/test_codex_plugin.py` before editing `README.md`, capture their expected
assertion failures against the stale Codex prose, then update the README in this same task and
commit:

- `ReadmeCodexDocumentationTest.test_harness_table_uses_jdi_run_and_preserves_other_harnesses`
- `ReadmeCodexDocumentationTest.test_install_requires_a_fresh_session_and_skill_discovery`
- `ReadmeCodexDocumentationTest.test_examples_cover_default_help_prep_yolo_and_pr`
- `ReadmeCodexDocumentationTest.test_codex_does_not_claim_bare_jdi_or_custom_slash_commands`
- `ReadmeCodexDocumentationTest.test_scope_snapshot_and_capability_delegation_are_accurate`
- `ReadmeCodexDocumentationTest.test_structure_lists_manifest_and_run_skill`
- `ReadmeCodexDocumentationTest.test_release_guidance_names_every_version_authority`

If TS1 records `off` or no `TDD:` line, do not claim a red-first run; add and run the same tests
normally.

## Files
- `README.md`
- `tests/test_codex_plugin.py`

## Verification
1. Run `python3 -m unittest discover -s tests -p 'test_codex_plugin.py' -v`. Expected: all seven
   README tests pass alongside the package tests, with positive checks for `$jdi:run`, `/skills`,
   `$` completion, fresh sessions, and preserved Claude/OpenCode examples, plus negative checks for
   unsupported Codex claims.
2. Run `python3 -m unittest discover -s tests -p 'test_enumerations.py' -v`. Expected: README's
   reference rows and command/role counts remain accurate after adding the two Codex structure rows.
3. Manually read the rendered `## Install`, `## Use it`, and `## How it is put together` sections.
   Expected: each harness's syntax is unambiguous, all five required Codex examples appear, and no
   global rewrite has changed Claude `/jdi:*` examples.
4. Run `python3 -m unittest discover -s tests -v`. Expected: the complete suite passes.
5. Run `git diff --check`. Expected: no whitespace errors.
