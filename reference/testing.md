# Testing operations

JDI's test-driven mode is two named operations. Commands and roles call them **by name**; this file
says what each one means and how to carry it out. The `TS` prefix is deliberate: these are not
`reference/tracker.md`'s `T1`–`T8`, and a command that names `T2` means the tracker.

Both are gated on `tdd.enabled` in `.jdi/config.yml` (`reference/config.md`). With the key unset —
which is every repository that has not opted in — neither operation does anything, and neither says
anything.

| Operation | Who performs it | When |
|---|---|---|
| **TS1** — prove the test suite runs | the Butler | once per plan, before the first task |
| **TS2** — write the failing test first | the Executor | once per task, only when TS1 said `on` |

## The universal rules

1. **Capability is proven, not assumed.** A `spec/` folder, a `tests/` directory, a Makefile
   target, a manifest dependency on a test framework — none of these is evidence that the suite
   runs *here*, in this environment, in this session. This is `reference/tracker.md`'s universal
   rule 5 ("'No error' is not proof; read the value back where the tracker offers a read") applied
   to a test runner: the only proof is a runner that was watched running.
2. **The `TDD:` line is written once and never rewritten.** TS1 resolves at the start of a plan and
   the answer holds for every task in it. Every later command **reads** the line; none re-runs TS1,
   and none edits it. Editing `.jdi/config.yml` mid-plan therefore changes nothing until the next
   plan. The reason is uniformity — re-deciding at task 4 would hold half a plan's tasks to a
   different standard from the other half, and the plan's own record of how it was built would stop
   being true of the commits it produced.
3. **No line means no TDD, for every command, always.** A plan written before the `tdd` key existed
   carries no `TDD:` line; so does a plan whose TS1 stopped at rung 1. The two are
   indistinguishable, by design, and neither is an invitation to detect anything. **No command may
   treat a missing `TDD:` line as a reason to run TS1, to go looking for a test runner, or to ask
   the user about one.** Absent means off, and off means silent.
4. **An unparseable line is an absent line.** A `TDD:` line in neither of TS1's two shapes —
   truncated, hand-edited, in some other format — is treated exactly as rule 3 treats no line at
   all: off, silently. Do not guess at what it meant, and do not repair it.

## TS1 — Prove the test suite runs

Resolved once per plan, before the first task is executed, by the Butler. Its output is one line in
`PLAN.md`'s metadata block, alongside `- Started:`, in exactly one of two shapes:

```
- TDD: on — proven 2026-09-02 with `python3 -m unittest discover -s tests -v`
- TDD: off — <the rung that applied, and the evidence for it>
```

**The degradation ladder.** Take the first rung that applies and stop there.

1. **`tdd.enabled` is not `true`** → off. **Say nothing.** Write no `TDD:` line. Stop. This is not a
   skip to be announced: nothing was skipped, because nothing was asked for. A repository that
   never enabled TDD produces output, and a `PLAN.md`, byte-identical to what it produced before
   the key existed. `commands/split.md:96-97` states the same rule for `split.pieces: commits` —
   "Say nothing; there is nothing to skip."
2. **Derive the invocation.** Read `tdd.test_instructions` as prose and translate it into a command
   for this environment; it is a description, not a string to execute, and its literal text is
   usually not runnable as typed. When it is empty, work the invocation out from the repository
   itself — its manifest, its CI configuration, its `CLAUDE.md` / `AGENTS.md`, the runner its test
   files import. **Say which invocation you derived and where you got it**, so the user can correct
   it before it is trusted for the rest of the plan.
3. **Run it, scoped as narrowly as the runner allows** — one file, one directory. This is a proof
   of capability, not a test run: seconds, not a full suite.
4. **Read the output, not the exit code.**

   **Proof** is a printed test-result tally: the runner reached the point of counting tests and said
   so. A run reporting **zero tests**, in a repository that has none yet, is still proof that the
   runner runs.

   **The exit code is not the signal.** `python3 -m unittest` exits `5` on "Ran 0 tests" (verified
   on 3.14.7), and a suite with a genuine pre-existing failure exits non-zero while proving the
   runner works perfectly. Report a pre-existing failure out loud — it does not turn TDD off, but
   the Executor must know, or it will read someone else's red as its own.

   **Not proof:** command not found, a missing interpreter, a dependency-resolution error, a config
   parse error, an unreachable container, a timeout, an interactive prompt. **Nor is an import or
   collection error**, even though most runners print a tally alongside one — `python3 -m unittest`
   answers a bad module path with `ModuleNotFoundError`, `Ran 1 test`, and `FAILED (errors=1)`, and
   that tally counts the failure to load, not a test. A runner that could not import the tests has
   not been shown to run them. This is the same exclusion **TS2** step 4 applies to a red run, for
   the same reason and at the other end of the operation. In every one of those cases, nothing ran —
   and an exit code of `0` from a wrapper that swallowed the failure would not change that. This
   is universal rule 1, and it is `reference/tracker.md:18-19`'s "no error is not proof" pointed
   at a runner instead of a tracker write.
5. **Proven** → write the `on` line into `PLAN.md`'s metadata, naming the date and the invocation
   the narrow run proved — **unscoped**. Rung 3 narrows the probe to make it cheap; rung 5 records
   the command the rest of the plan will actually use, which is that same invocation with the
   scoping removed. Recording the narrowed form instead is a quiet trap: every later TS2 would run
   the same slice, and a red raised by a test outside it would never appear. That command is what
   the Butler hands every Executor for the rest of the plan; nothing re-derives it later.
