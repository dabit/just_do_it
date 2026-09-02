# Add a TDD configuration

- Tracker: github
- Project: feature development
- Issue: #1
- Issue URL: https://github.com/dabit/just_do_it/issues/1
- Created: 2026-09-02
- Started: 2026-09-02
- Base commit: main @ a6823a921731d6fed62cff34afde988c1dc763a8
- Summary: A configurable TDD mode that has the Executor write failing tests before implementation, only when explicitly enabled and a viable test suite exists.

## References

**Precedent — how a config key was last added:** commit `c83963b` "feat: Make the splitter's
pieces configurable (1.0.2)" is the closest prior art: a new key, off by default, that changes
behaviour across several commands and degrades out loud. `git show c83963b` is the template.

**Architecture doc written during this research**
- `docs/config-key-lifecycle.md` — "Adding a configuration key": the resolution order, the
  mandatory file set, where behaviour goes (roles vs commands), the degradation idiom, what must
  never become a config key, and the release mechanics

**The config key itself**
- `reference/config.md:42-55` — the `split:` block; the shape a new block copies
- `reference/config.md:122` — the defaults table row every key needs
- `reference/config.md:134-141` — the `## Notes` invariants: "never changes what gets executed",
  "degrades down, never up"
- `reference/config.md:142-143` — repo conventions (commands, branch format) live in the repo's
  `CLAUDE.md`/`AGENTS.md`, not in `.jdi/config.yml`
- `jdi.config.example.yml:27-33` — the example block (shows a non-default value, deliberately)
- `commands/init.md:2` (frontmatter description) and `commands/init.md:41-55` (the question step)
- `commands/help.md:9-12` (closing config-state line), `:25` (init row), `:82-89` (prose section)
- `README.md:167`, `README.md:174` (both enumerate init's questions), `README.md:179-193` (section)
- `commands/prep.md:23` — the literal list of config blocks prep reads

**Where the Executor hand-off is written (triplicated, repeat-in-place)**
- `commands/execute.md:48-57` — step 5, the canonical long form
- `commands/next.md:53-58` — step 9, the compressed restatement
- `commands/yolo.md:60-65` — Step 2 item 3, the compressed restatement
- `agents/executor.md:54-59` — "What it receives": four inputs, no config
- `agents/executor.md:61-65` — "What it returns": no slot for a red run
- `agents/executor.md:38-46` — the existing test-epistemics responsibilities to extend
- `agents/executor.md:80-88` — the no-`git stash` rule; the worktree/base-ref idiom for
  reproducing a pre-change state
- `roles/butler.md:14-15` — pass a role exactly the inputs its "What it receives" lists
- `roles/butler.md:23-25` — announce every skip, once

**The degradation idiom to match**
- `reference/tracker.md:100-105` — the numbered ladder: first rung that applies, said out loud
- `reference/tracker.md:107-109` and `reference/config.md:138-141` — never degrade upward
- `commands/split.md:96-97` and `reference/tracker.md:97-98` — when the feature is off, say nothing
- `reference/tracker.md:18-19` — capability is proven, not assumed ("no error" is not proof)
- `commands/init.md:37-39` — the same shape applied to trackers at init time

**Where a per-plan detection result would be recorded**
- `commands/execute.md:22-40` — the first-task check; `:33` writes `Started:` into PLAN.md metadata
- `commands/yolo.md:21-27` — the same hook, before the loop
- `commands/yolo.md:69-72` — the loop stops on the first verification failure; an expected red run
  must not trip it
- `reference/plan-store.md:17-20` — where the precedent documented a new task-file metadata line

**Existing testing surface**
- `agents/planner.md:33-53` — the Planner's testing-strategy responsibility, including "buildable
  with the repo's existing test dependencies and injection seams"
- `commands/plan.md:74`, `commands/plan.md:77-78` — where `## Testing Strategy` is written
- `commands/prep.md:91-99` — the PLAN.md template containing `## Testing Strategy`
- `commands/split.md:29-33`, `commands/split.md:50` — tests already shape task boundaries and the
  Verification section
- `commands/split.md:83-91`, `agents/splitter.md:41-45` — the UAT must name unobservable clauses

**Release mechanics**
- `.claude-plugin/plugin.json:3` and `.claude-plugin/marketplace.json:10` — both bump; next is 1.0.3
- `CHANGELOG.md:3-24` — the entry shape (bold headline, then bullets with bold lead-ins)
- `git log --oneline` — commit subject shape: `feat: <Imperative sentence> (<version>)`

**Adapter**
- `bin/sync-opencode.sh:66`, `:135`, `:140` — glob-driven; no change for a key or body edits
- `README.md:223-226`, `AGENTS.md:46-49` — the two hand-maintained enumerations of reference files,
  which must be updated only if a new `reference/*.md` is added

## Implementation Plan

### Design decisions, settled before step 1

**The key:**

```yaml
tdd:
  enabled: false
  test_instructions: ""
```

`test_instructions` is **free-form prose an agent reads and translates**, never a string to exec.
Empty means "work it out from the repo". The user's own example — "run `bin/rails test` inside the
devcontainer" — is the shape: the literal string is usually not runnable as typed.

**Two named operations in a new `reference/testing.md`**, prefixed `TS` so no reader confuses them
with `reference/tracker.md`'s `T1`–`T8`:

- **TS1 — Prove the test suite runs.** Resolved once per plan, recorded in `PLAN.md`.
- **TS2 — Write the failing test first.** The Executor's per-task discipline.

**The `TDD:` metadata line**, written into `PLAN.md` immediately after `- Started: …`, in exactly
two shapes:

```
- TDD: on — proven YYYY-MM-DD with `<the invocation that ran>`
- TDD: off — <the TS1 rung, and the evidence>
```

**No line is written at all when `tdd.enabled` is not `true`.** That is the silence rule
(`commands/split.md:96-97`) expressed structurally: a repo that has never heard of TDD produces a
byte-identical `PLAN.md` to today, and "no `TDD:` line" reads unambiguously as "off, silently".
Only an ON-but-degraded run writes `off`, and only that run announces.

**Once written, the line is never rewritten for that plan.** Flipping `.jdi/config.yml` mid-plan
changes nothing until the next plan. This is why this plan's own execution resolves `off` (no suite
exists at task 1) and stays off even after step 1 creates one.

