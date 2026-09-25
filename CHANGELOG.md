# Changelog

## 1.0.10

**A Butler inside Herdr can run a delegated role as its own agent process, wait for it, and accept
its work only through a validated result file.**

- **`delegation.transport` decides how a role on another CLI runs: `native`, `auto` or `herdr`.**
  `native` is the default and is the delegation JDI already did; it probes nothing at step 0 and
  says nothing. `auto` checks for Herdr once, at step 0, and runs the role in a Herdr pane when
  Herdr is there; outside Herdr it is exactly `native`, and nothing is said. `herdr` does the same,
  but announces any failed check once. A repo with no `delegation` block behaves exactly as it did.
  Whether you work inside Herdr is usually true of your machine, so `reference/config.md` suggests
  setting the key in `.jdi/config.local.yml`.
- **Only a role configured on a different CLI gets a Herdr pane.** Herdr is used for a role whose
  `models.<role>.harness` names another CLI. A role on this session's own CLI stays a subagent, as
  before, and you can watch it in the harness itself. Any role on another CLI qualifies, Executor
  waves included: a wave gets one pane per task in its own tab, at most 4 open at once, and the
  Butler lets the whole wave settle before it acts on any one result.
- **`reference/herdr.md` is the one place every Herdr step is written.** Operations H1 to H9 cover
  detection, the worker-kind check, run preparation, start, prompt and wait, a blocked worker,
  result validation, pane close, and a Butler's own worktree for `/jdi:herd`.
  `reference/delegation.md` calls them by name. Workers run on Herdr's agent surface, so the Butler
  can tell `working`, `blocked`, `idle`, `done` and `unknown` apart. The older pane-run recipe is
  gone.
- **Work is accepted only through a validated result file.** Each run gets its own directory,
  `<gitdir>/jdi/runs/<run-id>/`, with the Butler's `manifest.json` and `prompt.md`, the worker's
  `report.md` and `result.json`, and the Butler's `outcome.json`. A terminal transcript is never
  the result, and `idle` or `done` is not proof of success. H7 checks the run ID and role,
  `status: complete`, every item the role returns, that HEAD did not move, and that
  `git status --porcelain` shows no write outside the run's allowed paths. A worker that needs an
  answer writes `needs_input`, and one that cannot do the work writes `failed`.
- **A blocked worker, a silent worker and a timeout all go to the user.** Approval, permission,
  trust and question dialogs belong to the user, who answers them in the worker's pane; the Butler
  never sends keys into a dialog. A worker that goes idle without a result file is inspected: when
  its pane ends in a question, the Butler tells the user which pane to answer in (agent name and
  pane ID) and keeps waiting. Every wait has a timeout, and the overall deadline defaults to 45
  minutes. At the deadline the Butler never counts the run as a success and never resubmits; it
  asks whether to keep waiting, accept a file the user has checked, or abandon. Every pane JDI
  opened is closed on every exit.
- **Degrades to `native`, never beyond.** A Herdr failure closes the pane, announces once, and runs
  the same role through its CLI's non-interactive mode. It is never retried on Herdr in the same
  phase, and the phase always runs. A transport-level failure switches the rest of the run to
  `native`. JDI detects and never repairs: it starts no Herdr server and installs no integration.
- **Every separately spawned process is announced in one fixed line, and `native` stays silent.**
  Before a non-interactive CLI run or a Herdr agent starts, the Butler prints one line that opens
  `JDI spawn <run-id or "-">: <Role> on <kind> (<model | CLI default>)` and then lists the args, the
  env keys and the run dir (a Herdr agent adds its agent name). A spawn without that line is a
  defect. Under `native`, or with no `delegation` block, step 0 runs no Herdr command, and the run
  mentions the transport nowhere, summaries included. Herdr's run files are now written after the
  pane exists, so `manifest.json` records the real pane ID and is never edited afterward.
- **The "watch the run" trigger is gone.** Herdr was also used when the user asked to watch a
  delegated role. `delegation.transport` alone decides now, and a role on this session's own CLI
  can already be watched in the harness.
- **Herdr's `kinds:` line is read correctly.** It lists the kinds Herdr supports, not the kinds
  installed. A worker kind must appear on that line and its CLI must resolve on `PATH`;
  `herdr integration status` affects only detection quality.
- **The Feedbacker should not run on the same model and harness as the agent it reviews.** The
  rule named only the model before. Where no second model or harness is available, the review still
  runs and says that producer and reviewer shared both.
