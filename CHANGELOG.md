# Changelog

## 1.0.7

**The Splitter cuts plans for parallelism, and execution runs every ready task at once.**

- **The Splitter prioritises parallelisation.** `agents/splitter.md` gains an *Analysing for
  parallelism* pass: find the independent pieces first, shorten the longest dependency chain by
  extracting what several tasks share into an early task the rest fan out from, and keep
  verification able to pass on one task's work alone. A dependency is a claim that two tasks
  **cannot** overlap, never a preferred reading order — numbering carries the order. Parallelism
  now counts as a real boundary when weighing task count, and is still not a licence to fragment.
- **Same-wave tasks are file-disjoint.** No path may appear in the `## Files` of two tasks with no
  dependency path between them, and `## Files` must be complete — creations, modifications and
  deletions. The Splitter checks that itself, mechanically; it is not a Jev question.
- **`## Tasks` is grouped by wave.** A wave is derived — every task whose dependencies are in
  earlier waves — and never declared: there is no new task-file field, `Depends on:` stays the only
  authority, and the commands compute the wave from it each time. The Splitter reports the plan's
  shape (waves, widest wave, critical path), and `/jdi:split` and `/jdi:prep` present it.
- **`/jdi:execute`, `/jdi:next` and `/jdi:yolo` run a wave at a time** — every unchecked task whose
  dependencies are done, one Executor per task, started together in one working tree. The Butler
  checks the wave's `## Files` for overlap before spawning (holding the higher-numbered task back
  if the split got it wrong), verifies every task itself **after the wave has settled**, and shows
  the diff task by task. `/jdi:yolo` stops at the end of a wave with a failure in it, and marks
  nothing from that wave done.
- **Still one commit per task.** `/jdi:done`, `/jdi:next` and `/jdi:yolo` mark every task of the
  wave, one at a time and in number order, each committed **by path** — its `## Files`, anything
  extra its Executor reported, its task file, and `PLAN.md` ticked for that task only. Never
  `git add -A`, never a bare `git commit` while a sibling's work is staged.
- **The Executor knows it is not alone.** New *Running alongside other Executors* section: stay
  inside the task's `## Files`, report any path outside them, never touch, revert, reformat or
  stage a sibling's change, retry on `index.lock` rather than delete it, and never read a
  sibling's half-finished edit as its own failure — under TDD, the red must be its **own** new
  assertion. It is handed the sibling tasks and their paths, and returns every path it touched.
  Inside a task, independent steps are done together too.
- **Concurrency degrades out loud.** `reference/delegation.md` gains *Delegating several roles at
  once*: subagents are spawned in one turn, separate CLI sessions as one process per task, and a
  harness with neither says so once and runs each wave in number order. `reference/plan-store.md`
  gains *Waves*, including the one trade-off: each commit in a wave was verified against the whole
  wave's tree.
- **Under TDD, a wave narrows the command once and uses it for both runs.** `reference/testing.md`
  TS2 gains *In a wave*: when the unscoped proven invocation is broken by a sibling's half-written
  file, the Executor scopes it to its own new test, uses that one command for the red **and** the
  green, and reports the narrowing; the Butler runs the unscoped invocation after the wave settles.
- **UAT never shares a wave**, whatever its `Depends on:` says, and the skip-Splitter path now
  writes `Depends on: 01` into it.
- **A plan split before this release runs exactly as it did.** A `## Tasks` with no `**Wave N**`
  headings is read as a pre-wave plan and runs one task at a time, in number order, said once —
  its `Depends on: None` was written when number order was a guarantee and never promised
  independence. Re-run `/jdi:split` to have it cut for parallelism. A plan that is honestly a chain
  is a wave of one task each time, which is the old flow. There is no new config key.

## 1.0.6

**JDI can ask Jev for a typed judgment where a role would otherwise skim a list.**

- New `jev:` block in `.jdi/config.yml` with one key, `enabled`. **A repo that does not set it
  behaves exactly as it did** — no role sends anything anywhere, and no command mentions Jev, not
  even to say it is off. Silence is the point: a degradation is announced because something was
  asked for and not delivered, and with the key off nothing was asked for.
- **Five named operations**, defined in the new `reference/jev.md` as J1–J5 and called by name the
  way the tracker's T1–T8 are. The Researcher ranks the candidate architecture docs (**J1**) so the
  ones that constrain the change are read first and in full, and screens `consumers` for contract
  breakage (**J2**); **J3** resolves a tracker's idiosyncratic workflow state names by role, which
  is what `reference/tracker.md`'s universal rule 3 already demanded and could only do by reading;
  the Splitter checks a fresh split is really atomic (**J4**); the Feedbacker orders its findings
  by what happens if they ship (**J5**).
