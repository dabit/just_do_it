# Changelog

## 1.0.1

**Installable at user scope or project scope.**

- **Claude Code** — documented `--scope project`, which writes a committable
  `.claude/settings.json` so JDI arrives with a clone. `examples/claude-project-settings.json` is
  the equivalent file for merging into settings that already exist.
- **OpenCode** — `bin/sync-opencode.sh` gained `--project [dir]`, alongside the existing (default)
  `--global`. Project mode writes `.opencode/{command,agent}/`, copies the reference files and roles
  into `.opencode/jdi/`, and rewrites every path **repo-relative** — the result holds no absolute
  paths and is committable. Also added `--help`.
- **Codex** — has no project scope; `codex plugin add` takes no `--scope` and records the install in
  `~/.codex/config.toml` machine-wide. Documented rather than worked around.
- Documented two things that bite when committing a project install: a directory source gets
  absolutized by the CLI (so use the `github` source for anything committed), and a marketplace
  **name** holds only one source per machine, so a local user-scope declaration blocks a git-URL
  project-scope one under the same name.

## 1.0.0

Initial extraction of the JDI workflow into a standalone, installable plugin.

- 16 commands, 7 delegatable roles, and the Butler orchestrator role.
- **Tracker-agnostic** — Linear, Jira, GitHub Issues, another, or none. `reference/tracker.md`
  defines six operations every command calls by name; each is capability-detected and skippable.
- **Plan-store-agnostic** — a folder in the repo (default) or an external service such as Obsidian
  or recuerd0. `reference/plan-store.md` carries the per-step differences, since external storage
  changes what is committable at every pause point.
- **Harness- and model-agnostic** — command and role bodies name roles and reasoning tiers
  (`deep` / `standard` / `fast`), never tools, models, or vendors. `reference/delegation.md` maps
  those onto whatever the harness offers, with inline role adoption as a first-class fallback where
  there are no subagents. Runs on Claude Code, Codex, and OpenCode.
- Per-repo configuration in `.jdi/config.yml`, written interactively by `/jdi:init`.
