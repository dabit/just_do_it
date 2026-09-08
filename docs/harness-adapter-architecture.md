# Harness Adapter Architecture

## Status

Proposed architecture for exposing JDI's canonical Markdown workflow across agent harnesses without
duplicating workflow behavior.

## Purpose

JDI is a harness-neutral workflow with harness-specific adapters. Its commands and roles must
behave consistently whether they are invoked through Claude Code, Codex, OpenCode, or a manual
Markdown-reading fallback.

This document defines the authoritative files, adapter boundaries, discovery and dispatch flow,
portable path rules, delegation fallback, compatibility effects, and verification requirements.
Configuration-key behavior is documented separately in `docs/config-key-lifecycle.md`.

## Canonical Sources

JDI behavior is defined by four source groups:

| Source | Responsibility |
|---|---|
| `commands/*.md` | Ordered workflow instructions for each public command |
| `roles/butler.md` | Main-session orchestration responsibilities |
| `agents/*.md` | Delegatable role definitions |
| `reference/*.md` | Shared configuration, testing, tracker, plan-store, and delegation contracts |

The public command inventory is the set of Markdown files directly under `commands/`. `AGENTS.md`
enumerates that set, and `tests/test_enumerations.py` checks the enumeration in both directions.

The current allowlist is:

```text
done
execute
feedback
help
init
next
plan
pr
prep
replan
reresearch
research
split
start
status
yolo
```

An adapter may expose commands through a harness-supported interface, validate a command name,
resolve the installed plugin root, transform harness-specific frontmatter, and substitute user
arguments. It must not copy, reorder, or reinterpret command bodies. This preserves the adapter
rule in `AGENTS.md`: canonical bodies stay shared, while harness-specific metadata and paths are
handled at the boundary.

Plugin manifests, marketplace catalogs, sync scripts, and skill dispatchers are packaging and
transport. They are not authorities for workflow semantics.

## Harness Matrix

| Harness | Distribution | Discovery | Invocation | Root handling | Delegation |
|---|---|---|---|---|---|
| Claude Code | `.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json` | Installed `commands/`, `skills/`, and `agents/` | Existing `/jdi:<command>` commands; a bundled skill is an additive namespaced entry | `${CLAUDE_PLUGIN_ROOT}` and command-relative fallback | Registered agents when available, then the shared fallback ladder |
| Codex | Marketplace install and cached plugin snapshot; native metadata in `.codex-plugin/plugin.json` | Skills under the manifest's `skills` root or default `skills/` | `$jdi:run <command> [arguments]` | Derived from the loaded `SKILL.md` location | Subagents when enabled, then the shared fallback ladder |
| OpenCode | `bin/sync-opencode.sh`, globally or into `.opencode/` | Synced `command/jdi-*.md` and `agent/jdi-*.md` files | `/jdi-<command>` | Checkout path in global mode; copied repo-relative dependencies in project mode | OpenCode subagents when available, then the shared fallback ladder |
| Manual | No installation | Caller points the agent at a command file | Read `commands/<command>.md` and replace `$ARGUMENTS` | Caller identifies the checkout once | Any available subagent, second session, or inline adoption |

Claude's marketplace already exposes the repository root through `source: "./"`. OpenCode's
adapter transforms commands and agents in `bin/sync-opencode.sh`. Manual invocation is documented
in `AGENTS.md`.

## Codex Packaging And Flow

### Marketplace And Installed Snapshot

`codex plugin marketplace add` registers a marketplace root. Codex 0.151.0 recognizes the existing
`.claude-plugin/marketplace.json` compatibility path, which explains why JDI can be installed today.
The marketplace entry names the plugin and points `source` at the repository root; it does not
expose a workflow by itself.

`codex plugin add` materializes the source into Codex's plugin cache. Runtime behavior must use that
installed snapshot, not the checkout from which the marketplace was added. Pulling the checkout is
not proof that an installed plugin was updated, and a dispatcher must never hardcode the checkout
path.

