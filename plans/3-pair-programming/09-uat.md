status: done
# 09 — UAT

Depends on: 08

## Why
Nothing in this repository's test suite observes command or role body prose — it is a regression
guard on structure, not on behaviour. Every claim this plan makes about what `/jdi:pair` actually
does when it runs — the ladder, the five-part handoff, the compulsory re-run, the turn-back cap —
is a markdown instruction to an agent, and the only thing that proves an instruction is followed is
following it. This task is that proof, run by a human, against the issue's own acceptance
criteria.

## Description
Two groups. State which group ran, and never record group B as passed if it was not actually run
with two live panes.

**Group A — runnable with no second pane.** A4 and A5 each need `pair.agents` in a specific state
(empty for A4, naming a failing kind for A5) that task 08's dogfooded block will not generally be
in by the time UAT runs. Run both against a scratch repo with its own `.jdi/config.yml`, or, if
run against this repository, temporarily move task 08's `pair:` block out of `.jdi/config.yml`
before A4 and A5 and restore it exactly afterward — do not let either scenario's write clobber the
dogfood entry.

| # | Scenario | Expected outcome |
|---|---|---|
| A1 | Run a plan through `/jdi:execute`/`/jdi:next`/`/jdi:yolo` with no `pair` block set, exactly as before this plan shipped | Byte-identical to a pre-plan run: no mention of pairing, no `Pair:` line, nothing asked |
| A2 | Run `/jdi:pair` on a plan whose `PLAN.md` carries no `TDD: on` line | P1 rung 1 fires: announced, degrades — offers single-agent `/jdi:yolo` or stop; no pane is started; no `Pair:` line written |
| A3 | Run `/jdi:pair` outside a Herdr-managed pane (`HERDR_ENV` unset) | P1 rung 2 fires: announced, degrades the same way as A2 |
| A4 | Run `/jdi:pair` inside Herdr, `TDD: on`, and no `pair.agents` configured | P1 rung 3 fires: asks inline, shows the exact YAML and path, writes only the `pair:` block on confirmation — proves criterion 1's shape (prose value, no `enabled` key) and criterion 7 together |
| A5 | Run `/jdi:pair` with `pair.agents` naming a kind that fails the three-layer check | P1 rung 4 fires: names which of the three layers failed, in the environment it was measured in; degrades the same way as A2 |
| A6 | With a `Pair:` line already in `PLAN.md`, run `/jdi:execute` and `/jdi:next` | Both ignore the line entirely — no different behaviour, no mention of pairing |
| A7 | With a `Pair:` line in `PLAN.md`, run `/jdi:pr` | The Synthesizer carries the `- Pair:` line into the condensed `PLAN.md`, unchanged |

**Group B — requires two live Herdr panes, and a human.**

| # | Scenario | Expected outcome |
|---|---|---|
| B1 | A full paired run of at least one task, both panes live | `/jdi:pair` starts both panes, P3 drives turns, P2's five-part handoff completes an exchange, the run alternates test-author per task, the shared report file carries the notes — not terminal scrollback |
| B2 | A handoff sent with one of the five parts missing (no read receipt) | P3's structural check catches it and returns it, without judging substance |
| B3 | A receiver that cannot reproduce the incoming red (it passes, or errors) | The handoff is returned with the receiver's own transcript; the sender's turn is not consumed |
| B4 | A navigator/driver rejection, with a stated reason | The turn returns without consuming a test-list item; disagreement is expressed as a test or a stated reason, never a silent edit |
| B5 | Two consecutive turn-backs in one task | The run stops; both positions and transcripts are handed to the user; the Butler does not break the tie |
| B6 | One pane hits `agent_blocked` | The run stops and surfaces it; neither agent answers the other's dialog |

**If group B is not run, record it under Remaining work as unverified — never as passed.** This is
the same shape the TDD-configuration plan used for the acceptance criteria its own UAT could not
exercise non-interactively.

### Mapping the issue's acceptance criteria (issue #3)

