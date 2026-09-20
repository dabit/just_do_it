status: pending
# 06 — The two architecture docs, the citation sweep, and the vocabulary guard

Depends on: 05

This task genuinely needs everything before it, not just its immediate predecessor: the citation
sweep (step 3 below) needs `reference/config.md`'s and `README.md`/`commands/help.md`/
`commands/init.md`'s **final** line numbers, which only exist once tasks 01 and 05 have landed, and
the vocabulary guard (T-H) can only go green once every prose task from 02 through 05 has actually
removed the word "tier" from its share of the repo.

## Why
`docs/harness-adapter-architecture.md` restates the same delegation ladder and the same (false)
authorization claim as `reference/delegation.md`, and `docs/config-key-lifecycle.md` still names the
old tier vocabulary as the sanctioned frontmatter exception. Left uncorrected, the repo asserts two
different positions on a security-relevant claim, and its own citations into `reference/config.md`
point at the wrong lines. This task closes both, and is where the tier-vocabulary guard finally goes
green.

## Description

**1. `docs/harness-adapter-architecture.md:243-245`** — the three-rung restatement. Rung 2 ("Use a
second non-interactive session if available") becomes a **selected** path driven by
`models.<role>.harness`, not only a fallback. Keep it a three-line summary that defers to
`reference/delegation.md` as the owner (`:241` already says the Butler uses that file's order).

**2. `docs/harness-adapter-architecture.md:256-257`** — the same false authorization claim as
`reference/delegation.md:58-60`, corrected in task 02. Current text: "Delegation does not widen
authorization. Subagents inherit the active sandbox and approval environment, and external
mutations remain governed by the active command and Butler rules." **This is the same false claim
task 02 corrected in `reference/delegation.md`, in the same words as the plan's corrected
paragraph**, reproduced here so this task does not have to reconstruct it from a diff:

> Delegation never grants additional authority, and JDI never composes any. An in-harness subagent
> and an inline adoption run inside this session's own sandbox and approval policy. **A separately
> spawned CLI does not** — it is another process that resolves its own sandbox, approval policy and
> credentials from its own configuration, which may be broader or narrower than this session's. JDI
> composes no authority-affecting flag and translates none between kinds: every flag a spawned CLI
> receives is a literal value the user wrote in `harnesses.<kind>.args`, passed through verbatim and
> **printed back before the spawn**. Any external mutation must still be allowed by the active
> command and the Butler's rules.

Amend `docs/harness-adapter-architecture.md:256-257` to this same invariant (word it to fit this
document's surrounding prose if needed; the content must match). **This must land in this task, not
be deferred** — until it does, the two documents disagree on a security-relevant claim, which is
exactly the state task 02 left them in on purpose (see task 02's own cross-reference note).

**3. `skills/run/SKILL.md` — considered, deliberately unchanged.**
`tests/test_codex_plugin.py:165-170` pins "Preserve the active sandbox, approval policy, and
authorization boundaries" and "Neither dispatch nor delegation grants additional authority." Both
remain true as written: the dispatcher runs in-session, and JDI still *grants* nothing — a spawned
CLI's authority comes from its own configuration and from flags the user wrote, not from JDI
widening anything. Make no edit here; state the decision and its reason in the commit body so it
reads as considered rather than missed.

**3a. `docs/harness-adapter-architecture.md:168` — a third site the plan does not name; read it and
decide, do not skip it because it is uncatalogued.** The dispatcher's numbered guarantee list ends
"9. Preserves the active environment's authorization and sandbox boundaries." This is the same
family of claim as `skills/run/SKILL.md`'s, describing the in-session dispatcher, not a spawned CLI
— so the same reasoning in step 3 above plausibly applies (true as written, left alone). But this is
this task's judgment call to make, not an inherited conclusion: read `:155-172` in context, and
either leave it with the same "considered, unchanged" note in the commit body, or amend it if
reading it in context shows otherwise. Do not leave it silently unaddressed.

**4. `docs/config-key-lifecycle.md` §5 — amend, without renumbering.** `:293-299` currently reads
(in part): "Concrete model names and tool allowlists live only in YAML frontmatter … The `models`
block … is the sanctioned exception, and note its shape: it maps JDI's own vocabulary
(`deep`/`standard`/`fast`) onto the harness's, so the bodies still name only tiers." Every clause of
that is inverted by this change. Rewrite it to say: a **tool allowlist** is a harness fact and
belongs in frontmatter; a **model name is not** — it is a fact about the user's account and harness
pairing, has no single right answer, and the `models` block is where it lives. Keep §5's
five-question test (`:305-320`) and show a per-role `models` key still earns its place under it: two
repos answer differently; no repo states it in prose humans read; it is not a harness fact in the
frontmatter sense; "unset" is a safe default needing nothing from the environment; the ladder was
written before the feature. **Do not renumber or restructure any section heading** —
`tests/test_versions.py:59-97` pins `"## 6. Release mechanics"` (via `jdi_files.section`, which
raises on absence) and five literals including `"Nine files are the **floor**"` and `"The nine
mandatory files:"`; none of those may move.

**5. The citation-rot sweep — wider than one line.** Task 01 grew `reference/config.md`'s schema
block, so **every citation with a line number at or above 104 into that file has moved**. Run:

```
grep -n "reference/config.md:" docs/config-key-lifecycle.md
```

and re-read every hit. Known sites from the plan: `:71-77` (the three-edit paragraph, citing
`:17-118`, `:42-55`, `:133-147`, `:139`, `:149-170`, `:153-160`), `:80-82`, `:276`, `:285`, `:297`,
`:311`. Also fix, by hand, because the grep above will not surface them:
- `docs/config-key-lifecycle.md:295` cites `README.md:322-323` for a sentence task 05 rewrote.
- `docs/config-key-lifecycle.md:107-110` cites `README.md:185`, `:192-198`, `:200-214`.
- `docs/config-key-lifecycle.md:100-105` cites `commands/help.md:9-12`, `:25`, `:30`, `:82-89`.
- `docs/config-key-lifecycle.md:86-94` cites `commands/init.md:2`, `:54-55`, `:100`.
- `tests/jdi_files.py:182-184`'s `schema_block()` docstring names `## Example tier mappings` and
  describes "three side-by-side `models:` columns." The heading was renamed in task 01 and the
  fence's shape changed. The docstring is the *reason* the helper is scoped the way it is, so a
  stale one invites someone to unscope it later — fix it.

**6. Tests, same commit — T-H, the vocabulary guard goes green here.** Add a new test class to
`tests/test_enumerations.py` (widen the module docstring by a line — the module's remit is
"consistencies that are maintained by hand and notice nothing on their own," and this is one). Scan
a fixed file list, case-insensitive `\btiers?\b`, assert no hits, reporting `path:line` for each:
- included: `commands/*.md`, `agents/*.md`, `reference/*.md`, `roles/*.md`, `docs/*.md`,
  `README.md`, `AGENTS.md`, `bin/sync-opencode.sh`
- excluded: `CHANGELOG.md:127-128` (historical 1.0.0 note, must not be rewritten), `plans/`
  (historical records), `tests/` (this test's own docstring contains the word)

This test can only go green in this task — every prose task from 02 through 05 shrank its failure
list, and this is the one where the last occurrence disappears (from `docs/config-key-lifecycle.md`
§5 above). After this task there should be no occurrence of the word "tier" outside `CHANGELOG.md`
and `plans/`.

## Files
- `docs/harness-adapter-architecture.md`
- `docs/config-key-lifecycle.md`
- `tests/jdi_files.py`
- `tests/test_enumerations.py`

## Verification
- `python3 -m unittest discover -s tests -v` — expect **at least 52 tests, OK** (51 from task 05,
  plus T-H), 0 failures, 0 errors. **This is the first task in the plan where T-H is expected to
  pass** — if it is red, read its `path:line` failure list; every entry names a task before this one
  that missed a site.
- `grep -rniE "\btiers?\b" --include=*.md --include=*.sh . | grep -v '^\./plans/' | grep -v '^\./CHANGELOG.md' | grep -v '^\./tests/'`
  — expect **no output**. This is the same scan T-H runs; if this task is done, the grep and the
  test agree.
- `grep -c "inherit the active sandbox" docs/harness-adapter-architecture.md` — expect **0** (was
  1, task 02's verification control). Positive check: `grep -l "A separately spawned CLI does not"
  reference/delegation.md docs/harness-adapter-architecture.md` — expect **both files listed**,
  confirming the same corrected invariant now lives in both places, not just the one task 02 wrote.
  `skills/run/SKILL.md` and `docs/harness-adapter-architecture.md:168` are unaffected by this
  check — they are the two "considered, unchanged" sites from steps 3 and 3a, verified separately by
  reading the commit body's stated reasoning, not by a grep expecting a specific count.
- Re-read every citation into `reference/config.md` found by
  `grep -n "reference/config.md:" docs/config-key-lifecycle.md` from step 5 above, and confirm each
  now points at the passage it claims to — the schema block, the defaults table, or the `## Notes`
  bullets, whichever it names — in the file as it stands after task 01, not before it.
