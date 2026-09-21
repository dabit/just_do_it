# Ask Jev for a typed judgment where a role would otherwise skim a list

- Tracker: GitHub Issues
- Project: feature development
- Issue: 11
- Issue URL: https://github.com/dabit/just_do_it/issues/11
- Created: 2026-09-20
- Base commit: origin/main @ f1af71f1aff03f1224f2db6c8ffa1afe8106e596
- Summary: Add an opt-in `jev.enabled` key that lets roles ask Jev — TypeSafe's System One model — for typed judgments at five named call sites, defined in a new `reference/jev.md` and called by name the way `reference/tracker.md`'s T1–T8 are. Off by default and silent when off; Jev narrows a list a role already has and never decides.
- Started: 2026-09-20
- TDD: **off for this plan** — see Test result. The repo's `.jdi/config.yml` sets `tdd.enabled: true`, and this plan did not honour it.

## How this plan was produced

**This change did not go through the JDI workflow.** There was no `/jdi:prep`, no Researcher, no
Planner, no Splitter, no task files, and no one-commit-per-task rhythm. The work was done directly
in one session and landed as a single commit, and issue #11 was filed *after* the implementation
existed rather than before it.

This document is therefore a **retrospective record**, written to the shape `/jdi:pr`'s Synthesizer
produces so that the plan store stays readable, not a condensation of a plan that was executed.
Every section below reports what actually happened. Where a section would normally carry evidence
from a phase that never ran, it says so rather than reconstructing it.

`docs/config-key-lifecycle.md` stood in for the planning phase: it is the repo's written procedure
for adding a configuration key, and it supplied the nine-file floor, the degradation idiom, the
five-question admission test, and the release mechanics.

## References

