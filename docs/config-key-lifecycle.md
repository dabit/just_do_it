# Adding a configuration key

`.jdi/config.yml` started as pure description — which tracker, where the plans go, which models.
With `split.pieces` (commit `c83963b`, version 1.0.2) it grew a second key that *changes what JDI
does*, and adding it touched seventeen files. Once is an incident; twice is a pattern, and a
pattern deserves a written procedure.

This document is that procedure: the resolution rules a new key inherits, the files it must touch,
where its behaviour is allowed to live, the shape a graceful-degradation rule takes, the test for
whether something belongs in the config at all, and how the result ships.

It is written for the contributor and for the agent doing the work on their behalf. Everything in
it is cited to a file and a line, because the whole point is that the sites are scattered and easy
to half-finish.

## 1. Resolution order and the never-invent rule

Every command reads the configuration **first, before doing anything else**
(`reference/config.md:3`). Resolution is three levels, in order (`reference/config.md:7-12`):

1. `.jdi/config.yml` at the root of the repository being worked in — the source of truth.
2. If it does not exist, defaults recorded in the repo's own `AGENTS.md` or `CLAUDE.md`.
3. If neither exists, the built-in defaults, plus **asking the user** only the one or two questions
   the current command actually depends on. A missing config file never blocks the workflow;
   `/jdi:init` is offered at the end instead.

Then the rule every new key inherits, at `reference/config.md:14-15`:

> A command must never invent a tracker, a project, or a plans location that the config does not
> record and the user has not confirmed.

**Design your key so that "unset" is a real answer, not a gap to be filled by guessing.** That is
why every behavioural key needs a default that is safe with no configuration at all, and why the
default is the mode that requires the least of the environment. `split.pieces: commits` is the
model — it is the default *and* the only mode that needs no tracker (`reference/config.md:44-46`).
An existing repo with no such key behaves exactly as it did before the key existed.

Level 2 is worth dwelling on. It exists because a repo often already states, in prose, what the
key wants to know. A new key that has no plausible level-2 source is a hint that it is
JDI-internal machinery rather than a fact about this repository — see section 5.

The load itself is repeated in twelve of the sixteen command files as a step 0 that begins
**"Load the JDI config"** — `commands/done.md:14`, `commands/execute.md:14`,
`commands/feedback.md:18`, `commands/next.md:13`, `commands/plan.md:14`, `commands/pr.md:15`,
`commands/research.md:14`, `commands/split.md:14`, `commands/start.md:14`,
`commands/status.md:14`, `commands/yolo.md:13`, and `commands/prep.md:19` (numbered 1 there rather
than 0). The four exceptions each have a reason: `/jdi:init` reads `reference/config.md` directly
before asking anything (`commands/init.md:13-15`), `/jdi:help` prints rather than acts, and
`commands/replan.md:16` and `commands/reresearch.md:16` delegate to their sibling command's step 0
by name.

## 2. The mandatory file set

Nine files are the **floor** for any new key. Below the floor, the key is half-added: it will be
documented but never asked about, or asked about but never shipped.

| File | What it contributes |
|---|---|
| `reference/config.md` | The schema, the default, and the invariant — **three separate edits** |
| `jdi.config.example.yml` | The filled-in example a human copies |
| `commands/init.md` | The question that puts the key in a real repo — **two edits** |
| `commands/help.md` | What a user learns without reading the reference — **three edits** |
| `README.md` | The public description — **two enumerations plus a section** |
| `CHANGELOG.md` | The release note |
| `.claude-plugin/plugin.json` | The version |
| `.codex-plugin/plugin.json` | The version, which must match the Claude manifest |
| `.claude-plugin/marketplace.json` | The version, which must match both manifests |

### The multi-site ones — where a change gets half-done