- **`/jdi:herd` arrives on the shared Herdr operations; `herd.args` and `herd.env` from PR #5 are
  replaced by `harnesses.<kind>`.** It preps several issues in parallel, one Herdr worktree,
  workspace and agent per issue, and it requires Herdr with no fallback. Herd agents take their
  arguments and environment verbatim from `harnesses.<herd.kind>`, and the `herd` block keeps
  `kind`, `max_parallel` and `seed`. Each worktree folder is named after its issue,
  `<worktrees dir>/<repo>/jdi-herd-<issue>`, so after a crash `git worktree list` shows which
  folder belongs to which issue; an existing folder is reported, never duplicated or removed.
  Scratch branches are unique per run, `jdi-herd-scratch-<herd-id>-<N>`, so a second herd in the
  same repo does not collide with the first. Cleanup is guarded: before a worktree is removed,
  `/jdi:herd` names any uncommitted plan files, offers the plan commit, and never forces the
  removal without an explicit yes.

## 1.0.9

**A personal `.jdi/config.local.yml` overrides the repository's `.jdi/config.yml`, key by key, and is
never committed.** The committed file says what is true of the repository; the local file says what
is true of this machine or this person — the model a role runs on, a `harnesses` entry carrying a
path from this disk, TDD off while the runner is broken locally — without editing a shared file in
a checkout that may be thrown away.

- **`.jdi/config.local.yml` is layered over the resolved config.** Whichever level answered —
  `config.yml`, the repo's `AGENTS.md` / `CLAUDE.md`, or the built-in defaults — the local file is
  merged over it: a mapping merges, a scalar or a list replaces the whole value, a key it does not
  name is left alone. It can override a value and never delete one, and a local file with no
  `config.yml` beside it still applies. **A repo with no local file behaves exactly as it did**; no
  command says a word about a file that is not there.
- **Every config load names the blocks it overrides, in one line.** The twelve step-0 sites now
  carry the merge rule in place and say which top-level blocks the local file touches — never the
  values — because it is the one divergence a collaborator reading the committed file cannot see.
  They also say so when git tracks the local file, since it is meant to be ignored.
- **`/jdi:init` writes `config.yml` only.** It reports what an existing local file overrides, offers
  to leave a personal answer out of the shared file for the user to put there, and runs
  `git check-ignore` on `.jdi/config.local.yml` whether or not it exists — a personal override that
  gets committed is applied to everyone, which is the destructive direction. It never writes the
  local file itself.
- **Neither config file is a secret store.** The three sentences that justified "never write the
  Jev key here" with "which is a committed file" now cover the local file too: uncommitted is not
  the same as secret. The key stays in `$TYPESAFE_API_KEY` or `~/.config/typesafe/api_key`.
- **The local file is per checkout.** A linked worktree, a fresh clone, and a colleague's machine
  do not have it, and `reference/config.md` says so: a setting that must survive the checkout
  belongs in `config.yml`, committed. `docs/config-key-lifecycle.md` records that a new key inherits
  the override for free, and that a key whose value is personal is the case the local file is for.

## 1.0.8

**A specification is executable prose, and the roles that write one now check it against what the
role downstream can actually perform.** Each entry below is an instruction that reads as precise
and cannot be carried out as written — or a field a later step parses that was only ever stated in
prose. Four of them came out of a single `/jdi:prep` → `/jdi:yolo` → `/jdi:pr` run; the rest were
found the same way, one workflow at a time.

- **The Splitter checks a prescribed template against its own case list.** `agents/splitter.md`
  gains a responsibility: naming an existing file as the template for a new test's harness asserts
  that the template can express **every** case the same task lists, so the template's return shape
  is read against that list before the instruction is written. A seam that concatenates two streams,
  or a call that discards one of them on a successful run, cannot carry a case that asserts on them
  separately — and where the template falls short, the task names the deviation instead of leaving
  the Executor to hit the conflict at the fourth case and choose which of two sentences from the
  same author to override.
- **The Planner owns the same check when the plan names the precedent.** `agents/planner.md` already
  said to default to the precedent test's assertion *style*; it now also requires checking that
  precedent's **harness** against the assertions the plan requires. The template is picked early
  and the cases are written late, and nothing re-reads the first against the second unless a rule
  says to.
