# Configure each agent's model in settings, not in the agent frontmatter

- Tracker: GitHub Issues
- Project: feature development
- Issue: 9
- Issue URL: https://github.com/dabit/just_do_it/issues/9
- Created: 2026-09-20
- Base commit: origin/main @ 815dfaeb1f67f1a142c9e04e2ca0c65459484c7f
- Summary: Replace the three-tier `models:` block and the hardcoded `model:` frontmatter in `agents/*.md` with a per-role mapping in `.jdi/config.yml` carrying both `model:` and `harness:`, making settings the single place a role's model — and the agent CLI it runs in — is named.
- Started: 2026-09-20
- TDD: on — proven 2026-09-20 with `python3 -m unittest discover -s tests -v`

## References

Research was produced against base commit `815dfae`. Every `file:line` below was opened and
spot-checked by the Butler; a later change to the base commit invalidates them.

### The two-place arrangement being collapsed

- `agents/*.md` — the seven frontmatter `model:` lines: `researcher.md:18`, `planner.md:18`,
  `executor.md:17`, `feedbacker.md:18` (`opus`); `splitter.md:17`, `synthesizer.md:16`,
  `pr-writer.md:17` (`sonnet`). Note they are **aliases**, not full identifiers.
- `roles/butler.md:3` — "**Tier: fast — but the Butler is never spawned.**" The Butler has no
  frontmatter at all and cannot have its model set by config.
- `reference/config.md:104-111` — the three-tier `models:` schema block; `:120-131` the
  `## Example tier mappings` three-column fence (full IDs, `claude-opus-5`); `:146` the defaults
  row; `:149-170` `## Notes`, which has **no** `models` invariant bullet today.
- `reference/delegation.md:72-73` — "It is the authority", false once the block is per-role;
  `:75-79` the three-rung fallback ladder whose **rung 1 is the frontmatter default** this change
  deletes; `:86-92` `## Harness-specific metadata`, which says a concrete model name belongs in
  frontmatter — directly inverted.
- `jdi.config.example.yml:67-73` — ships `deep: ""`, the default, violating the example convention
  at `docs/config-key-lifecycle.md:79-83`.
- `.jdi/config.yml` — has **no** `models:` block. This repo's roles run on opus purely by
  frontmatter, so the dogfood edit is required or JDI regresses on itself.

### Tier vocabulary — the removal surface

- `commands/*.md` — 11 "Delegates to: X (tier)" header lines (`research.md:8`, `reresearch.md:8`,
  `feedback.md:8`, `prep.md:9`, `execute.md:8`, `yolo.md:8`, `next.md:8`, `split.md:8`,
  `replan.md:8`, `plan.md:8`, `pr.md:9`) and 14 "at the **X** tier" hand-off sentences
  (`research.md:34,57`, `feedback.md:31`, `prep.md:104,120,136,156`, `execute.md:61`,
  `yolo.md:77`, `next.md:53`, `split.md:57`, `plan.md:64`, `pr.md:43,81`).
- `commands/help.md:2,23,25-39,113-118` — the `Tier` column and `### Tiers, not models`.
- `README.md:12,288,292,304-323` — including the heading `### Roles and tiers, not agents and
  models` and `:322-323` "Concrete model names … live only in YAML frontmatter".
- `AGENTS.md:44`, `commands/init.md:13,102-106`, `bin/sync-opencode.sh:78-81`.
- `reference/delegation.md:62-70` — the `## Tiers` table. **Keep its content**: it is the only
  place stating what each phase wants from a model. Recast per-role, do not delete.
- **Do not touch** `CHANGELOG.md:127-128` (historical 1.0.0 note) or the false positives
  "deep-dive" (`agents/researcher.md:4,24`), "standard language idiom" (`agents/planner.md:70`),
  "standard-library" (`CHANGELOG.md:67`), "data models" (`commands/research.md:58`).

### Cross-harness delegation

- `reference/delegation.md:44-46` — rung 2, "The harness has no subagents, but can run a second
  session … Shell out to it with the role file and the inputs as the prompt". This change makes
  rung 2 a **selected** path, not a fallback for a deficient harness.
- `reference/delegation.md:58-60` — "Subagents and fallback sessions stay inside the active
  sandbox, approval policy, and authorization boundaries." **True for rung 1 and 3, false for
  rung 2**; a spawned CLI resolves its own policy from its own config.
- `docs/harness-adapter-architecture.md:238-257` — "Capability-Based Delegation": restates the
  same three rungs at `:243-245` and repeats the authorization claim at `:256-257`. Must be
  amended in step with `delegation.md` or the two documents disagree.
- `docs/harness-adapter-architecture.md:173-197` — "Portable Root Resolution"; `:191-194` forbids
  searching ancestors for a plausible checkout, which rules out deriving a path across
  version-pinned plugin snapshots.
- `roles/butler.md:15` (pass exactly the declared inputs), `:18-20` (verify before relaying —
  applies doubly to a cross-harness report), `:23-25` (announce every skip, once).
- `bin/sync-opencode.sh:76-81` (`AGENT_DROP = {"model", "tools"}`), `:119-121`
  (`${CLAUDE_PLUGIN_ROOT}` rewrite), `:140-146` (`jdi-<stem>`, `mode: subagent`).

### Verified harness capability (this machine, 2026-09-20)

- `codex exec`: `-m/--model`, `-o/--output-last-message <FILE>` (lossless final message),
  `--json`, `--output-schema`, `-s/--sandbox`, `--dangerously-bypass-approvals-and-sandbox`.
- `opencode run`: `-m/--model provider/model`, `--agent <name>`, `--format json`, `--dir`,
  `--auto` ("auto-approve permissions … (dangerous!)").
- OpenCode already registers the roles by name: `~/.config/opencode/agent/jdi-*.md`.
- Codex snapshot is **version-pinned**: `~/.codex/plugins/cache/just-do-it/jdi/1.0.4/`; Claude's
  is `~/.claude/plugins/cache/just-do-it/jdi/1.0.4.1/`. The two share no derivation rule.
- `herdr` 0.9.0, `HERDR_ENV=1`, socket at `~/.config/herdr/herdr.sock`. Statuses are exhaustively
  `idle | working | blocked | done | unknown`; `unknown` does not prove completion.
  `herdr agent read` is a terminal scrape in every mode and **cannot recover rows lost to the
  alternate screen** — a role's long prose report does not survive it reliably.
- Negative cases available for UAT without breaking anything: `qwen` not installed (CLI absent
  rung); `gemini` installed but with no JDI (instructions-unresolvable rung).
- **Claude Code's own Agent tool takes `model` as an enum** (`sonnet | opus | haiku | fable`),
  not a free-form identifier — so a config value of `claude-opus-5` cannot be passed at spawn
  time in this harness. This closes the researcher's `UNVERIFIED-EXTERNAL` item by schema rather
  than by probe, and makes the "model this harness cannot express" rung a certainty.

### Prior art and procedure

- `plans/1-tdd-configuration/PLAN.md:114-124` — the 8-batch decomposition for a config key of this
  shape; `:52-53` "the Executor never reads `.jdi/config.yml`" — the Butler resolves and passes a
  value; `:102-104` self-caused citation rot is fixed in the task that causes it; `:139-142` no
  test observes command or role body prose, so prose changes need UAT; `:191-197` the
  "deliberately out of scope, with reasons" closing section.
- `plans/7-codex-skill-model/PLAN.md:53-61` — capability-based delegation prose and the
  four-authority release; `:88-96` the `UNVERIFIED — Issue #<n>` idiom for live-harness claims.
- `docs/config-key-lifecycle.md:52-68` the nine-file floor; `:212-248` the degradation idiom;
  `:288-299` §5's frontmatter rule, **inverted by this change and owed an amendment**;
  `:327-362` release mechanics.
- `origin/herd-command:commands/herd.md:29-44` the four-check Herdr validation ladder;
  `:187-195` args pass-through and the bypass-flag warning; `:266-273` the standing limits,
  including "**JDI itself must be installed there**".
- `origin/herd-command:reference/config.md:113-148` the `herd:` block (`kind`, `max_parallel`,
  `args` keyed by agent kind, `env`, `seed`); `:244-256` its stated rules. **PR #5 is open and
  unmerged, and its branch predates `815dfae`.**

### Tests

- `tests/test_frontmatter.py` — checks delimiters, a single `description:`, a non-empty body.
  **Nothing asserts `model:` is present**, so removing the seven lines breaks no test.
- `tests/jdi_files.py:179-194` — `schema_block()` scopes to the first fence under `## Schema`
  precisely because the example mappings fence would otherwise be read as schema keys. `key_paths`
  handles hyphenated keys, so `models.pr-writer` parses; the `models.*` prefix-match in
  `tests/test_config_schema.py:83-93` already covers per-role children. **No helper change needed.**
- `tests/test_codex_plugin.py:204` pins the literal `"the tier's model from the config"` and
  `:295` calls `normalized_section("### Roles and tiers, not agents and models")`, which **raises**
  when the heading is absent (`jdi_files.py:152-153`). Both go red on the prose edits and must be
  rewritten in the same task.
- `tests/test_versions.py:59-97` pins headings and phrases in `docs/config-key-lifecycle.md` §2
  and §6 — amend §5 freely, but **do not renumber or restructure its section headings**.
