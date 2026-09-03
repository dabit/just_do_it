# Pairing operations

JDI's pair programming mode is three named operations. `commands/pair.md` and the agents it drives
call them **by name**; this file says what each one means and how to carry it out. The `P` prefix is
deliberate: these are not `reference/tracker.md`'s `T1`–`T8`, and they are not
`reference/testing.md`'s `TS1` and `TS2` — a command that names `T2` means the tracker, and one that
names `TS2` means the Executor's failing test.

**Nothing here is gated on a config key.** `pair.agents` in `.jdi/config.yml`
(`reference/config.md`) names *which* two agents to pair; it never says *whether* to pair. Running
`/jdi:pair` is the whole of the intent. A repository that sets the key and never runs the command
behaves exactly like one that does not, and no other command reads any of this.

Two things need saying here that no other reference file needs.

**This file names an external CLI, `herdr`, in its body, and that is deliberate.** Herdr is a
capability, checked at **P1** and degraded from out loud — the same treatment `reference/tracker.md`
gives a tracker whose MCP server is unreachable (its universal rule 2). An adapter porting JDI to
another harness must not strip the name: removing it does not make these operations
harness-neutral, it makes them unperformable, because there is then nothing to check and nothing to
degrade from. The Herdr facts they rest on — the `HERDR_ENV` precondition, the four hops, the
three-layer kind check, the five lifecycle states, the four failure modes — are measured and
recorded in `docs/herdr-coordination.md`, and cited by section below rather than restated here.
Where that document and the installed binary disagree, the binary wins and the document is stale.

**Both paired agents read this file, by absolute path.** That is a consumer type the other reference
files do not have: not a command, and not an in-process delegated role, but two agents in separate
processes reached by `reference/delegation.md`'s path 2 — one of which may be a different kind of
agent with **no JDI installed at all**. It is why the protocol lives here rather than in
`commands/pair.md`, which is written to the Butler in the second person and describes orchestration
the panes must never perform. **P2** is therefore self-contained: every path it needs is handed to
the pane already resolved and absolute, and nothing in it depends on `${CLAUDE_PLUGIN_ROOT}`, which
resolves only inside Claude Code (`AGENTS.md`).

| Operation | Who performs it | When |
|---|---|---|
| **P1** — prove the pair can run | the Butler | once per `/jdi:pair`, before the first exchange |
| **P2** — the exchange | the two paired agents | every turn, once P1 said `on` |
| **P3** — drive a turn | the Butler | every turn |

## The universal rules

1. **Pairing is requested, never detected.** Two live panes, a `herdr` on `PATH`, a `pair.agents`
   value, a `Pair:` line left in a `PLAN.md` by an earlier run — none of these starts a paired run.
   Only `/jdi:pair` does. This is the reason `reference/testing.md`'s universal rule 3 gives for
   never treating a missing `TDD:` line as an invitation to detect a runner: a mode the user did not
   ask for, entered because the environment happened to look ready for it, is a workflow doing
   something nobody typed.
2. **The turn is the write lock.** Exactly one agent holds the turn, and only the turn-holder edits
   a file or touches the index. `agents/executor.md`'s staging discipline is written for a single
   writer and every rule in it assumes one (`docs/herdr-coordination.md` §7): with two writers,
   column 2 of `git status --short` stops being a statement about *your* work, and `git add` may
   stage a file the partner is halfway through editing.
3. **Neither agent drives the other.** A paired agent never prompts its partner, never answers its
   partner's approval dialog, and never reads its partner's pane. All of that belongs to the Butler,
   at P3. An approval dialog exists because that agent's own permission system decided a human
   should decide (`docs/herdr-coordination.md` §5); an agent that clicks through one has silently
   removed a control the user chose to have.
4. **Capability is proven, not assumed.** A kind named in the config, a `herdr` binary on `PATH`, an
   integration that appears in a list of installable ones — none of these is evidence that this pair
   can start *here*, in this environment, in this session. This is `reference/testing.md`'s
   universal rule 1 pointed at a multiplexer instead of a test runner: the only proof is a pane that
   was watched coming up.
