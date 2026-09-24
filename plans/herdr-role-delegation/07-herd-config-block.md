status: done
# 07 - The herd config block

Depends on: 02, 06

## Why

`/jdi:herd` (Task 08) reads `herd.kind`, `herd.max_parallel` and `herd.seed`, so the schema needs
those keys before the command can be written against them. The literal dependency is Task 02 (the
`delegation:` block establishes the pattern this task's schema edit sits after); the dependency on
Task 06 is declared only to place this task in the same wave as Task 08, per the instruction to keep
the `/jdi:herd` layer as one separable, clearly-marked wave that can be dropped as a unit to rebase
PR #5 instead - Task 07's own work does not need anything Task 06 writes.

**Separable: drop this task (and Task 08) to rebase PR #5 onto `reference/herdr.md` H1, H2 and H4
instead of superseding it.**

Rests on: the plan's "Wave 3: the `/jdi:herd` layer (separable; Steps 7 and 8 run in parallel)"
structure and Step 7's own content in the Implementation Plan.

## Description

Write `tests/test_config_schema.py`'s new class `HerdBlockTest` first:

- `herd.kind`, `herd.max_parallel` and `herd.seed` are schema keys.
- `herd.args` and `herd.env` are **not** schema keys.
- The defaults table covers `herd`.

Confirm it fails, then edit `reference/config.md`:

- Schema: after `delegation:` (the block Task 02 added), add a `herd:` block with `kind: claude` and
  `max_parallel: 5`. Base the comments on PR #5's own (`git show
  origin/herd-command:reference/config.md`, the `herd:` block), with the `kinds:` wording corrected to
  "a kind Herdr supports whose CLI is installed" (matching the fixed rung-7 reading Task 03 wrote).
  - `seed: {}` keeps PR #5's commented structure and placeholders - run `git show
    origin/herd-command:reference/config.md` and copy its `seed` comment block verbatim, adjusting
    only the corrected `kinds:` wording if it repeats there.
  - No `args` or `env` keys under `herd:`. A comment says herd agents take
    `harnesses.<herd.kind>.{args,env}`.
- Defaults rows: `herd.kind` → `claude`, `herd.max_parallel` → `5`, `herd.seed` → empty.
- Notes: four bullets, rewritten from PR #5's own:
  - "`herd` is read by `/jdi:herd` and nothing else."
  - "`/jdi:herd` validates Herdr and stops; it never repairs", with the justification that it has no
    fallback, and a herd that became one prep looks like a herd that worked.
  - The `herd.seed` bullet (adapt PR #5's own wording).
  - "Herd agents take their arguments and environment from `harnesses.<herd.kind>`, verbatim."

Edit `jdi.config.example.yml`: add `herd: {kind: opencode, max_parallel: 3}`, written as a two-space
block (not a flow mapping) because `key_paths` (in `tests/jdi_files.py`) only reads two-space-indented
mappings - a flow mapping would parse as zero keys and silently fail the schema-agreement test in the
wrong direction. `seed: {}` goes with PR #5's commented example (adapt from `git show
origin/herd-command:reference/config.md`'s example section).

The existing `ConfigSchemaTest` (unchanged) then proves the example agrees with the schema, in both
directions, automatically.

## Files

- `reference/config.md`
- `jdi.config.example.yml`
- `tests/test_config_schema.py`

## Verification

- `python3 -m unittest tests.test_config_schema.HerdBlockTest -v` - fails before the schema edit,
  passes after `herd.kind`, `herd.max_parallel`, and `herd.seed` are schema keys and `herd.args` /
  `herd.env` are absent.
- `python3 -m unittest tests.test_config_schema.ConfigSchemaTest -v` - passes (the herd keys agree
  between schema, example, and defaults).
- `grep -n "herd.args\|herd.env" reference/config.md` - empty, confirming the two keys PR #5 used are
  deliberately not reintroduced.
- `python3 -m unittest discover -s tests -v` - no new failures.
