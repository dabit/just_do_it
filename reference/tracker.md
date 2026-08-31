# Tracker operations

JDI talks to an issue tracker through six named operations. Commands call them **by name**; this
file says what each one means and how to carry it out against whichever tracker
`.jdi/config.yml` records.

## The universal rules

1. **`tracker.name: none` skips every operation.** Say so out loud once ("no tracker configured —
   skipping the issue update") and carry on. A missing tracker must never block, fail, or stall a
   command.
2. **A tracker with no available integration also skips.** If the configured tracker has no MCP
   server, CLI, or API reachable in this session, tell the user, then continue with whatever
   metadata they provided by hand. Warn; never fail.
3. **Never hardcode a status ID or name.** Always list the tracker's states for the relevant
   team/project and resolve the one you want by role. Workflow states differ per team.
4. **Never create an issue without explicit user confirmation.**
5. **Never claim a tracker write succeeded without seeing it succeed.** "No error" is not proof;
   read the value back where the tracker offers a read.

## T1 — Identify the issue

Establish which issue, if any, this work belongs to.

- If the user supplied an issue ID or URL, use it.
- Otherwise, if a tracker is configured, ask whether they want to give an existing issue, create a
  new one now, or continue without one.
- Record the result in the plan's metadata block as `Issue:` and `Issue URL:`, or `Issue: none`.

## T2 — Fetch issue context

Read the issue's title, description, acceptance criteria, and any assigned project/team, and use it
to enrich the task description. Skip if there is no issue or no integration.

| Tracker | How |
|---|---|
| Linear | `get_issue` via the Linear MCP server |
| Jira | the Atlassian MCP server's issue read, or `jira issue view` |
| GitHub Issues | the GitHub MCP server, or `gh issue view <n> --json title,body,labels` |
| other | that tracker's MCP tools; if none, ask the user to paste the issue text |

## T3 — Create an issue

Only on explicit confirmation. Ask for the project/board, defaulting to `tracker.project` from the
config, and the team, defaulting to `tracker.team`. Create it only if the tracker exposes issue
creation in this session; if it does not, say so and ask whether to continue without an issue or to
have the user create one and hand back the ID.

Before setting labels or fields on a tracker you have not written to this session, **list the
available values first** — never invent a label, status, or field value.

## T4 — Transition the issue's status

Move the issue to a target workflow role: **In Progress** when implementation begins, **In Review**
when the pull request opens.

- Resolve the destination state by listing the team's workflow states and picking the one whose
  role matches (`started` for In Progress, the review-type started state for In Review). Do not
  hardcode a name or an ID.
- If the issue is already at or past the target state, leave it alone.
- Skip silently-but-audibly when there is no issue.

| Tracker | How |
|---|---|
| Linear | `list_issue_statuses(<team>)` then `save_issue` |
| Jira | list transitions for the issue, then apply the matching transition |
| GitHub Issues | project-board column move, or a status label; if the repo uses neither, note that the tracker has no In Progress/In Review concept and skip |
| other | the equivalent read-states-then-set call |

## T5 — Upsert the research-findings comment

The issue is JDI's durable memory: the local plan folder is not guaranteed to outlive this machine
or this branch.

1. Compose a comment whose **first line is exactly** `tracker.research_comment_heading` from the
   config (default `## 🔬 Research findings (JDI)`), followed by the research findings: relevant
   past plans, existing and related docs, key files for the area, compatibility and gotcha notes,
   and a link to any architecture doc written during research.
2. **Idempotent write:** list the issue's existing comments first. If one already begins with that
   heading, **update that comment**. Otherwise create a new one. Re-running research refreshes the
   same record instead of stacking duplicates.
3. If the tracker is unreachable, warn the user and note that the findings still live in the plan.

## T6 — Suggest a branch name

Ask the tracker for its preferred branch name for the issue when it offers one (Linear's
`gitBranchName`, GitHub's "create a branch" suggestion). Otherwise build one from the issue key and
a kebab-case slug of the title: `<id-prefix>-<number>-<slug>`.

Apply the repo's own branch convention on top — the prefix in `git.branch_prefix`, or whatever the
repo's `CLAUDE.md` prescribes (`feat/`, `bug/`, `chore/`, …). With no issue, build the name from the
plan slug alone.