- **Jev narrows, it never decides.** It may reorder a list, flag a candidate, or pre-select one
  option from a set the caller already enumerated. It is never the reason a step is skipped, a
  tracker is written, a commit is made, or a pull request is opened. `/jdi:status`, `/jdi:done`,
  `/jdi:execute` and `/jdi:yolo` therefore rank nothing of their own, and `reference/jev.md`
  carries the five-question filter a new one has to pass — including why **T5** and **T8** are
  deliberately not J3 callers.
- **Degrades to more work, never less.** No key, no network, a failed request, or a state too large
  for one request all mean the role reads every candidate itself — precisely what it does with the
  key off. Dropping a consumer sweep because an optional model was unavailable would be a worse
  failure than never having asked, so the fallback is always the un-Jev'd path. A confidence below
  0.5 is treated as no answer.
- **The Butler probes once and passes a resolved fact.** The ladder runs at step 0 of `/jdi:prep`,
  `/jdi:research`, `/jdi:split`, `/jdi:feedback`, `/jdi:plan` and `/jdi:pr`; roles receive "Jev
  is available" or nothing,
  and never read the key or re-probe. Capability is **proven** — a key that exists is not proof and
  the absence of an error is not proof; only a real answer to a real request is. `roles/butler.md`
  now states that as a standing duty covering the test runner and the tracker too.
- **The key never lands in the repository.** It is read from `$TYPESAFE_API_KEY` or
  `~/.config/typesafe/api_key` and passed by reference. `/jdi:init` looks for it, sends one
  throwaway question to prove it works, and reports which source it found without printing the
  value.

## 1.0.5

**Every role's model is named in settings — and no file under `agents/` names a model at all.**

- New `models:` block in `.jdi/config.yml`, keyed by **role**: `researcher`, `planner`, `splitter`,
  `executor`, `synthesizer`, `pr-writer`, `feedbacker`. Each entry carries a `model` and an
  optional `harness`. **A repo with no `models:` block behaves exactly as it did** — every role
  runs in this session's harness on the session's own model, silently, because nothing was skipped.
  Such a repo's 1.0.5 run is indistinguishable from its 1.0.4 one.
- **The three pre-1.0.5 keys are gone.** `models.deep`, `models.standard` and `models.fast` are no
  longer read by anything. A `models:` block still keyed that way names no role, so **nothing in it
  is read**: JDI says so once, names `reference/config.md` as the current schema, and runs every
  role on the session's own model for that run. Nothing breaks, and nothing is silently
  reinterpreted as a role.
- **`models` is the only place a role's model is named.** No file under `agents/` carries a
  `model:` key any more — a model is a fact about the user's account and the harness that will run
  the role, not a fact about a file that ships to every repository. `/jdi:init` offers a model per
  role, proposing rather than asking from zero, and offers to rewrite a `deep`/`standard`/`fast`
  block per role rather than keep one that has no effect.
- **New `harnesses:` block** — per-CLI `args` and `env`, keyed by the kind that a
  `models.<role>.harness` names (`claude`, `codex`, `opencode`). Both are passed to that CLI
  **verbatim**: JDI composes, merges and translates nothing between kinds and adds no flag of its
  own, in particular no approval- or sandbox-affecting one, so any such flag is one the user typed
  — and JDI prints it back before it spawns anything. Write absolute paths; a leading `~` arrives
  as a literal tilde.
- **Degrades down, never up.** A model the named harness cannot express is announced, and the role
  runs on that harness's own default — never silently swapped, and never promoted to a stronger or
  costlier model because that one happened to be reachable. An unreachable CLI, an unresolvable
  role instruction, or a transport that never reported means the role runs in this session instead,
  announced once. The phase is never skipped, and a role never lands somewhere less supervised than
  this session.
- **A documentation correction on a security-relevant claim.**
  `docs/harness-adapter-architecture.md` said delegation does not widen authorization because
  subagents inherit the active sandbox and approval environment. That holds for an in-harness
  subagent and for inline adoption; it does **not** hold for a separately spawned CLI, which is
  another process resolving its own sandbox, approval policy and credentials from its own
  configuration — which may be broader or narrower than this session's. A user reading the old
  sentence would have believed a spawned CLI inherited this session's approval policy. It does not.
  That document and `reference/delegation.md` now carry the same invariant.

