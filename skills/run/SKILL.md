---
name: run
description: Dispatch and run any command in the complete JDI engineering workflow, from setup and planning through implementation, feedback, release, and pull request.
---

# JDI command dispatcher

Use this skill only as the thin adapter between Codex's `$jdi:run <command> [arguments]` interface
and JDI's installed canonical workflow. The canonical command files define behavior; do not copy,
reorder, summarize, or reinterpret their steps.

Treat the text immediately following the selected `$jdi:run` mention as the logical dispatcher
input. The user's current working repository is where the selected workflow operates. It is not the
location of JDI's installed support files.

## Exact command allowlist

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

This list is exact and case-sensitive. It is both the complete public command inventory and the only
source from which a command token may be accepted.

## Parse and validate the input

1. Absent or whitespace-only input selects `help` with an empty payload. Only absent or
   whitespace-only input defaults to `help`; unknown input never does.
2. Otherwise, parse only the first whitespace-delimited token as the command. Match the token
   exactly and case-sensitively against the allowlist. Do not lowercase, alias, abbreviate,
   fuzzy-match, or probe for a file.
3. Unknown tokens, including path-like tokens such as `../help`, `/tmp/help`, and
   `commands/help.md`, must be rejected before constructing a command path, reading any command
   file, or mutating the user's repository. Report the complete supported-command list from the
   allowlist above and stop.
4. For a validated command, the payload is empty if no separator follows it. Otherwise use the
   separator rule: The payload is the exact substring after the first whitespace separator that
   ends the command token.
   Preserve that substring verbatim, including additional whitespace, punctuation, quotes, and
   `$ARGUMENTS` text. Do not parse quoting, trim or normalize whitespace, expand variables, resolve
   paths, execute the payload, or serialize it through an argument list.

Do not construct any path from an unvalidated token.

## Resolve and load the installed workflow

Only after validating the token, derive `<plugin-root>` from this loaded file's installed location:
this file is exactly `<plugin-root>/skills/run/SKILL.md`, so ascend from `SKILL.md` to `run`, then
`skills`, then `<plugin-root>`. Derive that root once.

1. Require `<plugin-root>/roles/butler.md`. Read `<plugin-root>/roles/butler.md` completely.
2. Require the safe path formed from the validated allowlist value:
   `<plugin-root>/commands/<validated-command>.md`. Read
   `<plugin-root>/commands/<validated-command>.md` completely.
3. If either installed file is missing or unreadable, report its expected installed path and stop.
   Do not continue with a partial read and do not seek another installation.

Resolve every later `reference/`, `roles/`, and `agents/` dependency against that same
`<plugin-root>`. Do not use the process working directory, the user's repository, the original
marketplace checkout, or an ancestor search to locate JDI support files. If an installed support
file is missing, report its expected installed path and stop; do not search for another copy.

## Substitute and run

Work from the complete, original command body loaded above. Replace every literal `$ARGUMENTS`
occurrence in the original command body exactly once. The replacement is global, literal, and
single-pass. An empty payload replaces each occurrence with the empty string. Do not rescan
replacement text, so payload text that itself contains `$ARGUMENTS` remains unchanged.

Adopt the completely loaded Butler instructions as the operating contract. Run the selected
canonical command in this main session as the Butler, using the command body after substitution.
Never spawn the Butler. Keep the command's order, gates, questions, mutations, and reporting rules
intact.

Follow the installed `reference/delegation.md` contract whenever the command delegates work. Use
available subagents as that contract directs, followed by its second-session and announced-inline
fallbacks; do not replace the canonical delegation workflow with dispatcher-specific behavior.

Preserve the active sandbox, approval policy, and authorization boundaries for all reads, writes,
commands, delegation, tracker actions, and infrastructure changes. Neither dispatch nor delegation
grants additional authority.