- `tests/test_enumerations.py:84-107` only requires each delegation-table row to backtick its
  `agents/*.md` file, so replacing the `Tier` column is safe.
- Baseline: **47 tests, OK** (`python3 -m unittest discover -s tests -v`).

### Release

- `.claude-plugin/plugin.json:3`, `.codex-plugin/plugin.json:3`,
  `.claude-plugin/marketplace.json:10`, `CHANGELOG.md:3` — all `1.0.4`; next is `1.0.5`.
  `docs/config-key-lifecycle.md:338-340` requires a key **removal** to be stated deliberately in
  the CHANGELOG rather than inferred from convention.

## Implementation Plan

Eight batches, dependency-ordered. Adapted from `plans/1-tdd-configuration/PLAN.md:114-124` with one deliberate deviation, stated in batch 01.

`.jdi/config.yml:34` sets `tdd.enabled: true`, and `reference/config.md:62-64` says tests and implementation land in the **same commit**. There is therefore **no standalone test batch**: every test is attributed to the batch whose behaviour it proves and is written red first inside it.

**No commit in this plan ships a failing suite.** An earlier draft had the vocabulary guard (T-H) written in batch 02 and left knowingly red until batch 06, as a progress meter. That is withdrawn: `reference/config.md:62-64` requires tests and implementation in the **same commit**, and `/jdi:yolo` stops on the first failing task, so a deliberately-red commit would halt the run at batch 03. T-H is written in **batch 06**, the batch that makes it green. Batches 02–05 use the manual grep in its place — it is in the Risks section and in each batch's own step.

### Batch 01 — the config schema, the example, and the dogfood

**Deviation from the precedent, deliberate.** `plans/1-tdd-configuration/PLAN.md:120` put the dogfood edit in the release batch. Here it moves to batch 01. Batch 03 deletes the seven `model:` frontmatter lines, and `.jdi/config.yml` has no `models:` block today, so any ordering that puts the dogfood after batch 03 opens a window in which JDI regresses on itself on its own branch. The dogfood depends only on the schema, so it belongs here. Batch 07 re-verifies it rather than writing it.

1. **`reference/config.md` — replace the `models:` schema block.** Delete `:104-111` (the three-tier block) and write the per-role mapping in its place, inside the same fence under `## Schema`. Seven entries, one per `agents/*.md` stem, each carrying **both** `model:` and `harness:`:

   ```yaml
   # Optional. Names the model each role runs on, and optionally the agent CLI
   # it runs in. A role with no entry — or a whole block that is absent — runs
   # in this session's harness on whatever model the session is already using.
   # That is a supported configuration, not a degraded one.
   # See reference/delegation.md for what each role wants from a model and for
   # what happens when an entry cannot be honoured.
   models:
     researcher:
       model: ""
       harness: ""
     planner:
       model: ""
       harness: ""
     splitter:
       model: ""
       harness: ""
     executor:
       model: ""
       harness: ""
     synthesizer:
       model: ""
       harness: ""
     pr-writer:
       model: ""
       harness: ""
     feedbacker:
       model: ""
       harness: ""
   ```

   **There is no `models.butler`.** `roles/butler.md` has no frontmatter, `reference/delegation.md:23` says the Butler is never spawned, and no harness lets a config file set the model of a session that is already running. The absence is stated in `## Notes` (step 4) so a reader does not read it as an oversight.

   **Block form is mandatory, not stylistic.** `tests/jdi_files.py:8-13` and `:99-139` read a plain two-space-indented mapping only. A flow mapping (`researcher: {model: x}`) yields the key path `models.researcher` and silently loses its children, which would break the schema/example symmetry tests in a way that looks like a passing test.

2. **`reference/config.md` — add the `harnesses:` block.** New top-level block, immediately after `models:`, keyed by agent-CLI kind:

   ```yaml
   # Optional. Per-CLI settings, keyed by the kind that a `models.<role>.harness`
   # names. `args` are handed to that CLI verbatim, after its own flags; `env` is
   # set on the process — or, under Herdr, on the pane — that runs it.
   #
   # Both are passed through exactly as written. JDI never composes, merges, or
   # translates them between kinds, and adds no flag of its own — in particular
   # no approval- or sandbox-affecting one. Anything of that kind is a value you
   # wrote here, and JDI prints it back before it spawns anything.
   #
   # Write absolute paths: a leading "~" arrives as a literal tilde.
   #
   #   harnesses:
   #     codex:
   #       args: ["--sandbox", "workspace-write"]
   #       env: {CODEX_HOME: /home/you/.codex-other}
   harnesses:
     claude:
       args: []
       env: {}
     codex:
       args: []
       env: {}
     opencode:
       args: []
       env: {}
   ```

   **Two constraints the Executor must respect or the suite fails in a confusing direction.** (a) The schema and `jdi.config.example.yml` must name the **same set of kinds**; `tests/test_config_schema.py:35-53` compares key-path sets in both directions and `KNOWN_OMISSIONS` (`:22`) only forgives schema-not-in-example, not the reverse. (b) `env` must stay a **leaf flow mapping** (`env: {}` / `env: {KEY: value}`). Writing it as block children makes `key_paths` emit `harnesses.codex.env.CODEX_HOME`, which then has to match between the two files exactly. `args` is safe either way, because `- item` lines do not match `tests/jdi_files.py:99`'s `_KEY` and are skipped. `origin/herd-command:reference/config.md:137,148` is the precedent for the flow-leaf form.

3. **`reference/config.md` — defaults table** (`:133-147`). Replace `:146` and add one row:

   | `models.*` | empty — every role runs in this session's harness, on the session's own model |
   | `harnesses.*` | empty — a CLI JDI spawns receives no arguments and no extra environment |

   `tests/test_config_schema.py:65-78` will now demand the `harnesses` row; `:80-100` handles the `.*` suffix by prefix match, so both rows are legal.

4. **`reference/config.md` — four bolded invariant bullets under `## Notes`** (`:149-170`), which has no `models` invariant today:
   - **`models` is the only place a role's model is named.** No file under `agents/` carries a `model:` key. A role with no entry runs on the session's own model.
   - **A value in `models` is passed to the named harness verbatim.** Write the identifier that harness accepts: Claude Code's Agent tool takes an alias (`opus`, `sonnet`, `haiku`), while Codex and OpenCode take full identifiers. A model the harness cannot express is **announced** and the role runs on that harness's own default; it is never silently swapped for a different one.
   - **`harness` degrades down, never up.** An unreachable CLI, an unresolvable role instruction, or a transport that never reported means the role runs here instead, announced once. It never means the phase is skipped, never means JDI acquires a flag the user did not write, and never means the role lands somewhere less supervised than this session.
   - **There is no `models.butler`.** The Butler is the session you are already in, and no harness lets a config file change the model of a session that is already running. Its absence is deliberate, not an omission.

5. **`reference/config.md` — recast `## Example tier mappings`** (`:120-131`) as `## Example model mappings`. Replace the three-column fence. Show the enum constraint as a user-facing instruction rather than a trap: one Claude Code column using **aliases**, one Codex/OpenAI column using full identifiers, and one mixed column that sets `harness:` on a role. State above the fence: *the value is handed to the harness that will run the role, exactly as written — so write the identifier that harness accepts.*

6. **`jdi.config.example.yml` — replace `:67-73`.** Per `docs/config-key-lifecycle.md:79-83` the example must show a **configured**, non-default value; the current file ships `deep: ""`, which is the default and teaches nothing. Write all seven roles with both keys and a real mix, plus the two harness kinds with real values:

   ```yaml
   models:
     researcher:
       model: gpt-5.1-codex-max
       harness: codex
     planner:
       model: opus
       harness: ""
     splitter:
       model: qwen3-coder
       harness: opencode
     executor:
       model: opus
       harness: ""
     synthesizer:
       model: sonnet
       harness: ""
     pr-writer:
       model: sonnet
       harness: ""
     feedbacker:
       model: gpt-5.1
       harness: codex

   harnesses:
     claude:
       args: []
       env: {}
     codex:
       args: ["--sandbox", "workspace-write"]
       env: {}
     opencode:
       args: []
       env: {OPENCODE_CONFIG_DIR: /home/you/.config/opencode-jdi}
   ```

   The schema and the example must name the **same three kinds** — `claude`, `codex`, `opencode` — per the set-equality constraint in step 2.

   Two things this example is deliberately teaching: `harness: ""` on four of seven roles shows that omitting it is the normal case, and putting the Feedbacker on a different provider from the Executor is a worked instance of the producer/reviewer rule that survives from `reference/delegation.md:81-84`.

6b. **`.jdi/config.yml:2`** — the header comment reads `# Schema, defaults, and example tier mappings: reference/config.md` and names the heading step 5 just renamed. Update it to `example model mappings`. Self-caused citation rot, fixed in the task that causes it (`plans/1-tdd-configuration/PLAN.md:102-104`).