- `docs/config-key-lifecycle.md` — the procedure this change followed in place of a plan
- `reference/jev.md` — **new**: universal rules, the ladder, J1–J5, the admission filter
- `reference/config.md` — `jev:` schema, defaults row, four invariant bullets
- `reference/tracker.md` — universal rule 3 and T4 gain J3; T5/T8 deliberately excluded
- `jdi.config.example.yml`
- `.jdi/config.yml` — the dogfood, set to `enabled: true`
- `commands/init.md` — new step 6, steps 6–12 renumbered to 7–13
- `commands/help.md`, `README.md`, `AGENTS.md`
- `commands/prep.md`, `commands/research.md`, `commands/split.md`, `commands/feedback.md` — ladder at step 0, Jev availability in the hand-off
- `commands/plan.md`, `commands/pr.md` — ladder at step 0 for T4/J3 only; they rank nothing themselves
- `agents/researcher.md`, `agents/splitter.md`, `agents/feedbacker.md` — the discipline, plus "Whether Jev is available" in *What it receives*
- `roles/butler.md` — the standing duty: resolve capabilities once, pass roles the answer
- `commands/status.md`, `commands/done.md`, `commands/next.md`, `commands/yolo.md`, `commands/execute.md` — considered, deliberately unchanged
- `CHANGELOG.md`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json`
- `tests/test_config_schema.py`, `tests/test_enumerations.py`, `tests/test_versions.py` — all three cover the new key with no edit
- `plans/1-tdd-configuration/PLAN.md`, `plans/9-agent-model-settings/PLAN.md` — the two prior behavioural keys, and the nine-file-floor precedent
- https://docs.typesafe.ai/llms.txt — docs index; `api.md`, `models.md`, `confidence.md`, `primitives/score.md`, `concepts/how-to-build-with-system-one.md`, `cookbooks/parallel_questions.md`, `model-jaggedness/jev-1.13.md`

## Decisions

- **The key is `jev.enabled`, a block, not a bare `jev: true`.** The issue and the original request
  both said `jev: true`. A block matches `tdd.enabled` — the closest existing analogue, also a
  behavioural boolean that needs a capability proven before it can run — and leaves somewhere for a
  later key to land without a breaking rename.
- **No `jev.model` and no `jev.api_key_env` key.** Both fail question 1 of the lifecycle doc's
  admission test: two sensible repos would not answer them differently. There is exactly one model
  (`jev-latest` → `jev-1.13.0`), and `TYPESAFE_API_KEY` is the vendor's documented variable. Both
  are hardcoded, and the key lookup falls back to `~/.config/typesafe/api_key` because that is
  where this machine's key already lives.
- **"Wherever possible" became a closed list with a written admission filter.** The request was
  open-ended; leaving it open would have made every future role prompt a candidate call site.
  `reference/jev.md` closes it with five questions a new J-op must pass — is there a list, does the
  role currently skim, can the caller enumerate the candidates, is the answer advisory, does it
  degrade to more work — and records why `/jdi:status`, `/jdi:done`, `/jdi:execute` and `/jdi:yolo`
  rank nothing of their own.
- **Jev narrows; it never decides.** The destructive direction, named and closed per the
  degradation idiom: a Jev answer may reorder a list, flag a candidate, or pre-select one option
  from a set the caller already enumerated, and is never the reason a step is skipped, a tracker is
  written, a commit is made, or a pull request is opened.
- **Degrades to more work, never less.** The inverse of the usual ladder: the fallback for every
  rung is the un-Jev'd path, which is strictly *more* reading. A confidence below 0.5 is treated as
  no answer. Dropping a consumer sweep because an optional model was unavailable would be worse
  than never having asked.
- **The Butler probes once at step 0 and passes a resolved fact.** Per the lifecycle doc's
  "prefer passing a resolved value" rule, roles receive "Jev is available" or nothing — never the
  key, never the ladder. `roles/butler.md` gained this as a standing duty covering the test runner
  and the tracker too, because it was already true of both and had never been written down.
- **J3 is reached only through T4, and T5/T8 are deliberately not callers.** T5 resolves no state
  at all — it upserts a comment. T8 resolves one, but only in `subtickets` mode and only to the
  **completed** state, the one role a tracker's own state types name unambiguously. Wiring J3 into
  T8 would have put a network probe into `/jdi:done`, `/jdi:next` and `/jdi:yolo` — the three most
  frequently run commands — for the least ambiguous lookup JDI makes.
- **`/jdi:plan` and `/jdi:pr` carry the ladder although they rank nothing themselves**, because
  both call T4. This is the one place a command resolves Jev without having a J-op of its own, and
  both files say so in place.
- **J4 does not ask about dependency ordering.** Task files declare their dependencies, so
  "does this task depend on one numbered after it?" is a comparison of two numbers. Ordering is a
  documented weakness of Jev 1.13; the question was removed and the four documented weaknesses
  (counting, ordering, indirection, irrelevant state) are written into `reference/jev.md` as
  design constraints.
- **The dogfood sets `enabled: true` in this repo's `.jdi/config.yml`**, matching the
  dogfood-at-implementation precedent from #9 rather than dogfood-at-release from #1.
- **1.0.6 is a patch bump**, following the only observed convention — two prior full features
  shipped as patches, and #9 shipped as one while removing a key.

## Corrections caught during review

There was no execution phase to catch plan gaps, so these are defects found by reviewing the work
against the repo's own rules and the vendor's documentation, and fixed before the commit:

- **J3 was unreachable as first written.** It was wired into T4, T5 and T8, but the commands that
  call those ops — `plan.md`, `pr.md`, `done.md`, `next.md`, `yolo.md` — had no step-0 ladder, so
  "the Butler resolved Jev as available" could never be true there. Fixed by scoping J3 to T4 and
  adding the ladder to `plan.md` and `pr.md`; T5 and T8 were excluded with the reasoning recorded.
- **T5 was named as a J3 caller and resolves no state.** It is the idempotent research-comment
  upsert. Removed.
- **The CHANGELOG and `reference/jev.md` contradicted `reference/tracker.md`** for one revision —
  they claimed `/jdi:pr` had no J-ops while tracker.md routed J3 through T4, which `/jdi:pr` calls.
  Reworded to "ranks nothing of their own", which is the accurate claim.
- **J4 asked Jev to compare task numbers**, which the vendor's jaggedness notes list as a failure
  mode. Removed from both `reference/jev.md` and `agents/splitter.md`, along with the stale
  "any of the three" count that survived in two places.
- **`docs/config-key-lifecycle.md`'s line citations into `reference/config.md` went stale** when
  the `jev:` block, the defaults row and the four Notes bullets shifted everything below them. Six
  citations plus two version citations were recomputed and corrected.
- **Four citations in the same document were already stale at `HEAD`** — `README.md:164-168`,
  `jdi.config.example.yml:27-33`, `commands/help.md:83-90`, `commands/help.md:9-13` — and were
  **left alone**, out of scope for this change. They are still wrong.
- **`commands/prep.md`'s literal config-block list omitted `jev`** on first pass; `tdd` is legitimately
  absent from it (prep never executes), which made the omission easy to mirror by accident.
- Three inserted paragraphs exceeded the repo's ~100-column wrap and were reflowed.

## Outcome

### Shipped

| Batch | Commit |
|---|---|
| Whole change — schema, `reference/jev.md`, behaviour sites, roles, docs, release 1.0.6 | `3779438` |

One commit, not the usual one-per-task, because no split ran. It is on this branch per
`git log main..HEAD` in this session; push and merge state are unverified here.

### Deferred

- **UAT did not run.** No scenario in the Remaining work section below has been executed. No
  follow-up issue has been filed for it.
- **No test pins J1–J5 or the ladder.** See Risk note.
- Deliberately out of scope, not deferred (decisions, not gaps): `jev.model`, `jev.api_key_env`,
  J3 in T5/T8, J-ops in `/jdi:status`, `/jdi:done`, `/jdi:execute`, `/jdi:yolo`, and the four
  citations in `docs/config-key-lifecycle.md` that were already stale at `HEAD`.

## Test result

Baseline **54 tests, OK** at `f1af71f`. Final suite: `python3 -m unittest discover -s tests` →
**54 tests, OK**, 0 failures, 0 errors.

**No test was added, and TDD did not happen.** This repo's `.jdi/config.yml` sets
`tdd.enabled: true`; that mode was not honoured, because this change did not run through
`/jdi:execute` at all. The count is unchanged because the three existing structural guards cover
the new key with no edit — and each was confirmed to actually fire during the work:

- `tests/test_config_schema.py` — key parity across `reference/config.md`'s schema,
  `jdi.config.example.yml`, and the defaults table. Verified to hold `jev` and `jev.enabled` in all
  three.
- `tests/test_enumerations.py` — `reference/jev.md` is a new reference file, so both hand-maintained
  enumerations (README's "How it is put together" table, `AGENTS.md`'s reference-files paragraph)
  are required. This guard **failed first and was made to pass**, which is the one place in this
  change where a test drove the edit.
- `tests/test_versions.py` — the three manifests and the CHANGELOG heading all read `1.0.6`.

**What no test reads:** every word of `reference/jev.md`, the ladder, the J1–J5 definitions, the
five-operation count in three documents, and the prose added to six commands and three role files.
The suite is a structural regression guard, exactly as it was for #9.

### Verified live against the API

Three real requests to `POST https://api.typesafe.ai/v1/systemone`, so the contract written into
`reference/jev.md` is observed rather than transcribed from documentation:

