# Just Do It (JDI)

A structured, agent-driven development workflow that takes a change from idea to pull request:
**start → research → plan → split into tasks → execute → PR.**

JDI is deliberately boring about three things other workflows hardcode:

- **Your issue tracker.** Linear, Jira, GitHub Issues, something else, or none at all. Every
  tracker step is capability-detected and skippable, and "no tracker" is a first-class mode.
- **Where your plans live.** A folder in the repository (preferred — the plan is versioned and
  travels with the branch), or an external service like Obsidian, recuerd0, or Notion.
- **Which model, and which agent harness.** JDI names *roles* and *reasoning tiers*, never models
  or vendors. It runs under Claude Code, Codex, and OpenCode today, and degrades cleanly to a
  single-session workflow on any harness with no subagents at all.

## Install

### Claude Code

```sh
/plugin marketplace add ~/git/just_do_it     # or the git URL
/plugin install jdi@just-do-it
```

Commands appear as `/jdi:prep`, `/jdi:yolo`, and so on.

### Codex

Codex reads the same plugin format:

```sh
codex plugin marketplace add ~/git/just_do_it   # or the git URL
codex plugin add jdi@just-do-it
```

Codex migrates each command into a skill it invokes by description rather than by slash command.

### OpenCode

OpenCode has no plugin loader, so its copy is synced from this repository:

```sh
./bin/sync-opencode.sh
```

This writes `~/.config/opencode/command/jdi-*.md` and `~/.config/opencode/agent/jdi-*.md`,
namespaced `jdi-` because OpenCode has no plugin namespace of its own. Commands appear as
`/jdi-prep`, `/jdi-yolo`, and so on. **Re-run it after every `git pull`** — the sync copies, it does
not link. This repository is never modified by the sync.

### Anything else

See `AGENTS.md`. JDI is markdown: point any agent at `commands/<name>.md` and tell it to follow the
file.

### Updating

All three harnesses install a **copy**, so `git pull` here does not update them:

```sh
git pull
claude plugin update jdi@just-do-it     # Claude Code
codex plugin add jdi@just-do-it         # Codex — re-adding refreshes the snapshot
./bin/sync-opencode.sh                  # OpenCode
```

`claude plugin update` compares **versions**, not content: it reports "already at the latest
version" and does nothing if `version` in `.claude-plugin/plugin.json` has not moved. When editing
JDI itself, either bump the version in `plugin.json` **and** `marketplace.json` (they must match),
or reinstall:

```sh
claude plugin uninstall jdi@just-do-it && claude plugin install jdi@just-do-it
```

The OpenCode sync has no such gate — it copies every time.

## Set up a repository

```sh
/jdi:init      # asks about the tracker, the plan store, and the docs folder
```

This writes `.jdi/config.yml`. JDI works without it — it just asks as it goes — but a repo you use
more than once deserves the file. See `reference/config.md` for the schema and
`jdi.config.example.yml` for a filled-in starting point.

## Use it

```sh
/jdi:prep "Add presence indicators to pages"   # research + plan + split, in one pass
/jdi:yolo                                      # execute every task, stopping on failure
/jdi:pr                                        # condense the plan, push, open the PR
```

Or one phase at a time, stopping wherever you like:

```
/jdi:start → /jdi:research → /jdi:plan → /jdi:split → /jdi:execute ⇄ /jdi:done → /jdi:pr
```

`/jdi:help` prints the full command table. `/jdi:status` says where you are. `/jdi:feedback`
critiques the last thing an agent produced — on demand, never as an automatic gate.

## How it is put together

| Path | What it holds |
|---|---|
| `commands/` | The 16 workflow commands. Each one is written to the orchestrator |
| `agents/` | The 7 delegatable roles: Researcher, Planner, Splitter, Executor, Synthesizer, PR Writer, Feedbacker |
| `roles/butler.md` | The orchestrator role — never spawned; it is the session you are already in |
| `reference/config.md` | The `.jdi/config.yml` schema, the defaults, and example tier mappings |
| `reference/tracker.md` | The six tracker operations (T1–T6) every command calls by name |
| `reference/plan-store.md` | Repo mode vs external mode, and what changes in each |
| `reference/delegation.md` | How a role and a tier become an actual model on your harness |
| `bin/sync-opencode.sh` | The OpenCode adapter |

### Roles and tiers, not agents and models

Commands say *"delegate to the **Planner** role at the **deep** tier"*. What that becomes depends on
the harness:

- **Subagents available** → spawn one with the role file as its instructions.
- **No subagents** → adopt the role inline: read the file, announce the switch, follow it for the
  phase, then return to orchestrator voice.

Three tiers — **deep** (research, planning, implementation, review), **standard** (splitting,
condensing, PR writing), **fast** (orchestration, status, commits) — map to real models in
`.jdi/config.yml`. Leave them unset and everything runs on the session's own model. That is a
supported configuration, not a degraded one.

Concrete model names and tool allowlists live only in YAML frontmatter, which each adapter strips
or rewrites. The body of every file is shared verbatim across harnesses.

## The parts worth keeping

Most of JDI's value is not the phase diagram — it is the accumulated failure modes written into the
role definitions. A few of them:

- **The freshness gate.** Research is only valid against the commit it was read from, so every
  research and prep run fetches, compares against the default branch, and records the base commit
  in the plan. Stale-checkout citations are silently wrong, which is the worst way to be wrong.
- **The branch exists before the plan does.** Every phase then produces something committable, so
  the work can be paused or handed off at any point rather than only after planning.
- **The tracker is the durable memory.** Research findings are written back to the issue as a
  single idempotent comment, so they outlive the branch and the machine.
- **Verify, then relay.** The orchestrator re-runs the verification steps itself rather than
  trusting the executing role's report. A role that just wrote the code is the worst judge of
  whether it works.
- **Never upgrade a verification status.** When the plan is condensed at PR time, anything marked
  unverified stays marked unverified — in the summary as well as the risks section.
- **Skips are announced.** A tracker step skipped, a role adopted inline, a check not run: each is
  said out loud, once. Silent degradation is what makes a workflow untrustworthy.