- **A fenced example says which of its parts are exact.** A plan document wrapped at a fixed column
  breaks its own fences, and an ellipsis proves a fence is not literal — so *compare it character by
  character* against one is unsatisfiable, and the undecidable part (does that paragraph carry hard
  newlines?) silently becomes the contract between two tasks in different waves. The Planner states
  the encoding beside the fence, or carries the bytes in a verbatim appendix; the Splitter names
  which properties are exact and which are illustrative. (#14)
- **Every mandated emission names its stream.** Where a program's stdout is captured whole by its
  caller, a diagnostic mandated "before the payload" lands *in* the payload unless the instruction
  says otherwise — and the locally idiomatic reading is usually the wrong one. The Planner's risk
  mitigations and the Splitter's task files now name the stream for every emission, and say why
  local precedent does not apply when it disagrees. (#15)
- **A mutation target resolves to its definition site.** "Change the SHA slice in `<subject>.py`"
  names nothing at all when the subject imports the helper and the slice lives in the sibling. The
  Planner and Splitter follow imports to the file and symbol that define the behaviour and say what
  crossing that boundary proves; the Executor reports the file and symbol it actually edited, since
  a reverted mutation leaves no diff to record it. Naming the calling file fails into the same
  silent no-op the anti-vacuity check exists to detect. (#17)
- **A task file's machine-read parts are written first, and prose does not substitute for them.**
  `status:`, `Depends on:` and `## Files` — plus the `## Tasks` wave headings — are what the
  execute loop reads; a task that announces "Wave 2, in parallel with 03" in its text has declared
  nothing to the runner, and the degradation is silent and in the safe-looking direction. The
  `## Files` gap is the sharp one: that comparison is all that stands between two concurrent
  Executors and the same path. The Splitter now writes the skeleton before the prose;
  `reference/plan-store.md` states the contract where the consumer reads it, and `/jdi:split` says
  the wave a task announces is not the wave the runner computes. (#18)
- **A task's Why is checked against the decisions it cites.** The Why is the first thing an
  Executor reads and the text a tracker mirror publishes, so a paraphrase that reverses the
  decision quoted correctly two screens below is the version that gets acted on. The Splitter
  re-reads each decision by id, and the task template ends the Why with the ids it rests on, so a
  mismatch sits side by side. (#22)
- **The condensing target is a diagnostic, not a gate.** "70–80% smaller" now names its unit
  (words — a line count flatters a cut that has stopped compressing) and yields to the preserve
  list. Where preserved content alone exceeds the target, the Synthesizer reports the shortfall
  with its itemised reason and hands the cut/keep decision back rather than reaching the number by
  dropping a preserved item or collapsing two facts into one looser sentence — which is the failure
  mode the same role file already calls unacceptable. `/jdi:pr` stops asking for a harder cut when
  that reason is supplied. (#23)
- **A condensed plan states nothing about the commit that writes it.** A count, a hash or a push
  state that includes the condensing commit is false the moment it is stored, and correcting it
  adds another commit that reproduces the error at the same size. The Synthesizer points at
  `git log <base>..HEAD`, scopes any number to something already closed, and leaves one sentence
  saying the omission is deliberate; `/jdi:pr` removes such an assertion instead of updating it.
  (#24)
- **The TDD decision is stated in every dispatch, including when it is off.** An Executor told
  nothing about TDD cannot tell a resolved `off` from a decision lost in the handover, and the two
  demand opposite behaviour — so a silently dropped "TDD on" yields an Executor that implements
  first, tests after, reports green, and looks exactly like one obeying "off". TS1 rung 1's silence
  is owed to the user and to `PLAN.md`, never to a handover between roles. The Executor also gains a
  defined response to the absence: implement normally, and report that none was received. (#19)
- **TS1 may build the runner when the first task is what builds it.** A gate that runs before the
  first task cannot depend on what the first task produces — a container task 01 creates, a
  dependency directory nobody has installed. The Butler now performs such a task inline as part of
  TS1 and hands down the resolved invocation, because environment bring-up is a precondition it
  owns: whatever every task in a wave needs but no task *owns* is invisible to the same-wave file
  guard, which compares tracked paths and cannot see a gitignored build directory two Executors are
  about to race into. (#20)
- **UAT is walked before `/jdi:pr`.** Told that a criterion is "exercised at merge time", a split
  made the merge step 1 of the UAT task — which, since `/jdi:pr` follows UAT, can never be run in
  sequence. UAT now never contains a merge or a push to the default branch; criteria observable
  only afterwards go in an *after the merge — deferred* list, excluded from marking it done. (#21)
- **`reference/jev.md` shows a request body, not only a response.** Three separate sessions guessed
  the same two wrong shapes in the same order, and each guess cost the run its Jev, because the
  ladder allows one retry and a caller-side typo spent it. The reference now carries a verified
  body for all three question types — they disagree with each other: `noul` takes `instructions`,
  `choice` requires `criteria` as an object, `score` requires `criteria` as an ordered list, while
  the *response* echoes those levels back as a `legend` map. Rung 4 now separates a 400/422 naming
  a field path from a service failure: that request never reached a judgment, so it is corrected
  and sent once more instead of turning the feature off for the run. (#25)

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