| Criterion | Scenario(s) | Note |
|---|---|---|
| A `pair` block in `.jdi/config.yml`, documented, no `enabled` key | A4 (partial); `ForbiddenKeyTest` | **Group A observed the block's existence and shape by reading, not by writing it** — A4 stops at the ask. The no-`enabled`-key invariant was unguarded until UAT found it; `tests/test_config_schema.py`'s `ForbiddenKeyTest` now enforces it |
| Every existing repo behaves exactly as it does now | A1, A6 | Established for **execution**: A1, A6, and the fact that `commands/{yolo,execute,next,done}.md` are unchanged on this branch. **Not** established for `/jdi:init`, which now asks a new question of anyone with `herdr` on `PATH` who never runs `/jdi:pair` — a deliberate interpretation recorded in `PLAN.md`, not blanket coverage |
| A new `/jdi:pair` command that runs a plan end to end with two agents | B1 | Requires group B |
| Driver/navigator roles with ping-pong rotation at the red/green boundary, **derived from human pair-programming practice** | B1, B4 for the rotation mechanic | **The "derived from" provenance claim is not a runtime behaviour and no scenario observes it.** It is proven by reading `reference/pairing.md`'s cited sources and `PLAN.md`'s References section (Böckeler & Siessegger, Open Practice Library's ping-pong loop, Falco's strong-style pairing, Fintak's trunk-based ping-pong, the coderetreat catalogue, Tuple, Xebia) against the P2 rules that cite them — a documentation review, not a scenario |
| The pair shares notes and corrections through a file that survives the run | B1 | Requires group B |
| The navigator produces a concrete artifact each turn, falsifiable | B1, B2, B3 | Requires group B |
| Running `/jdi:pair` with no `pair` configuration asks inline and persists it | A4 (the ask only) | **The persistence half is NOT OBSERVED and cannot be by an agent** — rung 3 requires explicit user confirmation before writing, and fabricating one is the failure this feature exists to prevent. A4 reached the ask and composed the exact YAML; the write awaits a human |
| Outside Herdr, without `TDD: on`, or with an agent unreachable, degrades out loud | A2, A3, A5 | Established, with one qualifier: **A3 was simulated** with `env -u HERDR_ENV` inside a real Herdr pane. A genuinely non-Herdr session was not observed |
| A blocked agent stops the run and surfaces it; neither answers the other's prompts | B6 | Requires group B |
| `/jdi:init` asks about it, and the README documents it | — | **Not observed by any scenario here**, matching the TDD-configuration plan's precedent for its own criteria 5 and 6: `/jdi:init` is interactive, and scripting an answer to a question and then judging its own wording proves nothing. Substitute: task 07's verification — `commands/init.md`'s new step exists with the herdr-on-`PATH` skip intact, and `README.md`'s two enumerations plus its new section exist. **Remains genuinely unverified** (does the question get asked, in the right words, with the right default) until a live `/jdi:init` run against a repo with no existing `.jdi/config.yml`, or a dedicated scratch-repo check |

Two mechanisms exercised by group B that map to **no** acceptance-criterion clause, recorded here so
they are not mistaken for AC coverage: B5 (the turn-back cap) proves P2's own stop condition, not a
clause of issue #3; B2/B3 prove the falsifiability *mechanism* behind the navigator-artifact
criterion above, listed there rather than twice.

## Outcome — group A run 2026-09-03, group B not run

**Group A: 6 observed pass, 1 partial.** A1 (the regression guard), A2, A3, A5, A6 and A7 passed.
A4 reached rung 3's ask and composed the exact YAML; its *write* is unobserved, because the rung
requires explicit user confirmation and an agent inventing one is the failure this mode exists to
prevent.

**Group B: NOT RUN. Recorded as unverified, never as passed.** B1-B6 need two live Herdr panes and
a human. Nothing in group B is claimed.

**Running group A found five defects, all fixed before the PR:** P1 rung 3 was unperformable as
written (it required rung 4's check before any pane exists, while rung 4 named only the pane-bound
form of `herdr agent explain` — the offline `--file --agent` form is now named); `commands/init.md`
asked whether an integration was *current* where rung 4 asks whether a kind is *classifiable*, so
the two commands would have offered different kind sets on the same machine; rung 3's append-only
write produced a second `pair:` key against a config already carrying the schema's own empty one,
which YAML accepts silently; `docs/herdr-coordination.md` claimed the manifest question needs a live
pane and undercounted the classifiable kinds; and the no-`enabled`-key invariant was guarded by
nothing, which `ForbiddenKeyTest` now fixes.

## Files
None — this task runs the shipped commands against a live repo and records results; it edits
nothing but its own status and, on completion, `PLAN.md`'s Outcome/Remaining-work sections.

## Verification
- Every Group A scenario: run the named command, compare actual output against the expected outcome
  column, record pass/fail per row.
- Every Group B scenario, only if two live Herdr panes and a human are available: same recording.
  If unavailable, do not run them — record the omission.
- `python3 -m unittest discover -s tests -v` — expect `Ran 17 tests ... OK`, confirming this task
  introduced no code or structural regression while UAT ran.