7. **`.jdi/config.yml` — the dogfood, appended after the `git:` block (the file currently ends at `:55`).** Reproduce exactly what the frontmatter gave each role, using Claude Code's aliases, and set no `harness:`:

   ```yaml
   # Claude Code's Agent tool takes a model alias, not a full identifier, so
   # these are aliases — the same values agents/*.md frontmatter carried before
   # 1.0.5. No `harness:` is set: every role runs in whatever harness this
   # session is. Another harness will say once that it cannot express these and
   # run the role on the session's own model.
   models:
     researcher:
       model: opus
     planner:
       model: opus
     splitter:
       model: sonnet
     executor:
       model: opus
     synthesizer:
       model: sonnet
     pr-writer:
       model: sonnet
     feedbacker:
       model: opus
   ```

   **Why aliases and not full identifiers.** Claude Code is this repo's primary harness and its Agent tool takes `model` as an enum, so `claude-opus-5` cannot be passed at spawn time there — writing full identifiers would regress the primary harness on day one. Aliases give exact parity with `agents/*.md:17-18` under Claude Code, and under Codex/OpenCode they are unreachable, which is precisely what happens today (the OpenCode adapter strips `model:` at `bin/sync-opencode.sh:81`, and Codex never read the frontmatter). Strict non-regression in every harness, with a new announcement where there used to be a silent drop. No `harnesses:` block is added here: no role names another harness, and `commands/init.md:113-114` already says to omit optional blocks rather than write empty scaffolding. `.jdi/config.yml` is not read by any test — only `reference/config.md` and `jdi.config.example.yml` are — so asymmetry here is safe.

   Note that Executor and Feedbacker are both `opus`, which is what `agents/executor.md:17` and `agents/feedbacker.md:18` already give them. Keeping that is the non-regression choice; changing it is a separate decision, not this change's.

**Tests in this batch** (red first, same commit): the bidirectional role-stem test and the per-role shape test in `tests/test_config_schema.py`. See Testing Strategy.

**Files:** `reference/config.md`, `jdi.config.example.yml`, `.jdi/config.yml`, `tests/test_config_schema.py`.

---

### Batch 02 — `reference/delegation.md`: the ladder, the correction, the recast

This is the largest single edit and the load-bearing artifact. The file is rewritten section by section; the section order below is the proposed final structure.

8. **Title and intro** (`:1-6`). `# Delegation and model tiers` → `# Delegation and models`. The intro's claim that the prose "names a **role** and a **tier**" becomes: it names a **role**, and `.jdi/config.yml` says what that role runs on and where.

9. **`## Roles` table** (`:10-24`). Drop the `Tier` column; keep `Role | Definition`. `tests/test_enumerations.py:84-107` only requires each row to backtick its `agents/*.md` path inside the `## Roles` section, so dropping a column is safe. Keep the Butler row and the "never spawned" paragraph at `:23-24` verbatim.

10. **Recast `## Tiers` (`:62-70`), do not delete it.** New heading `## What each role wants from a model`, seven rows, `Role | For | Wants`. Carry the three existing `Wants` cells (`:68-70`) forward, redistributed per role — this is the only place in the repo that states what each phase wants from a model, and it is exactly the guidance a user needs in order to fill in seven keys. **Do not use the phrase "mid-tier"**: T-H, the vocabulary guard written in batch 06, forbids the word, and a term introduced here would fail it there.

11. **`## How to delegate`** (`:26-56`) — the in-session capability ladder stays, with rung 2 promoted from fallback to selected path.
    - Rung 1 heading `**1. The harness has first-class subagents**` — **keep verbatim** (pinned at `tests/test_codex_plugin.py:198`).
    - `:36` and `:39` "the tier's model from the config" → **"the role's model from the config"** (both occurrences).
    - Rung 2 heading `**2. The harness has no subagents, but can run a second session**` → **`**2. A second non-interactive session**`**, with body saying this is now a *chosen* path when `models.<role>.harness` names a different kind, not only a fallback for a deficient harness.
    - Rung 3 heading `**3. Neither.** **Adopt the role inline.**` — **keep verbatim** (pinned at `:200`).
    - `:53-56`'s "Do not silently skip a role because delegation is unavailable" — keep.

12. **New section `## Where a role runs`.** `models.<role>.harness` names a key in `harnesses:`. Resolution is **exec-first, Herdr second**:
    - **Prefer the CLI's own non-interactive mode.** It returns a lossless report, allocates no pane, and leaves nothing to clean up. The two JDI knows:
      - `codex` → `codex exec -m <model> -o <file> "<prompt>"`, then read `<file>`. Verified flags: `-m/--model`, `-o/--output-last-message`.
      - `opencode` → `opencode run -m <provider/model> --agent jdi-<role> --format json "<prompt>"`. Verified flags: `-m/--model`, `--agent`, `--format json`.
      - `claude` → `claude -p --model <alias> --output-format json "<prompt>"`. Verified flags: `-p/--print`, `--model`, `--output-format text|json|stream-json`. This matters for the reverse direction: a **Codex or OpenCode** session can put a role back on Claude, so `harness: claude` is a first-class value and not merely the no-op case of `harness:` naming the session's own kind.
    - **Use Herdr only** when the kind has no exec mode JDI knows, or when the user has asked to watch the run. Drive it with `herdr pane split` → `herdr pane run <PANE_ID> <command>` → `herdr pane wait-output --match <sentinel> --timeout <ms> <PANE_ID>` → read the file the command was told to write. **Not `herdr agent start`**, which is the primitive for an interactive occupant. `herdr agent read` is a terminal scrape in every mode and cannot recover rows lost to the alternate screen, so a role's prose report must arrive through a file, never through the pane buffer.
    - **A pane JDI created is JDI's to close.** Every exit from a Herdr path — success, timeout, or any of the failure rungs below — runs `herdr pane close <pane_id>` before it announces. A failed delegation must not leak a pane per attempt.
    - **Role-instruction portability.** Name the target's registered role where it has one (`opencode run --agent jdi-<role>`; the files exist at `~/.config/opencode/agent/jdi-*.md`, produced by `bin/sync-opencode.sh:140-146`). Otherwise **inline the role file** — read the installed `agents/<role>.md` and pass its text as part of the prompt. Take a path **only from an explicit config value, never derived**: the Codex snapshot is version-pinned (`~/.codex/plugins/cache/just-do-it/jdi/1.0.4/`), Claude's is `.../1.0.4.1/`, the two share no derivation rule, and `docs/harness-adapter-architecture.md:191-194` forbids searching ancestors for a plausible checkout.

13. **Rewrite the authorization paragraph** (`:58-60`). The current text is false for a spawned CLI and must be replaced with a form that is true at every rung:

    > Delegation never grants additional authority, and JDI never composes any. An in-harness subagent and an inline adoption run inside this session's own sandbox and approval policy. **A separately spawned CLI does not** — it is another process that resolves its own sandbox, approval policy and credentials from its own configuration, which may be broader or narrower than this session's. JDI composes no authority-affecting flag and translates none between kinds: every flag a spawned CLI receives is a literal value the user wrote in `harnesses.<kind>.args`, passed through verbatim and **printed back before the spawn**. Any external mutation must still be allowed by the active command and the Butler's rules.

    `docs/harness-adapter-architecture.md:256-257` carries the same false claim and is corrected in batch 06. **Both sites are part of one change**; if only one lands, the two documents disagree.

14. **New section `## When the configuration cannot be honoured` — the degradation ladder.** This is the artifact the whole change rests on. It follows the idiom at `docs/config-key-lifecycle.md:212-248`: first rung that applies wins, announced once, degrade down only, silent when nothing was skipped, capability proven rather than assumed.

    Open with the two-phase framing, because it is what makes the one-announcement rule applicable rather than merely agreeable:

    > Rungs 1–9 settle **where** the role runs. Rungs 10–12 settle **which model** it runs on, inside wherever 1–9 landed. When a harness rung and a model rung both fire — which is the common case, because a model chosen for another CLI is usually one this harness cannot express — that is **one announcement, not two**: name what was configured, what was reachable, and what the role is actually about to run on.

    The ladder:

    1. **No `harness:` for this role.** Run it in this session's harness. **Silent** — nothing was configured and nothing was skipped.
    2. **`harness:` names this session's own kind.** Delegate normally, rung 1 of *How to delegate*. **Silent** — the configuration was honoured.
    3. **The named CLI is not on `PATH`.** Announce and go to the floor. Detection is an observation: resolve the binary, do not infer from a failed run.
    4. **JDI knows no non-interactive exec mode for that kind.** Try the Herdr transport (rungs 6–8). If Herdr is unavailable, announce and go to the floor.
    5. **The role's instructions cannot be resolved for that CLI.** No registered role name, and the installed `agents/<role>.md` cannot be read to inline. Announce and go to the floor. **Never derive a plugin path** to close this gap.
    6. **Herdr is wanted but not detected** — no binary, no `HERDR_ENV`, or no server answering on the socket. Announce and go to the floor.
    7. **Herdr does not report the kind installed.** Announce and go to the floor. Herdr's `kinds:` line is the observation; an absent kind is not a reason to try anyway.
    8. **The pane cannot be created.** Announce and go to the floor. Nothing to close.
    9. **The run started but never reported usably** — the output file was never written, or the status stayed `unknown` with nothing readable. Herdr's statuses are exhaustively `idle | working | blocked | done | unknown`, and `unknown` does **not** prove completion. **Close the pane JDI opened**, announce, go to the floor.
    10. **The model cannot be expressed in the harness that will run the role.** Claude Code's Agent tool takes `model` as an enum (`sonnet | opus | haiku | fable`), so a full identifier like `claude-opus-5` cannot be passed at spawn time there; another kind may reject an unprefixed name. This is knowable **before** the spawn, from the harness's own schema. Announce and run the role on that harness's default model. Never substitute a different identifier and never silently drop it.
    11. **The configured model is unreachable** — authentication, quota, or a retired identifier. Knowable only after the attempt. Announce and run on the harness's default.
    12. **The floor.** Run the role in this session's harness, on its configured model if this session can both express and reach it, otherwise on the session's own model — adopting the role inline if there are no subagents. **The phase always runs.**

    Then close the destructive directions explicitly, which is the part `docs/config-key-lifecycle.md:223-228` requires by name:

    - **Never skip the phase.** A phase that never ran is the failure; the mechanism it ran through is not. The floor is always available.
    - **Never acquire a flag the user did not write.** JDI adds no argument of its own and translates none between kinds. A permission-bypass flag in `harnesses.<kind>.args` is a thing the user typed, and it is printed back before the spawn.
    - **Never land somewhere less supervised.** Degrading a harness means coming **back into this session**, which is the most supervised place available — never onward to a third CLI, and never into a broader approval policy in order to make a spawn succeed.
    - **Never promote a model.** An unreachable model falls to the session's or the harness's default. It is never swapped for a stronger or more expensive one because that one happened to be reachable.

    Finally, the **old-shape detection sentence**, which is what keeps the upgrade path from being the silent regression this whole change exists to prevent:

    > A `models:` block whose keys are `deep`, `standard` and `fast` is the pre-1.0.5 shape. It names no role, so **nothing in it is read**. Say so once, name `reference/config.md` as the current schema, and run every role on the session's own model for that run.

