status: done
# 01 — Add the `herdr.surface` config key

Depends on: None

## Why
Users need a way to pin which Herdr JDI drives, the TUI or the app, in their personal config. Whether Herdr is used at all stays with `delegation.transport`. Every later task reads `herdr.surface`, so the key needs its schema block, defaults row, notes and example. Rests on: D1, P7.

## Description
Planner's Task 1. Add a `herdr:` block with one key, `surface: auto | app | tui`, default `auto`, to the
three places a config key has to appear (`docs/config-key-lifecycle.md` §2). It has no `off` value:
on and off stay with `delegation.transport` (D1). An invalid value is announced once, and only when H1
runs, then treated as `auto`. A pinned `app` or `tui` never falls back to the other surface (P7).

TDD is on: write the tests first, run the module and watch it fail, then edit the docs until it
passes.

**1. Tests first: a new `HerdrBlockTest` in `tests/test_config_schema.py`.** Model it on
`DelegationBlockTest`, which is in the same file and uses the same `setUp`: `schema`,
`schema_comments`, `example` lines, `config_text`. It asserts:
- `"herdr.surface"` is in `jdi_files.key_paths(jdi_files.schema_block())`.
- Some schema line matches `^  surface: auto$`.
- Some schema comment line is **exactly** `  # auto | app | tui`.
- Some schema comment line contains ``Whether Herdr is used at all stays `delegation.transport` ``.
- Some example line matches `^  surface: (app|tui)$`. The example deliberately shows a non-default
  value.
- Some row in `jdi_files.section(config_text, "## Defaults when nothing is configured")` starts with
  ``| `herdr.surface` | `auto` ``.
- `jdi_files.section(config_text, "## Notes")` contains ``**`herdr.surface` only picks which Herdr.**``.

**2. `reference/config.md`.**
- **Schema block.** Insert the block below, verbatim (Appendix A1), after the `delegation:` block
  and before the `herd:` block:

  ```yaml
  # Optional. Which Herdr JDI drives when it uses Herdr: the Herdr TUI or the
  # Herdr desktop app. See reference/herdr.md, H1.
  herdr:
    # auto | app | tui
    #   auto - the Herdr this session runs in. When one runs inside the other,
    #          the innermost wins; when that cannot be told, the TUI.
    #   app  - only the Herdr app is checked.
    #   tui  - only the Herdr TUI is checked.
    #
    # Whether Herdr is used at all stays `delegation.transport` (`native` is
    # off), and /jdi:herd runs only when you invoke it. Which Herdr you run is a
    # fact about your machine: set it in .jdi/config.local.yml.
    surface: auto
  ```
  Inside the schema fence, the block goes at column 0, the same indentation as `delegation:`. The two
  spaces above come only from this list item.
- **Defaults row.** Add a row after the `delegation.transport` row, starting
  ``| `herdr.surface` | `auto` |``.
- **Three `## Notes` bullets:**
  1. Opens with ``**`herdr.surface` only picks which Herdr.**``. It decides between the TUI and the
     app. Whether Herdr is used at all is `delegation.transport`.
  2. **A pinned surface never falls to the other one.** With `app` or `tui` pinned and that surface
     unusable, delegation degrades to `native` and `/jdi:herd` stops. An invalid value is announced
     once, only when H1 runs, and treated as `auto`.
  3. The value is usually personal: set it in `.jdi/config.local.yml`.
- **Confinement.** Task 03 widens `HerdrConfinementTest` to scan `reference/config.md` for
  `herdr-app`, `hc`, `HC_*` and `space|tab|pane|agent.new|split|close|select|focus`. Write "the
  Herdr app" or "the Herdr TUI", and never a binary name, an `HC_` variable or an app command.

**3. `jdi.config.example.yml`.** After the `delegation:` block, add a commented `herdr:` block that
sets `surface: app`. Match the style of the neighbouring blocks: two or three comment lines, then
the block, then a blank line. Example:
```yaml
# Optional. `herdr.surface` picks which Herdr JDI drives: `auto` (the default),
# `app` or `tui`. A fact about your machine: set it in .jdi/config.local.yml.
herdr:
  surface: app
```

## Files
- `tests/test_config_schema.py`
- `reference/config.md`
- `jdi.config.example.yml`

## Verification
1. **Red first.** Before editing any doc, run
   `python3 -m unittest discover -s tests -p 'test_config_schema.py' -v`. Expected: every
   `HerdrBlockTest` method fails or errors, and every other test in the module passes. Use this
   `discover … -p` form: the `tests.<module>` form fails with `ModuleNotFoundError`.
2. **Green.** After the edits, run the same command. Expected: every test passes, including the
   existing `test_schema_keys_appear_in_the_example`, `test_example_keys_appear_in_the_schema` and
   `test_every_schema_block_has_a_defaults_row`.
3. **The tests bite.** Delete the `herdr:` block from `jdi.config.example.yml`, the file that
   carries the example key set, and run the module. Expected: `test_schema_keys_appear_in_the_example`
   fails and names `herdr.surface`, and `HerdrBlockTest`'s example assertion fails. Restore the
   block. Then delete the `herdr.surface` defaults row from `reference/config.md`. Expected:
   `test_every_schema_block_has_a_defaults_row` fails. Restore the row. Then
   `git diff --stat -- jdi.config.example.yml reference/config.md` shows only this task's additions.
4. **Confinement-ready.** Run
   `grep -nE '\bherdr-app\b|\bhc\b|\bHC_[A-Z]|\b(space|tab|pane|agent)\.(new|split|close|select|focus)\b' reference/config.md jdi.config.example.yml`.
   Expected: no output, exit status 1.
5. **Full suite.** Run `python3 -m unittest discover -s tests -v`. Expected: every test passes. The
   one allowed exception is a failure in a test module listed in the `## Files` of a task running
   at the same moment. Any failure in `tests/test_config_schema.py` belongs to this task.
