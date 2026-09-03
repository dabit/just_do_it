# Add a pair programming mode

- Tracker: github
- Project: feature development
- Issue: #3
- Issue URL: https://github.com/dabit/just_do_it/issues/3
- Created: 2026-09-03
- Started: 2026-09-03
- TDD: on — proven 2026-09-03 with `python3 -m unittest discover -s tests -v`
- Base commit: main @ 296103df517fa0527082f4a2f77898afc7951c41
- Summary: A /jdi:pair command and a pair config block that has two agents work a plan together as driver and navigator, requiring TDD and a Herdr session.

## References

### Prior art in this repo

- `plans/1-tdd-configuration/PLAN.md` — the closest precedent: same shape (a behavioural config
  key plus named operations plus hand-off interception). Read `## Decisions` and `## Plan gaps
  caught during execution` before designing the gate; two of those gaps are traps this plan can
  repeat verbatim
- `docs/config-key-lifecycle.md` — the repo's written procedure for adding a config key; pairing is
  the third instance. **Its `file:line` citations are stale** (recorded as deferred in the TDD
  plan's Remaining work) — trust the prose, re-derive the lines
- `reference/testing.md` — TS1/TS2. The model for a named-operation file: preamble naming the
  prefix convention, a who/when table, a universal-rules block, a numbered degradation ladder, and
  the once-per-plan metadata-line mechanism
- `reference/plan-store.md` — where the `TDD:` line is documented; a `Pair:` line belongs beside it
- `reference/tracker.md` — T7's degradation-ladder idiom, which testing.md already copies
- `reference/delegation.md` — the three delegation paths. **Path 2** (shell out to a second
  session) is how a Herdr-hosted agent is reached; path 1 cannot instantiate one from a role file

### The sites this change must touch

- `reference/config.md` — three edits: schema block, defaults table, `## Notes` invariants
- `jdi.config.example.yml` — the example, deliberately showing a non-default value
- `commands/execute.md`, `commands/next.md`, `commands/yolo.md` — the triplicated hand-off and
  verify sites. `yolo.md`'s "Check for failure" is the highest-consequence text in the repo
- `commands/replan.md`, `commands/reresearch.md` — the precedent for a command written as "follow
  `/jdi:<other>` in full, with N differences", sanctioned by the lifecycle doc as one of the two
  allowed exceptions to repeat-in-place. This is how `/jdi:pair` avoids a fourth copy of the
  hand-off block
- `agents/executor.md` — Responsibilities, "What it receives", "What it returns"; and the
  single-writer staging discipline that two agents in one worktree would break
- `agents/synthesizer.md` — carries the `TDD:` line into the condensed plan; a `Pair:` line owes
  the same treatment
- `roles/butler.md` — pass a role exactly the inputs its "What it receives" lists; announce every
  skip
- `commands/init.md`, `commands/help.md`, `README.md`, `AGENTS.md` — user-facing surface

### Enumerations: what is machine-checked and what silently rots

- `tests/test_enumerations.py`, `tests/jdi_files.py`, `tests/test_config_schema.py` — **checked**:
  `AGENTS.md`'s command table, README's command and role counts, `reference/delegation.md`'s roles
  table, the reference-file lists in README and `AGENTS.md`, schema/example/defaults agreement
- **Unchecked, and each would rot silently**: `commands/help.md`'s command table (the one a user
  actually sees), `roles/butler.md`'s ownership table, `reference/delegation.md`'s "eight roles /
  seven delegatable" prose, README's "seven roles" statements, and README's "two testing
  operations (TS1–TS2)" row
- `CHANGELOG.md`'s 1.0.0 entry names "16 commands, 7 delegatable roles" — **historical, must not
  be edited**
- `bin/sync-opencode.sh` — glob-driven; a new command, agent, or reference file needs no adapter
  edit

### Herdr

- `herdr --skill` is the authoritative agent-facing spec. `herdr agent` and `herdr pane` print
  current syntax
