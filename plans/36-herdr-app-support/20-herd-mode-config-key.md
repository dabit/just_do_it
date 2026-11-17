status: done
# 20 — The `herd.mode` config key

Depends on: None

## Why
`/jdi:herd` needs a repo-level `herd.mode: do | prep` key, defaulting to `do`, documented in the schema, the defaults table, the notes and the example, and saying plainly that `do` opens and merges pull requests unattended, that `prep` is the way back, and that an invalid value runs as `prep`. `/jdi:do` and `/jdi:prep` learn they run in a herd from the invocation, never from this block, and there is no `--mode` flag. Rests on: U1, E1, E6, M3, M7.

## Description
Planner's Task 20. Add `herd.mode` to `reference/config.md` (schema, defaults row, notes) and to
`jdi.config.example.yml`, and pin it in `HerdBlockTest` in `tests/test_config_schema.py`.

**Recorded deviation (E6), do not "fix" it:** `docs/config-key-lifecycle.md` prefers the
least-demanding default; `do` is not that. The user chose it (U1), and no herd has shipped, so
nobody's behaviour changes. Do not edit `docs/config-key-lifecycle.md`.

TDD is on: write the tests first and watch them fail on their own assertions.

### 1. Tests first, in `HerdBlockTest` (`tests/test_config_schema.py`)
Model them on `HerdrBlockTest` in the same file: in `setUp`, add `self.schema = jdi_files.schema_block()`,
`self.schema_comments` (schema lines whose `lstrip()` starts with `#`), and
`self.example = jdi_files.read("jdi.config.example.yml").split("\n")`, keeping the existing
`self.schema_keys` and `self.config_text`. `notes` below is
`"\n".join(jdi_files.section(self.config_text, "## Notes"))`, normalized with `" ".join(x.split())`
so wrapped prose matches.

- `test_mode_is_a_schema_key`: `"herd.mode"` in `self.schema_keys`.
- `test_schema_default_is_do`: some schema line matches `^  mode: do$`.
- `test_schema_comment_lists_mode_values`: `"  # do | prep"` is in `self.schema_comments` (the whole line, exactly).
- `test_schema_comment_says_do_merges`: some schema comment line contains `opens its pull request and merges it,`.
- `test_example_mode_is_not_the_default`: some example line matches `^  mode: prep$`.
- `test_defaults_table_covers_herd` (existing): add the tuple ``("herd.mode", "`do`")`` to its loop.
- `test_notes_say_do_mode_merges_unattended`: notes contain ``**`herd.mode: do` opens and merges pull requests unattended.**``.
- `test_notes_say_invalid_mode_runs_prep`: notes contain the fragment, without asterisks,
  ``An invalid `herd.mode` is announced once and runs as `prep` `` (no trailing space; the note
  wraps it in `**`, which the fragment leaves out).
- `test_notes_say_do_and_prep_learn_from_the_invocation`: notes contain `learn they run in a herd from the invocation`.
- Update the class docstring: the block carries `kind`, `mode`, `max_parallel` and `seed`; `mode` is `do | prep`, default `do`, and the example shows `prep` (a non-default value, per `docs/config-key-lifecycle.md`).

### 2. `reference/config.md`
**Schema, after the line `  kind: claude`** (inside `herd:`), insert exactly these 12 lines (M-A).
The first is blank; every other line is byte for byte as shown, at the herd block's two-space
indent (this fence is at column 0, so what you see is what goes in the file):

```yaml

  # do | prep
  #   do   - each agent runs /jdi:do: it reads, plans in chat, builds, verifies,
  #          opens its pull request and merges it, unattended and in parallel
  #          with the others. An agent whose work is too big for one session
  #          continues with /jdi:prep in the same session instead.
  #   prep - each agent runs /jdi:prep and stops at a plan.
  #
  # The repository's own rules still win: where its CLAUDE.md / AGENTS.md says
  # an agent may not merge, a `do` agent stops before the merge. Whether a herd
  # may ship unattended is the team's call: set it in .jdi/config.yml.
  mode: do
```

The existing blank line and `# How many issues one /jdi:herd run…` comment before
`  max_parallel: 5` follow unchanged.

- **Herd intro comment** (the two lines above `herd:` beginning `# Optional. Read only by /jdi:herd, which preps several issues in parallel,`):
  replace with the sentence "Optional. Read only by /jdi:herd, which runs several issues or untracked
  tasks in parallel, one Herdr worktree and agent each." wrapped as `# ` comment lines. Keep the
  `args`/`env` paragraph after it unchanged.
- **Placeholder comments**: append ` (an untracked task: its suffix)` to the `{{issue}}` line and the
  `{{issue_lower}}` line (`#   {{issue}}        the issue ID, e.g. JUT-3073 (an untracked task: its suffix)`).
