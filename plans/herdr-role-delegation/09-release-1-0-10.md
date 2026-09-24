status: done
# 09 - Release 1.0.10

Depends on: 04, 05, 06, 07, 08

## Why

`docs/config-key-lifecycle.md`'s release mechanics require the three version manifests and the
CHANGELOG to move together, in the commit that closes out the feature, once every file the release
note describes has actually landed - which is every task in Waves 1 through 3.

Rests on: the plan's release-mechanics application of `docs/config-key-lifecycle.md` section 6, and
the note that the herd CHANGELOG bullet is conditional: "unless the user dropped Wave 3... PR #5
stays open and must be rebased".

## Description

Bump all three version manifests from `1.0.9` to `1.0.10`:
- `.claude-plugin/plugin.json:3` (the `"version"` field).
- `.codex-plugin/plugin.json:3` (the `"version"` field).
- `.claude-plugin/marketplace.json:10` (the `"version"` field, inside the `jdi` plugin entry).

Add a new `## 1.0.10` entry at the top of `CHANGELOG.md`, above the current `## 1.0.9` entry, in the
shape `docs/config-key-lifecycle.md` section 6 describes (a bold one-line headline, a blank line,
then bullets with bold lead-ins, every key/mode/command in backticks, the first bullet stating
backward compatibility):

- A bold headline: "**A Butler inside Herdr can run a delegated role as its own agent process, wait
  for it, and accept its work only through a validated result file.**"
- The first bullet covers `delegation.transport` and states: "a repo with no `delegation` block
  behaves exactly as it did".
- Then bullets for:
  - `reference/herdr.md`;
  - the result contract;
  - blocked and timeout handling;
  - the fallback ("Degrades to `native`, never beyond");
  - only roles on another CLI get panes, Executor waves included (one pane per task, at most 4 at
    once); a role on the session's own CLI stays a subagent;
  - the corrected `kinds:` reading;
  - the Feedbacker's "model or harness" rule;
  - **the herd bullet, only if Tasks 07 and 08 shipped**: "`/jdi:herd` arrives on the shared Herdr
    operations; `herd.args` and `herd.env` from PR #5 are replaced by `harnesses.<kind>`." If the
    user dropped Wave 3, omit this bullet entirely and say so in the commit body - do not write a
    bullet describing a command that is not in this release.

The commit subject is `feat: Run delegated roles as Herdr agents with a result contract (1.0.10)`.
Its body names what was deliberately left out: waves, tiers, a runs-path override key, and
`skills/run/SKILL.md:90-92` (considered and unchanged, because "as that contract directs" covers rung
0). If Wave 3 was dropped, the body also says PR #5 stays open and needs rebasing onto
`reference/herdr.md` H1, H2 and H4 instead of closing as superseded.

## Files

- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `CHANGELOG.md`

## Verification

- `python3 -m unittest tests.test_versions.VersionTest -v` - passes: all three manifests read
  `1.0.10` and the CHANGELOG's newest heading is `## 1.0.10`.
- `python3 -m unittest tests.test_versions.ReleaseMetadataTest -v` - stays green (marketplace
  description stays harness-neutral; unaffected by this task).
- `grep -n '"version"' .claude-plugin/plugin.json .codex-plugin/plugin.json .claude-plugin/marketplace.json`
  - all three show `1.0.10`.
- `grep -n "^## " CHANGELOG.md | head -2` - the first line is `## 1.0.10`, the second `## 1.0.9`.
- `python3 -m unittest discover -s tests -v` - the full 60-plus-test suite passes; this is the gate
  that closes Wave 4 before UAT.
