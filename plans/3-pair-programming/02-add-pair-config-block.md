status: done
# 02 — Add the `pair` config block

Depends on: 01

## Why
`/jdi:pair` needs somewhere to read and write which two agents to pair, and that place has to
exist, be documented, and agree with itself before any command can read it. This is the
config-key groundwork every later task in this plan builds on.

## Description
Add a `pair` block to the configuration, following `docs/config-key-lifecycle.md`'s mandatory
three-edit shape for `reference/config.md` plus the example file:

- **Schema block**, in `reference/config.md`, immediately after `tdd:`. One key, `agents`, holding
  free-form prose an agent reads and translates — never a list JDI parses and never a command it
  executes. **There is no `enabled` key.** The comment above `agents:` must say why: running
  `/jdi:pair` is the intent, no other command reads this block, and leaving it empty means
  `/jdi:pair` asks inline and offers to persist the answer. Point the comment at
  `reference/pairing.md` and its P1/P2/P3 operations by name (that file does not exist yet — task
  03 writes it — the comment is naming where the behaviour will live, not asserting it exists).
- **A row in the `## Defaults when nothing is configured` table**: `pair.agents` is empty by
  default, and the row's description says `/jdi:pair` asks which two agents to pair and offers to
  persist the answer.
- **Two `## Notes` invariant bullets**: `pair` has no `enabled` key and no command reads it but
  `/jdi:pair` — a repo that sets it and never runs the command behaves exactly like a repo that
  never set it; and pairing degrades to not pairing, never to a half-pair, because one agent taking
  both sides of a ping-pong is the rubber stamp the protocol exists to prevent.
- **`jdi.config.example.yml`**, set to a deliberately **non-default** value, matching the file's own
  convention of showing a configured repo rather than restating the default: `agents: "claude and
  opencode, both started in this repository"`.

## Files
- `reference/config.md`
- `jdi.config.example.yml`

## Verification
- `python3 -m unittest discover -s tests -v` — expect `Ran 17 tests ... OK`. No new test is added
  in this task: `tests/test_config_schema.py`'s existing bidirectional checks (schema keys appear
  in the example and vice versa, every schema block has a defaults row) already cover any key this
  task adds, in both directions — that is why nothing new needs writing here, not a gap.
- If the schema block is added alone, before the example and the defaults row: expect
  `test_schema_keys_appear_in_the_example` to fail naming `pair` and `pair.agents` (`key_paths`
  emits the parent key alongside its child, so both are reported missing), and
  `test_every_schema_block_has_a_defaults_row`'s `pair` subTest to fail. Once the example and the
  defaults row are added, both go green and the suite returns to `Ran 17 tests ... OK`.
