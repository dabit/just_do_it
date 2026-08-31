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

First, get the code. Everything below assumes this path — substitute your own if it differs:

```sh
git clone <this-repo-url> ~/git/just_do_it
```

Claude Code and Codex both read the plugin format directly from that checkout, so there is nothing
to build. OpenCode has no plugin loader and gets a synced copy instead.

| Harness | You type | Prefix |
|---|---|---|
| Claude Code | `/jdi:prep`, `/jdi:yolo`, … | supplied by the plugin name |
| Codex | the JDI commands, discoverable with `/` in the TUI | supplied by Codex |
| OpenCode | `/jdi-prep`, `/jdi-yolo`, … | added by the sync script |

### Claude Code

From a terminal:

```sh
claude plugin marketplace add ~/git/just_do_it
claude plugin install jdi@just-do-it
```

Or from inside a session, with `/plugin marketplace add ~/git/just_do_it` then
`/plugin install jdi@just-do-it`. A git URL works in place of the path.

Verify: `claude plugin list` shows `jdi@just-do-it` enabled, and `/jdi:help` prints the command
table. The seven roles register as spawnable agents — `jdi:researcher`, `jdi:planner`, and so on.

### Codex

Codex consumes the same plugin manifest:

```sh
codex plugin marketplace add ~/git/just_do_it
codex plugin add jdi@just-do-it
```

Verify: `codex plugin list` shows `jdi@just-do-it` installed and enabled. Type `/` in the Codex TUI
to see the commands it registered — Codex owns the naming, so check the list rather than assuming a
prefix.

Codex has no subagents, so the roles are adopted inline instead of spawned. That path is designed
for, not tolerated: every phase still runs, sharing one context window. See
`reference/delegation.md`.

### OpenCode

OpenCode has no plugin loader, so its copy is synced from this repository:

```sh
~/git/just_do_it/bin/sync-opencode.sh
```

This writes `~/.config/opencode/command/jdi-*.md` and `~/.config/opencode/agent/jdi-*.md`. The
`jdi-` prefix is added by the script because OpenCode has no plugin namespace of its own —
without it, `next.md` would claim `/next`. Set `OPENCODE_CONFIG_DIR` if your config lives
elsewhere.

Verify: 16 files in `~/.config/opencode/command/` and 7 in `~/.config/opencode/agent/`, and
`/jdi-help` in a session.

The sync **copies** — it does not link, and it never modifies this repository. Re-run it after
every `git pull`.

### Anything else

See `AGENTS.md`. JDI is markdown with no harness machinery in the command bodies: point any agent at
`commands/<name>.md`, tell it to follow the file, and substitute your request for `$ARGUMENTS`.

### Updating

All three install a **copy**, so `git pull` here does not update them:

```sh
cd ~/git/just_do_it && git pull

claude plugin update jdi@just-do-it     # Claude Code
codex plugin add jdi@just-do-it         # Codex — re-adding refreshes the snapshot
./bin/sync-opencode.sh                  # OpenCode
```

**`claude plugin update` compares versions, not content.** It reports "already at the latest
version" and does nothing if `version` in `.claude-plugin/plugin.json` has not moved — so editing a
JDI prompt and pulling is not enough. Either bump the version in `plugin.json` **and**
`marketplace.json` (they must match), or reinstall:

```sh
claude plugin uninstall jdi@just-do-it && claude plugin install jdi@just-do-it
```

This matters most when you act on a `/jdi:feedback` prompt fix: unlike a workflow kept in a repo's
own `.claude/`, an installed plugin's prompts are a cached copy, and the edit does not take effect
until you reinstall. The OpenCode sync has no such gate — it copies every time.

## Set up a repository

```sh
/jdi:init      # asks about the tracker, the plan store, and the docs folder
```

This writes `.jdi/config.yml`. JDI works without it — it just asks as it goes — but a repo you use
more than once deserves the file. See `reference/config.md` for the schema and
`jdi.config.example.yml` for a filled-in starting point.

`/jdi:init` asks about the tracker, where plans should live, and where architecture docs live. It
proposes answers from the repo's own `AGENTS.md`, `CLAUDE.md`, and directory layout rather than
starting from zero, and it checks that the plans folder is not gitignored — a trap that loses plans
silently.

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
critiques the last thing an agent produced — on demand, never as an automatic gate. `/jdi:replan`
and `/jdi:reresearch` throw a phase away and redo it.

Command names above use the Claude Code prefix; substitute your harness's from the table in
**Install**.

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