- A batched `score` + `noul` request in J1's shape — confirmed the response envelope, the
  0-indexed `legend`, the probability-weighted `score` (2.52), and `usage`. The JSON example in
  `reference/jev.md` is this response.
- A `choice` request in J3's shape over five deliberately idiosyncratic state names
  ("Icebox", "On deck", "Baking", "Needs eyes", "Shipped it") — returned `"Baking"` at confidence
  **1.0**, above the 0.9 gate J3 specifies.
- The same J1-shaped request also demonstrated the state-thinness failure the ladder's rung 5
  warns about: a `noul` asking whether `docs/config-key-lifecycle.md` lays out a procedure returned
  **0.14** — wrong — when sent only the document's headings. This is why J1's state bullet requires
  the opening paragraph, not headings alone.

## Risk note

- **Nothing in the test suite would notice if `reference/jev.md` were deleted, gutted, or
  contradicted by a command file.** The five-operation count appears in `README.md`, `AGENTS.md`
  and `CHANGELOG.md` as prose, and `docs/config-key-lifecycle.md` §4 is explicit that counts in
  prose are citations too. `reference/tracker.md`'s T1–T8 and `reference/testing.md`'s TS1–TS2 have
  the same gap, so this is consistent with the repo rather than a new hole — but it is a hole.
  Detection signal: a J-op added or removed without the three prose counts moving. Remedy: a
  structural guard asserting the `## J<n>` headings in `reference/jev.md` match the count stated in
  the README row, extended to T- and TS-ops. Not filed.
