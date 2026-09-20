status: done
# 02 — `reference/delegation.md`: the ladder, the authorization correction, the recast

Depends on: 01

`reference/delegation.md` is the load-bearing artifact for this whole change: it is the only place
that says how a role's configured model and harness actually get honoured. Task 01 defines the
schema (`models.<role>.model` / `.harness`, `harnesses.<kind>.args` / `.env`) that this task's prose
now describes; writing the ladder against the old three-tier shape would mean rewriting it twice.

## Why
`reference/delegation.md` currently calls the old three-tier `models:` block "the authority" and
tells the reader that a spawned CLI "stays inside the active sandbox, approval policy, and
authorization boundaries" — both false once a role's harness can be a different CLI process. This
task rewrites the file section by section to match the per-role schema, promotes the second-session
path from fallback to a selected transport, and corrects the authorization claim.

## Description
Rewrite `reference/delegation.md` section by section, per PLAN.md steps 8–15:

1. **Title and intro** (`:1-6`). `# Delegation and model tiers` → `# Delegation and models`. Replace
   "It names a **role** and a **tier**" with: it names a **role**, and `.jdi/config.yml` says what
   that role runs on and where.
2. **`## Roles` table** (`:10-24`). Drop the `Tier` column; keep `Role | Definition`. Keep the
   Butler row and the "never spawned" paragraph (`:23-24`) verbatim.
3. **Recast `## Tiers` (`:62-70`) — do not delete it.** New heading `## What each role wants from a
   model`, `Role | For | Wants` rows. Carry the three existing `Wants` cells forward, redistributed
   per role — this is the only place in the repo stating what each phase wants from a model, which
   is exactly the guidance a user needs to fill in seven keys. **Do not use the phrase "mid-tier"**
   anywhere in the recast — the vocabulary guard (T-H, written in task 06) forbids the word, and it
   must not be reintroduced here for task 06 to be able to remove it later.
4. **`## How to delegate`** (`:26-56`). Keep the capability ladder; rung 2 is promoted from
   fallback to a *chosen* path:
   - Rung 1 heading `**1. The harness has first-class subagents**` — keep verbatim (pinned at
     `tests/test_codex_plugin.py:198`).
   - `:36` and `:39` "the tier's model from the config" → "the role's model from the config" (both
     occurrences).
   - Rung 2 heading `**2. The harness has no subagents, but can run a second session**` →
     `**2. A second non-interactive session**`, with body text saying this is now a chosen path
     when `models.<role>.harness` names a different kind, not only a fallback for a deficient
     harness.
   - Rung 3 heading `**3. Neither.** **Adopt the role inline.**` — keep verbatim (pinned at `:200`).
   - `:53-56`'s "Do not silently skip a role because delegation is unavailable" — keep.
5. **New section `## Where a role runs`.** `models.<role>.harness` names a key in `harnesses:`.
   Resolution is **exec-first, Herdr second** — write PLAN.md step 12 in full:
   - Prefer each kind's own non-interactive mode: `codex exec -m <model> -o <file> "<prompt>"` then
     read `<file>`; `opencode run -m <provider/model> --agent jdi-<role> --format json "<prompt>"`;
     `claude -p --model <alias> --output-format json "<prompt>"`. State explicitly that `harness:
     claude` is a first-class value (a Codex or OpenCode session putting a role back on Claude), not
     merely the no-op case of naming the session's own kind.
   - Use Herdr only when the kind has no exec mode JDI knows, or the user asked to watch the run.
     Drive it with `herdr pane split` → `herdr pane run <PANE_ID> <command>` → `herdr pane
     wait-output --match <sentinel> --timeout <ms> <PANE_ID>` → read the file the command was told
     to write. **Not `herdr agent start`** — `herdr agent read` is a terminal scrape that cannot
     recover a long report from the alternate screen.
   - "A pane JDI created is JDI's to close" — every exit from a Herdr path runs `herdr pane close
     <pane_id>` before it announces.
   - Role-instruction portability: name the target's registered role where one exists
     (`opencode run --agent jdi-<role>`); otherwise inline the role file. Take a plugin-root path
     **only from an explicit config value, never derived** — the Codex and Claude snapshots are
     version-pinned and share no derivation rule (`docs/harness-adapter-architecture.md:191-194`).
