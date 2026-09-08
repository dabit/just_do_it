status: pending
# 02 — Make delegation and manual substitution guidance capability-based

Depends on: 01

## Why
Codex can use subagents but does not automatically register JDI's Claude agent files, so the shared
guidance must describe what to do based on observed capability. Manual users also need the same
multi-placeholder substitution contract as the new dispatcher.

## Description
Update `reference/delegation.md` to name Codex among first-class subagent examples without switching
to harness-name detection. Specify that when no matching JDI role is registered, a suitable generic
subagent receives the installed `agents/<role>.md` instructions and exactly the role's declared
inputs. Preserve registered-role preference, second non-interactive session, announced inline
adoption, model-tier behavior, and sandbox/approval/authorization boundaries.

Correct `AGENTS.md` so manual invocation permits zero, one, or multiple `$ARGUMENTS` occurrences and
replaces every original occurrence globally, literally, and in one pass. Preserve the existing
manual command inventory and OpenCode adapter portability guidance.

**TDD:** This task has structurally testable prose contracts. If TS1 records `TDD: on`, add these
exact tests to `tests/test_codex_plugin.py` first, run them to capture assertion failures against the
old guidance, then make the prose changes in this same task and commit:

- `DelegationGuidanceTest.test_codex_is_a_first_class_subagent_example`
- `DelegationGuidanceTest.test_unregistered_role_uses_installed_definition_and_declared_inputs`
- `DelegationGuidanceTest.test_fallback_order_and_authorization_boundaries_are_preserved`
- `ManualInvocationGuidanceTest.test_arguments_replace_zero_one_or_many_original_occurrences_once`
- `ManualInvocationGuidanceTest.test_opencode_adapter_portability_rules_are_preserved`

If TS1 records `off` or no `TDD:` line, do not claim a red-first run; add and run the same tests
normally.

## Files
- `reference/delegation.md`
- `AGENTS.md`
- `tests/test_codex_plugin.py`

## Verification
1. Run `python3 -m unittest discover -s tests -p 'test_codex_plugin.py' -v`. Expected: the package
   and dispatcher tests from task 01 remain green, and all five guidance tests pass against the
   post-task capability-based and one-pass wording.
2. Run `python3 -m unittest discover -s tests -p 'test_enumerations.py' -v`. Expected: the manual
   command table and delegation role table still match the canonical directories in both
   directions; no guidance edit dropped or invented an entry.
3. Run `python3 -m unittest discover -s tests -v`. Expected: the complete suite passes.
4. Run `git diff --check`. Expected: no whitespace errors.