5. **The Butler is not half the pair.** It carries reports between two panes and checks their shape.
   It writes no code, proposes no test, and breaks no tie between the two agents. Its own
   verification stays what `roles/butler.md` already makes it — independent, run by the Butler
   itself, after the last exchange of a task. A Butler that joins in has removed the second party
   the whole mode exists to buy.

## P1 — Prove the pair can run

Resolved by the Butler once per `/jdi:pair` invocation, before the first exchange, and **re-run in
full every time**. Unlike `reference/testing.md`'s TS1 this cannot be settled once per plan: an
agent name is a handle on a live process, cleared the moment that process exits, and panes never
survive a session (`docs/herdr-coordination.md` §2). Inherited, these checks prove nothing. Only the
*record* is written once — rung 8's line.

**The degradation ladder.** Take the first rung that applies, say which one out loud, and stop
there. **Degradation is never automatic.** Degrading means not pairing, and the Butler announces the
rung and asks the user for one of two answers: run the plan single-agent — which is `/jdi:yolo`,
followed with zero differences — or stop here. It never quietly becomes a solo run, and it never
writes a `Pair:` line. **There is no half-pair.** One pane up and the other refused is a failure,
not a degraded mode: a single agent taking both sides of a ping-pong is precisely the rubber stamp
P2 exists to make impossible.

1. **The plan's `TDD:` line does not read `on`** → not paired. P2 is a test-first protocol end to
   end: with no proven runner there is no red to hand over and nothing for the partner to reproduce.
   **Do not run TS1 from here.** `reference/testing.md`'s universal rules 2 and 3 hold unchanged and
   pairing is not an exception to them — an absent line means off, silently, and is never an
   invitation to go looking for a test runner or to ask the user about one. Read the line *after*
   the pre-loop TDD step, because that step is what writes it.
2. **`HERDR_ENV` is not `1`** → not paired. It is the only reliable signal
   (`docs/herdr-coordination.md` §1). `herdr` on `PATH` says the tool is installed; a socket says a
   server is running somewhere; neither says *this process* sits in a pane Herdr manages. Without
   it the control commands would still run — against somebody else's focused session.
3. **`pair.agents` is empty or absent** → **ask; do not degrade.** The user asked to pair and the
   configuration is merely silent about with what, so the answer is a question, not a downgrade.
   This is the **only config write outside `/jdi:init`**, and it is fenced accordingly:
   - **Run rung 4's check first, and offer only kinds that clear it.** The ladder is inverted here
     on purpose: proposing a kind this environment cannot start is worse than proposing nothing. A
     kind named back to the user at this rung has already cleared rung 4, and rung 4 does not
     re-ask about it.
   - Say that the value is **prose** — a description JDI reads, never a list it parses and never a
     command it executes.
   - **Show the exact YAML, name the absolute path of the file it goes in, and get explicit
     confirmation** before writing anything.
   - **Fill the existing key in place when there is one; append the block only when there is not.**
     This rung fires on `pair.agents` being empty *or* absent, and those need different writes. A
     config already carrying the schema's own `pair:` / `agents: ""` gets its value filled in;
     appending a second `pair:` block there is not an error a YAML parser will report — it silently
     keeps the last — and an agent reading the file top-down would hit the empty one first,
     conclude nothing is configured, and re-ask on every run.
   - **Write nothing else.** Never reformat, reorder, or rewrite the rest of
     the file: it is the user's, and a config rewrite nobody asked for is a diff they must audit.
   - **If `.jdi/config.yml` does not exist, do not create it as a side effect of running a plan.**
     Offer a minimal file or a one-run answer that is not persisted, and let the user pick.
   - A user who wants a kind that did not clear rung 4 gets it recorded, **with the failure said out
     loud at the time**. It will fail rung 4 on the next run too, which is the honest outcome.
   - **Write before any pane starts**, so a run interrupted between panes leaves the answer behind
     instead of asking for it again.
