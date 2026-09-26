---
description: "Prep several issues in parallel - one Herdr worktree, pane, and agent for each."
argument-hint: "<issue-id> [<issue-id> ...] [--kind <kind>]"
---

# JDI: Herd

**Role: Butler** - JDI's orchestrator (`roles/butler.md`). **Delegates to: nothing directly.** It
starts one independent agent session per issue, and each session runs `/jdi:prep` on its own.

Prepare several issues at the same time. Each issue gets its own git worktree, its own Herdr
workspace, and its own agent, so the runs never share a branch or a working tree. The user asked
for: $ARGUMENTS

**This command sets work up and hands it off.** It does no research, no planning, no splitting,
and no code. Those happen inside the spawned agents, under `/jdi:prep`.

**It requires Herdr.** Step 2 proves that before anything else runs. Every Herdr step below is a
named operation in JDI's `reference/herdr.md` (beside `reference/config.md`), which holds the exact
commands and what to read from their results.

Follow these steps:

1. **Load the JDI config** - Read `.jdi/config.yml` at the repository root; fall back to defaults
   recorded in `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory - `${CLAUDE_PLUGIN_ROOT}/reference/config.md`,
   or, if that variable does not resolve, `reference/` one level up from this command file).
   Then, if `.jdi/config.local.yml` exists beside it, layer it over the result key by key: a mapping
   merges, a scalar or a list replaces the whole value, and a key it does not name is left alone. It
   is the personal, per-checkout override and is never committed. Say in one line which top-level
   blocks it overrides (never the values), and say so if git tracks it, because it is meant to be
   ignored.
   Everything below reads `herd`, `harnesses`, `git`, `tracker` and `plans` from it: `herd.kind`,
   `herd.max_parallel` and `herd.seed`, and the arguments and environment of the kind in use from
   `harnesses.<kind>.args` and `harnesses.<kind>.env`. The defaults are `claude`, `5`, no seeding,
   no arguments, and no environment variables.

2. **Validate Herdr - report the first failure and stop** - First, perform **H1** from
   `reference/herdr.md`. Then perform **H2** for `herd.kind`, or for the kind a `--kind <kind>` in
   `$ARGUMENTS` names, which wins over the configured one. For a herd, H2 checks that kind directly,
   and it accepts only a kind that has a row in H9's invocation table.

   **Validate, never repair.** The first failure stops the run with its reason: the check that
   failed and what came back. Never start a server, never install anything, never change a Herdr
   setting, and **never fall back to a sequential `/jdi:prep`**. A herd that quietly became one
   prep looks exactly like a herd that worked, so `/jdi:herd` has no fallback at all.

   `delegation.transport` is irrelevant here. It decides how a delegated role runs inside one
   command; a herd needs Herdr under every value, including `native`.

3. **Parse the issues** - Split `$ARGUMENTS` on whitespace and commas, and drop any `--kind <x>`
   the user passed. Normalize each ID per **T1** in JDI's `reference/tracker.md`. With no issue IDs
   at all, ask which issues to herd and stop; **never invent one, and never create one here**.
   `/jdi:herd` only prepares issues that already exist.

   Then perform **T2** from `reference/tracker.md` for each issue to read its title. Step 5 builds
   the agent name from it, and step 6 labels the workspace with it. A title read back also proves
   the issue exists. With no tracker integration, or when T2 cannot read a title for an issue, the
   herd falls back to the old name `jdi-herd-<issue>` for that issue and says so once, naming the
   issues it fell back for. That name is `jdi-herd-` plus the normalized issue ID, lowercased, with
   every character outside `[a-z0-9-]` replaced by `-`.

   Where the count is over `herd.max_parallel`, name the excess, explain that each agent is a full
   session with a real token cost, and ask before you go wider.

4. **Check the repository** - Confirm this is a git work tree. Run `git fetch origin --prune`, then
   resolve `<default>` from `git.default_branch`, and detect it with
   `git symbolic-ref refs/remotes/origin/HEAD` when that is `auto`. Report the current branch and
   whether the tree is clean.

   **Uncommitted work in this checkout does not reach the new worktrees.** Say so plainly; do not
   block on it. Every worktree is created from `origin/<default>`, which is the same freshness rule
   `/jdi:prep` step 6 applies for exactly the same reason. **Nothing gitignored reaches them
   either.** `herd.seed` in step 7 is what puts it back.

5. **Reserve the agent names - one name per issue** - Build **one name per issue**. It is the Herdr
   agent name, the tab label, and, in step 6, the worktree's folder name, so the folder shows the
   issue on disk. It is chosen once, here, and printed in the step 10 report. Nothing later depends
   on building it again.

   - The name is `<slug>-<suffix>`, the same kind of readable name `/jdi:prep` gives a plan. The
     herd cannot reuse prep's name, because it names the agent before prep runs, so it builds one
     from the step-3 title.
   - `<slug>` is a short kebab-case slug of the title's key words, built the way **T6** in
     `reference/tracker.md` builds a branch slug: lowercase, only `[a-z0-9-]`, a few words. Drop
     filler words, and drop prefixes that carry no meaning on their own. When no word survives,
     the name is the suffix alone.
   - `<suffix>` is the issue's short identity, so the name always shows the issue. Use the short ID
     the repo's own convention prescribes, when its `CLAUDE.md` / `AGENTS.md` or the comments in
     `.jdi/config.yml` state one (for example, the first eight characters of a UUID). Otherwise use
     the normalized issue ID, lowercased, with every character outside `[a-z0-9-]` replaced by `-`:
     `eng-1234`, `4`.
   - The whole name must match Herdr's `[a-z][a-z0-9_-]{0,31}`, so 32 characters at most. When it
     is too long, drop words from the end of the slug and keep the suffix whole. Cut the suffix only
     when the suffix alone does not fit. When the name would not start with a letter, prefix `jdi-`.
     When two names in one herd collide, append `-2`, `-3`, and say which issue got which name.
   - The fallback name from step 3, `jdi-herd-<issue>`, follows the same length rule.
   - List the live agents (H9, *Names*). Where a live agent already holds a name, a Butler for that
     issue may already exist. Say which agent holds it and ask, rather than start a second one
     beside it.
   - JDI passes no session-name flag to the harness.

   Worked examples. A commission whose UUID starts `f4960613`, in a repo whose config prescribes
   that eight-character short ID, titled "Seam 1 - A copy lands directly below the original as a
   sibling": prep's plan slug is `copy-lands-below-original`, but with the suffix that makes 34
   characters, so the herd drops the last word and names it `copy-lands-below-f4960613`. `ENG-1234`,
   "Add presence indicators to pages", gives `add-presence-indicators-eng-1234`, exactly 32
   characters. GitHub issue `4`, "Support importing calendar events from ICS files with recurring
   rules", gives `import-calendar-events-ics-4`. A title that starts with a digit, such as "2FA for
   admins" on issue `12`, gives `jdi-2fa-admins-12`.

   Getting back to a Butler's work later does not depend on this name. The plan on the worktree's
   branch is the durable state, and a fresh session started in that worktree continues it with
   `/jdi:status` or `/jdi:yolo`.

   Take the herd ID now: the UTC start time, `yyyymmddThhmmss`. H9 puts it in every scratch branch
   name, so this run's branches never collide with the ones an earlier herd left behind.

6. **Create one worktree per issue** - For issue *N*, perform **H9** from `reference/herdr.md`
   with the step-5 name, the suffix, the herd ID, *N*, `<default>`, and the workspace label. H9
   builds the path `<worktrees dir>/<repo>/<name>`, creates the worktree on the scratch branch
   `jdi-herd-scratch-<herd-id>-<N>` from `origin/<default>`, and returns the worktree path, the
   root pane, the workspace, and the tab.

   **The workspace label is the issue title**, in full, after the short ID: for the commission in
   step 5, `f4960613 Seam 1 - A copy lands directly below the original as a sibling` (with the
   title's own punctuation, verbatim). When step 3 read no title, the label is the issue ID.

   **The scratch branch name deliberately omits the issue ID.** `/jdi:prep` step 6 keeps the
   current branch when it already names the work, and creates the real feature branch otherwise. A
   scratch branch that named the issue would be adopted, and the plan would lose the descriptive
   slug from **T6**. The workspace label and the folder name carry the issue instead.

   **An existing folder is not overwritten, and it is found by the suffix.** The slug comes from a
   title and a judgment, so a second herd for the same issue can pick different words, and the
   title can change between runs. So H9 looks for any folder whose name ends in `-<suffix>`, or is
   the old `jdi-herd-<issue>`. When it finds one, a herd has run for this issue before. Show what
   H9 reports (the folder, its branch, and whether its plan folder has uncommitted files), and ask:
   continue there, in a fresh session in that folder with `/jdi:status`, or skip this issue. Never
   create a second folder beside it, and never remove it here.

   **Read every identifier from the result.** Do not predict an ID, and do not read one from the
   sidebar order. When the worktree path Herdr returned differs from the one asked for, report both
   and use the returned one. The returned root pane is a fresh shell in the worktree, which is what
   step 8 claims; do not split anything.

   **When `harnesses.<kind>.env` is not empty, the agent needs one more pane.** H9 creates a tab
   with that environment inside the returned workspace, and that tab's root pane is the pane for
   step 8. **Expand every path in a value first.** A value goes to the process verbatim, so a
   leading `~` arrives as a literal tilde and the variable silently points nowhere.

   H9 labels the tab with the step-5 name.

   When one worktree fails, record the failure, continue with the rest, and list it in step 10.
   A partial herd is useful; a silent one is not.

7. **Seed each worktree - `herd.seed`** - A worktree is created from `origin/<default>`, so
   **nothing gitignored reaches it**: no `.env`, no installed dependency, no local database name.
   An agent that discovers this repairs it mid-run, one worktree at a time and differently in
   each. That is how two agents come to share one test database and manufacture thousands of
   failures that read as a regression in the branch under test. Seed before the agent starts.

   **Run every seed step from JDI's own shell, with the worktree as the working directory. Do not
   run it in the worktree's root pane.** Step 8 claims that pane, and it must be a fresh shell when
   it does.

   `herd.seed` has three optional keys, applied per worktree in this order:

   ```yaml
   herd:
     seed:
       copy: [<path>, ...]                # gitignored files to copy in from this checkout
       set:  { <path>: { KEY: VALUE } }   # per-worktree values inside a dotenv-style file
       setup: [<command>, ...]            # commands that finish the worktree, cwd = its root
   ```

   - `copy`: each path is relative to the repository root and is copied from *this* checkout into
     the same place in the worktree. A path absent here is skipped with a note, never an error: not
     every machine holds every local file.
   - `set`: for each named file, replace the value of each key, appending the line where the key is
     absent. It runs after `copy`, so it edits the copy and never your original.
   - `setup`: commands that finish the worktree, run in order once it holds the files `copy` and
     `set` put there. **A non-zero exit disqualifies that worktree**: the remaining setup commands
     are skipped, **step 8 never starts its agent**, and step 10 reports the issue as failed with
     the command and its exit status. The other issues in the herd continue. A partial herd is
     useful, and an agent turned loose in a half-built worktree is not: it flounders on a broken
     dependency or a missing database and reports the wreckage as a finding about the branch.

   **Placeholders** are substituted in every `set` value and every `setup` command:

   | Placeholder | Expands to |
   |---|---|
   | `{{n}}` | the worktree's 1-based index in this herd |
   | `{{issue}}` | the issue ID, e.g. `JUT-3073` |
   | `{{issue_lower}}` | the same, lowercased, e.g. `jut-3073` |
   | `{{worktree}}` | absolute path to the new worktree |
   | `{{repo_root}}` | absolute path to this checkout |

   **This is where a shared resource becomes a per-worktree one.** Anything concurrent runs would
   otherwise collide on (a test database, a port, a cache directory, a container name) belongs in
   `set` or `setup` with `{{n}}` in it:

   ```yaml
   herd:
     seed:
       copy:
         - apps/core/api/.env
         - apps/core/frontend/.env
       set:
         apps/core/api/.env:
           TEST_DATABASE: myapp_test_herd{{n}}
       setup:
         - npm ci --prefix apps/core/frontend
         - cd apps/core/api && bin/rails db:test:prepare
   ```

   **JDI infers none of this.** It does not guess that a repo is Rails, that `.env` exists, or
   which key names a database. An absent or empty `seed` block copies nothing and runs nothing.

   Dependency installs are the slow part of a herd, and they run once per worktree. Where
   `setup` takes minutes each, say so before starting rather than after.

8. **Start one agent per worktree** - Perform **H4b** from `reference/herdr.md` with the step-5
   name, the kind from step 2, and the pane from step 6. Its arguments are `harnesses.<kind>.args`,
   verbatim, and nothing else. Pass **no model flag**: a herd Butler has no `models` key, so its CLI
   runs on its own default model.

   **Start no agent for a worktree step 7 disqualified.** A failed `setup` command means the
   tree is half-built; the issue is already recorded as failed, and starting an agent there
   turns one clear failure into a confusing one.

   **Take the list literally. Never add an argument JDI thinks is needed, and never translate one
   between kinds.** Each CLI has its own spelling, and a wrong flag either fails the start or means
   something else entirely. This is where an unattended run gets its permission-bypass flag, if the
   user wants one; that is the user's decision to record, not JDI's to infer.

   **Print the arguments before the start and in the step 10 report, verbatim.** They apply to
   every agent in the herd at once. Where they turn approvals off, say so in plain words: a fresh
   worktree isolates the branch and the working tree, and nothing else. The same credentials, the
   same network, and the same machine stay in reach.

   H4b returns only once Herdr sees the agent ready for input. An `agent_not_ready` result still
   leaves the name usable: inspect the pane per H9 *Watch* and report it as blocked at startup.
   **A first-run trust or permission prompt is the usual cause, unless `harnesses.<kind>.args`
   turned approvals off.** Do not answer it.

9. **Send the prompts - do not wait** - Send each Butler its command, the invocation from H9's
   invocation table for the kind in use, with the issue ID filled in, as H9 says.

   **Never pass `--wait` here.** A wait blocks until that agent settles, which would run the herd
   one issue at a time and defeat the whole command. Send to every agent first, then read the
   states once.

   An `agent_blocked` result means the agent already sits at an approval or question dialog and
   the prompt was not sent. Report it. **Do not answer another agent's dialog on the user's
   behalf.**

10. **Report what exists now** - One row per issue: issue ID, agent name, pane ID, workspace ID,
    and the state per H9 *Watch*. List any issue that failed in step 6, 7, 8 or 9, with the
    reason. For a seed failure, name the command and its exit status.

    Under a **Worktree** heading, list each issue's worktree path and scratch branch, so the
    cleanup in step 11 is not a surprise. Say that `/jdi:prep` renames the branch to one naming the
    issue, so `git worktree list` finds it later.

    Print `harnesses.<kind>.args` and the `harnesses.<kind>.env` keys the run passed, verbatim, or
    say that it passed none. **Print the env keys and their values**: a herd on the wrong account is
    otherwise invisible until the plans land somewhere unexpected. **Say what `herd.seed` copied,
    set and ran, or that it seeded nothing.** An unseeded herd looks identical until an agent trips
    over it.

    Say that the Herdr sidebar shows `blocked` and `done` per pane, and that it is how to follow the
    herd from here: JDI starts no poll. Close the report with H9's reattach command, which
    opens an existing worktree as a workspace again after a restart.

11. **Say how to clean up - clean nothing** - List, for each issue, the workspace ID, the worktree
    path, and the scratch branch, with the commands that remove them, per H9's *Cleanup*: the
    worktree removal by workspace, then `git branch -D jdi-herd-scratch-<herd-id>-<N>` once the
    real feature branch exists. A worktree that `herd.seed` wrote into is dirty, so its removal
    needs the force option; say that rather than let the plain command fail.

    **Guard the plan.** A herd worktree usually holds an uncommitted plan, because `/jdi:prep`
    commits only when asked. Before any worktree is removed, check it for
    **uncommitted plan files** as H9's *Cleanup* says. When the plan folder has any, say so, name
    the files, and offer the `docs: Add <slug> plan` commit in that worktree first. **Never remove
    such a worktree without the user's explicit yes**, because a forced removal deletes the plan.

    **Remove nothing yourself unless the user asks.**

## Limits worth stating in the report

- **A blocked agent is silent.** The Herdr sidebar is the signal. Nothing pushes, and nothing
  polls.
- **The first-run permission prompt lands before the agent reads its prompt.** With no bypass flag
  in `harnesses.<kind>.args`, the first alert of a herd is often about permissions, not about the
  issue. A bypass flag buys that out, and pays for it with an unsupervised agent.
- **`harnesses.<kind>.env` changes which configuration the agents run under.** A spawned agent
  reads the settings, plugins, MCP servers, and credentials of the account or profile the
  environment points at, not this session's. **JDI itself must be installed there**, or the prep
  command is not a command in that session and every agent stalls on an unknown input. Check that
  before the first herd on a new profile, and say plainly in the report which profile ran.
- **An unseeded worktree is not a clean worktree.** It holds no gitignored file: no `.env`, no
  installed dependency, no local database name. With `herd.seed` empty, every agent finds that
  out on its own, and two of them can quietly settle on the same shared resource; a shared test
  database yields thousands of failures that look like a regression in the branch. Report what
  was seeded. A `setup` command that fails takes its issue out of the herd rather than handing
  an agent a half-built tree.
- **Setup is not supervision.** Three prepped issues still mean three sets of questions, three
  plans to read, and three worktrees to merge or discard.
