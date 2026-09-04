# Changelog

## 1.0.4.1

**The pair can talk to each other — in a shape that cannot be waffled.**

The first live run of `/jdi:pair` showed the two agents working with strict turn-taking and no
interaction at all. An agent that was unsure, or that found something the plan had not anticipated,
had exactly two moves: implement it anyway and park a note, or reject the turn. Neither is "wait,
let us think about this". That rigidity was the deliberate cost of confining prose to the ledger to
kill the rubber stamp, and it only showed up in use.

- **The pair can consult, and it must do so in a shape that cannot be waffled.** Not every question
  is a disagreement and not every unknown is answerable by writing a test, so P2 has a third move
  beside implement-and-park and reject. A consult states **named options with the tradeoff and a
  recommendation**, never an open question — "what do you think?" invites agreement, and agreement
  costs one token. The reply is one of the options, or a third named and justified, with a reason;
  "either is fine" is malformed and comes back. Two consecutive consults on one question escalate.
- **A pair that outgrows its plan says so.** A consult whose answer changes the task's Files list or
  the plan's `## Testing Strategy` is allowed — two agents in the code often see what a plan written
  beforehand could not — but it is recorded as a `decided` note and surfaced at task end ahead of
  ordinary notes, because a plan quietly outgrown reads exactly like a plan ignored.
- **A turn is over when the report is complete *and* the pane is settled.** The second live run
  committed a task while its pane was still working: the report was there and read as final, so the
  orchestrator committed, and the pane went on to find a second defect whose fix was staged and in
  no commit. The rule said the report file *was* the turn-over signal and demoted pane state to
  "only the wake-up", which is what the orchestrator followed. **A report is written during a turn,
  not at its end** — a complete file and a working pane are a normal combination, not a
  contradiction. Anything that commits, stages, or hands work onward now needs both signals.
- **The read receipt must cite an added line in the diff.** The first live run found the check had
  a cheaper answer than reading the code: *read the incoming handoff's own receipt and restate it.*
  The channel carrying the handoff also carries the answer to the check meant to police it. One
  receipt did exactly that — citing unchanged context, not the partner's new work — and the
  orchestrator then framed the echo as two independent observations agreeing. A citation into
  context, or into a file the partner did not touch, is now grounds for return even when the
  observation is true.
- **One test-list item per turn, and the backstop scales with the list.** P2 defined an exchange as
  one test's whole life and said to write "the next failing test", but never said it as a rule and
  never told the Butler how to consume a multi-item list. In the first live run the one task that
  had a list — ten items — was handed over as "write all ten, in that order, and stop", collapsing
  ten exchanges into one: the partner reproduced one red instead of ten and reviewed one
  implementation instead of ten. A ten-item task is ten exchanges. The per-task backstop is now six
  **or two more than the list's length, whichever is greater**, because a flat six would make a
  ten-item list unfinishable and push a pair straight back into collapsing it to fit.
- **The Butler must not quote the incoming report's results into a brief.** Naming what to check is
  the job; naming what the answer was turns an independent verification into a confirmation
  exercise, and produces agreement indistinguishable from measurement.
- **`fix-now` is authorised, not merely listed.** P2's parts named it as a disposition while the
  Disagreement section said there were exactly two moves. The run hit the gap repeatedly — a defect
  with no design content, in an area with no test runner, where `next-test` is impossible and a
  rejection would spend a turn-back on nothing. It is now a third move with all three conditions
  stated. A choice with design content is a consult, not a `fix-now`.
- **Why the version has a fourth segment.** `1.0.4` was already installed and exercised when this
  was found. `claude plugin update` compares versions and not content, so a change made in place
  under `1.0.4` would never reach an installed copy — it would report "already at the latest
  version" and do nothing. This is that release.

## 1.0.4

**`/jdi:pair` runs a plan as two agents ping-ponging a failing test — but only when you ask.**

- **A repository that does not set the `pair` key is unaffected.** The block has no `enabled` key,
  because it never says *whether* to pair — only *which* two agents to pair. `/jdi:pair` is never
  invoked unless a user types it, and `/jdi:yolo`, `/jdi:execute` and `/jdi:next` stay single-agent
  regardless of what the block says. Nothing detects pairing, and no other command reads the key.