6. **Disproven** → off, and **announced**, with the command that was tried and the output showing
   why it is not proof. Write the `off` line naming both. This one *is* a degradation rather than a
   silence: the user asked for TDD and did not get it (`roles/butler.md:23-25` — "Silent
   degradation is the thing that makes a workflow untrustworthy"). Rung 1 is silent because nothing
   was asked for; rung 6 is loud because something was.
7. **Ambiguous** → **ask the user once.** Several plausible invocations, prose naming a container
   you cannot see, an environment that might work with a flag you would be guessing at: offer the
   three real answers — give the invocation, run this plan without TDD, or stop here. **The Butler
   asks; the Executor never does.** A delegated role may have no user in front of it, so a question
   raised from inside an Executor either hangs the workflow or gets answered by the orchestrator on
   the user's behalf. With no user to ask, degrade to off and say so — which is rung 6.

**Degrade down to off, never up to on.** An unproven runner, an unreachable environment, and an
unanswerable question all mean `off` for this plan. Nothing turns TDD *on* that the configuration
did not: a `tests/` folder that appears mid-plan does not, and neither does a suite created by the
plan's own first task. Running "on" against a runner nobody watched run produces fabricated red-run
evidence, which is a worse outcome than not running TDD at all — it is the exact failure the
operation exists to prevent.

## TS2 — Write the failing test first

Performed by the Executor, once per task, and **only** when the plan's `TDD:` line says `on`. The
Executor is handed that decision and the proven invocation already resolved; it does not read
`.jdi/config.yml`, and it does not repeat TS1.

1. **Judge whether the task has testable behaviour.** The plan's `## Testing Strategy` and the
   task's own Verification are the source — under TDD, the test to write first is the one the plan
   already named. Where the plan names none and the task's Files are documentation, prose, or
   configuration, **announce the skip** ("task NN has no testable behaviour: `<why>`; no test was
   written first") and implement normally. Where the plan names none but the task *does* touch
   executable code, say that too: it is a gap in the plan, and the Butler needs to hear it.

   **Never fabricate a test.** A test invented to satisfy the mode — that a constant equals itself,
   that a file exists, that a function returns without raising — is the worst available outcome
   here. It is worse than an announced skip, because it produces a green suite, a red-run
   transcript, and a record that proves nothing while looking precisely like proof.

   Under **P2** (`reference/pairing.md`) the granularity is a **list** rather than a single test,
   derived from exactly those same two named sources: one item per Verification clause in the task
   file, and one per `## Testing Strategy` item the plan attributes to the task. An item may be
   added mid-task only with a stated reason naming the clause it refines or the bug it came from; an
   item tracing to neither is not written as a test at all — it becomes a `next-test` parked note,
   which the Butler surfaces to the user as a plan gap. **The plan stays the authority; the list
   only refines it.** That is what keeps "never fabricate a test" true at six tests as well as at
   one.
2. **Write the test, and only the test.** No implementation, not even a stub beyond what the test
   needs in order to import.
3. **Run it and capture the red** — the exact command, which is the one TS1 proved, and its exact
   output.
4. **Confirm it failed for the right reason.** The failure must be the new expectation: an
   assertion that ran and did not hold. **A syntax error, an import error, or a collection error is
   a broken test, not a red run** — it proves the file does not load, not that the behaviour is
   missing. Fix the test and re-run until the failure is the assertion, and capture *that* failure.

   Under **P2** (`reference/pairing.md`) steps 3 and 4 happen **twice, and the doubling is the
   anti-rubber-stamp mechanism.** The agent that wrote the test captures the red and confirms its
   reason; the receiving agent then re-runs the same command **before it may implement**, confirms
   the same assertion fails for the same reason, and captures its own transcript. A receiver that
   cannot reproduce the red does not implement — it returns the handoff, carrying its own
   transcript of what happened instead. The exclusion above travels with it: a syntax, import, or
   collection error is a broken test at the receiving end too, and never a reproduced red.
5. **Write the implementation.**
6. **Re-run the same command and capture the green.** The same invocation, so that the two
   transcripts are comparable; a green from a different command proves nothing about the red.
7. **Return both. A task is not complete at red.** Red is the halfway point of TS2 and never its
   end; an Executor that returns a red run as its result has stopped in the middle of the operation.

   Under **P2** (`reference/pairing.md`) the unit of completion is the **exchange**, not the turn. A
   paired turn legitimately ends on a captured red, because that red *is* the handoff — it is the
   test the partner will make pass. **The rule above is unchanged in substance:** nobody stops at
   red here either, and no task is complete at red. What changes is *who* finishes it. A turn that
   returns a red without the other four parts of P2's five-part handoff has delivered nothing, and
   is returned rather than accepted.

**The Butler does not reproduce red.** It cannot do so cheaply: `agents/executor.md:109-117` forbids
`git stash` outright, and reconstructing the pre-change tree by any of the routes that rule leaves
open — a throwaway worktree, a second clone, a diff against the base ref — costs more, on every
task of every plan, than the check is worth. So the Butler verifies what it can see directly: that
the tests are in the diff, and that they are green now. For the ordering it reads the Executor's
captured red evidence. That transcript is the only thing that makes "the test was written first"
falsifiable; without it, TDD collapses into "the test was in the same commit", which is true of
every task whether or not anyone wrote a test first.
Under **P2** (`reference/pairing.md`) the Butler still does not reproduce red — but **a pair does it
for free**, because the receiving agent must run the test before it may implement, so every red in a
paired run is independently verified by a second party that did not write it.