15. **Rewrite `## Harness-specific metadata`** (`:86-92`). Its claim that "a concrete model name … lives in a file's YAML frontmatter" is directly inverted by this change. The rule that survives: harness-specific *frontmatter* (tool allowlists, argument hints) still belongs in frontmatter and is still stripped by adapters; a **model name now belongs in `.jdi/config.yml` and nowhere else**, because it is a fact about the user's account and harness rather than about the file.

16. **Tests in this batch.** Rewrite `DelegationGuidanceTest` (`tests/test_codex_plugin.py:173-209`) in this same commit — it is not allowed to be observed going red in a later batch. **Do not write T-H here**: the vocabulary guard cannot pass until batch 06 removes the last tier word, and no commit in this plan ships a failing suite. Verify this batch's share of the vocabulary removal with the manual grep instead. Full detail in the Testing Strategy.

**Files:** `reference/delegation.md`, `tests/test_codex_plugin.py`. (**Not** `tests/test_enumerations.py` — T-H is written in batch 06, the batch that makes it green.)

---

### Batch 03 — the frontmatter comes out

17. **Delete the seven `model:` frontmatter lines**: `agents/researcher.md:18`, `agents/planner.md:18`, `agents/executor.md:17`, `agents/feedbacker.md:18`, `agents/splitter.md:17`, `agents/synthesizer.md:16`, `agents/pr-writer.md:17`. Nothing else in those files changes; `tools:` stays. After batch 01 the models come from `.jdi/config.yml`, so this is behaviour-neutral in this repo under Claude Code.

18. **`roles/butler.md:3`** — `**Tier: fast — but the Butler is never spawned.**` → `**The Butler is never spawned.**` The Butler has no model key and the vocabulary guard forbids the word.

19. **`bin/sync-opencode.sh:78-81`** — reword the comment. It currently says "JDI's tiers live in prose and in .jdi/config.yml, not in this frontmatter", which names a concept that no longer exists. **Keep `AGENT_DROP = {"model", "tools"}` unchanged**: with no `model:` left to strip it is a no-op, but it is defensive against a role file reacquiring one, and removing it would be a behaviour change in an adapter for no gain. New comment should say models are resolved from `.jdi/config.yml` by the Butler and never appear in a role file's frontmatter, and that `model` stays in the drop set as a guard.

20. **Tests in this batch** (red first, same commit): the no-`model:`-frontmatter assertion in `tests/test_frontmatter.py`, plus a characterization assertion in `tests/test_opencode_sync.py`. See Testing Strategy.

**Files:** all seven `agents/*.md`, `roles/butler.md`, `bin/sync-opencode.sh`, `tests/test_frontmatter.py`, `tests/test_opencode_sync.py`.

---

### Batch 04 — the command hand-off sites

Twenty-five one-line edits. The lowest-risk form is **pure deletion of the tier clause**, not rewording: fewer decisions, fewer ways to be inconsistent across files, and `reference/delegation.md` is already named at almost every site.

21. **Eleven "Delegates to" header lines** — drop the parenthesised tier. `commands/research.md:8`, `reresearch.md:8`, `feedback.md:8`, `prep.md:9`, `execute.md:8`, `yolo.md:8`, `next.md:8`, `split.md:8`, `replan.md:8`, `plan.md:8`, `pr.md:9`. So `**Delegates to: Planner** (deep).` → `**Delegates to: Planner**.`, and `commands/prep.md:9` → `**Delegates to: Researcher**, **Planner**, **Splitter**.`

22. **Fourteen "at the **X** tier" hand-off sentences** — delete the clause and nothing else. `commands/research.md:34,57`, `feedback.md:31`, `prep.md:104,120,136,156`, `execute.md:61`, `yolo.md:77`, `next.md:53`, `split.md:57`, `plan.md:64`, `pr.md:43,81`. Read each sentence after the deletion; three need a word adjusted to stay grammatical — `research.md:57` ("again at the **deep** tier to explore" → "again to explore"), `prep.md:156` ("delegate to the **Splitter**\n at the **standard** tier. State" → "delegate to the **Splitter**. State"), and `prep.md:120` similarly.

23. **`commands/prep.md:23`** — the literal config-block list. `Everything below refers to \`tracker\`, \`split\`, \`plans\`, \`docs\`, and \`consumers\` from it.` → add `models` and `harnesses`. `/jdi:prep` delegates to three roles in steps 8, 13 and 16, so it genuinely reads both blocks. This is the opposite call from `tdd`, which `plans/1-tdd-configuration/PLAN.md:192` deliberately omitted because prep never resolves TS1.

24. **`commands/status.md` — deliberately excluded, and recorded.** It loads the config at `:14-17` and then never names a key; `:19-32` finds the plan, shows the checklist, shows the next task, reports git ground truth. It delegates to nothing — `:8` says "No delegation." Per `docs/config-key-lifecycle.md:140-142`, a command joins the set when the key changes what it *does*, not when it merely reads the config, and the same exclusion was made for `split.pieces` (`:132-138`) and for `tdd` (`plans/1-tdd-configuration/PLAN.md:194`). Excluded; the reason goes in the commit body.

**Files:** eleven `commands/*.md`.

---

### Batch 05 — init, help, README: the nine-file floor

`models` has never reached the full floor from `docs/config-key-lifecycle.md:52-68`. This batch closes that as part of the change rather than leaving it half-added.

25. **`commands/init.md:2`** — the frontmatter `description:` enumerates init's questions and does not mention models today. Add them.

26. **`commands/init.md:102-106` — step 8 is a rewrite, not an insert.** A question about models **already exists** as step 8, so **nothing renumbers** and the `grep -rn "step [0-9]" commands/` check from `docs/config-key-lifecycle.md:90-94` has nothing to find. An Executor following the lifecycle doc's default expectation will go looking for back-references; say plainly that there are none. Rewrite the step to ask per role rather than per tier, keep "optional, and say that it is optional", and fold the `harnesses` question in as a conditional sub-question — **asked only when the user named a different harness for at least one role**, mirroring the skip-the-question-that-cannot-apply shape at `commands/init.md:54-55`.

27. **`commands/init.md:13`** — "example tier mappings" → "example model mappings", matching the heading renamed in batch 01. Self-caused citation rot.

28. **`commands/help.md:9-12`** — the closing config-state line instruction currently names the tracker, the plan store, the split pieces and TDD. Add: which roles have a model configured, and whether any role runs in another harness.