**Tests and implementation land in the same commit.** TDD means test-first *within* a task, not a
red commit. One commit per task is unchanged — `commands/yolo.md:71-72`'s bisect promise depends on
it, as does `split.pieces`' "identical in all three modes" invariant.

**Deliberately excluded, and said so in the commit message:** `commands/prep.md:23`'s config-block
list and `commands/status.md` (neither executes a task), `commands/done.md`, `agents/splitter.md`
(its output shape is unchanged), `commands/pr.md` / `agents/synthesizer.md` (both already preserve
the metadata block, so `TDD:` survives condensation unedited), and CI (no `.github/` exists).

### Step 1 — The repository gains a test suite

Do this first. Every later step then has a real verification command, and steps 2–5's most likely
half-finishes fail a test the moment they land.

**Runner: `python3` + stdlib `unittest`, no third-party package.** `bin/sync-opencode.sh:68`
already shells to `python3`, so it is already a hard dependency of this repo's only executable.
Ruby ships minitest *and* psych in stdlib, which is attractive, but would make a markdown plugin
repo depend on two language runtimes where it now depends on one. pyyaml is rejected: not installed
by default, and a `skipUnless(HAS_YAML)` guard would make the suite's most valuable assertion
silently vanish on a contributor's machine — the exact "no error is not proof" failure
`reference/tracker.md:18-19` warns about.

The YAML problem is dissolved, not solved: the suite never needs a YAML *value*, only the set of
**key paths**, and both files are hand-written in a plain two-space-indented subset.

Files to create:

- `tests/jdi_files.py` — shared helpers, no tests. `ROOT` via
  `pathlib.Path(__file__).resolve().parents[1]`; `split_frontmatter(text)`; `key_paths(lines)`;
  `schema_block()`; `defaults_table_keys()`.
- `tests/test_frontmatter.py` — every `commands/*.md` and `agents/*.md` has well-formed frontmatter
  with a non-empty `description`, and a non-empty body. **Handle the block scalar**: `agents/*.md`
  use `description: |`, so a bare `^description:\s*\S` regex matches the pipe and proves nothing —
  where the value is `|` or `>`, assert the next line is indented and non-blank.
  *Why:* `bin/sync-opencode.sh`'s `convert()` splits on the `---` delimiters; malformed frontmatter
  breaks the OpenCode adapter and ships a malformed command, and nothing notices today.
- `tests/test_config_schema.py` — example keys ⊆ schema keys; schema keys ⊆ example keys minus
  `KNOWN_OMISSIONS = {"plans.service", "plans.location"}` (external-mode-only, commented out in the
  example); every schema block has a Defaults row; every Defaults row names a real schema key
  (`models.*` matched as a prefix).
- `tests/test_enumerations.py` — bidirectional: `reference/*.md` against `README.md:218-228` and
  `AGENTS.md:46-47`; `reference/delegation.md:12-21` against `agents/*.md`; `AGENTS.md`'s command
  table against `commands/*.md`; and the digits in `README.md:220-221` ("16 workflow commands",
  "7 delegatable roles") against the directories.
- `tests/test_versions.py` — `plugin.json` version == `marketplace.json` version == the first
  `^## (\S+)` heading in `CHANGELOG.md`.

**Deliberately not asserted:** that `file:line` citations resolve (line numbers legitimately move; a
suite that fails on every unrelated edit gets disabled), prose content, and any invocation of
`bin/sync-opencode.sh`.

Invocation, verified working from the repository root with no `__init__.py`:

```
python3 -m unittest discover -s tests -v
```

Also add a `tests/` row to `README.md`'s "How it is put together" table and a "Running the tests"
line — the enumeration test only scans `reference/`, so nothing catches this omission for you.

### Step 2 — The schema and the example

`reference/config.md`, three separate edits:

1. **Schema block** — insert `tdd:` after `split:` (`:42-55`), before `plans:` (`:57`), matching the
   surrounding comment style. Document `test_instructions` as prose, not a command.
2. **Defaults table rows** after `:122` — `tdd.enabled` → `false`; `tdd.test_instructions` → empty,
   derived from the repo.
3. **`## Notes`** (`:130-144`), two bolded invariants:
   - **`tdd` never changes what gets committed.** Tests and implementation land in the same commit,
     one per task, exactly as without it. It changes the order the Executor writes them, not history.
   - **`tdd` degrades down to off, never up to on.** An unproven runner, an unreachable
     environment, or an unanswerable ambiguity all mean off for that plan, announced. A repo with
     `enabled: false` is never turned on because a test folder happens to exist — running "on"
     against a runner nobody watched run produces fabricated red-run evidence.

`jdi.config.example.yml` — insert after `split:` (`:27-33`) with the **non-default** value, per the
example file's convention:

```yaml
tdd:
  enabled: true
  test_instructions: "run `bin/rails test` inside the devcontainer"
```

### Step 3 — `reference/testing.md`, the shared ladder

**TS1 — Prove the test suite runs.** Resolved once per plan, before the first task, by the Butler.
Preamble: capability is proven, not assumed (`reference/tracker.md:18-19`). A `spec/` folder, a
`tests/` folder, or a manifest dependency is **not** evidence.

1. **`tdd.enabled` is not `true`** → off. **Say nothing.** Write no `TDD:` line. Stop.
2. **Derive the invocation** — from `test_instructions` as prose, or from the repo when empty. Say
   which invocation you derived and where you got it.
