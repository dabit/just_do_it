# Running JDI on a harness with no plugin loader

Claude Code and Codex install this repository as a plugin, and OpenCode gets a synced copy from
`bin/sync-opencode.sh` — see the README. This file is for everything else: any agent that can read
markdown and edit files can run JDI without any installation at all.

## The manual invocation

JDI's commands are plain markdown files with no harness-specific machinery in their bodies. To run
one, tell your agent:

> Read `<path-to-this-repo>/commands/prep.md` and follow it. Where it says `$ARGUMENTS`, use:
> "Add presence indicators to pages".

That is the whole mechanism. `$ARGUMENTS` is the only substitution, and it appears at most once per
command.

The commands are:

| Command file | What it does |
|---|---|
| `commands/init.md` | Set JDI up for a repo — writes `.jdi/config.yml` |
| `commands/help.md` | Print the workflow's command table and flow |
| `commands/prep.md` | Start, research, plan, and split in one pass |
| `commands/start.md` | Create the branch and the initial plan |
| `commands/research.md` | Find or write the architecture docs for the area |
| `commands/plan.md` | Write the implementation plan |
| `commands/split.md` | Break the plan into atomic tasks, ending with UAT |
| `commands/execute.md` | Implement the next pending task |
| `commands/done.md` | Mark the current task done and commit |
| `commands/next.md` | `done` then `execute`, in one step |
| `commands/yolo.md` | Auto-pilot every remaining task |
| `commands/status.md` | Show progress on the current plan |
| `commands/pr.md` | Condense the plan, push, open the pull request |
| `commands/feedback.md` | Critique the last output on demand |
| `commands/replan.md` | Throw the plan away and write a fresh one |
| `commands/reresearch.md` | Throw the research away and look again |

## What the commands will ask of your harness

**Delegation.** Commands say "delegate to the *Researcher* role at the *deep* tier". If your harness
has no subagents, the fallback is written into `reference/delegation.md` and it is a first-class
path: read the role file in `agents/`, announce the switch, follow it for that phase, then return
to orchestrator voice. The phases still run; they share one context window.

**Reference files.** Commands refer to `reference/config.md`, `reference/tracker.md`,
`reference/testing.md`, `reference/plan-store.md`, and `reference/delegation.md` by name, and to
`${CLAUDE_PLUGIN_ROOT}/...` for the path. That variable only resolves inside Claude Code. Anywhere
else, the files are wherever you cloned this repository — tell your agent that once, at the start,
and the paths resolve for the rest of the session.

**A tracker.** Optional. With no integration, or with `tracker.name: none` in `.jdi/config.yml`,
every tracker step is skipped and said out loud. The workflow is fully functional without one.

**Git.** Not optional. JDI creates branches, commits per task, and opens a pull request. It reads
the repo's own `CLAUDE.md` / `AGENTS.md` for the branch and commit-message conventions rather than
imposing its own.

## Adding another adapter

`bin/sync-opencode.sh` is the template. An adapter is a transformation by subtraction: the Claude
plugin format is the superset, and a target harness needs some subset of the frontmatter, a
namespace prefix if it has no plugin namespace of its own, and `${CLAUDE_PLUGIN_ROOT}` rewritten to
a path that resolves. The bodies are never touched — if an adapter needs to rewrite a body, that
body has a harness assumption in it that belongs in frontmatter or in `.jdi/config.yml` instead.

Support both scopes if the harness has them. The sync script shows the shape: `--global` points the
synced files at the JDI checkout, so a `git pull` refreshes the reference files; `--project` copies
the reference files into the target repo and rewrites every path **repo-relative**, so the result
carries no absolute paths and can be committed. That relative rewrite is the whole trick — an
adapter that bakes in `/home/you/...` produces something that works only on the machine that ran it.