4. **A configured kind fails the three-layer check, run now** → not paired. Three independent
   layers, in order, and clearing one says nothing about the next (`docs/herdr-coordination.md` §3):
   the kind is in the list `herdr agent` prints; **Herdr can classify its lifecycle state**; and it
   is resolvable by `command -v`.

   **Layer 2 asks whether the kind is classifiable, not whether an integration is current.** A kind
   clears it two ways: an
   integration hook with authority (`full_lifecycle_hook_authority`), or a detection manifest that
   classifies by scraping the terminal (`osc_title_working` and its siblings). Neither is better
   evidence *that the kind can run* — they differ in how much you should trust a state reading, and
   that is what rung 6 records. An **outdated** integration is a warning, not a refusal: name the
   kind and both versions so the user can update, and carry on. A kind with **no** integration and
   **no** manifest is a genuine layer-2 failure — nothing would report when its turn ended.

   **Answer layer 2 without a pane**, because rung 3 needs it before any pane exists: `herdr agent
   explain --file <any path> --agent <kind> --verbose` reports the manifest that would classify that
   kind, with no pane and no running agent. That is the form to use here. The pane-bound form,
   `herdr agent explain <pane> --verbose`, answers a different question — which source actually
   classified *this* pane — and belongs to rung 6, after rung 5 has started one.

   Say which layer failed, and **name the environment you measured in.** Layer 3 is the one most
   likely to differ between the machine a plan was written on and the machine it runs on, and a
   `command -v` in the Butler's shell is not proof about a pane started with a different
   environment, a container, or a remote host. Two things must not be run while checking: **bare
   `herdr` launches or attaches the TUI**, taking over the terminal the Butler is speaking
   through, and **a mutating nested command probed with no arguments executes**. Print the
   command group instead.
5. **The panes do not come up** → not paired. `herdr pane layout` reports the caller's rect, so the
   split direction comes from geometry rather than habit — repeated same-direction splits produce
   columns too narrow for a TUI to render. Then `herdr pane split --current --direction <dir> --cwd
   <absolute repository root> --no-focus`, and `herdr agent start <name> --kind <kind> --pane <the
   id read out of the split's JSON>`. **Always name a target, and always `--no-focus`**: a pane
   command with no target may resolve to whichever pane has UI focus, and that pane belongs to the
   user or to another agent — the user's attention is not a resource the coordinator owns. **Never
   persist an agent name**; it is cleared when its agent exits, is released, or is replaced, so it
   is a handle on a live process and not an identifier a plan may carry. `agent_not_ready` means the
   agent is up and waiting on something — a trust prompt, a login, an update notice. Read the pane
   and wait for ready. **Do not restart**: restarting throws away a live process that is merely
   blocked.