**`reference/config.md` takes three edits, not one.** The YAML block under `## Schema`
(`reference/config.md:17-118`; `split:` occupies `:42-55`), a row in the
`## Defaults when nothing is configured` table (`reference/config.md:133-147`; `split.pieces` is
`:139`), and at least one **bolded invariant bullet** under `## Notes` (`:149-170`;
`split.pieces` earns two, at `:153-156` and `:157-160`). The schema block alone is the most common
half-finish: the key is documented, and then a command asks "what is the default?" and the table
does not say.

**`jdi.config.example.yml` deliberately disagrees with the schema.** The schema shows the default
(`reference/config.md:55` — `pieces: commits`); the example shows a **non-default** value
(`jdi.config.example.yml:27-33` — `pieces: subtickets`). This is intentional, not drift: a reader
skimming the example should see what a *configured* repo looks like, and a value identical to the
default teaches nothing. Match the convention — set the example to the interesting value.

**`commands/init.md` takes two edits, and the second one renumbers.** The frontmatter
`description:` enumerates the questions init asks (`commands/init.md:2`), and a new numbered step
is inserted among the existing steps (`split.pieces` is step 4; `tdd` became step 5), which
renumbers every step after it.
Inserting a step **renumbers everything after it**, and steps refer to each other by number —
`commands/init.md:100` says "propose whatever step 2 found". After renumbering, grep the file for
`step [0-9]` and fix the back-references. Nothing outside `init.md` references its steps by
number today, but other command files do reference each other's: `commands/prep.md:154` says
"Follow `/jdi:split` steps 2 through 5", and `commands/replan.md:19` says "`/jdi:plan` step 2". If
you renumber a *different* command, grep `commands/` for references to it before you finish.

Note also the shape of init's question, at `commands/init.md:54-55`: the step is skipped entirely
when it cannot apply ("Skip this question entirely when the tracker is `none`") and the default is
written anyway. A question that cannot be meaningfully answered is not asked.

**`commands/help.md` takes three edits.** The instruction for the closing line that names what
this repo is configured for (`commands/help.md:9-12`), the `/jdi:init` row in the command table,
which lists init's questions a second time (`commands/help.md:25`), and a `###` prose subsection
explaining the key (`commands/help.md:82-89`). If the key changes what a specific command does,
that command's row in the same table needs a clause too — `/jdi:split`'s row gained "Mirrors them
to the tracker if `split.pieces` says so" (`commands/help.md:30`).

**`README.md` states init's questions twice.** Once in the comment on the `/jdi:init` snippet
(`README.md:185`) and once in the prose immediately below it (`README.md:192-198`), plus a `###`
section describing the key (`README.md:200-214`). The two enumerations are close together and are
easy to half-update.

**All three JSON release files carry a version, and they must match.**
`.claude-plugin/plugin.json:3`, `.codex-plugin/plugin.json:3`, and
`.claude-plugin/marketplace.json:10` are all `1.0.4` right now. The reason is in
`README.md:164-168`: `claude plugin update` compares versions rather than content, so a prompt edit
shipped without a version bump silently does nothing on Claude's installed copy. The newest
`CHANGELOG.md` heading is the fourth version authority and must carry that same release number.

### The ceiling, and how to find it

Nine is the floor now. `git show --stat c83963b` touched seventeen files before the Codex manifest
existed; beyond that release's eight-file floor, its extra nine were the ones the key's *behaviour*
reached: `reference/tracker.md` (two new operations),
`reference/plan-store.md:17-19`, `agents/splitter.md:48-51`, and the command files that now branch
on the key — `split.md`, `prep.md`, `done.md`, `next.md`, `yolo.md`, `pr.md`.

There is no list for this, because it depends on the key. **Grep the key's own name when you think
you are done.** `grep -rn "split.pieces" . ` finds every one of those sites, and it is the check
that catches the file you forgot. Do the same for your key, and read each hit — a mention that
merely names the key is fine, a mention that describes behaviour that has since changed is not.

### `commands/status.md` is deliberately out of the set

