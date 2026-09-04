# Add a pair programming mode

- Tracker: github
- Project: feature development
- Issue: #3
- Issue URL: https://github.com/dabit/just_do_it/issues/3
- Created: 2026-09-03
- Started: 2026-09-03
- TDD: on — proven 2026-09-03 with `python3 -m unittest discover -s tests -v`
- Base commit: main @ 296103df517fa0527082f4a2f77898afc7951c41
- Summary: A /jdi:pair command and a pair config block that has two agents work a plan together as
  driver and navigator, requiring TDD and a Herdr session.

## References

- `plans/1-tdd-configuration/PLAN.md`, `docs/config-key-lifecycle.md` — closest precedent, and the
  repo's procedure for adding a config key
- `reference/testing.md`, `reference/plan-store.md`, `reference/tracker.md`,
  `reference/delegation.md` — TS1/TS2; the `TDD:` line, joined by `Pair:`; the degradation-ladder
  idiom; path 2, how a Herdr pane is reached
- `reference/config.md`, `jdi.config.example.yml`, `commands/execute.md`, `commands/next.md`,
  `commands/yolo.md`, `commands/replan.md`, `commands/reresearch.md`, `commands/init.md`,
  `commands/help.md`
- `agents/executor.md`, `agents/synthesizer.md`, `roles/butler.md`, `README.md`, `AGENTS.md`
- `tests/test_enumerations.py`, `tests/jdi_files.py`, `tests/test_config_schema.py`
- `docs/herdr-coordination.md` — architecture doc for this plan: caller context, the three-layer
  kind check, lifecycle states, failure modes, the single-writer rule
- `reference/pairing.md` — the shipped P1/P2/P3 protocol, citing the human pair-programming
  practice behind issue #3's "derived from" acceptance criterion (Böckeler & Siessegger, Open
  Practice Library, Falco, Fintak, the coderetreat catalogue, Tuple, Xebia) and Arisholm/Hannay
  for the cost figure below

## Decisions

- **Ping-pong, rotating at the red/green boundary TS2 already turns on** — why TDD is a
  prerequisite for pairing rather than a coincidence.
- **Ping-pong has no passive role, by design.** An agent asked to review and approve will approve
  — "LGTM" costs one token, exhortation cannot fix it — so the receiver must re-run the incoming
  failing test and confirm it fails on the named assertion before implementing; a red it cannot
  reproduce returns the handoff. **The capability this buys:** the Butler does not reproduce red
  (a worktree or second clone on every task costs more than the check is worth), but the partner
  does it for free, because it must run the test before implementing — every red is verified by a
  second party that did not write it.