29. **`commands/help.md:23-39`** — **drop the `Tier` column** from the command table. With roles carrying their own model, the column is redundant with the adjacent `Roles` column and is sixteen cells of dead vocabulary. No test reads this table (`tests/test_enumerations.py` reads README's `## How it is put together`, `AGENTS.md`'s two lists, and `reference/delegation.md`'s `## Roles`; nothing reads `commands/help.md`).

30. **`commands/help.md:25`** — the `/jdi:init` row lists init's questions a second time. Add models.

31. **`commands/help.md:113-118`** — `### Tiers, not models` → `### Roles and models`. Rewrite the prose: JDI names roles; `.jdi/config.yml` maps each role to a model and optionally to an agent CLI; leaving the block out runs everything on the session's own model and is fully supported; a role's harness or model that cannot be honoured is announced once and the phase still runs.

32. **`commands/help.md:2`** — the frontmatter `description:` says "the commands, the roles, the tiers, and the typical flow". Drop "the tiers".

33. **`README.md:12`** — "JDI names *roles* and *reasoning tiers*, never models or vendors" → names *roles*, and the model each role runs on lives in settings, not in the workflow prose.

34. **`README.md:185`** — the `/jdi:init` snippet comment enumerating init's questions. Add models. **`README.md:192-198`** — the prose immediately below, which enumerates them a second time. Add models. `docs/config-key-lifecycle.md:107-110` names these two as the pair that is easy to half-update.

35. **`README.md:288`** — the `reference/config.md` row says "example tier mappings". **`README.md:292`** — the `reference/delegation.md` row says "How a role and a tier become an actual model on your harness". Both recast.

36. **`README.md:304-323`** — the heading `### Roles and tiers, not agents and models` → **`### Roles and models, not agents and vendors`**. Use exactly this; do not improvise. An earlier draft proposed "not agents and tiers", which contains the very word T-H bans repo-wide in batch 06 — task 06 would have gone red on arrival and T-G, which pins the heading string exactly, would have needed rewriting a second time. `:314-317`'s three-tier paragraph becomes the per-role description plus the `harness:` sentence. **`:322-323`** — "Concrete model names and tool allowlists live only in YAML frontmatter" is now false for model names and must be split: tool allowlists still live in frontmatter; model names live in `.jdi/config.yml`.

37. **Tests in this batch.** `tests/test_codex_plugin.py:295` calls `normalized_section("### Roles and tiers, not agents and models")`, and `tests/jdi_files.py:150-153` **raises** `AssertionError` when the heading is absent. Update it to the new heading in this same commit, along with `:300-302`'s three fragment assertions if any of their wording moves.

36b. **`AGENTS.md:44`** — "Commands say \"delegate to the *Researcher* role at the *deep* tier\"" describes an invocation shape that batch 04 removed. Reword to match what the command files now say. T-H scans `AGENTS.md`, so this is not optional.

**Files:** `commands/init.md`, `commands/help.md`, `README.md`, `AGENTS.md`, `tests/test_codex_plugin.py`.

---

### Batch 06 — the two architecture docs, and the citation rot

38. **`docs/harness-adapter-architecture.md:243-245`** — the three-rung restatement. Rung 2 ("Use a second non-interactive session if available") becomes a **selected** path driven by `models.<role>.harness`, not only a fallback. Keep it a three-line summary that defers to `reference/delegation.md` as the owner; `:241` already says the Butler uses that file's order.

39. **`docs/harness-adapter-architecture.md:256-257`** — the same false authorization claim as `reference/delegation.md:58-60`. Amend it to the corrected invariant from batch 02, step 13. **This must land in the same change as the `delegation.md` correction** or the two documents disagree on a security-relevant claim.

40. **`skills/run/SKILL.md` — considered, deliberately unchanged.** `tests/test_codex_plugin.py:165-170` pins "Preserve the active sandbox, approval policy, and authorization boundaries" and "Neither dispatch nor delegation grants additional authority". Both remain true as written: the dispatcher runs in-session, and JDI still *grants* nothing — a spawned CLI's authority comes from its own configuration and from flags the user wrote, not from JDI widening anything. Left alone; the decision and its reason go in the commit body so it reads as considered rather than missed.

41. **`docs/config-key-lifecycle.md` §5 — amend, without renumbering.** `:293-299` currently reads "Concrete model names and tool allowlists live only in YAML frontmatter … The `models` block … is the sanctioned exception, and note its shape: it maps JDI's own vocabulary (`deep` / `standard` / `fast`) onto the harness's, so the bodies still name only tiers." Every clause of that is inverted by this change. The amended passage should say: a **tool allowlist** is a harness fact and belongs in frontmatter; a **model name is not** — it is a fact about the user's account and harness pairing, it has no single right answer, and the `models` block is where it lives. Keep §5's five-question test at `:305-320` and show that a per-role `models` key still earns its place under it: two repos answer differently, no repo states it in prose humans read, it is not a harness fact in the frontmatter sense, "unset" is a safe default that needs nothing from the environment, and the ladder was written before the feature.

    **`tests/test_versions.py:59-97` pins headings and phrases in §2 and §6** — `"## 6. Release mechanics"` via `jdi_files.section` (which raises on absence), and the five literals at `:83-89` including `"Nine files are the **floor**"` and `"The nine mandatory files:"`. §5 may be amended freely; **no section heading may be renumbered or restructured**, and the nine-file / three-JSON counts must stay as written.

42. **The citation-rot sweep — wider than one line.** `plans/1-tdd-configuration/PLAN.md:102-104` records the rule that self-caused rot is fixed in the task that causes it, and `:187-189` records that the last change deferred it instead. Do not defer it again. Run `grep -n "reference/config.md:" docs/config-key-lifecycle.md` and re-read every hit: batch 01 grew the schema block, so **every citation with a line number at or above 104 has moved**. Known sites: `:71-77` (the three-edit paragraph, which cites `:17-118`, `:42-55`, `:133-147`, `:139`, `:149-170`, `:153-160`), `:80-82`, `:276`, `:285`, `:297`, `:311`. Also:
    - `docs/config-key-lifecycle.md:295` cites `README.md:322-323` for a sentence that batch 05 rewrote.
    - `docs/config-key-lifecycle.md:107-110` cites `README.md:185`, `:192-198`, `:200-214`.
    - `docs/config-key-lifecycle.md:100-105` cites `commands/help.md:9-12`, `:25`, `:30`, `:82-89`.
    - `docs/config-key-lifecycle.md:86-94` cites `commands/init.md:2`, `:54-55`, `:100`.
    - `tests/jdi_files.py:182-184`'s `schema_block()` docstring names `## Example tier mappings` and describes "three side-by-side `models:` columns". The heading was renamed in batch 01 and the fence's shape changed. The docstring is the *reason* the helper is scoped the way it is, so a stale one invites someone to unscope it. Fix it.

43. **The vocabulary guard goes green here.** After this batch there should be no occurrence of the word "tier" outside `CHANGELOG.md` and `plans/`.

**Files:** `docs/harness-adapter-architecture.md`, `docs/config-key-lifecycle.md`, `tests/jdi_files.py`.

---

### Batch 07 — release 1.0.5

44. **Version to `1.0.5`** in all three JSON authorities, which must match: `.claude-plugin/plugin.json:3`, `.codex-plugin/plugin.json:3`, `.claude-plugin/marketplace.json:10`. Patch bump, per the only observed convention (`docs/config-key-lifecycle.md:334-337`: `c48137c` → 1.0.1 and `c83963b` → 1.0.2 were both full features shipped as patches).

45. **`CHANGELOG.md` — a new `## 1.0.5` entry at the top**, newest-first, in the shape at `docs/config-key-lifecycle.md:342-355`: a bold one-line headline naming the user-visible outcome, then bullets with bold lead-ins, every key and command in backticks. `docs/config-key-lifecycle.md:338-340` requires a key **removal** to be stated deliberately rather than inferred from convention, so the entry must carry all of:
    - **The three tier keys are gone.** `models.deep`, `models.standard` and `models.fast` are no longer read. Name them explicitly.
    - **What happens to a repo with the old shape.** A `models:` block keyed by `deep`/`standard`/`fast` names no role, so nothing in it is read; JDI says so once and runs every role on the session's own model. Nothing breaks and nothing is silently reinterpreted.
    - **What happens to a repo with no `models:` block at all.** Exactly what happened before: every role runs on the session's own model, silently, because nothing was skipped.
    - **No file under `agents/` carries a `model:` key any more**; settings are the single place a role's model is named.
    - **New `harnesses:` block**, and `models.<role>.harness` naming a key in it.
    - **Degrades down, never up** — a bold lead-in bullet, matching `CHANGELOG.md:90`'s precedent.
    - **The authorization correction**, stated as a documentation fix, because a user reading the old sentence would have believed a spawned CLI inherited this session's approval policy.
    - **Leave `CHANGELOG.md:127-128` alone.** It is a historical 1.0.0 note describing what 1.0.0 shipped; rewriting history is not a release note.

46. **Re-verify the dogfood** written in batch 01 against the final schema, rather than writing it here.

47. **Commit subject** `feat: Configure each role's model in settings (1.0.5)` — sentence case, imperative, version in parentheses (`docs/config-key-lifecycle.md:357-362`). The body opens with the problem in the past tense, describes the change, bullets the mechanics, and closes with **what was deliberately left out of scope**: `commands/status.md`, `models.butler`, `harnesses.<kind>.jdi_root`, `skills/run/SKILL.md`, and PR #5's `herd:` block.

**Files:** three JSON manifests, `CHANGELOG.md`.

---

### Batch 08 — UAT

Prose is the substance of this change and no test observes it (`plans/1-tdd-configuration/PLAN.md:139-142`). UAT carries the proof. Scenarios are in the Testing Strategy.

---

### Deliberately out of scope, with reasons

- **`models.butler`.** `roles/butler.md` has no frontmatter, `reference/delegation.md:23` says the Butler is never spawned, and no harness lets a config file set the model of a session that is already running. A key with no consumer is a promise to support a value forever for nothing. The absence is stated in `reference/config.md`'s `## Notes` so it reads as a decision.
- **`harnesses.<kind>.jdi_root`.** No kind needs it today. OpenCode and Claude Code both resolve the role by registered name; Codex takes the role file **inlined into the prompt**, which the Butler can always produce because it resolves its own plugin root. Adding the key now would be the same mistake as `models.butler` — a key with no consumer. The trigger that revives it: a kind that can take role instructions only as a file path.
- **`commands/status.md`.** Considered; excluded. See step 24.
- **`skills/run/SKILL.md`.** Considered; unchanged. See step 40.
- **PR #5's `herd:` block.** `harnesses:` ships independently and **this work does not depend on PR #5**. PR #5's branch predates `815dfae` and is not edited here. It is expected to rebase onto this afterwards, moving `herd.args` / `herd.env` into `harnesses:` and keeping only `kind` / `max_parallel` / `seed` in `herd:` — but that is that PR's work, not this one's.
- **A new `docs/cross-harness-delegation.md`.** `reference/delegation.md` is already the file every command names by path, so the ladder belongs there under `docs/config-key-lifecycle.md:249-256`'s rule. A third document would create a fourth place a model is described, which is the disease being treated. Verified for completeness: `grep -rn "docs/" README.md AGENTS.md` returns nothing — neither document enumerates `docs/*.md`, so a new file there would have cost no enumeration edit. It is still not worth it.
- **CI.** The repo has no `.github/`. Out of scope here, as it was for 1.0.3.

---

## Testing Strategy

`python3 -m unittest discover -s tests -v` from the repository root. Stdlib only, no install step, no third-party packages — in particular **no PyYAML**: the suite parses key *paths* out of hand-written two-space YAML (`tests/jdi_files.py:8-13`, `:99-139`), never YAML values. Baseline: **47 tests, OK**.

### What proves what

| Test | File | Kind | Proves | Goes green in |
|---|---|---|---|---|
| T-A role stems are bidirectional | `tests/test_config_schema.py` | **red-first** | step 1 — seven role keys, no `models.butler`, no tier keys | batch 01 |
| T-B every role has `model` and `harness` | `tests/test_config_schema.py` | **red-first** | step 1 — the per-role shape | batch 01 |
| T-C existing schema/example/defaults set checks | `tests/test_config_schema.py:35-100` | existing, newly load-bearing | steps 2, 3, 6 — `harnesses` symmetry and its defaults row | batch 01 |
| T-D no `model:` in `agents/*.md` frontmatter | `tests/test_frontmatter.py` | **red-first** | step 17 | batch 03 |
| T-E synced OpenCode agents carry no `model:` | `tests/test_opencode_sync.py` | **characterization — passes today** | step 19 | already green |
| T-F rewritten delegation guidance | `tests/test_codex_plugin.py:173-209` | rewrite-in-place | steps 11–14 | batch 02 |
| T-G rewritten README section heading | `tests/test_codex_plugin.py:292-302` | rewrite-in-place | step 36 | batch 05 |
| T-H the word "tier" is gone | `tests/test_enumerations.py` | **written green, in the batch that earns it** | proves steps 9–10, 18, 21–22, 29–36, 41 | batch 06 |

### The red-first ones

**T-A — `reference/config.md`'s `models:` block names exactly the `agents/*.md` stems.** In `tests/test_config_schema.py`, a bidirectional set comparison:

- `expected = {path.stem for path in agents/*.md}` — seven: `researcher`, `planner`, `splitter`, `executor`, `synthesizer`, `pr-writer`, `feedbacker`.
- `actual = {key.split(".")[1] for key in schema_keys if key.startswith("models.") and key.count(".") == 1}`.
- Assert equal in both directions.

Red today: the schema's children are `deep`, `standard`, `fast`. Green after step 1. This is the "7 stems" test — it is also what makes `models.butler`'s absence enforced rather than merely intended, since `butler` lives in `roles/`, not `agents/`, and would fail the stale-key direction. `tests/jdi_files.py:99`'s `_KEY` character class includes `\-`, so `models.pr-writer` parses; `tests/test_config_schema.py:83-93`'s `models.*` prefix match already covers per-role children, so **no helper change is needed**.

**T-B — every `models.<role>` carries both `model` and `harness`.** Assert `{"models.%s.model" % stem, "models.%s.harness" % stem} <= schema_keys` for each stem. Red today (no such keys). Green after step 1. This is what stops the block quietly reverting to a flat `role: model` mapping that the `harness:` feature would then have nowhere to live in.

**T-D — no `agents/*.md` frontmatter carries a top-level `model:` key.** In `tests/test_frontmatter.py`, reusing `jdi_files.split_frontmatter` exactly as the existing `description:` check does at `:34-84`: for each `agents/*.md`, assert no frontmatter line starts with `model:`. Red today — all seven do (`agents/researcher.md:18`, `planner.md:18`, `executor.md:17`, `feedbacker.md:18`, `splitter.md:17`, `synthesizer.md:16`, `pr-writer.md:17`). Green after step 17. Note the asymmetry worth stating in the test's message: nothing in the suite asserted `model:` was *present*, which is exactly why the two-place arrangement drifted for four releases.

**T-H — the tier vocabulary is gone.** A new class in `tests/test_enumerations.py` (widen the module docstring by a line; the module's remit is "consistencies that are maintained by hand and notice nothing on their own", and this is one). Scan a fixed file list for a case-insensitive `\btiers?\b` and assert no hits, reporting `path:line` for each:

- included: `commands/*.md`, `agents/*.md`, `reference/*.md`, `roles/*.md`, `docs/*.md`, `README.md`, `AGENTS.md`
- excluded: `CHANGELOG.md` (`:127-128` is a historical 1.0.0 note and must not be rewritten), `plans/` (historical records), `tests/` (this test's own docstring contains the word), `bin/` — no, **include `bin/sync-opencode.sh`**, because `:79` is a live comment this change rewrites.

**T-H is written in batch 06 and is green the moment it exists.** An earlier draft wrote it in batch 02 and left it red through batch 06 as a progress meter; that is withdrawn, because `reference/config.md:62-64` puts tests and implementation in the same commit and `/jdi:yolo` stops on the first failure — a deliberately-red commit would halt the run at batch 03. **Every commit in this plan ends with the full suite green.** Batches 02–05 verify their own share of the vocabulary removal with the manual grep, scoped to the files that batch touched; the residual hits in files a later batch owns are an expected control, not a failure.

A blunt word-scan rather than a precise regex is the right trade here: it also catches "mid-tier", "reasoning tier", the `Tier` table column header, and the `(deep)` / `(standard)` parentheticals' surrounding prose — the phrasings a partial edit leaves behind. The cost is that the recast prose in steps 10 and 31 may not use the word at all, which is the stated goal.

### The characterization one

**T-E — the OpenCode sync drops `model:`.** An assertion in `tests/test_opencode_sync.py` that no file under the synced `agent/` directory contains a frontmatter `model:` line. **This passes today and is not red-first**, because `bin/sync-opencode.sh:81`'s `AGENT_DROP = {"model", "tools"}` already strips it before writing. Calling it red would be dressing up a guard as a discovery. What it actually earns its place for: it pins the drop as *intentional* once the source files no longer carry the key, so a later contributor tidying `AGENT_DROP` down to `{"tools"}` gets a failing test with a message explaining that `model` stays as a guard against a role file reacquiring one.

### The two rewrites, in the batch that causes them

**T-F — `DelegationGuidanceTest`, `tests/test_codex_plugin.py:173-209`.** Rewritten in batch 02, in the same commit as `reference/delegation.md`. It is **not** two lines; here is every fragment and its fate:

| Line | Literal | Fate |
|---|---|---|
| `:185` | `"Delegation follows observed runtime capability, not the harness name."` | **survives** — keep this sentence at `reference/delegation.md:28` |
| `:186` | `"Claude Code's Agent tool, Codex subagents, OpenCode's subagent mode"` | **survives** — keep in rung 1 |
| `:191-193` | `"When no matching JDI role is registered, spawn a suitable generic subagent"`, `"the installed \`agents/<role>.md\` definition as its instructions"`, `"exactly the inputs the role's *What it receives* section declares — no more"` | **survive** — keep all three |
| `:198` | `"**1. The harness has first-class subagents**"` | **survives** — rung 1's heading is kept verbatim for this reason |
| `:199` | `"**2. The harness has no subagents, but can run a second session**"` | **dies.** `str.index` **raises `ValueError`** on absence — an error, not a failure. Replace with the new rung-2 heading, e.g. `"**2. A second non-interactive session**"` |
| `:200` | `"**3. Neither.** **Adopt the role inline.**"` | **survives** — rung 3's heading is kept verbatim |
| `:204` | `"the tier's model from the config"` | **dies.** Replace with `"the role's model from the config"` |
| `:205` | `"Shell out to it with the role file and the inputs as the prompt"` | **dies.** Replace with the new exec-mode sentence from step 12 |
| `:206` | `"announce the switch"` | **survives** |
| `:207` | `"Subagents and fallback sessions stay inside the active sandbox, approval policy, and authorization boundaries."` | **dies — this is the sentence being corrected.** Replace with two fragments from step 13: `"A separately spawned CLI does not"` and `"JDI composes no authority-affecting flag and translates none between kinds"` |
| `:208` | `"Delegation never grants additional authority."` | **survives, and should.** It is still true under the corrected invariant, and keeping it preserves continuity on the claim that matters most |

Add, in the same rewrite, a small number of new pins on the ladder — enough to make a half-written ladder fail, few enough not to make every future wording tweak a test edit:
- the floor rung's sentence, because a ladder without a floor is the skip-the-phase failure;
- `"one announcement, not two"`;
- `"Never skip the phase."` and `"Never acquire a flag the user did not write."`;
- `"herdr pane close"`, because pane hygiene is the one rung whose absence leaks state rather than merely misleading;
- an ordering assertion (`index` comparisons, as `:198-202` already do) that rung 1 precedes rung 12 in the ladder section.

**T-G — `tests/test_codex_plugin.py:292-302`.** `:295` calls `normalized_section("### Roles and tiers, not agents and models")`, and `tests/jdi_files.py:150-153` **raises `AssertionError`** when the heading is absent. Rewritten in batch 05 with the README edit, to the new heading. Re-check `:300-302`'s three fragments (`"Delegation follows observed runtime capability"`, `"a suitable generic subagent"`, `"adopt the role inline and announce the switch"`) against the rewritten `README.md:304-323` — all three should survive, but confirm rather than assume.

### What the suite cannot prove — and who carries it instead

`plans/1-tdd-configuration/PLAN.md:139-142` states it plainly for the last change and it is truer for this one: **no test observes command or role body prose.** Every test above checks *structure* — a key path exists, a heading exists, a literal substring is present, a word is absent. Almost everything this change ships is prose an agent reads and acts on. In particular, **nothing in the suite can prove**:

- that the twelve-rung ladder is followed at all, that the first applicable rung wins, or that anything is announced;
- that a harness degradation and a model degradation collapse into one announcement;
- that a pane JDI created is actually closed;
- that `codex exec -m … -o <file>` or `opencode run --agent jdi-<role>` is the command actually composed, or that its output is read back correctly;
- that no authority-affecting flag is composed or translated;
- that the old-shape `models:` block is detected and announced;
- that `/jdi:init` asks the new question in words a user can answer;
- that the recast role-wants table gives usable guidance.

The tests are a regression guard on structure. **Behavioural proof is UAT**, and the UAT task is not optional decoration on this plan — it is where the change is actually verified. Weight the UAT task accordingly when splitting.

### UAT scenarios

Negative cases are chosen for what is genuinely true on this machine (verified: `codex`, `opencode`, `gemini`, `herdr` and `claude` are on `PATH`; **`qwen` is not installed**; `~/.config/opencode/agent/jdi-*.md` exists for all seven roles; `gemini` is installed with no JDI).

**Positive — the exec path end to end, both installed kinds:**

1. **Codex exec.** Scratch repo, `.jdi/config.yml` with `models.researcher: {model: gpt-5.1-codex-max, harness: codex}` and `harnesses.codex.args: ["--sandbox", "workspace-write"]`. Run `/jdi:research`. Confirm: the composed command uses `codex exec -m … -o <file>`; the args are printed back **before** the spawn and appear verbatim, unmerged; the report comes back from the file, not from a terminal scrape; no pane was created.
2. **OpenCode exec.** `models.splitter: {model: <provider/model>, harness: opencode}`. Run `/jdi:split`. Confirm `opencode run -m … --agent jdi-splitter --format json` and that the role's own instructions were used. **This is the scenario that proves step 12's "name the target's registered role" claim.** The synced agents carry `mode: subagent` (`bin/sync-opencode.sh:144`), and whether `opencode run --agent` accepts a subagent-mode agent is **not verified on this branch** — "the files exist" is the evidence, not "it resolves". If `--agent jdi-splitter` is rejected, that is rung 5 firing correctly, and the contingency is the inline path (pass `agents/splitter.md`'s text in the prompt). Record whichever happened; either outcome is a pass for the ladder and only one is a pass for the `--agent` claim.

2b. **Claude exec, from a non-Claude session.** Run JDI under Codex or OpenCode with
    `models.planner: {model: opus, harness: claude}`. Confirm the composed command is
    `claude -p --model opus --output-format json`, that the report is parsed from the JSON
    result rather than scraped, and that the Planner phase runs. This is the direction the
    original request named and the one the other two scenarios do not cover — without it,
    "codex, opencode, claude" is only ever two of three.

**Negative — the rungs that are genuinely reachable here:**

3. **Rung 3, CLI absent from `PATH`.** `models.planner.harness: qwen`. `qwen` is not installed. Confirm: exactly one announcement, naming what was configured and what is running instead; **nothing is spawned**; the Planner phase still runs at the floor.
4. **Rung 4, no exec mode JDI knows.** `models.planner.harness: gemini`. `gemini` is on `PATH` but JDI knows no exec invocation for it. Confirm the announcement names the reason correctly — *no exec mode*, not *not installed* — and that the ladder then considers Herdr before the floor.
5. **Rung 5, instructions unresolvable.** `models.splitter.harness: opencode` with `OPENCODE_CONFIG_DIR` pointed at an empty directory via `harnesses.opencode.env`, so `--agent jdi-splitter` cannot resolve. Confirm the ladder either inlines the role file or announces rung 5 and floors — and that it **never** derives or searches for a plugin path.
6. **Rung 10, the model this harness cannot express.** Inside Claude Code, `models.planner: {model: claude-opus-5}` with **no** `harness:`. Claude Code's Agent tool takes `model` as an enum, so this cannot be passed at spawn time. Confirm an **announcement**, not a silent drop, and that the Planner runs on the harness default. **This is the regression the whole change exists to close; it is a certainty by schema, not a hypothesis, and it must be exercised live.**
7. **Rungs 6–9 and pane hygiene.** Force the Herdr transport (a kind with no exec mode, Herdr present). Interrupt it mid-run so it never reports usably. Confirm: one announcement; the phase still runs at the floor; and `herdr pane list` shows **no leaked pane** after three consecutive failed attempts. The three-attempt form is the point — a leak of one pane per attempt is the failure being guarded against.

**Compatibility and silence:**

8. **Old-shape `models:` block.** Scratch repo with `models: {deep: claude-opus-5, standard: claude-sonnet-5, fast: claude-haiku-4-5}`. Run `/jdi:plan`. Confirm exactly one announcement that the block is the pre-1.0.5 shape and is not read, that `reference/config.md` is named, and that the workflow proceeds on the session's model. **Nothing breaks and nothing is silently reinterpreted.**
9. **No `models:` block at all.** Scratch repo with a 1.0.4-era config. Run `/jdi:plan`. Confirm **complete silence** on models — the `commands/split.md:96-97` / `docs/config-key-lifecycle.md:230-240` distinction: a feature that is off produces no notice, because nothing was skipped. A run here must be indistinguishable from a 1.0.4 run.
10. **The dogfood.** In this repository, under Claude Code, run `/jdi:plan`. Confirm the Planner is spawned on `opus` resolved from `.jdi/config.yml`, and that **nothing is announced** — this is rung 1/2, the silent path. Then run the same under Codex or OpenCode and confirm the single announcement that the alias cannot be expressed, and that the phase still runs.
11. **`/jdi:init` read-through.** Scratch repo with no `.jdi/config.yml`. Run `/jdi:init`. Confirm step 8 asks per role, says it is optional, and asks the `harnesses` follow-up **only** when a role was given a different harness. Confirm the written file matches the schema. `plans/1-tdd-configuration/PLAN.md` records that init's question wording is genuinely unverifiable without this run — do not substitute a diff review.
12. **`/jdi:help` read-through.** Confirm the table has no `Tier` column, the `### Roles and models` section reads correctly, and the closing line names which roles have a model configured.
13. **OpenCode sync end to end.** `bin/sync-opencode.sh --global` into a temp `OPENCODE_CONFIG_DIR`; confirm no synced agent carries `model:`, then run `/jdi-plan` against the synced copy and confirm the workflow still runs.
14. **Acceptance-criteria sweep.** Map every clause of issue #9's acceptance criteria to the scenario or test above that proves it, and name any clause that nothing above proves.

---

## Risks

**The silent drop to the session model.** This is the regression the change is meant to close, and it is also the way the change most plausibly fails. Deleting `agents/*.md`'s `model:` removes the one mechanism that actually reached Claude Code today; if the ladder's rungs 10 and 11 are written as prose an agent skims rather than as an ordered instruction with an announcement attached, every role silently runs on the session model and the user believes their config is being honoured. *Mitigation:* rung 10 is knowable **before** the spawn from the harness's own schema, so it is detectable rather than inferred; T-F pins the floor sentence and the announcement rules; UAT 6 exercises it live in Claude Code, where it is a certainty rather than a hypothesis. Do not let UAT 6 be deferred — it is the single most important scenario in the list.

**An existing user's `models:` block breaks on upgrade.** A repo on 1.0.4 with `models: {deep: …, standard: …, fast: …}` upgrades to 1.0.5 and the block becomes unreadable. If JDI says nothing, the user keeps a config they believe is live; if JDI tries to interpret it — mapping `deep` onto the deep-ish roles — it invents a mapping the user did not write, which is exactly the never-invent violation at `reference/config.md:14-15`. *Mitigation:* the old-shape detection sentence in step 14, which does neither: it reads nothing from the block and says so once. CHANGELOG bullet (step 45) states the backward-compatibility position explicitly rather than leaving it to be inferred, per `docs/config-key-lifecycle.md:352-354`. UAT 8 proves it, UAT 9 proves the no-block case is silent.

**The ~25-site prose edit goes half-done.** Eleven header lines and fourteen hand-off sentences across eleven command files, plus four recast sections, plus README, help and AGENTS. Half-finished, the repo names a lookup concept with no table behind it and a reader cannot tell which half is current. *Mitigation:* the T-H vocabulary guard is exactly the executable form of `docs/config-key-lifecycle.md:409`'s pre-commit grep; it fails with a `path:line` list until every site is done. The manual equivalents, for the batch that touches each area: `grep -rni "tier" --include=*.md --include=*.sh . | grep -v '^./plans/' | grep -v '^./CHANGELOG.md'` and `grep -rn "Delegates to" commands/`. Expect the false positives already catalogued in the plan's references — "deep-dive" at `agents/researcher.md:4,24`, "standard language idiom" at `agents/planner.md:70`, "standard-library" at `CHANGELOG.md:67`, "data models" at `commands/research.md:58` — none of which the `\btiers?\b` word-boundary scan matches.

**The authorization claim is corrected in one document and not the other.** `reference/delegation.md:58-60` and `docs/harness-adapter-architecture.md:256-257` state the same thing, and it is false for a spawned CLI. Correcting one leaves the repo asserting both positions on a security-relevant claim, and a reader who finds the uncorrected one believes a spawned Codex or OpenCode session inherits this session's approval policy — which it does not. *Mitigation:* steps 13 and 39 are both named as parts of one change, with the words "or the two documents disagree" in the plan text; **The obvious grep does not work**: `grep -rn "sandbox, approval" .` misses `docs/harness-adapter-architecture.md:256`, which says "sandbox **and** approval". Use two signature greps that discriminate corrected from uncorrected text — `grep -rn "stay inside the active sandbox" .` and `grep -rn "inherit the active sandbox" .` — and note there is a **third** claim at `docs/harness-adapter-architecture.md:168` ("Preserves the active environment's authorization and sandbox boundaries", in the dispatcher's guarantee list) that the plan did not originally catalogue. Reviewer check before merge: `reference/delegation.md` and `docs/harness-adapter-architecture.md:256` amended, `:168` and `skills/run/SKILL.md:94` each recorded as considered-and-unchanged with a reason.

**Scope creep into PR #5's territory.** `harnesses:` is kind-keyed `args` + `env`, which is the same shape as `herd.args` / `herd.env` on the open `herd-command` branch. It is tempting to "finish the job" by editing that branch or by pre-shaping `herd:` here. *Mitigation:* `harnesses:` is defined as *about the CLI*, not about the command using it, which is what lets PR #5 rebase onto this rather than the reverse. This branch touches no file on that branch and reads no `herd.*` key. The relationship goes in the commit body's out-of-scope paragraph, not into code. Reviewer check: `git diff origin/main..HEAD --stat` names no `commands/herd.md` and no `herd:` key.

**Prose correctness is unverifiable by the test suite.** Every behavioural claim in this change is a markdown instruction to an agent, and the suite checks only that certain substrings and key paths exist. A ladder can be present, well-formed, pinned by three assertions, and still wrong. *Mitigation:* named explicitly in the Testing Strategy under "What the suite cannot prove"; the fourteen UAT scenarios are the proof and the UAT task should be sized as real work, not a checklist. Do not accept "the suite is green" as evidence that the ladder behaves.

**Schema/example asymmetry fails in a confusing direction.** `tests/test_config_schema.py` compares key-path *sets* bidirectionally, and `KNOWN_OMISSIONS` (`:22`) only forgives one direction. Writing `env:` with block children, or naming `opencode` in the example but not the schema, produces a failure whose message points at the config files rather than at the shape mistake. *Mitigation:* stated inline at step 2 with the reason and the fix; `origin/herd-command:reference/config.md:137,148`'s flow-leaf form is the precedent to copy. Also: the two files must name the **same** harness kinds, which is a constraint on the example's freedom to be interesting and is worth saying out loud in a comment in the example file.

**Herdr's own flag spellings drift.** The ladder names `herdr pane split` / `run` / `wait-output` / `close`, verified against `herdr pane --help` on this machine at herdr 0.9.0. A future Herdr may rename them, and the ladder would then instruct an agent to run a command that does not exist. *Mitigation:* the ladder's Herdr rungs are written so that a failed invocation lands on rung 8 or 9 and floors with an announcement rather than hanging — a wrong subcommand degrades correctly. Consider marking the literal spellings as verified-at-0.9.0 in the prose, in the `UNVERIFIED — Issue #<n>` idiom at `plans/7-codex-skill-model/PLAN.md:88-96`.

**A new announcement appears where there was silence — under Codex and OpenCode, on this repo.** The dogfood writes Claude Code aliases (`opus`, `sonnet`) into `.jdi/config.yml`. Under Claude Code that is exact parity with today. Under Codex or OpenCode, every JDI-on-JDI delegation now emits a rung-10 announcement that did not exist before. That is **correct behaviour** — the alias genuinely cannot be expressed there — but it is a real, visible UX change on the maintainers' own repo, and it will look like a bug to whoever sees it first. Named here so it is a known consequence rather than a surprise. The alternative, full identifiers, would regress the primary harness on day one and is worse. If the noise proves intolerable, the fix is a `harnesses:`-aware per-kind model in a later change, not silence.

**Pane leakage under repeated failure.** Rungs 6–9 are where state can be left behind, and a retry loop that opens a pane per attempt leaks one per attempt. *Mitigation:* "a pane JDI created is JDI's to close" is written as a standing rule in step 12 rather than as a clause on one rung; T-F pins `herdr pane close`; UAT 7 checks `herdr pane list` after **three** consecutive failures, not one.

**Citation rot is wider than the one line the brief names, and was already deferred once.** `docs/config-key-lifecycle.md:297` is the cited case, but batch 01 grows `reference/config.md`'s schema block and **every** citation into that file at or above line 104 moves — `:71-77`, `:80-82`, `:276`, `:285`, `:297`, `:311` — and `:295` cites a `README.md` sentence that batch 05 deletes. Some of these were already stale from 1.0.3 (`plans/1-tdd-configuration/PLAN.md:187-189` deferred them deliberately). Deferring again makes the repo's own written procedure the least trustworthy document in it. *Mitigation:* step 42 makes the sweep a named part of batch 06 with the grep that finds it, and includes `tests/jdi_files.py:182-184`'s docstring, which is a citation in code.

## Tasks

Nine tasks, strictly ordered — each depends on the one before it. One commit per task; every commit
ends with `python3 -m unittest discover -s tests -v` green (47 tests plus the ones each task adds).

- [x] `01-config-schema-and-dogfood.md` — the per-role `models:` and new `harnesses:` schema in
      `reference/config.md`, the worked `jdi.config.example.yml`, and the `.jdi/config.yml` dogfood.
      Tests T-A, T-B red-first. **Must precede task 03** or JDI regresses on itself mid-branch.
- [x] `02-delegation-rewrite.md` — `reference/delegation.md`: the roles table, the recast
      "what each role wants from a model", rung 2 promoted from fallback to chosen path, the new
      "Where a role runs" and the twelve-rung ladder, and the authorization correction.
      T-F rewritten in place, same commit.
- [ ] `03-frontmatter-removal.md` — the seven `model:` lines out of `agents/*.md`,
      `roles/butler.md:3`, the `bin/sync-opencode.sh` comment. T-D red-first, T-E characterization.
- [ ] `04-command-handoff-sites.md` — the 25 mechanical edits across eleven `commands/*.md`, plus
      `commands/prep.md:23`'s config-block list. `commands/status.md` excluded, reason recorded.
- [ ] `05-init-help-readme-agents.md` — `commands/init.md`, `commands/help.md`, `README.md`,
      `AGENTS.md:44`. Brings `models` to the nine-file floor it never reached. T-G in place.
- [ ] `06-architecture-docs-and-citation-sweep.md` — both architecture docs, the second half of the
      authorization correction, the citation-rot sweep, and T-H, written green here.
- [ ] `07-release.md` — 1.0.5 across the three JSON manifests, the CHANGELOG entry stating the key
      removal deliberately, dogfood re-verified.
- [ ] `08-uat.md` — fifteen scenarios and the acceptance-criteria map against the live issue #9.

### Things a later agent must not quietly undo

- **No commit ships a failing suite.** T-H is written in task 06 and is green immediately. An
  earlier draft had it red from task 02 onward as a progress meter; that would halt `/jdi:yolo` at
  task 03 and is withdrawn.
- **The authorization correction is one change across two tasks** — `reference/delegation.md:58-60`
  in task 02 and `docs/harness-adapter-architecture.md:256-257` in task 06. Landing one without the
  other leaves the repo asserting both positions on a security-relevant claim. The obvious grep
  misses the second site, which says "sandbox **and** approval"; there is also an uncatalogued third
  claim at `docs/harness-adapter-architecture.md:168` to be recorded as considered.
- **Unset is silent; only degradation is announced.** Any announcement during a run against a repo
  with no `models:` block is a failure, not harmless chatter.