`/jdi:status` loads the config (`commands/status.md:14-17`) and then never names a key: it finds
the plan, shows the checklist, shows the next task, and reports git ground truth
(`commands/status.md:19-32`). It reports the **local** state of the plan, and deliberately not the
tracker-side state of the pieces — that exclusion was called out as out of scope in `c83963b`'s
own commit message, not overlooked.

The general rule: a command joins the set when the key changes what it *does*, not when it merely
reads the config. Adding an unnecessary mention to `status.md` costs a site that must be
maintained forever, for no behaviour.

## 3. Where behaviour goes: roles vs commands, and repeat-in-place

**Role files hold durable discipline; command files hold per-step orchestration.** A role file
(`agents/*.md`, plus `roles/butler.md`) says what a role always does, in every command that
delegates to it. A command file (`commands/*.md`) says what happens at this step of this workflow,
in order, to the orchestrator in the second person.

A new key almost always lands in the command files. It lands in a role file only when the
behaviour is the role's own discipline regardless of which command spawned it — and even then, the
role usually gets a *constraint* rather than the key. `agents/splitter.md:48-51` is the pattern:
the Splitter is told it never writes to the tracker and that the Butler adds the `Ticket:` line
afterwards, so it should write task bodies that read well in a ticket. It is told the consequence
of `split.pieces`; it never reads the key.

### A role is passed exactly the inputs its "What it receives" lists

`roles/butler.md:14-15`:

> Coordinate delegation — decide which role to hand off to, what context it needs, and what to do
> with what it returns. Pass a role exactly the inputs its *What it receives* section lists

This makes the hand-off contract explicit and auditable in both directions. **A new fact a role
needs is therefore either added to that role's "What it receives" section, or resolved by the
Butler and passed as an already-decided value.** The Researcher shows the full loop:
`agents/researcher.md:70-71` lists "The resolved JDI config (plan store path, docs path,
consumers)", and `commands/prep.md:106-107` is the Butler handing over exactly those.

Prefer the second form. Passing a *resolved* value ("write the doc to `docs/`") rather than the
key ("read `docs.path`") keeps config resolution in one place — the Butler, at step 0 — and keeps
roles usable by a harness that adopts them inline with no file access of its own.

### An instruction shared by several commands is repeated in place

This is the repo's most surprising convention, and the most expensive one to get wrong.

The **T8 "Close the piece"** instruction lives at `commands/done.md:37-41`, `commands/next.md:35-38`
and `commands/yolo.md:64-68`. The **Executor hand-off** lives at `commands/execute.md:61-76`,
`commands/next.md:53-65` and `commands/yolo.md:77-89`. Neither site says "see `done.md`". Each
states the whole instruction.

They are *not* uniformly verbatim, which matters for maintenance. `commands/next.md:53-65` and
`commands/yolo.md:77-89` are byte-identical apart from the step number and one capital letter,
while `commands/execute.md:61-76` is a longer form of the same hand-off with the inputs as a
bullet list. The three T8 sites are three different compressions of one rule: `done.md` adds "the
commit is the real record", `yolo.md` adds "not a reason to stop the loop", `next.md` trims to
"Warn, never fail." **So you cannot find every site by grepping for a shared sentence.** Grep for
the key name or the operation name (`T8`, `split.pieces`) instead.

**Why the duplication is correct.** Every command file must be independently followable by an
agent that reads only that one file. `AGENTS.md:9-19` is the guarantee: "Read
`<path-to-this-repo>/commands/prep.md` and follow it" is the entire invocation mechanism on a
harness with no plugin loader. A step that said "see `done.md` step 5" would force a second read at
the exact moment the agent is mid-workflow, and an agent that skipped it would silently drop the
step. Duplication trades maintenance cost for the property that no file has a hole in it.

**Where cross-references are still allowed**, because they are cheap and load-bearing:

- **Reference files by name.** Commands say "perform **T8** from `reference/tracker.md`" rather
  than restating the operation (`commands/done.md:37-38`). The reference file is the single
  definition; the command names the operation and its local conditions.
- **A whole command by name.** `commands/replan.md:16` and `commands/reresearch.md:16` say to follow
  their sibling command in full, then define the exceptions. The unit being reused is the entire
  file, so the reader has it open regardless.

The rule is therefore precise: **step-level instructions are repeated in place; whole files and
named operations are referenced.** When your key adds a step to more than one command, write it
out at every site — and count the sites first, so you know how many you owe.

## 4. The degradation idiom

A behavioural key describes something the environment might not support. JDI's answer is always a
**numbered ladder** in a reference file, and `reference/tracker.md`'s T7 is the model
(`reference/tracker.md:94-146`). Four properties, each with a reason:

**First rung that applies wins, and is announced once.** `reference/tracker.md:100-105`: "Take the
first rung that applies, say which one out loud, and treat the run as `commits` from there on."
The ladder is ordered cheapest-check-first, and the run adopts the fallback mode wholesale rather
than re-deciding at each later step. Announcing is the Butler's standing duty
(`roles/butler.md:23-25`): "Silent degradation is the thing that makes a workflow untrustworthy."

**Degrade DOWN, never UP.** `reference/tracker.md:107-109`: a configured `tasks` the tracker
cannot express falls back to `commits`; it never becomes `subtickets`. The reasoning is stated,
and it generalises — "Silently creating issues the user did not ask for is a worse failure than
mirroring nothing." When you write your ladder, name which direction is the destructive one and
close it explicitly.

**Silent when the feature is off.** `commands/split.md:96-97`, for `commits` mode:

> **`commits`** — nothing to do. The task files are the pieces, and each one becomes a commit when
> it is marked done. Say nothing; there is nothing to skip.

This is the exception to "announce every skip", and the distinction is sharp. A *degradation* — a
configured mode the environment could not honour — is announced, because the user asked for
something and did not get it. A feature that is **off by default** produces no announcement,
because nothing was skipped. Get this backwards and every default-configuration run is polluted
with notices about features nobody enabled. `reference/tracker.md:96-98` states the same boundary
from the operation's side.

**Capability is PROVEN, not assumed.** Universal rule 5, `reference/tracker.md:18-19`: "Never claim
a tracker write succeeded without seeing it succeed. 'No error' is not proof; read the value back
where the tracker offers a read." Rule 3 (`:15-16`) is the same instinct applied to inputs — list
the tracker's states and resolve by role, never hardcode an ID — and `reference/tracker.md:145-146`
repeats it for T7 specifically. If your key makes JDI depend on a capability, the ladder must say
how that capability is *detected*, and detection must be an observation, not an absence of error.

### When a ladder earns its own reference file

Inline the ladder in the command when it is short and has exactly one caller — the way
`commands/split.md:93-108` carries the local reading of `split.pieces`. Promote it to
`reference/*.md` when **several commands must perform the same operation**, which is precisely
when the repeat-in-place rule would otherwise force you to copy the whole ladder N times. T7 and
T8 earned their place because five commands invoke them by name: `split.md` and `prep.md` call T7,
`done.md`, `next.md` and `yolo.md` call T8 (`CHANGELOG.md:87-89`).

**A new reference file is not free.** The OpenCode adapter handles it automatically —
`bin/sync-opencode.sh:66` copies the whole `reference/` directory, so no adapter edit is needed.
But two enumerations are hand-maintained and will not notice:

- `README.md`'s "How it is put together" table, one row per reference file.
- `AGENTS.md`'s **Reference files.** paragraph, the sentence naming the files commands refer to.