- **The whole feature is unexercised.** Not one J-op has run inside a JDI command. The API contract
  is proven, and the prose is reviewed, but no Researcher has ever ranked a document with J1 and no
  Splitter has ever checked its own output with J4. UAT below is the only thing that would change
  this. Detection signal: the first real `/jdi:research` on a repo with `jev.enabled: true`.
- **The silence guarantee is the highest-consequence unproven claim.** A repo with the key unset
  must be indistinguishable from a 1.0.5 run. It is asserted in six command files,
  `roles/butler.md`, three role files, `README.md`, `commands/help.md` and `reference/config.md`
  — eleven independent
  prose sites, any one of which could leak an announcement. Nothing tests it. Scenario 6 below
  exists for this specifically, and **any** announcement there is a failure, not harmless chatter.
- **The dogfood turns Jev on for this repository**, so every subsequent `/jdi:research`,
  `/jdi:split`, `/jdi:feedback`, `/jdi:prep`, `/jdi:plan` and `/jdi:pr` run here will probe the API
  and, without `TYPESAFE_API_KEY` exported in that session, announce rung 2 once. Correct behaviour
  — the key is configured and genuinely absent — but it will look like a bug to whoever sees it
  first, and it is a behaviour change to this repo's own workflow. Remedy if unwanted: set
  `enabled: false` in `.jdi/config.yml`; nothing else changes.
- **Cost and latency are unmeasured in situ.** The vendor's batching numbers (12.2× cheaper, 10×
  faster for 13 questions in one request) come from their cookbook, not from JDI. J1 sends one
  question per document and J4 one request per split; neither has been measured against a real plan.
  Rung 5's 32k state budget is likewise a documented limit, not an observed one.
- **Jev's calibration in this domain is untested.** The vendor is explicit that System One models
  are trained for calibrated decisions but must be validated in the target domain. J1's four score
  levels and J5's consequence levels were written once and never tuned against real JDI data; the
  0.5 and 0.9 thresholds are the vendor's general guidance, not thresholds evaluated here.

## Remaining work

**UAT did not run.** This section is the only record of the procedure and is carried in full so it
can be executed later — it is exempt from this document's compression target.

Machine state assumed: `TYPESAFE_API_KEY` exportable, or a readable `~/.config/typesafe/api_key`;
network access to `api.typesafe.ai`. For each scenario record the announcement verbatim and, where
Jev ran, the request and the answer — several scenarios exist to check *whether* something was said
at all.

### Scenarios

**Silence and compatibility — run these first; they are the backward-compatibility guarantee:**

1. **Key absent entirely.** Scratch repo with a 1.0.5-era `.jdi/config.yml` (no `jev:` block). Run
   `/jdi:research`, `/jdi:split` and `/jdi:feedback`. Confirm **complete silence** about Jev in all
   three — no announcement, no mention, nothing. Any output at all here is a **failure**, not
   harmless chatter. This is the guarantee eleven prose sites collectively make and nothing tests.
2. **Key present and false.** Same, with `jev: {enabled: false}` written explicitly. Confirm the
   same complete silence — an explicit `false` must be as quiet as an absent block.

**The ladder — each rung announced exactly once, then off for the run:**

3. **Rung 2, no key.** `jev.enabled: true`, `TYPESAFE_API_KEY` unset, no
   `~/.config/typesafe/api_key`. Run `/jdi:research`. Confirm exactly **one** announcement naming
   the missing key and the `export` line that fixes it, that the Researcher then reads every
   candidate document itself, and that the announcement does **not** repeat at the hand-off.
4. **Rung 4, bad key.** `TYPESAFE_API_KEY=invalid`. Confirm the announcement names the **401**
   specifically, that there is at most one retry, and that the phase still runs at the floor.
5. **Rung 5, oversized state.** Point `docs.path` at a directory holding a document larger than the
   32k state budget. Confirm that operation is skipped for the oversized input with an
   announcement, that the state is **never silently truncated**, and that the Researcher reads that
   document itself.
6. **One probe per run, not per role.** `/jdi:prep` with a valid key — it runs research, planning
   and splitting in one pass. Confirm the ladder ran **once** at step 1 and that neither the
   Researcher nor the Splitter re-probed or re-announced.

