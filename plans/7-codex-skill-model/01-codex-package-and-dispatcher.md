status: done
# 01 — Add the Codex package and safe dispatcher

Depends on: None

## Why
Codex needs one native, discoverable `jdi:run` skill that delegates behavior to JDI's canonical
command files without trusting user input as a path. This task also establishes structural and
OpenCode controls before documentation or release metadata claims the adapter is available.

## Description
Add `.codex-plugin/plugin.json` and the single `skills/run/SKILL.md` dispatcher described by the
selected architecture. Seed the Codex manifest with the repository's current authoritative version;
task 04 advances every release authority together. The dispatcher must implement the exact
16-command, case-sensitive allowlist; first-whitespace-token parsing; empty-input help default;
pre-path rejection with the supported list; opaque remainder handling; complete Butler and command
reads; global literal single-pass replacement of every original `$ARGUMENTS`; installed-skill-root
resolution; missing-file diagnostics; and preservation of the active sandbox and authorization
boundaries. It must run the command in the main session as Butler and use the installed delegation
contract rather than copying canonical workflow behavior. Keep the native manifest minimal and do
not add `skills/run/agents/openai.yaml`, MCP, hook, app, or asset declarations.

Extend the dependency-free test helpers and frontmatter coverage, add focused Codex package and
dispatcher contract tests, and add temporary-destination OpenCode sync regression tests. The
OpenCode controls must prove both sync modes retain their existing inventories and path behavior and
do not acquire the independent Codex package.

**TDD:** This task has testable behavior. If TS1 later records `TDD: on`, write the following exact
tests before either package file and capture the expected assertion failures caused by the missing
manifest/skill/dispatcher; then implement in this same task and commit. The OpenCode characterization
controls may already pass before implementation and are the opposite-result controls, not fabricated
red tests:

- `SkillFrontmatterTest.test_run_is_the_only_bundled_skill`
- `SkillFrontmatterTest.test_run_skill_has_valid_matching_frontmatter_and_body`
- `CodexManifestTest.test_manifest_is_native_minimal_and_portable`
- `CodexManifestTest.test_manifest_and_skill_form_jdi_run`
- `DispatcherContractTest.test_allowlist_matches_commands_in_both_directions`
- `DispatcherContractTest.test_empty_input_defaults_to_allowlisted_help`
- `DispatcherContractTest.test_matching_is_exact_and_rejects_unknown_or_path_like_tokens_before_paths`
- `DispatcherContractTest.test_remainder_is_opaque_and_preserved_verbatim`
- `DispatcherContractTest.test_every_original_argument_placeholder_is_replaced_globally_once`
- `DispatcherContractTest.test_feedback_keeps_the_multiple_placeholder_probe_non_vacuous`
- `DispatcherContractTest.test_butler_and_validated_command_are_read_completely`
- `DispatcherContractTest.test_dependencies_resolve_only_from_the_installed_skill_root`
- `DispatcherContractTest.test_dispatcher_has_no_checkout_path_or_claude_root_variable`
- `DispatcherContractTest.test_dispatch_preserves_sandbox_approval_and_authorization_boundaries`
- `OpenCodeGlobalSyncTest.test_global_sync_preserves_command_agent_inventory_and_checkout_paths`
- `OpenCodeProjectSyncTest.test_project_sync_copies_dependencies_and_uses_only_portable_paths`
- `OpenCodeSyncIsolationTest.test_codex_package_is_not_synced_into_opencode`

If TS1 records `off` or no `TDD:` line, do not claim a red-first run; still add and run the same
tests with the implementation.

## Files
- `.codex-plugin/plugin.json` (create)
- `skills/run/SKILL.md` (create)
- `tests/jdi_files.py`
- `tests/test_frontmatter.py`
- `tests/test_codex_plugin.py` (create)
- `tests/test_opencode_sync.py` (create)

## Verification
1. Run `python3 -m unittest discover -s tests -p 'test_frontmatter.py' -v`. Expected: all existing
   command/agent checks and both new skill checks pass; exactly `skills/run/SKILL.md` is found.
2. Run `python3 -m unittest discover -s tests -p 'test_codex_plugin.py' -v`. Expected: every manifest
   and dispatcher contract test above passes, including both directions of inventory equality and
   the `feedback.md` two-placeholder control.
3. Run `python3 -m unittest discover -s tests -p 'test_opencode_sync.py' -v`. Expected: global and
   project syncs succeed in temporary directories, emit all canonical commands and agents, project
   output contains copied roles/references and no checkout path, global output retains the checkout
   path, and neither output contains `.codex-plugin/` or `skills/run/`.
4. Run `python3 -m unittest discover -s tests -v`. Expected: the complete suite passes in the
   post-task state; existing Claude, config, enumeration, and version tests remain green while all
   release authorities still use the pre-release current version.
5. Run `git diff --check`. Expected: no whitespace errors.