3. **Run it, scoped as narrowly as the runner allows** — seconds, not a full suite.
4. **Read the output, not the exit code.**
   - **Proof:** the runner printed a test-result tally. A run reporting **zero tests** in a repo
     that has none yet is still proof the runner runs. **The exit code is not the signal** —
     `python3 -m unittest` exits `5` on "Ran 0 tests" (verified on 3.14.7), and a suite with a
     genuine pre-existing failure exits non-zero while proving the runner works. Report a
     pre-existing failure out loud; it does not turn TDD off, but the Executor must know.
   - **Not proof:** command not found, missing interpreter, dependency-resolution error, config
     parse error, unreachable container, timeout, interactive prompt. Nothing ran.
5. **Proven** → write `- TDD: on — proven <date> with \`<command>\`` after `- Started:`.
6. **Disproven** → off, **announced** with the command tried and the output showing why. Write
   `- TDD: off — …`. A degradation, not a silence (`roles/butler.md:23-25`).
7. **Ambiguous** → **ask the user once**, offering: give the invocation, run without TDD, or stop.
   **The Butler asks, never the Executor** — a delegated role may have no user in front of it. With
   no user to ask, degrade to off and say so.

Anything unparseable in an existing `TDD:` line is treated as absent — off, silent.

**TS2 — Write the failing test first.** By the Executor, per task, only when the line says `on`.

