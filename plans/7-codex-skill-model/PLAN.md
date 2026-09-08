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

- [GitHub issue #7](https://github.com/dabit/just_do_it/issues/7) - problem statement, proposed
  implementation, and acceptance criteria.
- `docs/harness-adapter-architecture.md` - canonical sources, Codex packaging and namespacing,
  dispatcher contract, compatibility effects, and verification requirements.
- `AGENTS.md:7-74` - manual invocation, command inventory, and adapter portability rules.
- `README.md:24-31`, `README.md:80-99` - stale Codex discovery and delegation claims that must be
  corrected.
- `reference/delegation.md:26-54` and `roles/butler.md:10-25` - capability-based delegation and
  orchestrator responsibilities.
- `commands/feedback.md:23-28` - evidence that `$ARGUMENTS` can occur more than once.
- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` - existing package identity,
  version, and repository-root source.
- `bin/sync-opencode.sh:62-69`, `bin/sync-opencode.sh:118-146` - independent OpenCode adapter and
  portable path rewriting.
- `tests/jdi_files.py:20-47`, `tests/test_enumerations.py:110-132`,
  `tests/test_versions.py:17-37` - existing parser, inventory parity, and release-version patterns.
- [OpenAI: Build skills](https://developers.openai.com/codex/build-skills.md) - skill structure and
  Codex `$` and `/skills` selection.
- [OpenAI: Package your plugin](https://developers.openai.com/plugins/build/plugins.md) and
  [Build plugin skills](https://developers.openai.com/plugins/build/skills.md) - native
  `.codex-plugin/plugin.json` and bundled skill packaging.
- [OpenAI: Codex subagents](https://developers.openai.com/codex/agent-configuration/subagents.md) -
  current capability and `agents.enabled` fallback conditions.
- [Codex 0.151.0 host loader](https://github.com/openai/codex/blob/rust-v0.151.0/codex-rs/ext/skills/src/loader/host.rs#L309-L319)
  and [selection logic](https://github.com/openai/codex/blob/rust-v0.151.0/codex-rs/skills/src/selection.rs#L164-L195)
  - plugin qualification and exact explicit skill selection.

## Implementation Plan

### Decision

Package one Codex-native dispatcher skill named `run` under the existing `jdi` plugin. The public
Codex interface is `$jdi:run <command> [arguments]`; `$jdi:run` with no command dispatches `help`.
Do not add a standalone `$jdi` skill or one skill per command. Existing Claude Code
`/jdi:<command>` and OpenCode `/jdi-<command>` interfaces remain canonical for those harnesses.

### 1. Lock the selected adapter architecture

- Update `docs/harness-adapter-architecture.md` so `skills/run/SKILL.md` and `$jdi:run` are the
  selected design rather than unresolved alternatives.
- Keep `commands/*.md` as the sole source of command behavior. The dispatcher validates and loads
  those files but does not copy, reorder, or reinterpret their steps.
- Distinguish the user's current repository, where a JDI command operates, from the installed JDI
  plugin snapshot, where `commands/`, `roles/`, `agents/`, and `reference/` are resolved.
- Document that Codex does not automatically register JDI's Claude-style `agents/*.md` as custom
  Codex agents. A suitable subagent must receive the installed role file and exactly the role's
  declared inputs when no registered JDI role exists.
- Preserve the verified Codex 0.151.0 namespacing and exact-selection references. Record rejected
  alternatives as rationale, not supported interfaces.

### 2. Add test-first structural coverage

- Extend `tests/jdi_files.py` with no-dependency helpers to enumerate `skills/*/SKILL.md`, extract
  simple skill frontmatter scalars, parse `.codex-plugin/plugin.json`, and return its version.
- Extend `tests/test_frontmatter.py` with skill-specific checks: exactly one `skills/run/SKILL.md`,
  valid frontmatter, `name: run` matching its directory, a non-empty JDI-focused description, and a
  non-empty body. Leave existing command and agent fixtures unchanged.
- Add `tests/test_codex_plugin.py` to verify the native manifest, dispatcher contract, command
  inventory parity, portability, and Codex-specific documentation.
- Parse the dispatcher's dedicated allowlist and compare it in both directions with the stems of
  `commands/*.md`. Include `help`, even though the command table printed by help omits itself.
- Assert that the dispatcher specifies an empty-input help default, exact case-sensitive matching,
  pre-path rejection of unknown and path-like tokens, opaque and verbatim remainder handling,
  global literal single-pass replacement of every original `$ARGUMENTS`, complete Butler and
  command reads, and installed-root resolution for later dependencies.
- Keep the global replacement test non-vacuous by asserting `commands/feedback.md` contains two
  placeholders. Reject machine-specific checkout paths and `${CLAUDE_PLUGIN_ROOT}` in the Codex
  dispatcher.
- Assert that Codex README prose uses `$jdi:run`, `/skills`, `$` completion, and a fresh session;
  rejects bare Codex `$jdi` and custom-slash-command claims; and preserves Claude `/jdi:help` and
  OpenCode `/jdi-help` examples.
- Add `tests/test_opencode_sync.py` using `tempfile` and `subprocess` to exercise global and project
  sync into temporary destinations. Verify canonical command and agent inventories, project-mode
  copied references and roles, portable project paths, unchanged global path behavior, and that
  Codex packaging is not copied into OpenCode's independent surface.
- Extend `tests/test_versions.py` so the Claude manifest, Codex manifest, marketplace entry, and
  newest CHANGELOG heading must all agree.

### 3. Add the native Codex package and dispatcher

- Create `.codex-plugin/plugin.json` with plugin name `jdi`, the repository's current authoritative
  version, metadata consistent with `.claude-plugin/plugin.json`, and `skills: "./skills/"`. Add no
  MCP, hook, app, or asset entries. Advance every release authority together in step 6 rather than
  leaving the suite red between tasks.
- Create `skills/run/SKILL.md` with Agent Skills frontmatter, `name: run`, and a description covering
  the complete JDI workflow and its command-dispatch role.
- Define the public grammar as `$jdi:run <command> [arguments]` and include the exact 16-command
  allowlist represented by `commands/*.md`.
- Derive the plugin root from the loaded `skills/run/SKILL.md` location. Never use the process
  working directory, original marketplace checkout, a machine-specific path, arbitrary ancestor
  search, or `${CLAUDE_PLUGIN_ROOT}` to locate installed support files.
- Parse only the first whitespace-delimited token as the command. Absent or whitespace-only input
  selects `help`; known commands match exactly and case-sensitively; unknown and path-like tokens
  fail before path construction, file reads, or workflow mutation and report the supported list.
- Preserve the substring after the command separator unchanged. Do not parse quoting, normalize
  whitespace, expand variables, resolve paths, execute text, or serialize it through an argument
  list.
- Read `roles/butler.md` and the validated command completely. Replace every literal `$ARGUMENTS`
  occurrence in the original command body exactly once, globally and literally; an empty payload
  becomes an empty string and payload text is never rescanned.
- Resolve every later `reference/`, `roles/`, and `agents/` dependency against the same installed
  root. Missing installed files produce a diagnostic instead of searching for another checkout.
- Run the selected command in the main session as Butler. Use available subagents per
  `reference/delegation.md`, then its second-session or announced-inline fallbacks. Preserve the
  active sandbox, approval, and authorization boundaries.
- Do not add optional `skills/run/agents/openai.yaml`; it is unnecessary for the acceptance
  criteria.

### 4. Correct delegation and manual adapter guidance

- Update `reference/delegation.md` to include Codex in first-class subagent examples while keeping
  capability detection, not harness detection, as the rule.
- Clarify that an unregistered role runs in a generic subagent loaded with the installed
  `agents/<role>.md` instructions and only the role's declared inputs.
- Preserve the fallback order: first-class subagent, second non-interactive session, announced
  inline adoption. Delegation must not widen sandbox or authorization boundaries.
- Update `AGENTS.md` to state that `$ARGUMENTS` may occur zero, one, or multiple times and that every
  original occurrence is replaced literally in one pass. Preserve the manual invocation and
  OpenCode adapter rules otherwise.

### 5. Correct public Codex documentation

- Update `README.md`'s harness table and Codex section to use `$jdi:run <command> [arguments]` while
  preserving Claude `/jdi:<command>` and OpenCode `/jdi-<command>` syntax.
- Keep the existing Codex marketplace and plugin installation commands. Require a new Codex session
  after install or refresh and document discovery through `/skills` and `$` completion.
- State explicitly that canonical `commands/*.md` do not register as arbitrary Codex custom slash
  commands. Verify the qualified skill name `jdi:run` rather than typing `/` to find legacy
  commands.
- Include `$jdi:run`, `$jdi:run help`, `$jdi:run prep 4`, `$jdi:run yolo`, and `$jdi:run pr`
  examples. Do not document a standalone skill or one-skill-per-command alternative.
- Replace the blanket no-subagents claim with capability-based delegation and the announced inline
  fallback. Keep Codex's machine-wide scope and cached-snapshot update behavior accurate.
- Add `.codex-plugin/plugin.json` and `skills/run/SKILL.md` to the repository structure explanation.
  Do not globally rewrite `/jdi:*`, which remains valid Claude documentation.

### 6. Release the adapter as 1.0.4

- Set version `1.0.4` in `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and the
  new `.codex-plugin/plugin.json`.
- Change the marketplace description so it no longer presents the package as Claude-only.
- Add a newest-first `CHANGELOG.md` entry covering Codex-native `jdi:run` discovery, invocation,
  safe dispatch and root resolution, multi-occurrence argument replacement, capability-based Codex
  delegation, and unchanged existing Claude/OpenCode interfaces.
- Update `docs/config-key-lifecycle.md` so its release invariants, file counts, JSON-edit counts,
  tables, prose, and checklists include `.codex-plugin/plugin.json`.
- Reconcile the release number if another version lands on `main` before implementation; all
  version authorities must still advance together from the then-current base.

### 7. Verify the complete adapter

- Run `python3 -m unittest discover -s tests -v` and require all existing and new tests to pass.
- Run `claude plugin validate .` and require successful validation.
- Run `git diff --check` and inspect the diff for unintended canonical command, agent, Butler, or
  OpenCode sync changes.
- Complete the installed-harness scenarios in the Testing Strategy from isolated environments so
  cached or standalone JDI skills cannot hide discovery defects.

## Testing Strategy

The repository suite stays dependency-free and uses `python3 -m unittest discover -s tests -v`.
Structural tests prove package shape, text contracts, inventories, paths, and version parity; they
cannot prove model compliance, TUI completion, or real subagent behavior, which remain UAT.

| Acceptance criterion, reconciled to `$jdi:run` | Automated proof | Live proof |
|---|---|---|
| A clean plugin install exposes `jdi:run` | Codex manifest path, single-skill inventory, and skill-frontmatter tests | Install into an isolated Codex home, inspect the cached snapshot, start a fresh session, and confirm `/skills` lists `jdi:run` |
| Typing `$jdi:run` offers the skill | Plugin and skill identity assertions match the verified qualification behavior | Type `$` and `$jdi:run` in the Codex TUI and observe completion |
| `$jdi:run` and `$jdi:run help` run canonical help | Dispatcher contract requires the help default and `help` allowlist entry | Run both in a fresh session and compare the result with `commands/help.md` |
| `$jdi:run prep 4` preserves `4` | Allowlist and verbatim payload contract assertions | Run in a disposable git repo with `tracker.name: none` and verify the resulting workflow treats `4` as the complete prep argument |
| Codex subagents run when available and inline fallback remains | Delegation prose and installed-role path assertions | Run a delegating command with subagents enabled, inspect the child role and inputs, then repeat with `agents.enabled = false` and confirm an announced fallback |
| Claude Code behavior does not regress | Existing command and agent inventories plus `claude plugin validate .` | Install/update the release, run `/jdi:help`, confirm registered agents, and ensure the additive `/jdi:run` skill does not shadow commands |
| OpenCode behavior does not regress | Temporary global/project sync tests prove inventory and path behavior | Start OpenCode against a temporary sync and run `/jdi-help` |
| README matches supported behavior | Codex-scoped documentation assertions and preserved Claude/OpenCode examples | Follow the README from a clean install and review it for clarity |

Additional dispatcher UAT:

1. Install from a temporary marketplace snapshot into an isolated Codex home. Ensure no standalone
   or older cached JDI skill can participate.
2. Verify the installed snapshot contains `.codex-plugin/plugin.json`, `skills/run/SKILL.md`, and
   the canonical commands, roles, agents, and references.
3. Run from a separate scratch repository containing a decoy `commands/help.md`; verify support
   files are read from the installed snapshot while plans and git operations target the scratch
   repository.
4. Invoke an unknown token, `../help`, `/tmp/help`, and `commands/help.md`; compare repository state
   before and after and require no mutation.
5. Invoke a valid command with repeated spaces, punctuation, and a literal `$ARGUMENTS`; inspect the
   command-visible payload and require unchanged whitespace and no recursive replacement.
6. Exercise `feedback`, whose command body has two placeholders. Use an older matching plan and a
   newer unrelated plan, then verify the matching plan is selected rather than the fallback.
7. Follow `AGENTS.md` manually with commands containing zero, one, and multiple placeholders.
8. Run the OpenCode sync tests in both modes and verify no generated project file contains the
   checkout's absolute path.

## Risks

- **Version-sensitive namespacing:** `$jdi:run` is verified against Codex 0.151.0 source. Clean
  installed-session UAT must confirm the actual release target before shipping.
- **Natural-language dispatcher:** Structural tests guard its explicit contract but cannot prove
  every model follows the instructions; live invocation remains mandatory.
- **Cached-install false positives:** An older plugin or standalone `$jdi` skill can mask discovery
  failures. UAT must isolate the Codex home and inspect the installed snapshot.
- **Root confusion:** JDI support files come from the installed snapshot, while plans, source code,
  tracker context, and git operations belong to the user's current repository.
- **Delegation assumptions:** Codex does not natively register Claude-style agent files by their JDI
  names. Documentation and UAT must not claim named agents unless the runtime actually exposes
  them.
- **Command-token safety:** Unknown-command validation must happen before any token is interpolated
  into a path. Valid command arguments retain the selected workflow's normal authority and must
  remain subject to Butler and host authorization rules.
- **Cross-harness visibility:** A shared `skills/run/SKILL.md` is additive in Claude Code. Existing
  Claude commands must not be shadowed, and Codex syntax must not replace valid Claude examples.
- **Release race:** Main is currently `1.0.3`, while other in-flight work may claim a later version.
  Rebase reconciliation must advance all manifests, marketplace metadata, and CHANGELOG together.
- **Test scope:** Structural tests can prove inventory and text invariants, not Codex completion UI,
  real prompt dispatch, or subagent spawning. The UAT task must report those gaps honestly.

## Tasks

- [x] 01 — Add the Codex package and safe dispatcher (depends on: none)
- [x] 02 — Make delegation and manual substitution guidance capability-based (depends on: 01)
- [ ] 03 — Document the supported Codex interface (depends on: 01)
- [ ] 04 — Release the adapter with synchronized metadata (depends on: 01, 02, 03)
- [ ] 05 — UAT the installed adapter across harnesses (depends on: 01, 02, 03, 04)
