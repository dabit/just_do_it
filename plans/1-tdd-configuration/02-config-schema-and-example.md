status: pending
# 02 — Add the `tdd` key to the config schema, defaults, notes, and example

Depends on: 01

## Why
This is the acceptance criterion that everything else in the plan hangs off: `.jdi/config.yml`
needs a documented, off-by-default `tdd` setting before any command, role, or the user-facing
init flow can ask about it or read it. Landing the schema, its default, its invariants, and the
worked example together — rather than any one alone — is what keeps the key from shipping
half-documented.

## Description
Add the key:

```yaml
tdd:
  enabled: false
  test_instructions: ""
```

`test_instructions` is free-form prose an agent reads and translates, never a string to execute.
Empty means "work it out from the repo."

Three separate edits to `reference/config.md`:
1. **Schema block** — insert `tdd:` after `split:` (`:42-55`), before `plans:` (`:57`), matching
   the surrounding comment style. Document `test_instructions` explicitly as prose, not a command.
2. **Defaults table** — after `:122`, a row for `tdd.enabled` → `false` and one for
   `tdd.test_instructions` → empty, derived from the repo.
3. **`## Notes`** (`:130-144`) — two bolded invariants:
   - **`tdd` never changes what gets committed.** Tests and implementation land in the same
     commit, one per task, exactly as without it. It changes the order the Executor writes them,
     not history.
   - **`tdd` degrades down to off, never up to on.** An unproven runner, an unreachable
     environment, or an unanswerable ambiguity all mean off for that plan, announced. A repo with
     `enabled: false` is never turned on because a test folder happens to exist.

One edit to `jdi.config.example.yml` — insert after `split:` (`:27-33`) with a **non-default**
value, matching the file's own convention of showing a configured repo rather than the default:

```yaml
tdd:
  enabled: true
  test_instructions: "run `bin/rails test` inside the devcontainer"
```

## Files
- `reference/config.md`
- `jdi.config.example.yml`

## Verification
1. `python3 -m unittest discover -s tests -v` — expect `OK`. The discriminating module is
   `tests/test_config_schema.py`. Its falsifiability control: if the schema block is added but the
   example is not (or vice versa), `test_schema_keys_appear_in_the_example` fails naming
   `tdd.enabled` and `tdd.test_instructions`; if the schema block is added but the Defaults row is
   not, `test_every_schema_block_has_a_defaults_row` fails naming `tdd`. A green run here is
   evidence that neither half of the edit was skipped, not just that nothing crashed.
2. `grep -n "tdd" jdi.config.example.yml` — expect the block present with `enabled: true` (the
   non-default value, per the file's own convention — a bare `false` here would silently reproduce
   the default and teach a reader nothing).
3. `grep -n "degrades down" reference/config.md` — expect one of the two new invariant bullets to
   be present under `## Notes`.
