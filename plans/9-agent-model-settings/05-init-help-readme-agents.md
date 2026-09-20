status: done
# 05 — init, help, README, AGENTS.md: the nine-file floor

Depends on: 04

## Why
`models` has never reached the full nine-file floor `docs/config-key-lifecycle.md:52-68` requires
of a config key: `/jdi:init` doesn't ask about it per-role, `/jdi:help` still shows a `Tier` column,
and `README.md` still tells a reader that model names live in frontmatter. This task closes that as
part of the change rather than leaving it half-added, and removes the remaining tier vocabulary from
every user-facing document.

## Description

**`commands/init.md`:**
1. `:2` — the frontmatter `description:` enumerates init's questions and does not mention models.
   Add them.
2. `:102-106` — **step 8 is a rewrite, not an insert.** A question about models already exists as
   step 8, so nothing renumbers and `grep -rn "step [0-9]" commands/` has nothing new to find — say
   this plainly in the diff/commit so an Executor following the lifecycle doc's default expectation
   does not go looking for back-references that do not exist. Rewrite the step to ask per role
   rather than per tier, keep "optional, and say that it is optional," and fold the `harnesses`
   question in as a conditional sub-question, **asked only when the user named a different harness
   for at least one role** — mirroring the skip-the-question-that-cannot-apply shape already at
   `commands/init.md:54-55`.
3. `:13` — "example tier mappings" → "example model mappings", matching the heading task 01 renamed
   in `reference/config.md`.

**`commands/help.md`:**
4. `:9-12` — the closing config-state line instruction currently names the tracker, plan store,
   split pieces, and TDD. Add: which roles have a model configured, and whether any role runs in
   another harness.
5. `:23-39` — **drop the `Tier` column** from the command table. With roles carrying their own
   model, the column is redundant with the adjacent `Roles` column. No test reads this table.
6. `:25` — the `/jdi:init` row lists init's questions a second time. Add models.
7. `:113-118` — `### Tiers, not models` → `### Roles and models`. Rewrite the prose: JDI names
   roles; `.jdi/config.yml` maps each role to a model and optionally to an agent CLI; leaving the
   block out runs everything on the session's own model and is fully supported; a role's harness or
   model that cannot be honoured is announced once and the phase still runs.
8. `:2` — the frontmatter `description:` says "the commands, the roles, the tiers, and the typical
   flow." Drop "the tiers."

**`README.md`:**
9. `:12` — "JDI names *roles* and *reasoning tiers*, never models or vendors" → names *roles*, and
   the model each role runs on lives in settings, not in the workflow prose.
10. `:185` — the `/jdi:init` snippet comment enumerating init's questions. Add models. `:192-198` —
    the prose immediately below, enumerating them a second time. Add models there too —
    `docs/config-key-lifecycle.md:107-110` names this pair as easy to half-update.
11. `:288` — the `reference/config.md` row says "example tier mappings"; recast. `:292` — the
    `reference/delegation.md` row says "How a role and a tier become an actual model on your
    harness"; recast.
12. `:304-323` — the heading `### Roles and tiers, not agents and models` → **`### Roles and models, not agents and vendors`**.
    Use exactly this heading; do not improvise. "not agents and tiers" contains the word T-H
    bans repo-wide in task 06, and T-G below pins the heading string exactly. `:314-317`'s three-tier paragraph becomes the per-role
    description plus the `harness:` sentence. `:322-323` — "Concrete model names and tool
    allowlists live only in YAML frontmatter" is now false for model names and must be split: tool
    allowlists still live in frontmatter; model names live in `.jdi/config.yml`.

**`AGENTS.md` — not in the plan's numbered steps; added here to close a gap.** `AGENTS.md:44` is
named in PLAN.md's reference list of the removal surface (`plans/9-agent-model-settings/PLAN.md:45`)
and is scanned by T-H (task 06), but no numbered implementation step assigns it an edit. Its current
text: `**Delegation.** Commands say "delegate to the *Researcher* role at the *deep* tier". If your
harness has no subagents...` — the same hand-off phrasing removed from `commands/*.md` in task 04.
13. `AGENTS.md:44` — delete the `at the *deep* tier` clause, matching task 04's pattern: `Commands
    say "delegate to the *Researcher* role at the *deep* tier"` → `Commands say "delegate to the
    *Researcher* role"`. Confirmed safe against the test suite: `tests/test_codex_plugin.py`'s
    `ManualInvocationGuidanceTest` (which reads `AGENTS.md`) checks `$ARGUMENTS` replacement rules
    and the OpenCode adapter portability rules, not this sentence.

**Tests, same commit.** `tests/test_codex_plugin.py:317` calls
`normalized_section("### Roles and tiers, not agents and models")`, and
`tests/jdi_files.py:150-153` **raises** `AssertionError` when the heading is absent — this is
**T-G**. (An earlier draft cited `:295`; that line is inside a different test method.) Update the
call to the new heading from step 12 above, in this same commit. Re-check the three fragment
assertions that follow it (`"Delegation follows observed runtime capability"`, `"a
suitable generic subagent"`, `"adopt the role inline and announce the switch"`) against the
rewritten `README.md:304-323` — confirm they still appear rather than assuming they do.

## Files
- `commands/init.md`
- `commands/help.md`
- `README.md`
- `AGENTS.md`
- `tests/test_codex_plugin.py`

## Verification
- `python3 -m unittest discover -s tests -v` — expect **53 tests, OK**, unchanged from task 04:
  T-G is a rewrite-in-place, not a new test. (An earlier draft said "at least 51", written before
  task 03 added T-D and T-E.) 0 failures, 0 errors.
- `grep -n "step [0-9]" commands/init.md` — read every hit and confirm none needs renumbering; step
  8's own text changed but no step number moved.
- `grep -riE '\btiers?\b' README.md AGENTS.md commands/init.md commands/help.md` — expect **no output**.
  This closes the remaining non-command, non-architecture-doc vocabulary sites; `reference/*.md`,
  `roles/butler.md`, and `docs/*.md` still carry residual hits until task 06.
- Read `commands/help.md`'s command table — confirm the `Tier` column header and its sixteen cells
  are gone and the table still renders as a valid markdown table (same column count on every row).
- Read `README.md:304-323`'s rewritten heading and prose — confirm the tool-allowlist-vs-model-name
  split from step 12 is stated as two separate sentences, not one that still conflates them.
