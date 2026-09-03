---
description: "Prep several issues in parallel — one Herdr worktree, pane, and agent for each."
argument-hint: "<issue-id> [<issue-id> ...]"
---

# JDI: Herd

**Role: Butler** — JDI's orchestrator (`roles/butler.md`). **Delegates to: nothing directly** —
it starts one independent agent session per issue, and each session runs `/jdi:prep` on its own.

Prepare several issues at the same time. Each issue gets its own git worktree, its own Herdr
workspace, and its own agent, so the runs never share a branch or a working tree. The user asked
for: $ARGUMENTS

**This command sets work up and hands it off.** It does no research, no planning, no splitting,
and no code. Those happen inside the spawned agents, under `/jdi:prep`.

**It requires [Herdr](https://herdr.dev).** Step 1 proves that before anything else runs.

Follow these steps:

1. **Load the JDI config** — Read `.jdi/config.yml` at the repository root; fall back to defaults
   recorded in `AGENTS.md` / `CLAUDE.md`, then to the built-in defaults. The schema is in JDI's
   `reference/config.md` (in the JDI plugin directory — `${CLAUDE_PLUGIN_ROOT}/reference/config.md`,
   or, if that variable does not resolve, `reference/` one level up from this command file).
   The optional `herd:` block sets `kind`, `max_parallel`, `args`, and `env`. The defaults are
   `claude`, `5`, no arguments, and no environment variables.

2. **Validate Herdr — report the first failure and stop** — Run these four checks in order. Each
   one has a distinct cause and a distinct message. **Repair nothing:** never start a server, never
   install anything, and never quietly fall back to a sequential `/jdi:prep`.

   | # | Check | Command | Message when it fails |
   |---|---|---|---|
   | a | This session runs inside a Herdr pane | `test "${HERDR_ENV:-}" = 1` | Not inside Herdr. Start the session from a Herdr pane, or run `/jdi:prep` per issue. |
   | b | The CLI is on `PATH` | `command -v herdr` | `HERDR_ENV` is set but the `herdr` binary is missing. The pane's environment is broken. |
   | c | The server answers | `herdr workspace list` | The CLI cannot reach the Herdr server over its socket. Check `herdr status`. |
   | d | The agent kind is installed | `herdr agent` — read the `kinds:` line | `<kind>` is not an installed Herdr agent kind. The installed kinds are: `<list>`. |

   Check (c) must exit `0` **and** return JSON. A server error is JSON on stderr with exit `1`; a
   syntax error exits `2`. Do not treat a non-zero exit as an empty session.

   If the user named a kind in `$ARGUMENTS`, validate that one instead of the configured default.

3. **Parse the issues** — Split `$ARGUMENTS` on whitespace and commas, and drop any `--kind <x>`
   the user passed. Normalise each ID per **T1** in JDI's `reference/tracker.md`. With no issue IDs
   at all, ask which issues to herd and stop; **never invent one, and never create one here** —
   `/jdi:herd` only prepares issues that already exist. Where the count is over
   `herd.max_parallel`, name the excess, explain that each agent is a full session with a real
   token cost, and ask before you go wider.

4. **Check the repository** — Confirm this is a git work tree. Run `git fetch origin --prune`, then
   resolve `<default>` from `git.default_branch`, and detect it with
   `git symbolic-ref refs/remotes/origin/HEAD` when that is `auto`. Report the current branch and
   whether the tree is clean.

   **Uncommitted work in this checkout does not reach the new worktrees.** Say so plainly; do not
   block on it. Every worktree is created from `origin/<default>`, which is the same freshness rule
   `/jdi:prep` step 6 applies for exactly the same reason.

5. **Reserve the agent names** — Read `herdr agent list`. Build a name per issue from the
   lowercased issue ID. A Herdr agent name must match `[a-z][a-z0-9_-]{0,31}` and be unique among
   live agents. Where a name is taken, a run for that issue may already exist — say which agent
   holds it and ask, rather than start a second one beside it.

6. **Create one worktree per issue** — For issue *N*:

   ```sh
   herdr worktree create --cwd "$PWD" \
     --branch jdi-herd-scratch-<N> \
     --base origin/<default> \
     --label "<ISSUE-ID>" \
     --no-focus
   ```

   **The scratch branch name deliberately omits the issue ID.** `/jdi:prep` step 6 keeps the
   current branch when it already names the work, and creates the real feature branch otherwise. A
   scratch branch that named the issue would be adopted, and the plan would lose the descriptive
   slug from **T6**. The `--label` carries the issue ID into the Herdr UI instead.

   Read every identifier from the JSON response — `.result.worktree.path`,
   `.result.root_pane.pane_id`, `.result.workspace.workspace_id`, `.result.tab.tab_id`. **Do not
   predict an ID, and do not read one from the sidebar order.** The returned root pane is a fresh
   shell in the worktree, which is exactly what step 7 needs; do not split anything.

   **`worktree create` takes no `--env`, so `herd.env` needs one more pane.** When `herd.env` is
   empty, the worktree's own root pane is the pane for step 7. When it holds anything, create a tab
   inside the returned workspace and use *that* tab's root pane instead:

   ```sh
   herdr tab create --workspace <workspace_id> \
     --cwd <worktree_path> \
     --env KEY=VALUE [--env KEY=VALUE ...] \
     --no-focus
   ```

   Read the pane from `.result.root_pane.pane_id`. **Expand every path in a value first** — a
   value goes to the process verbatim, so a leading `~` arrives as a literal tilde and the variable
   silently points nowhere.

   When one worktree fails, record the failure, continue with the rest, and list it in step 9.
   A partial herd is useful; a silent one is not.

7. **Start one agent per worktree** — Read `herd.args` for the kind in use. It is a list of the
   agent CLI's own arguments, and it is empty by default.

   ```sh
   herdr agent start <name> --kind <kind> --pane <root_pane_id> [-- <args for kind>]
   ```

   **Pass `--` only when the list has entries.** Everything after it goes to the agent CLI
   untouched; everything before it belongs to Herdr. A kind with no entry starts with no arguments.

   **Take the list literally. Never add an argument JDI thinks is needed, and never translate one
   between kinds** — each CLI has its own spelling, and a wrong flag either fails the start or
   means something else entirely. This is where an unattended run gets its permission-bypass flag,
   if the user wants one; that is the user's decision to record, not JDI's to infer.

   **Print the arguments in the step 9 report, verbatim.** They apply to every agent in the herd at
   once. Where they turn approvals off, say so in plain words: a fresh worktree isolates the branch
   and the working tree, and nothing else — the same credentials, the same network, and the same
   machine stay in reach.

   `agent start` returns only once Herdr sees the agent ready for input. An `agent_not_ready`
   result still leaves the name usable: read the pane with `herdr agent read <name>` and report it
   as blocked at startup. **A first-run trust or permission prompt is the usual cause, unless
   `herd.args` turned approvals off.** Do not answer it.

8. **Send the prompts — do not wait** —

   ```sh
   herdr agent prompt <name> "/jdi:prep <ISSUE-ID>"
   ```

   **Never pass `--wait` here.** A wait blocks until that agent settles, which would run the herd
   one issue at a time and defeat the whole command. Send to every agent first, then read the
   states once.

   An `agent_blocked` result means the agent already sits at an approval or question dialog and
   the prompt was not sent. Report it. **Do not answer another agent's dialog on the user's
   behalf.**

9. **Report what exists now** — One row per issue: issue ID, agent name, pane ID, workspace ID,
   worktree path, and the state from `herdr agent get`. List any issue that failed in step 6, 7, or
   8, with the reason. Name the scratch branches, so the cleanup in step 11 is not a surprise.
   Print the `herd.args` and the `herd.env` keys the run passed, verbatim, or say that it passed
   none. **Print the env keys and their values** — a herd on the wrong account is otherwise
   invisible until the plans land somewhere unexpected.

10. **Offer the watch loop — ask with `AskUserQuestion`** — A spawned agent that waits at a question
    holds its turn and runs no tools, so **it cannot call for help at the moment help is needed**.
    A poll is the only signal that covers that case, and it is also the only one that catches an
    agent blocked before it ever read its prompt.

    Ask one question, through the harness's multiple-choice tool (`AskUserQuestion` in Claude
    Code):

    | Header | Question | Options |
    |---|---|---|
    | `Watch` | Watch these `<N>` agents for questions? | Every 5 minutes (Recommended) · Every 15 minutes · No, I will watch the Herdr sidebar |

    Where the harness has no such tool, or a repository hook blocks it, ask the same question
    inline in plain text as a numbered list. **Do not retry a blocked tool.**

    On either interval, invoke the harness's loop facility with this prompt:

    ```
    Check herdr agents <names>. Report any agent that is blocked, with its question text
    from `herdr agent read`. Report any agent that finished, with its plan path. Say
    nothing when nothing changed.
    ```

    On a decline, say that the Herdr sidebar shows `blocked` and `done` per pane, and print the loop line
    so the user can start it later. **Never start a loop without an answer** — it spends tokens on
    a cadence, so it is the user's call.

    Where the harness has no loop facility, say so and stop at the sidebar advice.