6. **Record which lifecycle source each pane's state comes from.** `herdr agent explain <pane>
   --verbose`, once per pane, and say whether the answer came from an integration hook with
   authority or from a **detection manifest pattern-matching the terminal title**. This rung informs
   and never degrades: it changes nothing about the protocol, because P3 rule 5 already refuses to
   treat state as the turn-over signal. But the two halves of the intended pair do not report state
   the same way (`docs/herdr-coordination.md` §3), and the user is entitled to know which of the
   readings in the run's summary were a screen scrape.
7. **Designate the shared report directory** — chosen now, resolved now, **absolute**, and **outside
   the working tree**. Outside because the Executor stages every file it writes
   (`agents/executor.md`), so a report written inside the tree lands in the task's commit as though
   it were part of the change. The path goes in the **first** prompt of the session, and every turn
   writes to it thereafter. **This is a deliberate departure from `herdr --skill`**, which advises
   asking for file output only as a *fallback*, after a read has come up short, and explicitly not
   in the first prompt. That advice is right for an ad hoc read of unknown size and wrong here: this
   payload is known to be large on **every** turn, and a truncated report still parses as a report,
   so the fallback would fire constantly and fail silently when it did not
   (`docs/herdr-coordination.md` §6). **Ask before reusing an earlier run's files**: a resumed run
   can find a previous run's reports, and neither silently reading them nor silently overwriting
   them is a decision the Butler gets to make on its own.
8. **Paired** → say so, and write the `Pair:` line into `PLAN.md`'s metadata block alongside
   `- Started:`, only if no such line is there already:

   ```
   - Pair: on — <kind A> + <kind B>, first paired YYYY-MM-DD
   ```

   **There is one shape, and there is no `off` shape.** That is the single way this line diverges
   from `TDD:` (`reference/plan-store.md`). TS1 writes an `off` line because the *configuration*
   asked for something the environment refused, and every later command has to be told not to
   re-detect it. Pairing is asked for by a **command**, so its degradation is announced to the user
   who typed it, in the same turn — the announcement *is* the record, and there is no later command
   to warn. An `off` line would be a persistent artefact some future command might be tempted to
   read, which is the failure universal rule 1 exists to prevent. The line written here is a record
   of what happened; **no command reads it to decide anything.**

**Degrade down to not pairing, never up to paired.** An unstartable kind, an absent multiplexer and
an unanswerable question all mean this run is not paired. Nothing turns pairing on that the user did
not: not a second pane that appears mid-plan, not an integration that becomes current, and not a
`Pair:` line an earlier run left behind.

## P2 — The exchange

Performed by the two paired agents, every turn, once P1 said paired. Both are running
`agents/executor.md`'s Executor role: **driver and navigator are turn assignments, not roles.** The
agent holding the turn is the Executor implementing; the other is the Executor that wrote the test
being implemented against, waiting to review what comes back. Neither is senior to the other, and
the assignment alternates every turn.

**A turn** is: reproduce the incoming red → make it pass → refactor → write the next failing test →
hand off. **An exchange** is one test's whole life, from written-failing to passing-and-reviewed.

**The completion unit is the exchange, not the turn.** A paired turn legitimately ends on a captured
red, because that red *is* the handoff — it is the test the partner will make pass. This does not
soften `reference/testing.md`'s TS2 rule 7 that a task is not complete at red: nobody stops at red
here either. What changes is *who* finishes it. A task is complete when the test list is empty and
the plan's Verification passes, and the last turn of a task carries green.

**The test list is derived, never invented.** One item per Verification clause in the task file and
one per `## Testing Strategy` item in the plan. **The plan stays the authority; the list only
refines it.** An item may be added mid-task only with a **stated reason naming the clause it refines
or the bug it came from**; an item that traces to neither is not written as a test at all — it
becomes a `next-test` parked note, which the Butler surfaces to the user as a plan gap. That rule is
what keeps `reference/testing.md`'s "never fabricate a test" true at six tests as well as at one:
without it, a pair with a list can generate work indefinitely while every item looks like progress.

**The opener seeds the list and alternates per task**, so that neither agent is permanently the test
author and permanently the implementer.

### The five-part handoff

Every handoff is written to the designated report path and carries all five parts. **A handoff
missing any part is returned unread**, and the return counts against the turn-back cap below.

1. **A failing test — the sender's entire design authority.** No prose telling the receiver how to
   implement it: no suggested signature, no file to put it in, no algorithm. The test states what
   must become true and the receiver decides everything else. This is Falco's highest-abstraction
   rule made structural rather than exhorted — keystroke dictation is not merely discouraged, it is
   unreachable, because the channel does not carry it.
2. **The red transcript** — the exact command, its exact output, which assertion failed, and one
   sentence on why that failure is the right one. Same standard as `reference/testing.md`'s TS2
   steps 3 and 4: a syntax, import, or collection error is a broken test, not a red run.
3. **The test-list delta** — what was consumed, what was added and the stated reason for each, what
   was struck and why.