6. **Rewrite the authorization paragraph** (`:58-60`). The current sentence — "Subagents and
   fallback sessions stay inside the active sandbox, approval policy, and authorization
   boundaries" — is **true for rungs 1 and 3, false for rung 2**. Replace it with the corrected
   paragraph from PLAN.md step 13, verbatim:

   > Delegation never grants additional authority, and JDI never composes any. An in-harness
   > subagent and an inline adoption run inside this session's own sandbox and approval policy.
   > **A separately spawned CLI does not** — it is another process that resolves its own sandbox,
   > approval policy and credentials from its own configuration, which may be broader or narrower
   > than this session's. JDI composes no authority-affecting flag and translates none between
   > kinds: every flag a spawned CLI receives is a literal value the user wrote in
   > `harnesses.<kind>.args`, passed through verbatim and **printed back before the spawn**. Any
   > external mutation must still be allowed by the active command and the Butler's rules.

   **Cross-reference — read before you write this.** `docs/harness-adapter-architecture.md:256-257`
   states the same false claim in different words ("Subagents inherit the active sandbox and
   approval environment, and external mutations remain governed by the active command and Butler
   rules") and is **not** corrected in this task — it is corrected in task 06, from this same
   corrected text. Until task 06 lands, the two documents disagree on a security-relevant claim.
   That is expected and named in the plan; it is not this task's job to fix the other file.
7. **New section `## When the configuration cannot be honoured` — the twelve-rung degradation
   ladder.** Write PLAN.md step 14 in full: the two-phase framing (rungs 1–9 settle *where*, rungs
   10–12 settle *which model*, one announcement when both fire), the twelve rungs verbatim, the
   four "never" closing rules (never skip the phase, never acquire a flag the user did not write,
   never land somewhere less supervised, never promote a model), and the old-shape detection
   sentence for a pre-1.0.5 `deep`/`standard`/`fast` block.
8. **Rewrite `## Harness-specific metadata`** (`:86-92`). Its claim that "a concrete model name …
   lives in a file's YAML frontmatter" is directly inverted. The rule that survives: harness-specific
   *frontmatter* (tool allowlists, argument hints) still belongs in frontmatter; a model name now
   belongs in `.jdi/config.yml` and nowhere else.

**Tests, same commit.** Rewrite `DelegationGuidanceTest` in `tests/test_codex_plugin.py:173-209` —
it must not be observed going red in a later task. Every fragment's fate is in PLAN.md's T-F table
(Testing Strategy, "The two rewrites, in the batch that causes them"); the load-bearing ones:
- `:199` `"**2. The harness has no subagents, but can run a second session**"` dies —
  `str.index` **raises** on absence (an error, not a failure) — replace with the new rung-2 heading.
- `:204` `"the tier's model from the config"` dies → `"the role's model from the config"`.
- `:205` `"Shell out to it with the role file..."` dies → the new exec-mode sentence.
- `:207` `"Subagents and fallback sessions stay inside..."` dies → replace with the two surviving
  fragments from the corrected paragraph: `"A separately spawned CLI does not"` and `"JDI composes
  no authority-affecting flag and translates none between kinds"`.
- `:185`, `:186`, `:191-193`, `:198`, `:200`, `:206`, `:208` **survive** verbatim.

Add a small number of new pins on the ladder in the same rewrite: the floor rung's sentence, `"one
announcement, not two"`, `"Never skip the phase."`, `"Never acquire a flag the user did not
write."`, `"herdr pane close"`, and an ordering assertion (`index` comparisons, as the existing test
already does) that rung 1 precedes rung 12.

**Do not write T-H (the "tier" word scan) in this task.** It cannot pass until task 06 removes the
last occurrence, and no task in this plan may end with a failing suite. Verify this task's share of
the vocabulary removal with the manual grep below instead.

## Files
- `reference/delegation.md`
- `tests/test_codex_plugin.py`

## Verification
- `python3 -m unittest discover -s tests -v` — expect **at least 49 tests, OK**, 0 failures, 0
  errors (task 01's T-A/T-B stay green; `DelegationGuidanceTest`'s rewritten methods pass; any new
  test methods added for the ladder's new pins add to the count).
- `grep -ciE '\btiers?\b' reference/delegation.md` — expect `0`. This is the file with the largest share of
  tier vocabulary in the whole repo (title, roles table, "How to delegate", the `## Tiers` section,
  and the authority paragraph); after this task none of it should remain here. (Other files —
  `commands/*.md`, `README.md`, `AGENTS.md`, `roles/butler.md`, `bin/sync-opencode.sh`,
  `docs/config-key-lifecycle.md` — still say it until tasks 03–06; that is expected, not a bug.)
- `grep -c "stay inside the active sandbox" reference/delegation.md` — expect **0** (was 1, the
  exact false-claim sentence this task deletes). Do not use a bare `grep -n "sandbox"` count as the
  check: `reference/delegation.md`'s own corrected paragraph still says "sandbox" twice (once for
  the in-harness case, once for the spawned-CLI case), and `docs/harness-adapter-architecture.md`
  independently says "sandbox" at **two** sites today (`:168`, in the dispatcher's guarantee list,
  and `:256`, the claim this task does not touch) — a raw count would not tell you whether the right
  sentence disappeared.
- Control, same command, unrelated file: `grep -c "inherit the active sandbox" docs/harness-adapter-architecture.md`
  — expect **1**. This file's parallel claim (`:256-257`) is **not** corrected in this task — it is
  corrected in task 06, from this same text — so it must still read the old, uncorrected wording
  here. If this control also reads `0`, someone edited the wrong file.