**The operations — each must narrow without deciding:**

7. **J1 ranking.** A repo with fifteen or more architecture documents, only two of which bear on
   the change. Confirm the two are scored *Required*/*Useful* and read first and in full; confirm
   every *Irrelevant* document is **still listed** in the findings as considered-and-not-read, not
   dropped; confirm a sub-0.5 confidence caused the document to be read anyway.
8. **J2 consumer screen.** A repo with three or more `consumers`, one genuinely affected by a
   public-interface change. Confirm the affected one is flagged and investigated properly, that the
   others are recorded as swept-and-clear, and that **no consumer is marked clear on a screen that
   did not run** — kill the network mid-command to force this.
9. **J3 tracker state.** A tracker whose workflow states are idiosyncratic. Run `/jdi:plan` and
   confirm the state resolved by role is correct, that the write was read back per
   `reference/tracker.md` universal rule 5, and — the important half — that a **sub-0.9 confidence
   asks the user** instead of writing. Force the latter with two near-synonymous states.
10. **J4 atomicity.** Hand the Splitter a plan containing one task that is obviously two. Confirm
    the task is **reported to the Butler as a question** — which task, which property, what the
    Splitter would do — and that the Splitter did **not** silently re-split it or rewrite the file.
11. **J5 finding order.** Run `/jdi:feedback` on an output with six or more findings of genuinely
    mixed severity. Confirm the order matches consequence, that **nothing was dropped**, and that a
    finding failing the support check is kept and marked unsupported rather than deleted.

**The invariant, tested adversarially:**

12. **Jev never decides.** Across scenarios 7–11, confirm no Jev answer alone caused a step to be
    skipped, a tracker to be written, a commit to be made, or a PR to be opened. Specifically: run
    `/jdi:pr` with Jev available and confirm the pull request still required the same user approval
    it requires with the key off.
13. **`/jdi:init` read-through.** Scratch repo, no config. Run `/jdi:init`. Confirm step 6 asks the
    Jev question, explains what it buys before asking, **finds** the key rather than asking for it,
    **never prints its value**, sends one throwaway question to prove it, and records the setting
    even when the probe failed. Confirm the written file has no key in it.
14. **`/jdi:help` read-through.** Confirm the `### Typed judgments with Jev` section reads
    correctly, that the `/jdi:research`, `/jdi:split` and `/jdi:feedback` rows carry their clauses,
    and that the closing line names whether Jev is on.
15. **OpenCode sync.** `bin/sync-opencode.sh --global` into a temp `OPENCODE_CONFIG_DIR`; confirm
    `reference/jev.md` arrives with paths rewritten and that a synced command's step 0 still
    resolves it.

### Acceptance-criteria mapping (against issue #11's "Wanted" list)

| AC | Clause | Proven by | Notes |
|---|---|---|---|
| 1 | Off by default and silent when off; a repo that does not set it behaves exactly as today | Scenarios 1, 2 | **Nothing structural tests this.** Eleven prose sites assert it; any one could leak |
| 2 | Named operations in a reference file, called by name the way T1–T8 are | `reference/jev.md` J1–J5; reviewer-verified | No test reads the file or counts the ops — see Risk note |
| 3 | An admission filter a future operation must pass | `reference/jev.md` "Adding an operation" | Reviewer-verified only |
| 4 | Jev narrows; never the reason a step is skipped, a tracker written, a commit made, a PR opened | Scenario 12 | Adversarial; the single most important scenario |
| 5 | Degrade to more work, never less | Scenarios 3, 4, 5 | Each must show the role doing the *full* un-Jev'd path afterwards |
| 6 | Capability proven, not assumed; Butler probes once and passes a resolved fact | Scenario 6 | Live API contract already proven this session; the once-per-run property is not |
| 7 | The key never lands in the repository | `grep -rn "apikey_"` clean in this session; scenario 13 | Confirmed for the commit; scenario 13 confirms `/jdi:init` never writes it |

**Reviewer-verified-only clauses (no test reads them):** all of `reference/jev.md`; the
five-operation count in `README.md`, `AGENTS.md` and `CHANGELOG.md`; the ladder text repeated
across six command files; the discipline paragraphs in three role files; the standing duty in
`roles/butler.md`.