4. **The parked-notes ledger entry, or an explicit "nothing parked."** Each note carries a
   `file:line`, the observation, and a disposition of `fix-now`, `next-test`, or `defer`. The ledger
   is how the reviewing agent's observations survive a turn without becoming a mid-turn instruction:
   the goal boundary stays where the current test put it, and nothing is lost for having waited.
5. **A read receipt with content — name one thing the previous implementation does that the test did
   not require.** Not "looks good", not "reviewed": a receipt with no concrete answer makes the
   handoff malformed, and it is returned. The question is chosen precisely because **no generic
   answer to it exists.** It can only be answered by an agent that actually read the code, so unlike
   an approval it cannot be rubber-stamped. On a task's **first** turn there is no previous
   implementation, and the receipt says exactly that — an exception checkable from the turn number
   the prompt carries, which is what stops it from becoming an escape hatch on turn five.

### Why the review is compulsory rather than exhorted

**An agent asked to review and approve will approve.** "LGTM" costs one token, satisfies the
instruction as written, and is indistinguishable in a transcript from a review that actually
happened. **Exhortation does not fix this**: no amount of "review carefully" changes what the
cheapest compliant answer is. So the protocol does not ask for a review. It makes one structurally
unavoidable:

**The receiver MUST re-run the incoming test itself, and confirm it fails on the named assertion,
before it may implement.** If it cannot reproduce that red — the test passes, or it errors on
import, syntax, or collection — it does not implement. It returns the handoff, carrying its **own**
transcript of what happened instead.

**What this buys.** `reference/testing.md` records that the Butler does not reproduce red, because
a throwaway worktree or a second clone on every task of every plan costs more than the check is
worth. **The partner does it for free, because it must run the test before it can implement.** So
under P2 every red is independently verified by a second party that neither wrote the test nor chose
the assertion. That is this mode's main quality claim, and it is why the re-run is a precondition
rather than a request.

### Disagreement

A test the receiver believes is wrong is still never edited and never implemented around. Silently
satisfying a bad test in a way that makes it pass and does nothing else destroys the only channel
the pair has. There are exactly two moves:

- **Make it pass, and park a `next-test` note** proposing the corrective test. The list advances and
  the disagreement is recorded as work rather than as an opinion.
- **Reject it**, with a stated reason, returning the turn **without consuming a list item**.

Wherever it can be, disagreement is expressed as a test — the Mute Ping-Pong constraint — because a
proposed test is checkable and an opinion about a test is not.

**The turn-back cap: two consecutive turn-backs stop the run.** A return for a malformed handoff, a
return for a red that would not reproduce, and a rejection are all turn-backs. Two in a row means
the pair is not converging, and a third pass over the same argument is a loop rather than progress.
Stop, and hand both positions to the Butler for P3 rule 10.

**Single writer.** Only the turn-holder edits a file or touches the index. The other agent reads,
reviews, and advises, and runs no `git add`, `git rm`, `git mv`, `git commit`, or `git stash`. This
is universal rule 2, and it is stated here, in `agents/executor.md`'s staging section, and in every
turn prompt — three times on purpose, because an agent running the Executor role already has "stage
after every edit" as a standing instruction and will follow it unless told otherwise
(`docs/herdr-coordination.md` §7). **`herdr worktree` is named and rejected**: separate checkouts
give each agent its own branch and turn the pair into two solo sessions plus a merge, which is the
opposite of the second pair of eyes the mode is for.

**Termination.** A task's exchanges end when the test list is empty *and* the plan's Verification is
satisfied. The last handoff of a task carries the green run and the Verification result, parts 2
through 5, and **no next test** — that absence is the signal the task is finished. Backstop: **six
exchanges per task**, after which the run stops and escalates rather than carrying on.

## P3 — Drive a turn

The Butler's mechanical duty, every turn. It moves reports between two panes and checks that they
have the right shape. It does not write code, judge the work, or take a side.