## 1.0.4

**JDI now installs as a native Codex skill without changing its Claude Code or OpenCode workflows.**

- Codex discovers the bundled `jdi:run` skill through `/skills` and `$` completion. Its supported
  interface is `$jdi:run <command> [arguments]`; invoking `$jdi:run` without a command runs help.
- **Dispatch fails closed.** The skill accepts only the exact canonical command allowlist, rejects
  unknown and path-like tokens before constructing a path or mutating the working repository, and
  resolves commands, roles, agents, and references from the installed plugin snapshot rather than
  the user's current repository or the original marketplace checkout.
- **Arguments stay opaque.** Every original `$ARGUMENTS` occurrence in a canonical command body is
  replaced globally, literally, and exactly once. Whitespace and punctuation are preserved, and
  replacement text is never rescanned, including commands such as `feedback` with two occurrences.
- Codex delegation follows observed capability: use an available matching or generic subagent with
  the installed role instructions and exactly its declared inputs, then a second non-interactive
  session or announced inline adoption when subagents are unavailable.
- Existing Claude Code `/jdi:<command>` and OpenCode `/jdi-<command>` interfaces are unchanged. The
  Codex manifest and dispatcher are additive; canonical `commands/*.md` remain the sole source of
  workflow behavior for every harness.

## 1.0.3

**Opt in and the Executor writes the failing test first — once the suite has been watched to run.**

- New `tdd` block in `.jdi/config.yml` — `enabled` (default `false`) and `test_instructions`. A repo
  that does not set the key behaves **exactly** as it did: no `TDD:` line is written, nothing is
  announced, and the `PLAN.md` a run produces is byte-identical to what it produced before the key
  existed. Off is silent, because nothing was skipped.
- Two named operations in `reference/testing.md`. **TS1** proves the test suite runs — the Butler,
  once per plan, before the first task. **TS2** writes the failing test first — the Executor, once
  per task, and only when TS1 said `on`. TS1's answer is one `TDD:` line in `PLAN.md`'s metadata:
  `on` names the date and the exact command that was proven, `off` names the rung that applied and
  the evidence for it.
- **Proven, not assumed.** TS1 derives an invocation, says out loud where it got it, and then
  watches the runner actually run before honouring the setting. A `tests/` folder, a `spec/`
  directory, a Makefile target, or a manifest dependency on a test framework is not evidence, and
  "no error" is not proof. **The exit code is not the signal** — `python3 -m unittest` exits `5` on
  "Ran 0 tests", which in a repo that has none yet is still proof the runner runs, while a wrapper
  that swallowed a missing interpreter can exit `0` and prove nothing. Proof is a printed
  test-result tally.
- **Degrades down, never up.** An unproven runner, an unreachable environment, or an ambiguity with
  nobody there to answer it all mean off for that plan, announced with the command that was tried
  and the output showing why it is not proof. Nothing turns TDD *on* that the configuration did not
  — not a `tests/` folder that appears mid-plan, and not a suite created by the plan's own first
  task. Fabricated red-run evidence is a worse outcome than not running TDD at all.
- **A plan whose first task ran before this key existed simply runs without TDD.** TS1 resolves once
  per plan and its line is never rewritten, so editing `.jdi/config.yml` mid-plan changes nothing
  until the next plan. **No line means no TDD, for every command, always** — a plan started before
  the key carries no `TDD:` line, is indistinguishable from one that started with TDD off, and
  neither is an invitation to go looking for a test runner or to ask the user about one.
- **`test_instructions` is prose, not a command.** An agent reads it and translates it into an
  invocation for the environment in front of it; the literal text is usually not runnable as typed,
  because the real invocation depends on a container, a service, or a working directory. "run
  `bin/rails test` inside the devcontainer" is a *better* answer than a bare `bin/rails test`.
  Leave it empty and the Butler works the invocation out from the repository itself.
- **`tdd` never changes what gets committed.** Tests and implementation land in the same commit, one
  per task, exactly as without it. TDD changes the order they are written in, not the history. A
  task with no testable behaviour is an announced skip, never a fabricated test, and a task is never
  complete at red — the Executor returns both the red run and the green.
