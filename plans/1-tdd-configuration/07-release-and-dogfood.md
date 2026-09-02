status: done
# 07 — Version bump, changelog, and dogfood this repo's own config

Depends on: 02, 03, 04, 05, 06

## Why
JDI's release mechanic is two matching version numbers and a changelog entry — nothing else ships
a change to an installed copy (`README.md:151-154`). This task closes the release out and turns
`tdd` on in this repository's own `.jdi/config.yml`, which is what makes the TDD-on path
exercisable here at all rather than only in theory.

## Description
- `.claude-plugin/plugin.json:3` → `1.0.3`, plus `"tdd"` and `"test-driven"` added to `keywords`.
- `.claude-plugin/marketplace.json:10` → `1.0.3`. Must match the version above.
- `CHANGELOG.md` — a `## 1.0.3` entry above `## 1.0.2`: a bold one-line headline, bullets with bold
  lead-ins, everything backticked, and a first bullet stating what happens to a repo that does not
  set the key (it behaves exactly as it did). Include **Proven, not assumed.** and **Degrades down,
  never up.** Mention the new `tests/` suite as its own bullet.
- This repository's own `.jdi/config.yml` (an existing file — this is an edit, not a new file):
  add `tdd.enabled: true` with `test_instructions: "python3 -m unittest discover -s tests -v, from
  the repository root. No install step and no third-party packages."`

Commit subject, when this task is implemented: `feat: Add a TDD configuration (1.0.3)`, body
closing with what was deliberately left out of scope. Before committing, run:
`grep -rn "tdd\|TDD" .`, `grep -rn "step [0-9]" commands/init.md`, and
`python3 -m unittest discover -s tests -v`.

**Note for whoever verifies this task and for UAT:** turning `tdd.enabled: true` on here does
**not** retroactively add a `- TDD:` line to *this plan's own* `PLAN.md`. TS1 resolves once per
plan, at the first task, and this plan's first task ran before `tdd` existed in the config — so
TS1's rung 1 applied (off, silent) and, per the design decision that the line is never rewritten
once a plan has run, stays that way for the rest of this plan's execution. The setting takes effect
starting with the *next* plan run in this repository.

## Files
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `CHANGELOG.md`
- `.jdi/config.yml`

### Carried over from task 05

The CHANGELOG entry must state that **a plan whose first task ran before this key existed simply
runs without TDD.** No line means no TDD, for every command, always — a plan started before the key
carries no `TDD:` line, is indistinguishable from one that started with TDD off, and neither is an
invitation to detect. Without this said out loud, a user who enables `tdd` mid-plan will expect
behaviour they will not get.

## Verification
1. `python3 -m unittest discover -s tests -v` — expect `OK`. The discriminating module is
   `tests/test_versions.py`. Its falsifiability control: if one version file is bumped and the
   other is not, `test_plugin_and_marketplace_versions_match` fails naming the two differing
   versions. A green run here is evidence both files and the changelog heading agree, not just
   that nothing crashed.
2. `grep -n '"version"' .claude-plugin/plugin.json .claude-plugin/marketplace.json` — expect
   `1.0.3` in both.
3. `grep -n "^## 1.0.3" CHANGELOG.md` — expect present, above the `## 1.0.2` heading.
4. `grep -n "tdd" .jdi/config.yml` — expect `enabled: true` and the `test_instructions` string
   present.
5. `grep -rn "tdd\|TDD" .` and `grep -rn "step [0-9]" commands/init.md` — the plan's own
   pre-commit checklist; read every hit rather than counting them.