1. **Judge whether the task has testable behaviour**, from the plan's `## Testing Strategy` and the
   task's own Verification — under TDD the test to write is the one the plan already named. If the
   plan names none and the Files list is docs/prose/config, **announce the skip** ("task NN has no
   testable behaviour: `<why>`; no test was written first") and implement normally. Never fabricate
   a test. If the plan names none but the task *does* touch executable code, say that too — it is a
   gap in the plan.
2. Write the test, and only the test.
3. Run it and capture the red — exact command and output.
4. **Confirm it failed for the right reason** — the new expectation. A syntax, import, or
   collection error is a broken test, not a red run. Fix and re-run until the failure is the
   assertion.
5. Write the implementation.
6. Re-run the same command and capture the green.
7. **Return both.** A task is **not complete at red.**

Close with why **the Butler does not reproduce red**: `agents/executor.md:80-88` forbids `git stash`
and makes reconstructing a pre-change tree expensive. The Butler verifies the tests are in the diff
and green now, and reads the red evidence.

**The two hand-maintained enumerations, in this same step** — `README.md:218-228` gains a
`reference/testing.md` row; `AGENTS.md:46-47` currently names four reference files by listing them
and must name five. Both are required; `test_reference_files_are_enumerated_in_readme_and_agents_md`
fails naming `testing.md` if either is skipped.

**`reference/plan-store.md`** — after `:17-19` (the `Ticket:` precedent), document the `TDD:` line:
its absence means TDD was never enabled, and every command reads it rather than re-detecting.

### Step 4 — The roles

**`agents/executor.md`**, three edits:

- **Responsibilities** — a new bullet after `:38-42`: perform **TS2** when the Butler hands over
  "TDD on". An untestable task is an announced skip, never a fabricated test. Not complete at red.
- **"What it receives"** (`:54-59`, currently four items) — insert before "The codebase": the TDD
  decision, already resolved — either "TDD off" or "TDD on, and the proven invocation is
  `<command>`". **The Executor never reads `.jdi/config.yml`** (`roles/butler.md:14-15`).
- **"What it returns"** (`:61-65`) — insert after "Verification results": under TDD, the red-run
  evidence (exact command, failing output from before the implementation existed, the assertion line
  showing it failed for the intended reason), then the same command's green output. Where the task
  had no testable behaviour, that judgement and its reason instead.

**`agents/planner.md`** — append to the existing testing-strategy bullet at `:33-41` (same
responsibility, not a new one): **attribute the strategy to the implementation steps** — say which
test proves which step — and **name explicitly any step whose behaviour no test can observe**, with
what proves it instead. This makes the untestable-task judgement a two-party one — the Planner
marks it, the Executor announces it — rather than the Executor deciding alone. It needs no
knowledge of the key.

### Step 5 — The nine command sites

Step-level instructions are **repeated in place**, never cross-referenced; named operations (TS1,
TS2) *are* referenced. No command's step numbers are referenced anywhere in the repo, so
renumbering is safe — but every insertion below fits inside an existing step anyway.

**`commands/execute.md` — three sites**

- **5a. Step 2, new sub-step `c`** after the plan-approval commit (`:33-40`). If `tdd.enabled` is
  not true, do nothing and say nothing. Otherwise perform **TS1** and record the `- TDD:` line after
  `- Started:`. It belongs inside the first-task check because that is where the plan is committed
  anyway, so the line rides that commit.
- **5b. Step 5, the hand-off** (`:48-57`) — a fourth input bullet: read the `TDD:` line. `on` means
  pass the proven invocation and instruct TS2. Missing or `off` means pass nothing and say nothing.
- **5c. Step 6, "Verify independently"** (`:59-61`) — when TDD is on, confirm the tests are in
  `git diff --staged` and that **your own** run is green. **Do not reproduce the red**; read the
  Executor's captured red and check it names the new assertion rather than an import or syntax
  error. If a task touching executable code carries **no red evidence and no stated reason**, lead
  with that the way a failed verification is led with, and ask whether to accept or send back.

**`commands/next.md` — two sites**

- **5d. Step 9, the hand-off** (`:53-58`) — as 5b, compressed. **`/jdi:next` reads the `TDD:` line;
  it never runs TS1.** It has no first-task check, and it must not acquire one: under the silence
  rule a TDD-*off* plan writes no line either, so "no line" cannot distinguish "plan predates the
  key" from "plan started with TDD off". A lazy-detect here would let a mid-plan config flip turn
  TDD on through `/jdi:next` — exactly what the never-rewritten invariant forbids — and would make
  `/jdi:next` and `/jdi:execute` behave differently on the same plan. **No line means no TDD, for
  every command, always.** A plan whose first task ran before this key existed simply runs without
  TDD; say so in the CHANGELOG.
- **5e. Step 10, "Verify independently"** (`:60-61`) — as 5c, compressed.

**`commands/yolo.md` — four sites**

- **5f. Before the loop** (`:21-27`) — perform TS1 once and write the line, as 5a, **and gate it on
  the same condition 5a uses: every task still unchecked.** A resumed `/jdi:yolo` on a plan that
  already started must read the existing state, not re-detect — otherwise resuming a plan that
  began with TDD off would silently turn it on, the same hole as 5d. This is the only place yolo
  resolves TDD: one detection per run, not one per task. TS1's ambiguous rung asks the
  user here, at the top, rather than mid-flight — consistent with the blocked-dependency stop at
  `:57-59`.
- **5g. Step 2 item 3, the hand-off** (`:60-65`) — as 5d. This site and `next.md:53-58` are
  byte-identical apart from the step number and one capital; keep them so.
- **5h. Step 2 item 4, "Self-verify"** (`:66-68`) — as 5c/5e.
- **5i. Step 2 item 5, "Check for failure"** (`:69-72`) — **the sharpest edit in this plan.** The
  existing stop is **not weakened**. Add a scoping sentence naming which run the stop is about, plus
  one new stop:

  > **The failure being checked is the outcome of *your own* run in item 4, against the tree as it
  > stands now.** Under TDD the Executor's report will contain a failing test run: that red is
  > required evidence, captured before the implementation existed, and it is a record of a past
  > state, not a verification result. Do not treat it as one. If your own item-4 run is green, the
  > task passed, whatever red the report contains; if your own run is red, stop, whatever the report
  > says.
  >
  > One new stop: **TDD is on, the task touched executable code, and the report carries neither
  > red-run evidence nor a stated reason there was nothing to test.** Stop the loop and show the
  > report — that is the same class of failure as a verification that was never run.

  The discriminator is structural and needs no heuristic: **the Butler's own post-Executor run is
  the sole arbiter of pass/fail**, and it happens after both halves of the cycle. An expected red
  only ever appears inside a delegated report; a real failure only ever appears in the Butler's own
  output. They never occupy the same channel.

### Step 6 — The user-facing surface

**`commands/init.md`** — the frontmatter `description:` at `:2` gains the TDD question; a **new step
5** goes in after the `split.pieces` question (`:41-55`), renumbering 5→6 through 11→12 (the
back-reference at `:70` points at step 2, which does not move; grep `step [0-9]` afterwards anyway).
The question follows `init.md:37-39`'s precedent — prove the capability, do not record an
aspiration: ask whether the Executor should write tests first (default `false`, and say that off
means nothing changes); on a yes, **propose `test_instructions` from what step 2 already found**,
saying plainly that the value is prose a later agent reads, so "run `bin/rails test` inside the
devcontainer" is a *better* answer than a bare command; **then try it once**, scoped small, and say
whether the suite actually ran. If it did not, say so and record the setting anyway — JDI re-checks
per plan and degrades out loud. Unlike the `split.pieces` question there is no condition under
which this one is skipped entirely: TDD does not depend on a tracker.

**`commands/help.md` — six edits.** The closing config-state line (`:9-12`) gains whether TDD is on;
the `/jdi:init` row (`:25`) gains TDD; a new `###` subsection after "What the pieces become"
(`:82-89`); and the rows for `/jdi:execute` (`:31`), `/jdi:next` (`:33`) and `/jdi:yolo` (`:34`) —
yolo's clause matters most: an expected red inside a TDD task is not a failure and does not stop it.

**`README.md` — two enumerations plus a section.** `:167` (the snippet comment) and `:174` (the
prose) both list init's questions and both gain TDD; then a `### Test-first execution` section after
"What a split piece becomes" (`:179-193`).

### Step 7 — Release, and dogfood

- `.claude-plugin/plugin.json:3` → `1.0.3`, plus `"tdd"` and `"test-driven"` in `keywords`.
- `.claude-plugin/marketplace.json:10` → `1.0.3`. They must match (`README.md:151-154`).
- `CHANGELOG.md` — a `## 1.0.3` entry above `## 1.0.2`: bold one-line headline, bullets with bold
  lead-ins, everything backticked, and a **first bullet stating what happens to a repo that does not
  set the key** — it behaves exactly as it did. Include **Proven, not assumed.** and **Degrades
  down, never up.** Mention the new `tests/` suite as its own bullet.
- **This repo's own `.jdi/config.yml`** — add `tdd.enabled: true` with `test_instructions:
  "python3 -m unittest discover -s tests -v, from the repository root. No install step and no
  third-party packages."` This is the dogfooding, and it is what makes the TDD-on path exercisable
  here at all.

Commit: `feat: Add a TDD configuration (1.0.3)`, the body closing by naming what was deliberately
left out of scope. Before committing: `grep -rn "tdd\|TDD" .`, `grep -rn "step [0-9]"
commands/init.md`, and `python3 -m unittest discover -s tests -v`.

## Testing Strategy

### What the automated suite covers

Twelve assertions across four modules. Each guards a failure this repo has documented as likely:
adapter-breaking frontmatter, schema/example drift, a missing Defaults row, a hand-maintained
enumeration that did not notice a new file, and a version bumped in one of the three places it
lives.

**The falsifiability trace** — each check is green on the current tree and computed from the files
the step edits, so it fails *because the edit is absent*, not because a fixture arranged it:

| Mutation | Test that fails | Names |
|---|---|---|
| Step 2 adds `tdd:` to the schema but not the example | `test_schema_keys_appear_in_the_example` | `tdd.enabled`, `tdd.test_instructions` |
| Step 2 adds the schema block but no Defaults row | `test_every_schema_block_has_a_defaults_row` | `tdd` |
| Step 3 creates `reference/testing.md` but skips either enumeration | `test_reference_files_are_enumerated_in_readme_and_agents_md` | `testing.md`, and which document |
| Step 7 bumps one version file but not the other | `test_plugin_and_marketplace_versions_match` | the two differing versions |

**What the suite cannot cover:** every behavioural claim here is a markdown instruction to an agent.
No unit test can assert a Butler followed TS1's rung 4 rather than trusting an exit code. That is
what UAT is for, and UAT is the *only* proof of the TDD-on path.

### How the TDD-on path gets proven

**How this repo is installed — verified, and it is not what it looks like.** The `just-do-it`
marketplace is registered with a **directory source** pointing at `/home/dabit/git/just_do_it`
(`~/.claude/plugins/known_marketplaces.json`), so the commands executing in this repo are read
**live from the working tree**. There is a stale cache copy at
`~/.claude/plugins/cache/just-do-it/jdi/1.0.0/` — a real copy, not a symlink, reporting version
1.0.0 and containing zero occurrences of `split.pieces` — and it is not what runs. The decisive
check: the `/jdi:init` text this session executed matches `commands/init.md:2` in the working tree
("what the split pieces become") and not the cached copy's line 2 ("where plans live, and where
docs live").

**So UAT runs natively here.** `/jdi:execute`, `/jdi:next` and `/jdi:yolo` exercise the new
behaviour as soon as the working tree has it — no reinstall, no version bump needed to test. The
manual invocation from `AGENTS.md:9-16` ("Read `<abs path>/commands/execute.md` and follow it")
remains the documented fallback for a normal end-user machine, where the install *is* a cached copy
and `README.md:151-162`'s version gate applies.

**The consequence: this plan edits its own runtime mid-execution.** Tasks 03, 04 and 05 rewrite the
very command and role files used to run the tasks after them. Once the task touching
`commands/execute.md` is committed, the next `/jdi:execute` follows the new text. A surprising
change in behaviour part-way through this plan may therefore be the feature taking effect rather
than a bug — note which tasks are already committed when reading any scenario's result.

**Scenarios:**

1. **TDD off is silent (the regression guard).** `tdd` absent; run the first-task check. Expect no
   `TDD:` line, no mention of TDD anywhere, a diff identical in shape to today's. *This is the
   "every existing repo behaves exactly as it does now" claim.*
2. **TS1 proves the runner.** `enabled: true` here. Expect the derived invocation announced, output
   containing a `Ran N tests` tally, and the `- TDD: on — proven …` line written after `- Started:`.
3. **TS1 degrades out loud.** Set `test_instructions` to name an unreachable environment. Expect the
   attempt described, the failure shown, `- TDD: off — <reason>` written, the plan proceeding
   normally, and TDD **not** silently re-enabled by the presence of `tests/`.
4. **The red run is real and reported.** Give the Executor a task with genuine testable behaviour.
   Expect a `FAIL:` line naming the new assertion, then the same command green. **Verify the red
   names the assertion, not an ImportError** — that is the whole point.
5. **Yolo does not stop on the expected red.** Two-task plan, first task testable. Expect the loop to
   continue past the red-containing report, with the Butler's own run reported as pass/fail.
6. **Yolo still stops on a real red (the safety guard).** Same plan, implementation broken so the
   Butler's own run fails. Expect an immediate stop. *Scenario 5 without 6 proves nothing.*
7. **The announced skip.** A markdown-only task. Expect the skip announced and **no fabricated test**
   in the diff.
8. **Missing red evidence is caught.** A report with tests in the diff but no red run on a task
   touching executable code. Expect yolo to stop and execute to lead with it.
9. **The line is not rewritten.** Flip `tdd.enabled` mid-plan, run `/jdi:next`. Expect the existing
   line honoured unchanged.
9b. **A plan that started off stays off.** Start a plan with `tdd.enabled: false` (so no line is
   written at all), then flip it to `true` and run `/jdi:next`. Expect TDD to stay **off** and
   silent — no TS1 run, no line written. Then resume `/jdi:yolo` on the same plan and expect the
   same. *This is the pair to scenario 9: 9 proves an existing line is honoured, 9b proves an
   absent one is not an invitation to re-detect.*

Scenarios 1, 6 and 7 must not be dropped under time pressure: they are the three places this change
could silently damage something that works today.

## Risks

**The `TDD:` line is a new contract on `PLAN.md`**, and a plan can be resumed by a different agent on
a different day. A malformed or hand-edited line has no schema and no validator. Mitigation: exactly
two shapes, and anything unparseable is treated as absent (off, silent). TS1 says so.

**Dogfooding turns TDD on for every future task here, and most are markdown.** The "no testable
behaviour" skip will fire on the large majority of runs. Good for exercising that path, but also
noise — a future contributor may read the repeated skip as "TDD does nothing here". If the noise
proves worse than the signal, the honest fix is `enabled: false` here and proving the mode in a
scratch repo, not weakening the announcement.

**"Failed for the right reason" is a judgement the Executor makes about its own work.** The
structural mitigations are that the red output is quoted verbatim (so the Butler reads the `FAIL:`
line itself), the Butler's green run is independent, and yolo stops on missing evidence. An Executor
that writes a trivially-true test and watches it fail trivially cannot be detected by this design.
That is a known limit — the alternative is the Butler reproducing red, which
`agents/executor.md:80-88` makes expensive on purpose.

**Yolo's scoping sentence is the highest-consequence edit.** If the Executor's red leaks into the
channel the Butler's own run reports on — a harness concatenating a subagent transcript into the
orchestrator's context, say — the safety stop weakens invisibly. The wording mitigates it by
defining the stop positively ("the outcome of *your own* run in item 4") rather than listing reds to
ignore. UAT scenario 6 exists to catch a regression here.

**`test_instructions` is prose, which is a translation surface.** A wrong-but-runnable command (the
wrong suite, the wrong scope) would pass TS1 and produce meaningless red runs all plan. TS1 requires
*saying which invocation you derived and where you got it*, so the user sees it once and can correct
it. This is the cost of choosing prose over a command string; restate it in the CHANGELOG.

**The key-path extractor is not a YAML parser.** It handles the plain two-space-indented subset the
two files are hand-written in, and would misread flow mappings, multi-line scalars, or tabs. If the
schema ever grows exotic YAML the test must grow with it — and it will fail loudly rather than
quietly, which is the right direction.

**The suite has no CI, so it only runs when someone runs it.** A deliberate exclusion (no `.github/`
exists), but it means these guards protect the Executor following this plan, not a future drive-by
edit. A ~15-line workflow would close it; that is a separate issue, not scope creep here.

**`marketplace.json`'s `source: "./"` means `tests/` ships inside the installed plugin.** Harmless —
nothing loads it — but new weight in every installed copy, worth knowing rather than discovering.

**This plan edits its own runtime.** Because the plugin is a directory source read live from the
working tree (see `## Testing Strategy`), tasks 03, 04 and 05 rewrite the command and role files
used to execute the tasks after them. A failure or a behaviour change part-way through may be the
new instructions taking effect rather than a defect. Mitigation: note which tasks are committed
when reading any result, and treat task 05 — the command sites — as the point after which the
workflow itself has changed.

**Nine command sites will drift.** More than the six `split.pieces` needed, and three are new *kinds*
of site (detection, verification-scoping, evidence-checking) rather than repeats of one instruction.
The grep that finds them all is `grep -rn "TS1\|TS2\|TDD" commands/` — name it in the commit body.

## Tasks
- [x] 01 — Add the repository's first automated test suite (depends on: none)
- [x] 02 — Add the `tdd` key to the config schema, defaults, notes, and example (depends on: 01)
- [x] 03 — Write the shared TS1/TS2 ladder and update both reference-file enumerations (depends on: 01)
- [ ] 04 — Give the Executor and Planner their TDD responsibilities (depends on: 03)
- [ ] 05 — Wire TS1/TS2 into execute, next, and yolo (depends on: 03, 04)
- [ ] 06 — Document TDD in init, help, and README (depends on: 02, 03)
- [ ] 07 — Version bump, changelog, and dogfood this repo's own config (depends on: 02, 03, 04, 05, 06)
- [ ] 08 — UAT: prove the TDD-on path and the off-by-default regression guard (depends on: 07)