Neither states a number; each states a count by listing one. Adding a file without editing both
leaves the repo describing itself incorrectly, in the two documents a newcomer reads first — which
is exactly what `reference/testing.md` had to do when it arrived, editing both in the same
commit. Note also the README row naming "The eight tracker operations (T1–T8)"
(`README.md:289`) — a count that had to move when T7 and T8 arrived. Counts in prose are citations
too; if you add an operation, grep for the old number.

## 5. What must never become a config key

Three categories are permanently out of scope. The reasoning for each is already in the repo.

**Repo conventions the team already writes down.** `reference/config.md:168-169`:

> **Branch and commit message conventions are not configured here.** They come from the repo's own
> `CLAUDE.md` / `AGENTS.md`, which is where a team already writes them down.

Duplicating them into `.jdi/config.yml` creates a second source of truth that silently diverges
from the one humans and every other tool already read. `commands/init.md:116-120` turns this into
behaviour: init explicitly does **not** configure them, and instead offers to write them into
`CLAUDE.md` / `AGENTS.md` if they are missing. `git.branch_prefix` is the deliberate seam —
`reference/config.md:100-102`, "Leave empty to follow whatever the repo's `CLAUDE.md` prescribes" —
an override, not a home.

**Harness specifics.** `AGENTS.md:67-68`, on adapters:

> The bodies are never touched — if an adapter needs to rewrite a body, that body has a harness
> assumption in it that belongs in frontmatter or in `.jdi/config.yml` instead.

Every command and role **body** is shared verbatim across Claude Code, Codex and OpenCode. Concrete
model names and tool allowlists live only in YAML frontmatter, which each adapter strips or
rewrites (`README.md:322-323`). A key that only means something on one harness — a tool name, a
subagent flag, a vendor's API shape — belongs in frontmatter, and the adapter's job is to remove
it. The `models` block (`reference/config.md:104-111`) is the sanctioned exception, and note its
shape: it maps JDI's own vocabulary (`deep` / `standard` / `fast`) onto the harness's, so the
bodies still name only tiers.

**Anything with a right answer.** If one setting is correct for every repo, hardcode it. A config
key is a promise to support every value of it forever, in every command that reads it, on every
harness and against every tracker.

### The test

Ask, in order:

1. **Would two sensible repos answer this differently?** No → hardcode it.
2. **Does the repo already state it somewhere humans read?** Yes → read it from there
   (`reference/config.md:8-9` is the level-2 fallback that makes this work), and at most add an
   override.
3. **Is it a fact about the harness rather than the repository?** Yes → frontmatter, and the
   adapter strips it.
4. **Is there a safe default that needs nothing from the environment?** No → the key cannot honour
   the never-invent rule, and needs redesigning before it needs adding.
5. **Can you write the degradation ladder before you write the feature?** No → you do not yet know
   what the key does when the environment says no, which is most of what a key does.

Only a "yes, no, no, yes, yes" earns a key.

## 6. Release mechanics

There are **no git tags** in this repository. A release is exactly: three JSON version edits, a
CHANGELOG entry, and a commit whose subject carries the version. Nothing else.

**Three version files, and they must match.** `.claude-plugin/plugin.json:3`,
`.codex-plugin/plugin.json:3`, and `.claude-plugin/marketplace.json:10`, all `1.0.4`.
`README.md:164-168` is the why: cached plugin releases use versioned metadata, and
`claude plugin update` specifically compares versions rather than content. An unbumped release is
invisible to installed copies — a workflow change that no user receives. The newest
`CHANGELOG.md` heading is the fourth version authority and carries the same number.

**A full feature ships as a PATCH bump.** This is the observed convention, not an inference from
one data point: `c48137c` "Install at user scope or project scope" shipped as **1.0.1**, and
`c83963b` "Make the splitter's pieces configurable" shipped as **1.0.2**. Both were features; both
were patch bumps. The version tracks *shipments*, not semantic weight. Follow it — bump the patch
digit. The repo has made no minor or major bump, so there is no observed rule for one; if you are
removing a key or changing what an existing value means, decide it deliberately and say so in the
CHANGELOG rather than reading a convention out of these two data points.