- Three separate layers must all be checked before honouring a configured agent: 22 kinds the
  binary supports, 17 installable integrations, and the binary actually on `PATH`
- `docs/herdr-coordination.md` — architecture doc written for this plan: the precondition and
  caller context, the four hops and what each refuses, the three-layer kind check, the five
  lifecycle states, the four failure modes, the shared-file exception, and the single-writer rule
- **Measured 2026-09-03:** `opencode` reports state through an authoritative hook
  (`full_lifecycle_hook_authority`); `claude` is detected by **scraping the terminal title**
  (`osc_title_working`). The two halves of the intended pair do not report state the same way

### Human pair-programming practice

- Böckeler & Siessegger, *On Pair Programming* (Thoughtworks, 2020) — driver/navigator definitions;
  the named failure modes (Micro-Management Mode, Keyboard Hogging); "agree on one tiny goal at a
  time … defined by a unit test"; the 5-seconds rule; parking notes for the goal boundary
- Open Practice Library, *Ping-Pong Programming* — the canonical loop: A writes a failing test, B
  makes it pass writing only enough code, B writes the next test, A makes that pass
- Llewellyn Falco, *Llewellyn's Strong-Style Pairing* (2014) — "for an idea to go from your head
  into the computer it must go through someone else's hands", and the highest-abstraction rule
- Kody Fintak, *Trunk-Based Ping-Pong* (Industrial Logic) — rotation tied to an integrable state
  rather than a clock
- Coderetreat constraint catalogue — Mute Ping-Pong (express disagreement through a test) and Evil
  Coder, both framed as deliberate-practice constraints
- Tuple, *Pair Programming Antipatterns* — the checked-out navigator, and the remedy of asking a
  question that cannot be rubber-stamped
- Xebia, *Practical Styles of Pair Programming* — "The Tour" and "The Disconnected Pair"
- Arisholm et al., IEEE TSE 33(2) 2007; Hannay et al., IST 51(7) 2009 — the honest cost literature:
  pairing's overall correctness gain was not significant for ~84% more effort, with the large gains
  confined to complex tasks and less-expert pairs

## Decisions

**A new `reference/pairing.md`, with the `P` prefix.** `grep -rn '\bP[0-9]\b'` returns nothing, so
`P1`–`P3` collide with neither `tracker.md`'s `T1`–`T8` nor `testing.md`'s `TS1`/`TS2`. The
lifecycle doc's test for a new reference file — "several commands perform the same operation" —
pairing fails; only `/jdi:pair` invokes it. It earns the file on a **third consumer type the
lifecycle doc does not list: the two paired agents themselves.** They are reached by delegation
path 2 and handed an absolute path to read. That path cannot be `commands/pair.md`, which is
written to the Butler in the second person and describes orchestration the panes must not perform.
Adding a `TS3` was rejected: it would rot README's "two testing operations (TS1–TS2)" row, which
nothing checks.

**No new `agents/*.md` file.** Files in `agents/` register as spawnable agent types. An
`agents/driver.md` would create a **delegation path 1 route to something that must only ever be
reached by path 2** — an in-process subagent named "driver" that is not in a Herdr pane, cannot
ping-pong, and shares the orchestrator's context. That is worse than a file nothing can
instantiate; it is one that can be instantiated wrongly. Driver and navigator are **turn
assignments inside the Executor role**: the agent in the pane *is* an Executor, handed a paired
turn. Six enumerations stay still as a result.

**The `Pair:` line has one shape, not two.** `- Pair: on — <kind A> + <kind B>, first paired
YYYY-MM-DD`, written once by `/jdi:pair`, never rewritten. It owes what the `TDD:` line owes —
documented in `plan-store.md`, carried by the Synthesizer — and diverges in one way: **there is no
`off` shape.** The `TDD:` line writes `off` because the *configuration* asked for something the
environment refused, and later commands must be told not to re-detect. Pairing is requested by a
**command**, so the degradation is announced to the user who typed it, in the same turn — the
announcement is the record. An `off` line would create a persistent artefact a later command might
be tempted to read, which is the failure universal rule 3 exists to prevent. **No command reads the
line to decide anything.**

