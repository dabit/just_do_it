status: pending
# 02 - Add the `delegation` block to the config documents

Depends on: None

## Why

Every later task that resolves a transport (the step-0 lines in Task 04, the init question in
Task 05, the herd config in Task 07) reads `delegation.transport`, so the key has to exist in the
schema, the example, and the defaults table before anything can point at it or degrade from it.

Rests on: the Design summary's "The config key" decision ("A new `delegation:` block has one key,
`transport`, with the values `native | auto | herdr` and the default `native`... The key passes the
five-question test in `docs/config-key-lifecycle.md:320-335`") and "What `native` means" ("It is
exactly today's behavior... Nothing is probed at step 0 and nothing is announced").

## Description

Write `tests/test_config_schema.py`'s new class `DelegationBlockTest` first:

- `delegation.transport` is in `key_paths(schema_block())`.
- A schema line matches `^  transport: native$`.
- A schema comment line contains `native | auto | herdr`, and a schema comment line contains "A role
  on this session's own CLI is never affected".
- The `## Notes` section contains "The transport only changes how a role on another CLI runs".
- An example line matches `^  transport: (auto|herdr)$`, which proves the value is non-default.
- The defaults table has a row starting `` | `delegation.transport` | `native` ``.

Confirm it fails (the key does not exist yet), then make three edits to `reference/config.md`:

1. **Schema.** Insert this fenced block, literal except the `<...>` note below, into the `## Schema`
   fence after `harnesses:` (currently ending at line 187, `env: {}` under `opencode:`) and before
   `consumers:` (currently line 189). Line breaks are the block's own; there are no elisions:

   ```yaml
   # Optional. How a delegated role reaches its own process. See
   # reference/delegation.md, "Choosing the transport", and reference/herdr.md.
   delegation:
     # native | auto | herdr
     #   native - the delegation JDI has always done: a subagent where the harness
     #            has one, the CLI's non-interactive mode where `models.<role>.harness`
     #            names another kind, inline otherwise. Herdr is reached only for a
     #            kind with no known non-interactive mode. This is the default, and
     #            the only mode that probes nothing at step 0.
     #   auto   - when this session runs inside Herdr, a role whose
     #            `models.<role>.harness` names another CLI runs as that CLI's
     #            interactive agent in its own Herdr pane, where you can answer it,
     #            and the Butler waits for it. Every Executor of a wave gets its own
     #            pane. Outside Herdr, exactly `native`, and nothing is said.
     #   herdr  - as `auto`, but Herdr is expected: when it cannot be used, JDI says
     #            why, once, and delegates as `native`. The phase still runs.
     #
     # A role on this session's own CLI is never affected: it stays a subagent.
     # Whether you work inside Herdr is usually true of your machine, not the
     # repository: set it in .jdi/config.local.yml.
     transport: native
   ```

2. **Defaults row.** After the `harnesses.*` row (currently the row ending
   `a CLI JDI spawns receives no arguments and no extra environment`), add:
   `` | `delegation.transport` | `native` - roles are delegated exactly as before this key existed;
   nothing is probed at step 0 and nothing is announced | ``.

3. **Invariant bullets under `## Notes`**, inserted after the `harness` degradation bullet (currently
   `**`harness` degrades down, never up.**`, ending "...somewhere less supervised than this
   session."):
   - **`delegation.transport: native` is today's delegation, unchanged.** A repo with no
     `delegation` block behaves exactly as before the key existed.
   - **`auto` and `herdr` are detected once, at step 0, and never repaired.** State H1
     (`reference/herdr.md`, written in Task 01) and the announcement rules.
   - **The transport never grants authority.** A Herdr worker is a separately spawned CLI, and its
     dialogs belong to the user.
   - **The transport only changes how a role on another CLI runs.** A role with no
     `models.<role>.harness`, or one naming this session's own CLI, stays a subagent under every
     value.
   - **The transport degrades to `native`, never beyond.** A failed Herdr run returns the role to
     native resolution for its kind. It never skips the phase, never opens a third CLI, and never
     acquires a flag.
   - **`delegation.transport` is usually personal.** It belongs in `config.local.yml`, because
     working inside Herdr is a fact about the machine.

Two wording corrections in the same file:

- In the `harnesses` comment (currently "...and adds no flag of its own — in particular no approval-
  or sandbox-affecting one."), change to "adds no flag of its own beyond the model flag and the
  invocation JDI needs to reach the CLI, and never an approval- or sandbox-affecting one." Keep "or,
  under Herdr, on the pane", which stays true under H4.
- In the `## Notes` bullet about a value passed to the harness verbatim (currently "**A value in
  `models` is passed to the named harness verbatim.**..."), add that under a separate process,
  including Herdr, the model is passed as the CLI's own model flag, so a full identifier the Agent
  tool's enum cannot express can be expressed there.

Then edit `jdi.config.example.yml`: add a `delegation:` block after `harnesses:` (currently ending at
`env: {OPENCODE_CONFIG_DIR: /home/you/.config/opencode-jdi}` on line 122, before the `consumers`
comment on line 124), with a three-line comment and `transport: auto` - matching the pattern the
schema uses (a short comment, non-default value, per `docs/config-key-lifecycle.md`'s "the example
deliberately disagrees with the schema" convention).

The existing `ConfigSchemaTest` (unchanged) then guards schema/example/defaults agreement in both
directions automatically - no edit needed to that class.

## Files

- `reference/config.md`
- `jdi.config.example.yml`
- `tests/test_config_schema.py`

## Verification

- `python3 -m unittest tests.test_config_schema.DelegationBlockTest -v` - fails before the schema
  edit, passes after all three `reference/config.md` edits and the example edit land.
- `python3 -m unittest tests.test_config_schema.ConfigSchemaTest -v` - passes (schema, example, and
  defaults table agree on `delegation.transport`).
- `grep -n "delegation.transport" reference/config.md jdi.config.example.yml` - each file shows at
  least one hit; read them to confirm the key path matches (`docs/config-key-lifecycle.md:136-139`'s
  grep-the-key check, run early since two more tasks touch this key later).
- `python3 -m unittest discover -s tests -v` - no new failures.
