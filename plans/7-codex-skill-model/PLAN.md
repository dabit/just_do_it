# Make JDI Fully Compatible with Codex's Skill Model

- Tracker: github
- Project: feature development
- Issue: #7
- Issue URL: https://github.com/dabit/just_do_it/issues/7
- Created: 2026-09-08
- Base commit: origin/main @ 296103df517fa0527082f4a2f77898afc7951c41
- TDD: on — proven 2026-09-08 with `python3 -m unittest discover -s tests -v`
- Started: 2026-09-08
- Summary: Add a Codex-native JDI skill adapter, capability-based delegation guidance, accurate Codex documentation, and compatibility tests.

## References

- `docs/harness-adapter-architecture.md`
- `AGENTS.md`
- `README.md`
- `reference/delegation.md`
- `roles/butler.md`
- `commands/feedback.md`
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.codex-plugin/plugin.json`
- `skills/run/SKILL.md`
- `bin/sync-opencode.sh`
- `docs/config-key-lifecycle.md`
- `tests/jdi_files.py`
- `tests/test_codex_plugin.py`
- `tests/test_frontmatter.py`
- `tests/test_opencode_sync.py`
- `tests/test_versions.py`

## Decisions

- Codex uses one bundled dispatcher skill, `run`, under plugin `jdi`, yielding
  `$jdi:run <command> [arguments]`; empty input dispatches `help`. The issue's bare `$jdi`
  expectation was stale because Codex 0.151.0 qualifies bundled skills as `<plugin>:<skill>`. One
  skill per command was rejected because it duplicates metadata and expands parity burden.
- `commands/*.md` remain the sole workflow source. The dispatcher reads the Butler and selected
  command completely rather than copying, reordering, or interpreting command behavior. Claude
  `/jdi:<command>` and OpenCode `/jdi-<command>` remain their canonical interfaces.
- The dispatcher uses an exact, case-sensitive 16-command allowlist before path construction.
  Unknown and path-like tokens fail closed; only absent input defaults to help. The explicit
  duplication prevents user input from becoming a path and prevents new command files from becoming
  public without review.
- Argument text after the command separator remains opaque and verbatim. Every original
  `$ARGUMENTS` occurrence is replaced globally, literally, and once; introduced `$ARGUMENTS` text
  is not rescanned. This corrected manual guidance that did not account for
  `commands/feedback.md` containing two placeholders.
- Support files resolve from the installed `skills/run/SKILL.md` root, while plans, source changes,
  and git operations target the user's current repository. Missing installed files produce a
  diagnostic instead of searching another checkout.
- Delegation is capability-based, not harness-based. An unregistered JDI role uses a suitable
  generic subagent loaded with the installed role definition and exactly its declared inputs, then
  falls back to a second non-interactive session or announced inline adoption. Delegation cannot
  widen sandbox, approval, or authorization boundaries.
- The Codex manifest stays minimal: no `skills/run/agents/openai.yaml`, MCP, hook, app, or asset
  declarations. Codex packaging remains independent of OpenCode synchronization.
- Release `1.0.4` advanced the Claude manifest, Codex manifest, marketplace entry, and CHANGELOG
  together; release guidance now treats all three JSON files as version authorities and no longer
  describes the package as Claude-only.

## Plan Gaps Caught During Execution

- The UAT plan assumed isolated Codex and Claude homes could be authenticated. They could not;
  Codex attempts stopped at HTTP 401 before model dispatch, so task 05 produced an agent-run smoke
  test rather than user acceptance.
- The available harnesses did not expose exact hidden child inputs, byte-for-byte payload receipt,
  or pre-read ordering. Structural tests prove the shipped instruction contract only, not live model
  compliance.
- No implementation failure, missed call site, or automated-test fallout was observed.

## Outcome

### Shipped

| Batch | Commit |
|---|---|
| Plan approval | `c768863` |
| 01 — Codex package and safe dispatcher | `d0d9763` |
| 02 — Capability-based delegation and manual substitution | `cb04f69` |
| 03 — Public Codex documentation | `e39ed9a` |
| 04 — Synchronized 1.0.4 release metadata | `38ad21f` |
| 05 — Cross-harness smoke-test record | `7a31be3` |

### Deferred

- **UNVERIFIED — Issue #7:** Codex live command behavior, including canonical help, prep, rejection
  behavior, `/skills`, `$` TUI completion, root isolation, and delegation. The isolated home was
  unauthenticated and attempts stopped at HTTP 401 before model dispatch.
- **UNVERIFIED — Issue #7:** Claude live `/jdi:help` behavior. Isolated plugin installation
  succeeded, but the unauthenticated configuration could not execute the command.
- **UNVERIFIED — Issue #7:** Byte-for-byte payload receipt, pre-read ordering, and exact hidden
  child inputs remain unobservable. Structural tests are mechanism evidence only, not live passes.
- These clauses require authenticated Codex and Claude user acceptance; no separate follow-up issue
  is recorded.

## Test Result

Agent-run UAT was a smoke test, not user acceptance.

- **PASS:** `python3 -m unittest discover -s tests -v` completed all 47 tests successfully.
- **PASS:** `claude plugin validate .`.
- **PASS:** `git diff --check`.
- **PASS:** Codex CLI 0.151.0 installed `jdi@just-do-it` 1.0.4 into an isolated home. Its cached
  snapshot contained `.codex-plugin/plugin.json`, `skills/run/SKILL.md`, all 16 commands, all seven
  agents, the Butler, and all five reference files.
- **PASS:** OpenCode 1.18.25 global and project synchronization retained 16 commands and seven
  agents; `/jdi-help` produced canonical help in both modes, project paths remained portable,
  global mode retained its intentional checkout path, and Codex packaging was not copied.
- **PASS:** Manual zero-, one-, and multiple-placeholder substitution followed the global, literal,
  single-pass rule and preserved introduced literal `$ARGUMENTS` text.
- **PASS:** Claude plugin installation reported 17 skills — 16 commands plus additive `run` — and
  seven agents. Live Claude command behavior remains **UNVERIFIED**.

## Risk Note

- The natural-language dispatcher remains subject to model compliance. Detection signals are
  behavior differing from canonical commands or host traces showing altered payload/read order;
  remedy is authenticated qualification with tracing and correction of the dispatcher contract.
- Codex namespacing is source-verified for 0.151.0 and package inventory passed, but live `/skills`
  and completion remain **UNVERIFIED**. Detect absence or misqualification of `jdi:run` in a clean,
  fresh session; remedy by reconciling the adapter to the observed target runtime.
- Root isolation and delegation remain **UNVERIFIED** live. Detect support content coming from the
  user repository, fallback to another checkout, missing delegation, widened authorization, or
  excess child inputs; remedy by rerunning Issue #7 acceptance in authenticated sessions with
  filesystem and subagent observability.