**P1 runs per invocation; the line is written once per plan.** Unlike TS1 the preflight *cannot* be
once-per-plan: an agent name is a handle on a live process, and panes never survive a session. The
live checks re-run every time; only the record is written once.

**`/jdi:pair` is written as "follow `/jdi:yolo` in full, with seven differences"** — the
`replan.md` / `reresearch.md` shape the lifecycle doc sanctions as one of two allowed exceptions to
repeat-in-place. A fourth copy of the Executor hand-off would be a fourth thing to drift.

**Degradation is never automatic.** P1 failing at any rung means the Butler announces which rung and
asks: run single-agent — which is `/jdi:yolo`, followed with zero differences — or stop. It never
silently becomes a solo run and never writes a `Pair:` line.

**Deliberately out of scope:** `commands/prep.md`'s config-block list (prep never resolves P1),
`commands/status.md` (matching both precedents), `agents/planner.md` (its existing "say which test
proves which step" bullet is already the granularity P2 consumes), `bin/sync-opencode.sh`
(glob-driven), and `CHANGELOG.md`'s historical 1.0.0 entry.

## Implementation Plan

Tasks are grouped so **every machine-checked enumeration lands in the same commit as the file it
enumerates.** Not tidiness: this plan's own execution runs TDD-on under `/jdi:yolo`, and a task
adding a file without the lists naming it leaves the suite red, which stops the loop.

### 1. Make a new command and a new config key falsifiable

**Files:** `tests/jdi_files.py`, `tests/test_enumerations.py`, `commands/help.md`.

Two enumerations currently unguarded become checked, bidirectionally: **`commands/help.md`'s command
table** (the one a user actually sees) and **`roles/butler.md`'s ownership table**. Butler's rows
*group* commands, so the check extracts every `` `/jdi:<name>` `` from the table rows rather than
expecting one row each. Add `command_slugs()` to `jdi_files.py` and a `slash_commands(lines)`
extractor scoped with the existing `table_rows()` helper.

**This step's red is real and pre-existing.** `commands/help.md`'s table names 15 commands for 16
files: **`/jdi:help` is missing from its own table**, so a user who runs it never learns the command
exists. The new assertion fails on the current tree naming `help`. **The fix is to add the
`/jdi:help` row, not to exempt `help`** — exempting it is the tempting green and would neuter the
guard exactly when `/jdi:pair` arrives.

The butler guard is green today; its red comes from temporarily removing one command name,
capturing the failure, restoring. **Say in the report which red was real and which induced.**

### 2. Add the `pair` block to schema, defaults, notes, and example

**Files:** `reference/config.md` (three edits), `jdi.config.example.yml`.

Schema block after `tdd:`, one key, no `enabled`:

```yaml
pair:
  # Free-form prose naming the two agents `/jdi:pair` should pair — never a list
  # JDI trusts and never a command to execute. "claude and opencode, both in this
  # repository" is the shape. The Butler reads it, translates it into two Herdr
  # agent kinds, and proves each startable here and now before honouring it.
  # There is no `enabled` key: running `/jdi:pair` is the intent, and no other
  # command reads this block. Leave it empty and `/jdi:pair` asks, then offers to
  # write the answer here. See reference/pairing.md, P1/P2/P3.
  agents: ""
```

Defaults row: `` | `pair.agents` | empty — `/jdi:pair` asks which two agents to pair and offers to
persist the answer | ``. Two `## Notes` invariants:

- **`pair` has no `enabled` key, and no command reads it but `/jdi:pair`.** A repo that sets it and
  never runs the command behaves exactly as one that does not.
- **Pairing degrades to not pairing, never to a half-pair.** One pane up and one refused is a
  failure, not a degraded mode: a single agent taking both sides of a ping-pong is the rubber stamp
  the protocol exists to make impossible.

Example file gets the **non-default** value: `agents: "claude and opencode, both started in this
repository"`.

### 3. Write `reference/pairing.md`, and both reference-file enumerations

**Files:** `reference/pairing.md` (new), `README.md`, `AGENTS.md`.

Preamble names the `P` prefix and two things other reference files do not need: that it **names an
external CLI (`herdr`) in its body deliberately** — a capability checked at P1 and degraded from out
loud, exactly as the tracker files treat an MCP integration, and an adapter must not strip it — and
that **both paired agents read this file by absolute path**, which is why the protocol lives here
and not in `commands/pair.md`.

| Operation | Who | When |
|---|---|---|
| **P1** — prove the pair can run | the Butler | once per `/jdi:pair` run, before the first exchange |
| **P2** — the exchange | the two paired agents | every turn, once P1 said `on` |
| **P3** — drive a turn | the Butler | every turn |

**Universal rules:** pairing is requested, never detected; the turn is the write lock; neither agent
answers the other's approval dialog or prompts the other; capability is proven, not assumed; the
Butler is not half the pair, so its verification stays independent.

**P1 — the ladder**, first rung that applies, announced, degrade down only:

1. **The `TDD:` line does not read `on`** → not paired. **Do not run TS1 here**, and never treat an
   absent line as an invitation to detect. Read *after* the pre-loop TDD step yolo supplies.
2. **`HERDR_ENV` is not `1`** → not paired. `herdr` on `PATH` says installed; a socket says a server
   runs somewhere; neither says *this process* is in a managed pane.
3. **`pair.agents` empty or absent** → **ask, do not degrade.** The only config write outside
   `/jdi:init`: run rung 4's check first and offer only kinds that clear it; say the value is prose;
   **show the exact YAML, name the path, get explicit confirmation**; append the `pair:` block only,
   never reformat anything else. If `.jdi/config.yml` does not exist, do not create it as a side
   effect — offer a minimal file or a one-run answer. Record an unstartable choice if the user still
   wants it, saying so. **Write before any pane starts.**
4. **The three-layer kind check, run now:** in `herdr agent`'s list; **classifiable** — an
   authoritative hook or a detection manifest, an outdated integration being a warning not a
   refusal; resolvable by `command -v`. **Name the environment measured in.** Warn
   that bare `herdr` launches the TUI and a mutating nested command probed bare executes.
5. **Bring the panes up.** `pane layout` to pick a direction from the reported rect; `pane split
   --current --direction <dir> --cwd <absolute root> --no-focus`; `agent start <name> --kind <kind>
   --pane <id>`. Always name a target, always `--no-focus`. **Never persist an agent name.**
   `agent_not_ready` means read the pane and wait — **do not restart.**
6. **Record which lifecycle source you are trusting.** `agent explain --verbose` per pane, and say
   whether state comes from a hook with authority or a **detection manifest scraping the terminal
   title**. Changes nothing about the protocol; tells the user which readings are weaker evidence.
7. **Designate the shared directory** — absolute, resolved now, **outside the working tree**, because
   the Executor stages every file it writes and a report inside the tree lands in the commit. Ask
   before reusing files from an earlier run.
8. **Paired** → write the `Pair:` line alongside `- Started:`, only if absent.

**P2 — the exchange.** A **turn** is: reproduce the incoming red → make it pass → refactor → write
the next failing test → hand off. An **exchange** is one test's full life. **The completion unit is
the exchange, not the turn.** The opener seeds the list and **alternates per task**, so neither
agent is permanently the test author.

**The test list is derived, never invented** — one item per Verification clause and per Testing
Strategy item. Added mid-task only with a stated reason naming the clause it refines or the bug it
came from; an item tracing to neither becomes a `next-test` parked note the Butler surfaces as a
plan gap.

**The five-part handoff**, all five or it is returned:

1. **A failing test — the sender's entire design authority.** No prose telling the receiver how to
   implement. Falco's highest-abstraction rule made structural; keystroke dictation unreachable.
2. **The red transcript** — exact command, exact output, which assertion failed, why that is right.
3. **The test-list delta** — consumed, added (a reason each), struck.
4. **The parked-notes ledger entry, or an explicit "nothing parked."** Each note: `file:line`, the
   observation, a disposition of `fix-now` / `next-test` / `defer`.
5. **A read receipt with content — name one thing the previous implementation does that the test did
   not require.** No generic answer exists, which is the point. "Looks good" makes it malformed. On
   a task's first turn there is no previous implementation and the receipt says exactly that — a
   condition checkable from the turn number, so it cannot become an escape hatch.

**Why review is compulsory rather than exhorted.** An agent asked to approve will approve; "LGTM"
costs one token. **The receiver must re-run the incoming test itself and confirm it fails on the
named assertion before it may implement.** Failure to reproduce — it passes, or errors on import,
syntax or collection — returns the handoff with the receiver's own transcript.

**The capability this buys.** `testing.md` records that the Butler does not reproduce red, because a
worktree or second clone on every task costs more than the check is worth. **The partner does it for
free, because it must run the test before implementing.** Every red is independently verified by a
second party that did not write it. That is the mode's main quality claim.

**Disagreement:** never silently implement around a test, never edit it. Two moves — make it pass and
park a `next-test` note proposing the corrective test, or **reject** with a stated reason, returning
the turn without consuming a list item. Mute Ping-Pong: disagreement is expressed as a test.

**Turn-back cap:** returns and rejections are both turn-backs; **two consecutive stop the run.**

**Single writer.** Only the turn-holder edits or touches the index. State it in P2, in the Executor's
staging section, **and in every turn prompt** — a partner running the Executor role has "stage after
every edit" as a standing instruction and will follow it. `herdr worktree` is named and rejected:
separate checkouts turn the pair into two solo sessions plus a merge.

**Termination:** the list is empty and Verification is satisfied. The last turn returns green plus
the Verification result, parts 2–5, and **no** next test. Backstop: **six exchanges per task.**

**P3 — drive a turn.** The Butler's mechanical duty:

1. **Never prompt an agent not just observed at `idle`, `done` or `blocked`.** `--wait` is not a
   mutex: a prompt to an already-working agent can be satisfied by the *previous* turn settling, and
   nothing in the return value shows it.
2. **`idle` and `done` are one condition.** CLI reads do not mark a tab seen, so a background-driven
   pane settles on `done`, never `idle`. Branch on the difference and you wait forever.
3. **`unknown` is never "turn over."**
4. **Prompt short, with resolved absolute paths** — the text is keystrokes into another process's
   TUI, so `${CLAUDE_PLUGIN_ROOT}`, `$PWD` and `~` arrive literal, and the partner may have no JDI
   installed. Payload goes in the file **in both directions**; the prompt ceiling is unmeasured.
5. **The report file is the turn-over signal; Herdr state is only the wake-up.** One rule for both
   kinds — this is how the Claude/OpenCode asymmetry is handled rather than assumed away.
6. **Structural check before relaying** — five headings present and non-empty. **Do not judge the
   substance**: re-running the red is the receiver's compulsory work, and a Butler that pre-judged
   would be doing the review on its behalf, destroying the property being bought.
7. **`agent_blocked` → stop and ask the user.** Never answer another agent's dialog: it exists
   because that agent's permission system decided a human should decide.
8. **`agent read` is for looking at a pane, not transporting a report** — a short read is not
   recoverable by raising `--lines`.
9. **Handle an unseen error code** — the schema types `ErrorBody.code` as a bare string.
10. **Escalation** on two turn-backs, six exchanges, or a blocked pane: stop, hand over both
    positions and transcripts. **The Butler does not break the tie** — it wrote neither side. Offer:
    accept the test, replace it with the proposed corrective test, strike the item, or stop.

Then: a `reference/pairing.md` row in README's table, and `AGENTS.md`'s paragraph gains it.
README's "two testing operations" row is **unchanged**.

### 4. Resolve the three `reference/testing.md` collisions

**File:** `reference/testing.md` only. Every edit additive and scoped to P2, so the single-agent path
reads exactly as today.

- **TS2 rule 7** ("A task is not complete at red") stays verbatim; a scoped paragraph follows: under
  P2 the completion unit is the **exchange**. A paired turn legitimately ends at a captured red
  because that red *is* the handoff. **Unchanged in substance** — nobody stops at red; what changes
  is *who* finishes it.
- **TS2 step 1** (one test per task) stays; add that under P2 the granularity is a **list** derived
  from the same two named sources, with the tracing rule. **The plan stays the authority; the list
  refines it.** That is what keeps "never fabricate a test" true at six tests.
- **TS2 steps 3–4** gain: under P2 this happens **twice, and the doubling is the anti-rubber-stamp
  mechanism.** And the closing "The Butler does not reproduce red" paragraph gains one sentence: **a
  pair does it for free.**

### 5. Add `commands/pair.md`, and its four enumerations

**Files:** `commands/pair.md` (new), `AGENTS.md`, `README.md`, `commands/help.md`, `roles/butler.md`.

Frontmatter with `description:` and `argument-hint: "[plan slug]"`, the Butler role line, then
*"Follow `/jdi:yolo` in full … with seven differences"*:

1. **A preflight** after yolo's pre-loop steps — P1. It runs *after* yolo's TDD step, because that
   step writes the line P1 rung 1 reads. Degraded → announce the rung and ask single-agent or stop.
2. **Step 2's hand-off is replaced** — drive the task as exchanges across two panes: P3 every turn
   while the agents perform P2. Same inputs yolo hands the Executor, **as resolved absolute paths**,
   plus the turn assignment, the report path, and the single-writer rule.
3. **Self-verification runs once per task, after the final green — not per turn.** Between turns the
   tree is *legitimately red*: a failing test exists by design and is the handoff.
4. **The failure checked is your own run after the last exchange**, in the positive voice yolo
   already uses. Three new stops: a blocked pane; six exchanges; two consecutive turn-backs. Yolo's
   existing stops are unchanged.
5. **Step 1's commit runs only when neither pane holds the turn.** Column 2 is trustworthy again
   precisely because the turn-holder staged and released.
6. **Teardown** per task and per run — surface the ledger, carry `defer` items forward, release the
   panes, say what was left behind.
7. **The closing summary says the run was paired**, naming both kinds and each one's lifecycle
   source, so a reader knows which state readings were a screen scrape.

Then the four enumerations in the same commit: `AGENTS.md`'s table, README's count **16 → 17**,
`help.md`'s table, and `roles/butler.md`'s row.

### 6. Give the Executor its paired turn, and document the `Pair:` line

**Files:** `agents/executor.md`, `agents/synthesizer.md`, `reference/plan-store.md`.

"What it receives" gains a sixth bullet: the paired-turn assignment — report path, which side, the
list and ledger, all absolute — and the instruction to perform P2. **Driver and navigator are turn
assignments, not roles: you are the Executor either way.** "What it returns" gains the five-part
handoff written to the report path, **with the path as the only reply.** The staging section's five
rules are unchanged; a closing paragraph scopes the whole discipline to the turn-holder, and says
why: rule 3's column 2 stops being a statement about *your* work, and `git add` may stage a file the
partner is mid-edit in.

The Synthesizer carries the `Pair:` line on the same terms as `TDD:`. `plan-store.md` documents the
single shape, the absence of an `off` shape and why, and that **no command reads it to decide
anything** — and states that the commit-points table is unchanged.

### 7. Document pairing in init, help, and the README

**Files:** `commands/init.md`, `commands/help.md`, `README.md`.

`init.md`'s frontmatter gains the question; a **new step 6** renumbers 6–12 to 7–13, after which
`grep -n 'step [0-9]'` fixes back-references. The step follows init's own precedent that *a question
that cannot be meaningfully answered is not asked*: **skip it entirely when `herdr` is not on
`PATH`**, saying once that `/jdi:pair` asks inline when needed. Where Herdr is present: explain there
is no on/off switch, propose kinds that clear all three layers, say the value is prose.
*(Interpretation, reversible in one edit: the criterion says init asks about it; asking every repo
about pairing when most machines have no multiplexer is noise, and step 4's skip is the precedent.)*

`help.md`: the closing config-state line gains the pair block, phrased as what it *names* rather than
on/off; and a `###` subsection. **Say the quality claim plainly**: every red is re-run by the agent
that did not write it, because it cannot implement until it has.

`README.md`: both enumerations of init's questions, and a `### Pair programming` section with one
honest sentence on cost — Arisholm et al. found the overall correctness gain **not significant** for
~84% more effort, so `/jdi:pair` is a deliberate choice for hard tasks, not a default. README's role
counts and testing-operations row are **unchanged**.

### 8. Release 1.0.4, and dogfood

Both versions to **1.0.4**; a `## 1.0.4` entry whose **first bullet says what happens to a repo that
does not set the key** — nothing, and `/jdi:yolo` never pairs. Commit `feat: Pair two agents through
a plan (1.0.4)`. Add a `pair:` block to this repo's own config naming two kinds that clear all three
layers here, noting it is a claim about one machine and a contributor lacking a kind gets rung 4's
announced degradation — the path that most needs exercising.

### 9. UAT

Two groups, and the split stated in the task file so nobody records group B as passed when it was
not run. **Group A** (no second pane): byte-identical unpaired run; rung 1 with no `TDD:` line; rung
2 outside Herdr; rung 3's ask-and-persist; rung 4 naming which layer failed; `/jdi:execute` and
`/jdi:next` ignoring a `Pair:` line; `/jdi:pr` carrying it. **Group B** (two live panes, and the
user): a full exchange; a handoff missing its read receipt; a receiver that cannot reproduce; a
rejection; two turn-backs stopping the run; a blocked pane. If group B is not run it is recorded
under **Remaining work as unverified**, never as passed.

## Testing Strategy

**The ceiling first: no test in this repository observes command or role body prose.** Every
behavioural claim here — P1's ladder, the five-part handoff, the compulsory re-run, the turn-back cap
— is a markdown instruction to an agent. The suite is a regression guard on **structure**, and the
grouping below is what makes structure enough to falsify each step at the boundary where a file and
the lists naming it must agree. Behavioural proof is UAT group B.

| Step | What proves it | The red |
|---|---|---|
| 1 | Its own two new tests | **Real and pre-existing**: `/jdi:help` absent from its own table, so the assertion fails naming `help`. The butler guard is green today; its red is induced by removing one name and restoring. **Report which was which** |
| 2 | Existing `test_config_schema.py` | Add the schema block alone → two failures naming `pair.agents` and the missing defaults row. **No new test, and that is not a skip** — the plan's named test exists and is bidirectional |
| 3 | Existing `ReferenceFileEnumerationTest` | Create the file alone → both subtests red, naming README and `AGENTS.md` |
| 4 | **Nothing can observe this step** | Diff read against the three quoted originals, plus UAT A1: a single-agent run must be byte-identical |
| 5 | `CommandTableTest`, `ReadmeCountTest`, and step 1's two guards | Create `pair.md` alone → four assertions red naming `pair`. Also the proof step 1's guards earn their place |
| 6 | **Nothing observes it**; frontmatter passes either way | Diff review, and UAT A6/A7 |
| 7 | **Nothing observes the prose**; only `grep -n 'step [0-9]'` after the renumber | PR review of the diffs, and UAT A4. Repeat the TDD plan's honesty rather than claiming more |
| 8 | Existing `test_versions.py` | Bump one file alone → two failures naming the other and the CHANGELOG |
| 9 | Itself | — |

**Steps 4, 6 and 7 will produce TS2's announced skip.** Three of nine tasks are pure prose. **It must
not be answered with a fabricated test**: asserting that `testing.md` contains the word "exchange"
would give a green suite and a red transcript that prove nothing while looking exactly like proof —
which TS2 names as the worst available outcome. The skip is the right answer, announced.

Suite grows 15 → 17 tests, stdlib only, `python3 -m unittest discover -s tests -v`.

## Risks

- **Half the intended pair reports state by terminal-title scrape.** Measured 2026-09-03: `opencode`
  classifies through `full_lifecycle_hook_authority`; `claude` through a manifest whose winning rule
  is `osc_title_working`. A redesigned prompt box yields `unknown`, which does not prove completion.
  **Mitigated structurally** by making the report file the turn-over signal, not the state. Residual:
  a genuinely stuck pane reads `unknown` and never writes a report, so P3 needs a generous per-turn
  timeout and must escalate rather than wait.
- **The `agent prompt` payload ceiling is unmeasured**, and plausibly belongs to the receiving
  agent's input widget, so it differs by kind. Mitigated by putting the payload in the file both
  ways. Closing it needs a runtime probe per kind.
- **The installed `claude` integration is v7 against the binary's v8.** Bodies diff identical apart
  from the version marker, and Claude's state comes from the manifest rather than that hook — so
  expected impact is low. **"Expected" is not "measured"**, and the installer side is untested
  because running it is mutating.
- **The single-writer rule is prose, not enforcement.** A partner running the Executor role has
  "stage after every edit" as a standing instruction and will follow it unless told otherwise. If it
  does, the commit silently contains both agents' work with no way to attribute it. Detection: the
  Butler's `git status --short` showing a file the turn-holder never named. Stated in three places
  for that reason.
- **The honest cost.** Arisholm et al. (IEEE TSE 2007, 295 professionals) found the overall
  correctness gain **not significant** for ~84% more effort, gains confined to complex tasks and
  less-expert pairs. Two panes each carry a full context per turn, so token cost roughly doubles on
  top. Document `/jdi:pair` as a deliberate choice for hard tasks, never a default — which is why it
  is a separate command and not a yolo flag.
- **Step 1's real red invites the wrong green.** Adding `/jdi:help` to its own table is the fix;
  exempting `help` is the shortcut that would neuter the guard exactly when `/jdi:pair` needs it.
- **`commands/pair.md` is a delta on `/jdi:yolo` and drifts when yolo changes** — the accepted cost
  of not making a fourth copy. Drift grep: `grep -rn 'P1\|P2\|P3\|/jdi:pair\|pair\.' commands/
  reference/ agents/ roles/ README.md AGENTS.md`.
- **`init.md`'s renumber re-stales `docs/config-key-lifecycle.md`'s citations**, already recorded as
  deferred. This plan does not chase them; the deferral should stay one dedicated pass rather than
  being half-done twice.
- **The scratch directory across sessions.** A resumed run can find a previous run's reports. P1
  rung 7 asks rather than reusing or clobbering silently.
- **This repo's dogfooded `pair.agents` is a claim about one machine.** A contributor lacking a kind
  gets rung 4's announced degradation — designed behaviour that will look like a defect to someone
  who has not read this plan.

## Tasks

- [x] 01 — Make the new command and config key falsifiable (depends on: none)
- [x] 02 — Add the `pair` config block (depends on: 01)
- [x] 03 — Write `reference/pairing.md`, and both reference-file enumerations (depends on: 02)
- [x] 04 — Resolve the three `reference/testing.md` collisions (depends on: 03)
- [x] 05 — Add `commands/pair.md`, and its four enumerations (depends on: 01, 02, 03, 04)
- [ ] 06 — Give the Executor its paired turn, and document the `Pair:` line (depends on: 05)
- [ ] 07 — Document pairing in init, help, and the README (depends on: 05)
- [ ] 08 — Release 1.0.4, and dogfood (depends on: 06, 07)
- [ ] 09 — UAT (depends on: 08)