**The CHANGELOG entry shape** (`CHANGELOG.md:76-97` is the configuration-key reference):

- `## <version>` heading.
- A **bold one-line headline** stating the user-visible outcome, not the mechanism —
  `CHANGELOG.md:78`: "**The splitter is configurable: pieces become subtickets, tracker tasks, or
  just commits.**"
- A blank line, then bullets. The load-bearing ones open with a **bold lead-in**:
  `CHANGELOG.md:90` — "**Degrades down, never up.**"; `CHANGELOG.md:81` — "**in addition to**".
- Every key, mode and command in backticks: `split.pieces`, `commits`, `/jdi:done`,
  `reference/tracker.md`.
- The first bullet describes the key and **says what happens to a repo that does not set it**
  (`CHANGELOG.md:82-83`: "an existing repo with no such key behaves exactly as it did"). Backward
  compatibility is stated, never left to be inferred.
- Entries are newest-first; the version's own bullets say what changed, not how it was built.

**The commit subject shape** is `feat: <Imperative sentence> (<version>)`:

```
feat: Make the splitter's pieces configurable (1.0.2)
feat: Install at user scope or project scope (1.0.1)
```

Sentence case, imperative mood, no trailing period, version in parentheses. The body of `c83963b`
is worth reading as a template: it opens with the problem in the past tense, describes the key in a
paragraph, bullets the mechanics, and closes with what was **deliberately** left out of scope. That
closing paragraph is what let a later reader know `/jdi:status` was excluded on purpose — write it.

## Checklist

Design:

- [ ] The key passes the five-question test in section 5.
- [ ] The default is safe with no configuration and needs nothing from the environment.
- [ ] The degradation ladder is written down before the feature is.
- [ ] The ladder degrades down only; the destructive direction is named and closed.

The nine mandatory files:

- [ ] `reference/config.md` — YAML block under `## Schema`.
- [ ] `reference/config.md` — row in the `## Defaults when nothing is configured` table.
- [ ] `reference/config.md` — bolded invariant bullet(s) under `## Notes`.
- [ ] `jdi.config.example.yml` — the example, set to a **non-default** value.
- [ ] `commands/init.md` — frontmatter `description:`.
- [ ] `commands/init.md` — the new numbered step, plus intra-file step back-references renumbered.
- [ ] `commands/help.md` — the closing config-state instruction.
- [ ] `commands/help.md` — the `/jdi:init` table row (and the affected command's row).
- [ ] `commands/help.md` — the `###` prose subsection.
- [ ] `README.md` — both enumerations of init's questions.
- [ ] `README.md` — the `###` section.
- [ ] `CHANGELOG.md` — headline, bullets, backward-compatibility statement.
- [ ] `.claude-plugin/plugin.json` — version.
- [ ] `.codex-plugin/plugin.json` — the **same** version.
- [ ] `.claude-plugin/marketplace.json` — the **same** version as both manifests.

Behaviour:

- [ ] `commands/prep.md:23` — the literal list of config block names includes the new block.
- [ ] Every command whose behaviour changes has the instruction **written out in place**, not
      cross-referenced. Count the sites first.
- [ ] Any role that needs the fact has it in its "What it receives" — or, preferably, is passed the
      resolved value by the Butler.
- [ ] A shared operation lives in `reference/*.md`; if that is a **new** file, `README.md:288-292`
      and `AGENTS.md:49-53` are both updated, and any prose count is corrected.
- [ ] `commands/status.md` was considered and deliberately excluded or included.

Before committing:

- [ ] `grep -rn "<your.key>" .` — read every hit; the ones you did not expect are the point.
- [ ] `grep -rn "step [0-9]" commands/` if you renumbered anything.
- [ ] Commit subject is `feat: <Imperative sentence> (<version>)`, with a body that names what was
      deliberately left out of scope.