- **No `enabled` key in the `pair` block** — it names *which* two agents, never *whether*, and
  running `/jdi:pair` is the intent. Pairing degrades to not pairing, never a half-pair: one pane
  up and one refused is a failure, since one agent taking both sides of ping-pong is the rubber
  stamp the protocol exists to prevent. **The `Pair:` line has one shape and no `off` shape** for
  the same reason `TDD:` has one — pairing is requested by a **command**, so degradation is
  announced to the user who typed it, in the same turn, and no command reads `Pair:` to decide
  anything (unlike `TDD:`'s `off`, which a later command must be told not to re-detect). Gate on
  the resolved `TDD: on` line, not `tdd.enabled`, which can stay configured on after TDD resolves
  off.
- **A new `reference/pairing.md`, with the `P` prefix**, earned on a consumer type the lifecycle
  doc doesn't list: the two paired agents themselves, reached by delegation path 2 and handed an
  absolute path — not `commands/pair.md`, written to the Butler about orchestration the panes must
  never perform.
- **No new `agents/*.md` role file** — files there register as spawnable types, and
  `agents/driver.md` would create a delegation-path-1 route to something that must only be reached
  by path 2. Driver/navigator are turn assignments inside the existing Executor role instead.
- **`/jdi:pair` written as "follow `/jdi:yolo` in full, with seven differences"** — the
  `replan.md`/`reresearch.md` shape the lifecycle doc sanctions, avoiding a fourth copy of the
  triplicated Executor hand-off. **Single writer; a shared report file, not terminal scrollback** —
  an alternate-screen switch loses scrollback.
- **`init.md` asks about pairing only when `herdr` is on `PATH`**, following init's precedent
  that an unanswerable question is not asked (reversible in one edit) — so "every existing repo
  behaves as before" holds for execution but not for `/jdi:init`, which now asks anyone with
  `herdr` on `PATH` a new question.

**A third P2 move, added from live testing.** The first real run showed the pair working with
strict turn-taking and no interaction at all: an agent that was unsure, or that found something the
plan had not anticipated, had only two moves — implement it anyway and park a note, or reject the
turn. Neither is "wait, let us think about this". That rigidity was a deliberate consequence of
confining prose to the ledger to kill the rubber stamp, and the cost only showed up in use.

P2 now has **consult**. It states named options with the tradeoff and a recommendation, never an
open question, because "what do you think?" invites agreement and agreement costs one token — the
rubber stamp reappearing in prose. The reply is one of the options or a third, named and justified,
with a reason. It consumes no test-list item, is not a turn-back, and produces a `decided` ledger
entry recording what was chosen *and what was rejected*.

**The pair may settle an architectural surprise itself** — two agents in the code often see what a
plan written beforehand could not — but a decision that changes the task's Files list or the plan's
`## Testing Strategy` is recorded as such and surfaced at task end ahead of ordinary notes (P3 rule
11). The accepted trade is that a run can outgrow its plan without the user in the loop; the
mitigation is that it cannot do so quietly, because a plan quietly outgrown reads exactly like a
plan ignored.

## Defects caught during execution

Reading the files did not find these; running the shipped instructions did (UAT, `3dfa530`):

- **Rung 4's "installed and current" check (task 03, `d341d61`) refused `claude` — half the
  intended pair — over a version lag on a hook that does not govern Claude's lifecycle state at
  all** (Claude reports via a detection manifest, not that hook). Rewritten mid-plan to ask whether
  Herdr can *classify* the kind, by hook or manifest; outdated is a warning, not a refusal.
- **UAT then found `commands/init.md` still asking whether an integration was *current*, where
  rung 4 now asks *classifiable*** (same machine, same minute, `/jdi:init` would have offered 4
  kinds and `/jdi:pair` accepted 7), **and found `docs/herdr-coordination.md` undercounting for the
  same reason** — 7 kinds are classifiable here, not 4, since it wrongly claimed the manifest
  question needs a live pane.
- **P1 rung 3 was unperformable** — it required rung 4's check before any pane exists, while rung
  4 named only the pane-bound `herdr agent explain <pane>`. The offline form, `herdr agent explain
  --file <path> --agent <kind>`, was unnamed anywhere; rung 4 now names it.
- **Rung 3's append-only write produced a duplicate `pair:` key** against a config already
  carrying the schema's own empty one — YAML swallows this silently, keeping the last block, while
  an agent reading top-down re-asks every run. Fixed to fill in place.
- **The no-`enabled`-key invariant was guarded by nothing** — `pair.enabled` could have been added
  to schema/example/defaults and passed all 17 tests. `ForbiddenKeyTest` now enforces it; suite 18.
- **Two render gotchas nothing in the suite catches:** TS2's P2 paragraphs must stay indented
  inside their list items or the ordered list renumbers (`c8a6d53`); a missing blank line rendered
  a P2 caveat inside the single-agent paragraph above it (`3dfa530`).
- Task 01: `commands/help.md`'s table named 15 commands for 16 files — `/jdi:help` was missing;
  fixed by adding the row, not exempting `help`. And `bin/sync-opencode.sh` literal-replaces the
  plugin-root variable across every `agents/*.md` body — reference files aren't passed through
  that conversion, agent/command bodies are, so the same token as prose there would have garbled.

## Outcome

### Shipped

| Batch | Commit(s) |
|---|---|
| Plan approved | `937bb5e` |
| 01 — help/butler enumeration guards | `db7888f` |
| 02 — `pair` config block | `a7537e7` |
| 03 — `reference/pairing.md`, reference-file enumerations | `d341d61` |
| 04 — reconcile `testing.md` (TS2) with P2 | `c8a6d53` |
| 05 — `commands/pair.md`, its four enumerations | `176dd46` |
| 06 — Executor paired turn, `Pair:` line documented | `b1f1e7a` |
| 07 — document pairing in init/help/README | `9554190` |
| 08 — release 1.0.4, dogfood | `7dd06e1` |
| 09 — UAT, five defects found and fixed | `3dfa530` |

All ten commits are on this branch per `git log origin/main..HEAD`; no push/merge/deploy state
asserted here.

### Deferred

- `docs/config-key-lifecycle.md`'s stale `file:line` citations into `commands/init.md` — this
  plan's renumber re-staled two more, joining the existing deferral.
- UAT group B, and A4's persistence half (see Remaining work).

## Test result

18 stdlib `unittest` tests, green: `python3 -m unittest discover -s tests -v` reports `Ran 18
tests ... OK` (grew 15 → 17 at task 01 → 18 for `ForbiddenKeyTest`, added during UAT). **No test
observes command or role body prose** — every behavioural claim (P1's ladder, the five-part
handoff, the compulsory re-run, the turn-back cap) is a markdown instruction to an agent; the
suite is a regression guard on structure only. Behavioural proof is UAT.

## Risks

- **The single-writer rule is prose, not enforcement.** A partner follows "stage after every
  edit" unless told otherwise; if not, the commit silently mixes both agents' work with no
  attribution. Detection: `git status --short` showing a file the turn-holder never named.
- **Half the intended pair reports state by terminal-title scrape** (`opencode`: an authoritative
  hook; `claude`: a detection manifest, measured a version behind the binary). Mitigated
  structurally — the report file, not Herdr state, is the turn-over signal. Residual: a stuck pane
  reads `unknown` and never writes a report, so P3 needs a per-turn timeout and must escalate.
- **The `agent prompt` payload ceiling is unmeasured** — mitigated by putting the payload in the
  report file both ways; closing it needs a runtime probe per kind.
- **`commands/pair.md` drifts when `/jdi:yolo` changes** — accepted cost of not writing a fourth
  hand-off copy. Drift grep: `grep -rn 'P1\|P2\|P3\|/jdi:pair\|pair\.' commands/ reference/ agents/
  roles/ README.md AGENTS.md`.
- **The honest cost:** Arisholm et al. (IEEE TSE 2007, 295 professionals) found pairing's
  overall correctness gain **not significant** for ~84% more effort, gains confined to complex
  tasks and less-expert pairs — `/jdi:pair` is a deliberate choice for hard tasks, never a default.

## Remaining work

**UAT group A ran 2026-09-03: 6 pass, 1 partial.** A1 (regression guard), A2, A3, A5, A6, A7
passed. A4 reached P1 rung 3's ask and composed the exact YAML to write, but its *write* is
unobserved: rung 3 requires explicit user confirmation before writing, and an agent fabricating one
is the failure this mode exists to prevent. A3 (`HERDR_ENV` unset) was **simulated** with `env -u
HERDR_ENV` inside a real Herdr pane, not a genuinely non-Herdr session.

**UAT group B did NOT run and is unverified — never passed.** It needs two live Herdr panes and a
human, and an agent ticking off its own acceptance is the evidence-shaped-like-proof this mode
exists to prevent. Six scenarios remain, listed here so the checklist survives the task files'
deletion:

- B1 — a full paired run of at least one task, both panes live: both panes start, P3 drives turns,
  P2's five-part handoff completes an exchange, the run alternates test-author per task, the
  shared report file (not terminal scrollback) carries the notes.
- B2 — a handoff sent with one of the five parts missing (no read receipt): P3's structural check
  catches and returns it without judging substance.
- B3 — a receiver that cannot reproduce the incoming red (it passes, or errors): the handoff
  returns with the receiver's own transcript; the sender's turn is not consumed.
- B4 — a navigator/driver rejection, with a stated reason: the turn returns without consuming a
  test-list item; disagreement is a test or a stated reason, never a silent edit.
- B5 — two consecutive turn-backs in one task: the run stops, both positions and transcripts go to
  the user, the Butler does not break the tie.
- B6 — one pane hits `agent_blocked`: the run stops and surfaces it; neither agent answers the
  other's dialog.

**Also unverified, confirmed by reading only, not by running:**

- `/jdi:init` asking about pairing, and the README documenting it — confirmed only by reading
  `commands/init.md`'s new step and `README.md`'s two enumerations plus its new section. Whether
  the question is actually asked, in the right words, at the right time, needs a live `/jdi:init`
  run against a repo with no existing `.jdi/config.yml`.
- The "derived from human pair-programming practice" acceptance criterion — proven only by reading
  `reference/pairing.md`'s cited sources against the P2 rules that cite them, a documentation
  review rather than a runtime scenario.

**Deliberately out of scope**, each with a stated reason: `commands/prep.md`'s config-block list
(prep never resolves P1); `commands/status.md` (matches both precedents); `agents/planner.md` (its
existing "say which test proves which step" bullet already covers P2's granularity); no new
`agents/*.md` role file (see Decisions); `bin/sync-opencode.sh` (glob-driven, needs no adapter
edit for a new file). This repo's dogfooded `pair.agents` is a claim about one machine — a
contributor lacking a named kind gets rung 4's announced degradation, designed behaviour, not a
defect.