- **Ping-pong, rotating on the red/green boundary.** One agent writes a failing test and hands it
  over; the other reproduces it, makes it pass, refactors, and writes the next failing test. TDD is
  a prerequisite rather than a coincidence — the rotation point *is* the red/green boundary
  `reference/testing.md`'s **TS2** already turns on, so the swap is structural rather than a timer.
- **An agent asked to review and approve will approve.** "LGTM" costs one token, satisfies the
  instruction as written, and is indistinguishable in a transcript from a review that happened; no
  amount of "review carefully" changes what the cheapest compliant answer is. So the protocol does
  not ask for a review: **the receiver must re-run the incoming failing test itself, and confirm it
  fails on the named assertion, before it may implement.** `reference/testing.md` records that the
  Butler does not reproduce red, because a throwaway worktree or a second clone on every task costs
  more than the check is worth — **the partner does it for free, because it must run the test
  before it can implement.** Every red is independently verified by a second party that neither
  wrote the test nor chose the assertion. That is this mode's whole quality claim.
- **Two requirements, checked at run time.** A resolved `TDD: on` line in the plan — not merely
  `tdd.enabled`, because TDD can be configured on and still resolve off — and a Herdr session
  (`HERDR_ENV=1`). Either unmet and the run is not paired: the Butler announces which rung stopped
  it and offers to run the plan single-agent instead.
- **Degrades to not pairing, never to a half-pair.** One pane up and the other refused is a
  failure, not a degraded mode — a single agent taking both sides of a ping-pong is exactly the
  rubber stamp the protocol exists to prevent. Degradation is never automatic, and nothing turns
  pairing on that the user did not type.
- New `reference/pairing.md`, three operations under the `P` prefix. **P1** proves the pair can run
  — an eight-rung ladder, re-run in full on every invocation, because an agent name is a handle on
  a live process and panes never survive a session. **P2** is the exchange: a five-part handoff
  carrying the failing test, the red transcript, the test-list delta, the parked-notes ledger, and
  a read receipt with content. **P3** is the Butler moving reports between two panes and checking
  their shape, never their substance. Driver and navigator are turn assignments inside the existing
  Executor role, so no new spawnable agent type was added.
- Two new bidirectional test guards, on `commands/help.md`'s command table and `roles/butler.md`'s
  ownership table. Adding the first immediately found `/jdi:help` missing from its own table — 15
  commands listed against 16 files in `commands/` — so a user who ran `/jdi:help` never learned the
  command exists. The suite is 17 tests.
- `/jdi:init` now asks which two agents to pair, **but only when `herdr` is on `PATH`** — with no
  multiplexer to pair in, every answer would be unusable, so the question is skipped and no `pair`
  block is written. When it does ask, it proposes kinds rather than asking from zero: it settles
  P1's first and third layers here and now, takes `herdr integration status` as the evidence for
  the second, and says out loud that the second's definitive answer needs a live pane — and that
  `/jdi:pair` re-runs every layer in full on every invocation regardless.
- **The honest cost.** Arisholm et al. found pairing's overall correctness gain **not significant**
  for ~84% more effort, with the gains confined to complex tasks and less-expert pairs; two panes
  each carrying a full context per turn roughly doubles token cost on top. `/jdi:pair` is a
  deliberate choice for a hard task, not a default — which is why it is its own command rather than
  a flag on `/jdi:yolo`.
- **Deliberately left out of scope**, each for a stated reason: `commands/prep.md`'s config-block
  list (prep never resolves P1), `commands/status.md` (matching both earlier config-key releases),
  `agents/planner.md` (its "say which test proves which step" bullet is already the granularity P2
  consumes), a new `agents/*.md` role file (a file in `agents/` registers a spawnable agent type,
  and a "driver" reachable as an in-process subagent — not in a pane, unable to ping-pong — is
  worse than one nothing can instantiate), `bin/sync-opencode.sh` (glob-driven, so it needs no
  edit), and this changelog's own 1.0.0 entry (a historical record of what shipped then, so its
  command count is not a number to update).

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