11. **Say how to clean up — clean nothing** — List, for each issue, the workspace ID, the worktree
    path, and the scratch branch, with the commands that remove them:
    `herdr worktree remove --workspace <id>`, then `git branch -D jdi-herd-scratch-<N>` once the
    real feature branch exists. **Remove nothing yourself unless the user asks.**

## Limits worth stating in the report

- **A blocked agent is silent.** The loop, or the sidebar, is the signal. Nothing pushes.
- **The first-run permission prompt lands before the agent reads its prompt.** With no bypass flag
  in `herd.args`, the first alert of a herd is often about permissions, not about the issue. A
  bypass flag buys that out, and pays for it with an unsupervised agent.
- **Long output can be unreadable.** Agents that draw on the terminal's alternate screen lose rows
  to Herdr's scrollback. When a larger `--lines` reveals no more, ask that agent to write its
  answer to a file and read the file instead.
- **`herd.env` changes which configuration the agents run under.** A spawned agent reads the
  settings, plugins, MCP servers, and credentials of the account or profile the environment points
  at — not this session's. **JDI itself must be installed there**, or `/jdi:prep` is not a command
  in that session and every agent stalls on an unknown input. Check that before the first herd on a
  new profile, and say plainly in the report which profile ran.
- **Setup is not supervision.** Three prepped issues still mean three sets of questions, three
  plans to read, and three worktrees to merge or discard.