- `/jdi:init` now asks about TDD, and asks **every time**: unlike the split pieces it depends on no
  tracker, so there is no configuration in which the question is skipped. It proposes
  `test_instructions` from what the repo already says about itself, tries the invocation once, and
  records the setting even when the run proved nothing — where that is still what the user wants.
  The config records intent, and the Butler re-checks it once per plan.
- **A `tests/` suite, the repository's first.** 15 tests on Python's standard-library `unittest`,
  with no third-party dependency and no install step: run `python3 -m unittest discover -s tests -v`
  from the repository root. They guard what this repo has historically half-finished — the version
  agreeing across `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` and the newest
  `CHANGELOG.md` heading; `reference/config.md`'s schema block, its defaults table and
  `jdi.config.example.yml` agreeing with one another; the enumerations in `README.md`, `AGENTS.md`
  and `reference/delegation.md` matching the `commands/`, `agents/` and `reference/` directories;
  and every command and role file carrying frontmatter with a description and a non-empty body.

## 1.0.2

**The splitter is configurable: pieces become subtickets, tracker tasks, or just commits.**

- New `split.pieces` key in `.jdi/config.yml` — `commits` (the default), `tasks`, or `subtickets`.
  It says what a split piece becomes **in addition to** a task file and a commit; the task files and
  the one-commit-per-task rhythm are identical in all three modes, so an existing repo with no such
  key behaves exactly as it did.
- `subtickets` mirrors every task, UAT included, as a child issue of the plan's issue — a Linear
  sub-issue, a Jira sub-task, a GitHub sub-issue. `tasks` mirrors them as a checklist on the issue
  where the tracker has one.
- Two new tracker operations in `reference/tracker.md`: **T7** materialises the pieces at split
  time, **T8** closes a piece when its task is marked done. `/jdi:split` and `/jdi:prep` call T7;
  `/jdi:done`, `/jdi:next`, and `/jdi:yolo` call T8.
- **Degrades down, never up.** No tracker, no issue, no reachable integration, no native checklist,
  or a declined confirmation all mean `commits` for that run, announced out loud. A configured
  `tasks` never quietly becomes `subtickets` — creating issues nobody asked for is the worse
  failure. Sub-issue creation asks once for the whole batch, listing the titles.
- Each mirrored task file records a `Ticket:` line, so re-running `/jdi:split` updates the mirror
  instead of stacking duplicates — the same idempotency rule T5 uses for the research comment.
- `/jdi:init` asks the new question, but only when a tracker is configured, and says plainly whether
  that tracker can express the mode being chosen.

## 1.0.1

**Installable at user scope or project scope.**

- **Claude Code** — documented `--scope project`, which writes a committable
  `.claude/settings.json` so JDI arrives with a clone. `examples/claude-project-settings.json` is
  the equivalent file for merging into settings that already exist.
- **OpenCode** — `bin/sync-opencode.sh` gained `--project [dir]`, alongside the existing (default)
  `--global`. Project mode writes `.opencode/{command,agent}/`, copies the reference files and roles
  into `.opencode/jdi/`, and rewrites every path **repo-relative** — the result holds no absolute
  paths and is committable. Also added `--help`.
- **Codex** — has no project scope; `codex plugin add` takes no `--scope` and records the install in
  `~/.codex/config.toml` machine-wide. Documented rather than worked around.
- Documented two things that bite when committing a project install: a directory source gets
  absolutized by the CLI (so use the `github` source for anything committed), and a marketplace
  **name** holds only one source per machine, so a local user-scope declaration blocks a git-URL
  project-scope one under the same name.

## 1.0.0

Initial extraction of the JDI workflow into a standalone, installable plugin.

- 16 commands, 7 delegatable roles, and the Butler orchestrator role.
- **Tracker-agnostic** — Linear, Jira, GitHub Issues, another, or none. `reference/tracker.md`
  defines six operations every command calls by name; each is capability-detected and skippable.
- **Plan-store-agnostic** — a folder in the repo (default) or an external service such as Obsidian
  or recuerd0. `reference/plan-store.md` carries the per-step differences, since external storage
  changes what is committable at every pause point.
- **Harness- and model-agnostic** — command and role bodies name roles and reasoning tiers
  (`deep` / `standard` / `fast`), never tools, models, or vendors. `reference/delegation.md` maps
  those onto whatever the harness offers, with inline role adoption as a first-class fallback where
  there are no subagents. Runs on Claude Code, Codex, and OpenCode.
- Per-repo configuration in `.jdi/config.yml`, written interactively by `/jdi:init`.
