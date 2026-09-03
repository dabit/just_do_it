---
description: "Pair two agents through the plan: one writes a failing test, the other makes it pass."
argument-hint: "[plan slug]"
---

# JDI: Pair

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). **Delegates to: Executor** (deep), ×2 in
Herdr panes.

Run every remaining task in the plan as a pair: two agents in two Herdr panes ping-ponging a failing
test at each other, with this session driving the turns and taking neither side. Pairing roughly
doubles what a run costs, so it is a deliberate choice for a hard task and never a default — which
is why it is a command of its own rather than a flag on `/jdi:yolo`.

Which plan, and anything you want the pair to concentrate on: $ARGUMENTS

Follow `/jdi:yolo` in full — including step 0's config load and the plan lookup, which uses the
argument above — with seven differences:

1. **One more pre-loop step: the preflight.** After `/jdi:yolo`'s durable-memory gate and its TDD
   step, and before the first task, perform **P1** from JDI's `reference/pairing.md`. **The order
   matters and is not incidental**: P1's rung 1 reads the plan's `TDD:` line, and on a plan that has
   never been executed the TDD step above is what writes that line. Run P1 first and rung 1 reads a
   line that does not exist yet, degrading a run that was about to qualify.

   **If P1 degrades at any rung, say which rung, and ask.** There are two answers: continue this run
   single-agent — which is `/jdi:yolo`, followed with **zero** differences, the pre-loop steps above
   having already run — or stop here. **Degradation is never automatic**, and no `Pair:` line is
   written either way: a degraded run is an unpaired run, and the announcement you just made is the
   whole of its record.

2. **Step 2's item 3 is replaced.** Do not hand the task to a single Executor. Drive it as
   **exchanges** across the two panes instead: you perform **P3** every turn, while the two agents
   perform **P2**. Every turn prompt carries the same inputs `/jdi:yolo` hands the Executor — the
   task file, `PLAN.md`, the referenced architecture docs, and the TDD decision together with the
   proven invocation the `TDD:` line names — **as resolved absolute paths**, because the prompt
   arrives as keystrokes in another process and the agent receiving it may have no JDI installed at
   all. P1 has already established that the line reads `on`, so there is no case here where the TDD
   decision is passed as nothing. Add to those inputs: the absolute path of `reference/pairing.md`,
   the turn assignment and the turn number, the absolute report path P1 rung 7 designated, and the
   single-writer rule.

3. **Step 2's item 4 runs once per task, after the final green — not once per turn.** A task's last
   handoff carries the green run and no next test; that is when you verify. **Between turns the tree
   is legitimately red**: a failing test sits there by design, because that test *is* the handoff.
   Verifying mid-task would stop the loop on a red the protocol put there on purpose. Do not
   reproduce any of those reds either — under P2 each one has already been re-run by the agent that
   did not write it, which is a stronger check than a single-agent run gets.

4. **Step 2's item 5 checks your own run after the last exchange.** The task passed when the
   verification you ran yourself in difference 3, against the tree as it stands after the final
   handoff, is green — whatever reds the handoffs along the way contain. Those reds are records of
   past states, captured before the implementation existed, and a record is not a verification
   result.

   **Three new stops, additive to `/jdi:yolo`'s.** Its existing stops — a failing verification step,
   and its one TDD stop for a report carrying neither red evidence nor a stated reason there was
   nothing to test — are unchanged. Stop the loop as well on:
   - **a blocked pane** (P3 rule 7);
   - **six exchanges on one task** — P2's backstop;
   - **two consecutive turn-backs** — a returned handoff or a rejection, twice in a row.

   Each of the three is a P3 rule 10 escalation.

5. **Step 1's commit runs only when neither pane holds the turn** — in the window between receiving
   a task's final handoff and prompting the first turn of the next one. Its item 3 reads column 2 of
   `git status --short` for unstaged work, and that reading is a statement about a single writer. It
   is trustworthy again here precisely because the turn-holder staged its own edits and then
   released the turn. Commit while a pane still holds it and you may stage a file that agent is
   halfway through editing.

6. **Tear down, per task and per run.** After each task's final handoff, **surface the parked-notes
   ledger** to the user: every note still open, with its `file:line`, its observation, and its
   disposition. `fix-now` notes were dealt with inside the task; **`defer` notes are carried forward
   into the next task's first prompt, never deleted along with the scratch directory**; and any plan
   gap P2 flagged is surfaced alongside them. At the end of the run, **release both panes and say
   what was left behind** — the absolute report directory and whether it still holds this run's
   reports, plus any `defer` note no later task picked up.

7. **The closing summary says the run was paired.** `/jdi:yolo`'s `## When every task is complete`
   additionally names both agent kinds and, for each, the lifecycle source P1 rung 6 recorded: an
   integration hook with authority, or a detection manifest matching on the terminal title. A reader
   weighing how much to trust the run's account of who was working when is entitled to know which of
   those state readings were a terminal-title scrape.

Everything else is `/jdi:yolo`'s and unchanged — the loop itself, the dependency check, the per-task
commit format, the tracker write, and the UAT caveat in the closing summary. Where this file and
`reference/pairing.md` appear to differ about P1, P2, or P3, that file is the authority: these seven
differences say *where* the operations sit in the loop, never what they contain.
