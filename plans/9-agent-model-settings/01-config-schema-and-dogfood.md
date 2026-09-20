status: done
# 01 — Config schema: per-role `models`, `harnesses`, and the dogfood

Depends on: None

## Why
`agents/*.md` frontmatter hardcodes each role's model, and `.jdi/config.yml`'s three-tier
`models:` block (`deep`/`standard`/`fast`) names no role and is unused in this repo — every deep
role here runs on opus purely because of the frontmatter line a later task deletes. This task
replaces the three-tier schema with a per-role `model:`/`harness:` mapping, adds a `harnesses:`
block for per-CLI args/env, and immediately writes the dogfood into `.jdi/config.yml` so this
repository keeps running on the models it runs on today once the frontmatter comes out. It lands
first, ahead of the frontmatter deletion (task 03), specifically so that window never opens.

## Description
In `reference/config.md`:
1. Replace the three-tier `models:` schema block (currently `:104-111`) with the seven-role
   mapping — one entry per `agents/*.md` stem (`researcher`, `planner`, `splitter`, `executor`,
   `synthesizer`, `pr-writer`, `feedbacker`), each carrying `model:` and `harness:`. Use PLAN.md
   step 1's exact block, in **block form** (two-space-indented mapping) — `tests/jdi_files.py:8-13,
   99-139` parses only block form; a flow mapping (`researcher: {model: x}`) silently loses its
   children and the schema/example symmetry tests would pass while the shape is wrong. There is no
   `models.butler` key — the Butler has no frontmatter and no harness lets a config file change a
   session that is already running. State that absence in the `## Notes` bullets, not as an inline
   comment on the block, so it reads as a decision rather than an oversight.
2. Add a new top-level `harnesses:` block immediately after `models:`, keyed by CLI kind (`claude`,
   `codex`, `opencode`), each carrying `args: []` and `env: {}` — PLAN.md step 2 has the exact
   comment text and fence. Keep `env` as a **flow-mapping leaf** (`env: {}` / `env: {KEY: value}`),
   never block children — writing it as block children changes the key-path shape the schema/example
   symmetry test compares (`harnesses.codex.env.CODEX_HOME` vs. a bare `harnesses.codex.env`), and
   the two files must name the same set of harness kinds or `tests/test_config_schema.py:35-53`'s
   bidirectional set comparison fails in a way that points at the wrong file.
3. Update the defaults table (`:133-147`): replace the old `models.*` row and add a `harnesses.*`
   row (exact wording in PLAN.md step 3).
4. Add the four bolded invariant bullets under `## Notes` (PLAN.md step 4): `models` is the only
   place a role's model is named; a value is passed to the named harness verbatim; `harness`
   degrades down, never up; there is no `models.butler`.
5. Recast `## Example tier mappings` (`:120-131`) as `## Example model mappings` (PLAN.md step 5):
   three columns — Claude Code aliases, Codex/OpenAI full identifiers, a mixed column that sets
   `harness:` on a role — with the framing sentence that the value is handed to the harness that
   will run the role, exactly as written.

In `jdi.config.example.yml`, replace `:67-73` with the seven-role example and the two harness
entries from PLAN.md step 6 — a real, non-default mix (per `docs/config-key-lifecycle.md:79-83`'s
example convention), not the current `deep: ""`. The schema and the example must name the same
three harness kinds (`claude`, `codex`, `opencode`).

In `.jdi/config.yml`, append the dogfood block (PLAN.md step 7) after the `git:` block, which
currently ends the file at `:55`: all seven roles, using Claude Code's **aliases** (`opus`/`sonnet`)
— the exact values `agents/*.md` frontmatter carries today (`agents/executor.md:17`,
`agents/feedbacker.md:18` both `opus`; `agents/splitter.md:17`, `synthesizer.md:16`,
`pr-writer.md:17` all `sonnet`) — and **no `harness:` key**. Do not write full model identifiers
here: Claude Code's Agent tool takes `model` as an enum and cannot accept a full identifier like
`claude-opus-5` at spawn time, so writing one would regress this repo's primary harness on day one.
No `harnesses:` block is added to `.jdi/config.yml` either — no role here names another harness.

**Tests, same commit.** In `tests/test_config_schema.py`, add:
- **T-A** — a bidirectional set comparison: the seven `models.<stem>` keys match the
  `agents/*.md` stems exactly, in both directions. This is also what enforces `models.butler`'s
  absence, since `butler` lives in `roles/`, not `agents/`, and would fail the stale-key direction.
- **T-B** — every `models.<stem>` carries both a `.model` and a `.harness` child key.

Both are red against today's three-tier block (`deep`/`standard`/`fast`) and green once step 1
lands. No change to `tests/jdi_files.py` is needed — `key_paths`'s hyphen handling already parses
`models.pr-writer`, and the existing `models.*` prefix match at `tests/test_config_schema.py:83-93`
already covers per-role children.

## Files
- `reference/config.md`
- `jdi.config.example.yml`
- `.jdi/config.yml`
- `tests/test_config_schema.py`

## Verification
- `python3 -m unittest discover -s tests -v` — baseline was 47 tests, OK. Expect **at least 49
  tests, OK** (T-A and T-B, possibly split across more than one test method each), 0 failures, 0
  errors. The existing schema/example/defaults symmetry tests (T-C) must also still pass — they
  become load-bearing here for the `harnesses` block's set-equality and defaults-row constraints.
- Open `reference/config.md` and `jdi.config.example.yml` side by side — confirm both name the same
  seven role keys under `models:` and the same three harness kinds (`claude`, `codex`, `opencode`)
  under `harnesses:`. (T-A/T-C already assert this programmatically; this is a human sanity check,
  not a substitute for running the suite.)
- `grep -ciE '\btiers?\b' reference/config.md` — expect `0`. This task removes every "tier" occurrence from
  this specific file (the old schema comment, the `## Example tier mappings` heading, the old
  defaults row). The word may still appear elsewhere in the repo until later tasks (02–06) remove
  it there — this check is scoped to `reference/config.md` only, not the whole tree.
- `cat .jdi/config.yml` — confirm the appended `models:` block lists all seven roles with alias
  values (`opus` or `sonnet`, matching the frontmatter values named above) and **no `harness:` key**
  anywhere in the block.
