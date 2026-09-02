status: done
# 01 — Add the repository's first automated test suite

Depends on: None

## Why
Every later task in this plan edits a file whose correctness (schema/example agreement, a
Defaults row, a hand-maintained enumeration, matching version numbers) can be checked mechanically.
Until this suite exists, "does the edit match its counterpart" is a manual grep every time. This
task creates the suite first so every subsequent task in the plan has a real, repeatable
verification command from the start, and so a half-finished edit later in the plan fails a test the
moment it lands rather than being caught by review alone.

## Description
Add a `tests/` directory using Python's stdlib `unittest` (no third-party dependency — the repo
already shells to `python3` in `bin/sync-opencode.sh`). The suite does not parse YAML; it extracts
key paths from the plain, hand-written two-space-indented subset both config files already use.

Create:
- `tests/jdi_files.py` — shared helpers, no tests of its own: `ROOT` (via
  `pathlib.Path(__file__).resolve().parents[1]`), `split_frontmatter(text)`, `key_paths(lines)`,
  `schema_block()`, `defaults_table_keys()`.
- `tests/test_frontmatter.py` — every `commands/*.md` and `agents/*.md` has well-formed frontmatter
  with a non-empty `description` and a non-empty body. Handle the block scalar: `agents/*.md` use
  `description: |`, so a bare `^description:\s*\S` regex matches the pipe character and proves
  nothing — where the value is `|` or `>`, assert the next line is indented and non-blank.
- `tests/test_config_schema.py` — example keys are a subset of schema keys; schema keys are a
  subset of example keys, minus `KNOWN_OMISSIONS = {"plans.service", "plans.location"}`
  (external-mode-only, commented out in the example); every schema block has a Defaults row; every
  Defaults row names a real schema key (`models.*` matched as a prefix).
- `tests/test_enumerations.py` — bidirectional checks: `reference/*.md` against
  `README.md:218-228` and `AGENTS.md:46-47`; `reference/delegation.md:12-21` against `agents/*.md`;
  `AGENTS.md`'s command table against `commands/*.md`; the digits in `README.md:220-221`
  ("16 workflow commands", "7 delegatable roles") against the actual directory counts.
- `tests/test_versions.py` — `plugin.json` version equals `marketplace.json` version equals the
  first `^## (\S+)` heading in `CHANGELOG.md`.

Deliberately not asserted: that `file:line` citations resolve (line numbers legitimately move), any
prose content, or any invocation of `bin/sync-opencode.sh`.

Also add a `tests/` row to `README.md`'s "How it is put together" table and a short "Running the
tests" line naming the invocation — the enumeration test only scans `reference/`, so nothing else
in the suite catches this omission.

## Files
- `tests/jdi_files.py` (new)
- `tests/test_frontmatter.py` (new)
- `tests/test_config_schema.py` (new)
- `tests/test_enumerations.py` (new)
- `tests/test_versions.py` (new)
- `README.md` (add the `tests/` row and "Running the tests" line)

## Verification
1. `python3 -m unittest discover -s tests -v` — expect a nonzero test count and `OK` on the final
   line, exit code `0`. This is the baseline run: nothing else in the plan has changed yet, so
   every test should pass against the tree as it stands today (current schema/example already
   agree, current enumerations already agree, current versions already match).
2. `ls commands/*.md | wc -l` and `ls agents/*.md | wc -l` — expect `16` and `7`. These are the
   counts `test_enumerations.py` checks against the prose in `README.md:220-221`; if either number
   is wrong on this tree, that assertion is not testing what it claims to.
3. Confirm the run is not a false positive: `python3 -m unittest discover -s tests -v; echo "exit: $?"`
   — expect `exit: 0`, not `5`. `python3 -m unittest` exits `5` on "Ran 0 tests", which would read
   as "no error" while proving nothing; the count from step 1 rules that out here.
4. `grep -n "tests/" README.md` — expect the new table row and the "Running the tests" line to
   both appear.