- **Defaults table**, directly after the `| `herd.kind` | `claude` |` row:
  ``| `herd.mode` | `do` - each herd agent runs `/jdi:do` and merges its own pull request; `prep` stops each at a plan |``
- **`## Notes`**: append to the bullet that starts ``**`herd` is read by `/jdi:herd` and nothing else.**``
  the sentence "`/jdi:do` and `/jdi:prep` learn they run in a herd from the invocation, never from
  this block." Then add two bullets directly after that bullet (M-A, prose may be rewrapped):
  - "**`herd.mode: do` opens and merges pull requests unattended.** Each herd agent runs `/jdi:do`, which treats its request as the authorization to merge, so a `do` herd ships several changes in parallel with nobody approving each one. The repository's own rules still win, and `herd.mode: prep` stops every agent at a plan instead. It is the team's call, so it belongs in `config.yml`."
  - "**An invalid `herd.mode` is announced once and runs as `prep`**, the mode with less authority, never the other way."

### 3. `jdi.config.example.yml`
In `herd:`, between `  kind: opencode` and `  max_parallel: 3`, a two-line comment and the key (the
comment wording is yours; the key line is exact):

```yaml
  # `do` (the default) has each agent open and merge its own pull request,
  # unattended; this repo keeps a person on every merge, so it stops at a plan.
  mode: prep
```

No other file. `tests/test_config_schema.py`'s `ConfigSchemaTest` already requires every schema key
to appear in the example and to have a defaults row; adding the key in all three places keeps it
green.

## Files
- `tests/test_config_schema.py`
- `reference/config.md`
- `jdi.config.example.yml`

## Verification
Run from the repository root.

1. **Red first.** After writing the tests, before editing the two config files: `python3 -m unittest discover -s tests -p 'test_config_schema.py' -v` — expected: `Ran 32 tests`, `FAILED`; the failing methods are exactly the eight new ones plus `test_defaults_table_covers_herd` (its `herd.mode` subtest only); the other 23 pass.
   red when: a new method passes before the edit, or a pre-existing method other than `test_defaults_table_covers_herd` fails.
   at base: `Ran 24 tests`, `OK`.
2. **Green.** The same command after the edits — expected: `Ran 32 tests`, `OK`.
   red when: any test fails (in particular `test_schema_keys_appear_in_the_example` or `test_every_schema_block_has_a_defaults_row`, which mean the key reached one file and not the other).
   at base: `Ran 24 tests`, `OK` (the 8 new methods are written by this task).
3. **The tests bite at the definition site.** In `reference/config.md`, the file that defines the key, change the schema line `  mode: do` to `  mode: prep` and rerun step 2's command — expected: `test_schema_default_is_do` fails. Restore it. Then delete the bullet starting ``**`herd.mode: do` opens and merges`` from `## Notes` — expected: `test_notes_say_do_mode_merges_unattended` fails. Restore it.
   red when: either mutation leaves the module green.
   at base: none — the mutated lines are written by this task.
4. **The key is in all four places.** `grep -rn "herd.mode" reference/config.md jdi.config.example.yml` — expected: hits in `reference/config.md` on the defaults row (``| `herd.mode` | `do` - ``) and on the notes bullets (`` `herd.mode: do` opens``, ``An invalid `herd.mode` ``); the schema and example carry the key as `mode:` under `herd:`, so also run `grep -n '^  mode: ' reference/config.md jdi.config.example.yml` — expected: exactly `reference/config.md:<n>:  mode: do` and `jdi.config.example.yml:<n>:  mode: prep`.
   red when: the first grep prints no defaults row or no notes line, or the second prints anything other than those two lines (a second `mode:` key, or a missing one).
   control: `grep -n '^  max_parallel: ' reference/config.md jdi.config.example.yml` prints two lines (`  max_parallel: 5`, `  max_parallel: 3`), so the anchored pattern finds a herd key when it is there.
   at base: the first grep prints nothing (exit 1); the second prints nothing.
   compliant hits: none beyond the lines named — no other file is in the pathspec.
5. **Full suite.** `python3 -m unittest discover -s tests -v` — expected: every test passes. Task 21 runs beside this one and edits `reference/herdr.md`, `tests/test_herd.py` and `tests/test_herd_record.py`; a failure in those two modules belongs to it while it is unfinished.
   red when: a failure in `tests/test_config_schema.py`, in `tests/test_delegation_transport.py` (`HerdrConfinementTest` scans `reference/config.md`), or in any module Task 21 does not own.
   at base: `Ran 219 tests`, `OK`, no known reds.