1. **Never prompt an agent not just observed in a settled state.** Read the state immediately
   before prompting. `--wait` is not a mutex: a prompt delivered to an agent that was already
   working can have its wait satisfied by the *previous* turn settling, and **nothing in the return
   value shows which turn completed** (`docs/herdr-coordination.md` §5). The Butler serialises
   turn-taking on its own side; Herdr does not do it for you. `idle` and `done` mean prompt;
   `blocked` means rule 7 and never a prompt — `agent prompt` refuses a blocked agent anyway,
   *before* writing anything, and that ordering is what keeps a turn's text out of somebody's yes/no
   dialog.
2. **`idle` and `done` are one condition, and nothing branches on the difference.** They are the
   same underlying state, separated only by whether a human has looked at the tab — and **CLI reads
   do not mark a tab seen** (`docs/herdr-coordination.md` §4). A pane driven entirely from a
   background loop is therefore never seen, so its finished turns settle on `done` and never reach
   `idle`. Wait for `idle` alone and you wait forever on work you are driving yourself.
3. **`unknown` is never "turn over."** It means an agent is present that Herdr could not classify
   confidently: not that it finished, not that it failed. Read as completion, it produces a
   half-written report relayed as a handoff.
4. **Prompt short, with every path resolved and absolute.** The text arrives as keystrokes into
   another process's TUI, so `${CLAUDE_PLUGIN_ROOT}`, `$PWD`, and `~` are delivered as literal
   characters, and the receiving agent may be a different kind of agent with no JDI installed at all
   (`docs/herdr-coordination.md` §6). Resolve every path in the Butler, where those things mean
   something: the report path, the plan, the task file, this file. The prompt also carries the turn
   assignment, the single-writer rule, and the **turn number** — which is what makes part 5's
   first-turn exception checkable rather than merely asserted. **The payload goes in the file in
   both directions**, not only the reply direction: the `agent prompt` size ceiling is unmeasured
   and plausibly belongs to the receiving agent's input widget, so it differs by kind.
5. **The report file is the turn-over signal; Herdr state is only the wake-up.** A settled state
   says the pane is ready to be looked at. A complete report at the designated path says the turn
   is over. **One rule for both kinds** — which is how the asymmetry between a pane whose state
   comes from a hook with authority and one whose state is a terminal-title scrape gets *handled*
   rather than assumed away. It also removes the silent-truncation failure: rows that have left an
   alternate screen never enter host scrollback, so a short `agent read` cannot be recovered by
   raising `--lines` (`docs/herdr-coordination.md` §5).
6. **Check the handoff's structure before relaying it — structure only.** Five parts present and
   non-empty; that is the entire check. **Do not judge the substance.** Re-running the red is the
   receiver's compulsory work, and a Butler that pre-judged the test would be performing the
   receiver's review on its behalf, destroying the exact property the mode is bought for. A
   malformed handoff goes back to its sender: never repaired, never relayed.
7. **`agent_blocked` → stop and ask the user.** Inspect the pane with `agent get` and `agent read`,
   say what it is asking, and hand the question over. **Never answer another agent's dialog**: it
   exists because that agent's permission system decided a human should decide, and it is not a
   decision the Butler has the context to make — it is being asked about an action it did not
   propose.
8. **`agent read` is for looking at a pane, not for transporting a report.** Use it to see what a
   pane is doing right now and to inspect a blocked dialog. A short read is not a flag problem to be
   solved by raising `--lines`; the rows are gone (rule 5).
9. **Handle an error code you have never seen.** Herdr's schema types the error code as a bare
   string with no enumeration (`docs/herdr-coordination.md` §5), so matching the known codes is
   necessary and not sufficient. An unrecognised code stops the run and is reported verbatim; it is
   never treated as a transient failure to retry through.
10. **Escalate on two consecutive turn-backs, six exchanges in one task, or a blocked pane.** Stop,
    and hand the user both positions and both transcripts. **The Butler does not break the tie** —
    it wrote neither side and has run neither test. Offer the four real answers: accept the test as
    written, replace it with the corrective test the rejection proposed, strike the list item, or
    stop the run. Then do what the user says.