Codex's native plugin entry point is `.codex-plugin/plugin.json`. The manifest should carry the
same stable plugin name and release version as the other packaging metadata, point `skills` at a
plugin-relative directory such as `./skills/`, and keep all declared paths inside the plugin root.

References:

- [Package your plugin](https://developers.openai.com/plugins/build/plugins.md)
- [Build plugin skills](https://developers.openai.com/plugins/build/skills.md)
- [Codex 0.151.0 manifest precedence](https://github.com/openai/codex/blob/rust-v0.151.0/codex-rs/exec-server-protocol/src/protocol.rs#L43-L50)
- [Codex 0.151.0 marketplace compatibility](https://github.com/openai/codex/blob/rust-v0.151.0/codex-rs/core-plugins/src/marketplace.rs#L20-L25)

### Skill Discovery

A dispatcher skill has this shape:

```text
<plugin-root>/
|-- .codex-plugin/
|   `-- plugin.json
|-- skills/
|   `-- run/
|       `-- SKILL.md
|-- commands/
|-- agents/
|-- roles/
`-- reference/
```

`SKILL.md` follows the [Agent Skills specification](https://agentskills.io/specification). Its
frontmatter has a name matching the directory and a non-empty description that advertises the JDI
workflow. Its body is a thin dispatcher, not another copy of the workflow.

### Namespacing

Codex qualifies a bundled skill name as:

```text
<plugin-manifest-name>:<skill-frontmatter-name>
```

The target-version host loader applies this qualification before exposing the skill, and explicit
text selection matches the qualified name:

- [Codex host skill qualification](https://github.com/openai/codex/blob/rust-v0.151.0/codex-rs/ext/skills/src/loader/host.rs#L309-L319)
- [Codex explicit skill selection](https://github.com/openai/codex/blob/rust-v0.151.0/codex-rs/skills/src/selection.rs#L164-L195)

JDI uses one dispatcher named `run` under the existing `jdi` plugin, producing the public Codex
interface `$jdi:run <command> [arguments]`. This keeps plugin installation and a single thin
adapter while avoiding the redundant `$jdi:jdi` spelling.

The alternatives were rejected for these reasons:

| Packaging | Explicit mention | Trade-off |
|---|---|---|
| Plugin `jdi`, dispatcher `jdi` | `$jdi:jdi` | One obvious dispatcher, but redundant-looking |
| Plugin `jdi`, dispatcher `run` | `$jdi:run` | Selected: one concise dispatcher with a clear qualified name |
| Plugin `jdi`, one skill per command | `$jdi:prep`, `$jdi:yolo`, etc. | Familiar command shape, but duplicates adapter metadata and expands parity burden |
| Standalone skill `jdi` | `$jdi` | Bare name, but different installation, update, and namespace behavior from a bundled plugin |

A successful standalone `$jdi` skill does not prove that a bundled plugin exposes the same bare
name. `$jdi:run` must be tested from a clean plugin installation and documented as a versioned
public interface.

Codex's supported explicit skill mechanisms are `$` mentions and `/skills`; see
[Build skills](https://developers.openai.com/codex/build-skills.md). Documentation must not promise
that canonical `commands/*.md` become arbitrary legacy custom slash commands.

### Dispatcher

After Codex selects the skill, the dispatcher:

1. Resolves the installed plugin root.
2. Parses the requested JDI command using the grammar below.
3. Rejects a command not in the exact allowlist.
4. Reads `roles/butler.md` completely.
5. Reads `commands/<validated-command>.md` completely.
6. Replaces every original `$ARGUMENTS` occurrence with the argument payload.
7. Treats the resolved root as the meaning of every plugin-relative path.
8. Follows the command and its role and reference contracts.
9. Preserves the active environment's authorization and sandbox boundaries.

The dispatcher does not implement command behavior itself. The main session remains the Butler;
the Butler is never spawned.

## Portable Root Resolution

The user's project is the process working directory, so it is not evidence of JDI's installed
location. The portable anchor is the loaded file:

```text
<plugin-root>/skills/run/SKILL.md
```

The dispatcher derives the plugin root from that location once, then resolves:

```text
<plugin-root>/roles/butler.md
<plugin-root>/commands/<validated-command>.md
<plugin-root>/agents/<role>.md
<plugin-root>/reference/<document>.md
```

It must not assume JDI is under `~/git`, depend on the original marketplace source, resolve command
files from the user's project, use an unvalidated token in a path, depend on
`${CLAUDE_PLUGIN_ROOT}` in Codex, or search arbitrary ancestors for a plausible checkout. Missing
required files are a diagnostic failure, not a reason to fall back to another copy.

Claude continues to use `${CLAUDE_PLUGIN_ROOT}`. OpenCode rewrites that reference during sync at
`bin/sync-opencode.sh:118-130`.

## Dispatcher Grammar

The logical input is:

```text
<command> [arguments]
```

Only the first whitespace-delimited token is the command. Everything after its separator is opaque
argument text.

| Input | Behavior |
|---|---|
| No following text, or whitespace only | Dispatch `help` with an empty payload |
| Known command without a remainder | Dispatch it with an empty payload |
| Known command followed by text | Dispatch it and preserve the remainder verbatim |
| Unknown token | Reject it and print the supported commands |
| Path-like token such as `../help` | Reject it; never use it in a path |

Matching is exact and case-sensitive. Adapters do not lowercase, alias, abbreviate, fuzzy-match, or
probe `commands/<token>.md` for existence.

The explicit allowlist intentionally duplicates the command inventory. It prevents user text from
becoming a path and prevents a new Markdown file from becoming public without review. A
bidirectional structural test keeps both sets equal.

After recognizing the command token, the dispatcher preserves the remaining substring verbatim. It
does not tokenize quotes, normalize whitespace, expand variables, resolve paths, execute text, or
serialize through an intermediate argument list.

The payload replaces every literal `$ARGUMENTS` occurrence in the original command body. The
replacement is global, literal, single-pass, and uses an empty string when no arguments were
supplied. Text introduced by the payload is not scanned again. Global replacement matters because
`commands/feedback.md` contains the placeholder twice; `AGENTS.md` must not claim it appears only
once.

Unknown commands fail closed before any command path is built or workflow mutation occurs. Only
absent input defaults to help; a typo does not.

## Capability-Based Delegation

Delegation follows observed runtime capability, not a permanent claim about a harness. The Butler
uses the order in `reference/delegation.md`:

1. Use a first-class subagent, preferring an already registered JDI role.
2. Use a second non-interactive session if available.
3. Adopt the role inline, announce the switch, and return to Butler voice afterward.

The delegated phase is never skipped merely because the preferred mechanism is unavailable.

Current Codex releases enable subagent workflows by default, while `agents.enabled = false` can
disable them. Codex does not register JDI's Claude-style `agents/*.md` files as named custom agents
merely because they are in the plugin. When a matching JDI role is not registered, the Butler uses
a suitable generic subagent, gives it the installed `agents/<role>.md` instructions and exactly the
role's declared inputs, and announces the normal fallback when subagents are unavailable. See
[Codex subagents](https://developers.openai.com/codex/agent-configuration/subagents.md).

Delegation does not widen authorization. Subagents inherit the active sandbox and approval
environment, and external mutations remain governed by the active command and Butler rules.

## Compatibility Effects

### Claude Code

Adding a root `skills/` directory creates an additional Claude-visible skill. Existing
`/jdi:<command>` commands and registered agents must keep working. "Unchanged" means no regression
to those interfaces; it cannot mean that no additive skill is visible.

### OpenCode

`bin/sync-opencode.sh` currently copies only commands, agents, references, and roles. A Codex
manifest and root skill do not change OpenCode's `/jdi-<command>` surface unless the sync script is
deliberately extended.

### Manual Invocation

Manual invocation continues to read canonical command files directly. Its documentation must allow
multiple `$ARGUMENTS` occurrences, but the mechanism otherwise remains unchanged.

### Consumers

No sibling consumers are configured. The README, marketplace metadata, cached plugin installs, and
user-authored setup instructions are nevertheless consumers of the public invocation contract.

## Verification Strategy

Repository tests prove structural consistency. Installed-harness UAT proves discovery and prompt
execution. Both are required.

### Structural Tests

Add checks for:

- Agent Skills-compliant frontmatter and a skill name matching its directory.
- A non-empty dispatcher body with no machine-specific checkout path.
- Bidirectional equality between the dispatcher allowlist and `commands/*.md` stems.
- Empty-input help default, exact allowlisting, unknown-command rejection, installed-root
  derivation, global single-pass replacement, and verbatim remainder preservation.
- A parseable `.codex-plugin/plugin.json` whose relative `skills` path stays under the plugin root.
- Version parity across Claude and Codex manifests, marketplace metadata, and CHANGELOG.
- Codex-specific README claims, capability-based delegation, and preservation of Claude and
  OpenCode examples.

Extend the existing patterns in `tests/jdi_files.py`, `tests/test_frontmatter.py`,
`tests/test_enumerations.py`, and `tests/test_versions.py` rather than introducing a dependency.

Run:

```sh
python3 -m unittest discover -s tests -v
claude plugin validate .
```

### Live UAT

Use a clean or isolated Codex installation so an existing standalone skill cannot hide discovery or
namespacing defects. Verify:

1. The installed snapshot contains the Codex manifest, dispatcher, commands, roles, agents, and
   references.
2. A new session shows the exact selected skill name through `/skills` and `$` completion.
3. Empty and explicit help follow `commands/help.md`.
4. A distinctive multi-word argument reaches the selected command unchanged.
5. Multiple placeholders are replaced, while unknown and path-like tokens fail before mutation.
6. References resolve from the installed snapshot while working in a separate scratch repository.
7. Enabled Codex subagents receive the requested role; disabled subagents produce an announced
   fallback.
8. Existing Claude commands and agents still work and `claude plugin validate .` passes.
9. OpenCode global and project sync remain portable and retain their command and agent counts.
10. Manual invocation works for commands with zero, one, and multiple placeholders.

## Release Invariants

Adapter changes alter installed public behavior and require a release version change. Once the
Codex manifest exists, this equality must hold:

```text
Claude plugin version
= Codex plugin version
= marketplace plugin version
= newest CHANGELOG version
```

`tests/test_versions.py` should enforce it. `docs/config-key-lifecycle.md` must also describe the
additional version-bearing manifest.

A release includes implementation files, structural tests, updated user and architecture docs, a
CHANGELOG entry naming the invocation, matching versions, passing repository tests, Claude plugin
validation, and recorded Codex, Claude, and OpenCode UAT.

## Invariants

1. `commands/*.md` remains the sole source of command behavior.
2. The Butler remains the main-session orchestrator and is never spawned.
3. Adapters do not rewrite canonical command or role bodies.
4. Every public command is explicitly allowlisted.
5. Dispatcher and command inventories agree in both directions.
6. Unknown command text never becomes a filesystem path.
7. Empty input defaults to help; unknown input fails closed.
8. Every original `$ARGUMENTS` occurrence is replaced once with opaque user text.
9. Plugin roots are derived from installed artifacts, never hardcoded.
10. Delegation follows observed capability, with inline adoption as a first-class fallback.
11. Plugin and skill names together define the bundled Codex mention.
12. Invocation spelling is versioned as an external interface.
13. A shared plugin skill is an additive Claude Code surface.
14. OpenCode and manual behavior remain independent of Codex packaging.
15. Structural tests and installed-runtime UAT are both required.
16. Every version-bearing manifest, marketplace entry, and CHANGELOG heading agrees.
