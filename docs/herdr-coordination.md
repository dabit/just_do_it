# Coordinating a second agent through Herdr

JDI is adding a pair programming mode: a second agent — and later a third — runs in a pane that
Herdr manages, takes a turn, and hands back. Nothing in this repository describes how that pane
gets created, what each step is allowed to refuse, or where the coordination layer will quietly
tell you something untrue. This document is that knowledge.

It is written for the contributor and for the agent doing the work on their behalf. Every claim
about Herdr below was measured on **2026-09-03** against **herdr 0.8.2**, from inside a
Herdr-managed pane, and the command that produced it is named so a reader on a later version can
re-run it and watch the answer change. Every claim about JDI is cited to a file and a line.

**The installed binary is the authority, not this document.** `herdr --skill` prints the
agent-facing spec; `herdr agent`, `herdr pane` and `herdr integration`, each run without a
subcommand, print current syntax; `herdr api schema --json` prints the wire types. Where the binary
disagrees with anything here, the binary wins and this document is stale.

Two things must not be run during discovery. **Bare `herdr` launches or attaches the TUI**, which
takes over the terminal a coordinating agent is speaking through. And **a mutating nested command
probed with no arguments executes** — `herdr workspace create` is valid with defaults. Print the
group instead: measured on 2026-09-03, `herdr workspace`, `herdr integration` and `herdr agent`
each exit 2 with a usage list and change nothing.

## 1. The precondition, and the caller context

Every control command is gated on one check:

```bash
test "${HERDR_ENV:-}" = 1
```

**This is the only reliable signal, and the reason is that everything else is ambiguous.** The
`herdr` binary being on `PATH` says the tool is installed, not that this process is inside a pane it
manages. A socket existing at `~/.config/herdr/herdr.sock` says a server is running somewhere, not
that this shell belongs to it. `HERDR_ENV` is injected by Herdr into the pane it created, so its
presence is the one fact that means *this process*. If the check fails, say so and stop: the
commands would still run, and they would operate on somebody else's focused session.

Herdr injects the caller's own position alongside it. Measured in the pane this document was
written from (home directory abbreviated as `~`):

```
HERDR_ENV=1
HERDR_WORKSPACE_ID=wQ
HERDR_TAB_ID=wQ:t1
HERDR_PANE_ID=wQ:p1
HERDR_BIN_PATH=/usr/bin/herdr
HERDR_SOCKET_PATH=~/.config/herdr/herdr.sock
```

The shape is worth reading: IDs are opaque and hierarchical, and a tab or pane ID carries its
workspace as a prefix (`wQ:t1`, `wQ:p1`). They are stable handles, not indexes — closed tab and pane
IDs are never reused, and a pane moved into another workspace gets a **new** workspace-qualified ID.
Never derive one from sidebar order or from an example; read it out of the JSON that created it.

**Always name a target: `--current`, an explicit pane ID, or a unique agent name.** This is a
correctness rule, not a style preference. A pane command with no target may resolve to the
UI-focused pane, and the focused pane belongs to whichever client currently has focus — the user's,
or another agent's. A background coordination loop that omits the target will, sooner or later,
split a pane inside the work someone else is doing. The cost of `--current` is six characters.

The same instinct applies to focus. Use `--no-focus` for background work, because the user's
attention is not a resource the coordinator owns.

## 2. The data path, hop by hop

Four hops carry one turn to a second agent and bring the answer back. Each returns JSON on stdout;
read the next hop's identifier out of it rather than predicting it. The result shapes below are from
`herdr api schema --json`, which types every response variant.

### Hop 1 — `herdr pane split`

```bash
herdr pane split --current --direction right --cwd "$PWD" --no-focus
```

Returns a `pane_info` result. **The ID you need next is `.result.pane.pane_id`.**

`--cwd "$PWD"` is not optional in practice. The second agent must start in the repository the plan
belongs to, and inheriting the caller's directory is the only way to guarantee that without
hardcoding a path. Choose the direction from geometry, not habit: `herdr pane layout --pane
"$HERDR_PANE_ID"` reports the pane's `rect`, and a wide pane splits right while a narrow or tall one
splits down. Repeated same-direction splits produce columns too narrow for a TUI to render.

What it can refuse: a pane ID that does not exist. Whether it also refuses an unusably small
geometry was not measured — the skill only says to avoid one. Server errors arrive as JSON on
stderr with exit status 1; a CLI syntax error exits 2.

### Hop 2 — `herdr agent start`

```bash
herdr agent start <name> --kind <kind> --pane <pane-id-from-hop-1>
```

Returns an `agent_started` result carrying `.result.agent` (the full agent record, including
`.result.agent.name` and `.result.agent.pane_id`) and `.result.argv`. Native arguments for the
agent itself go after `--`, never before it.

**`agent start` never creates layout.** It requires a pane that already exists and is *available* —
sitting at an interactive shell prompt, with the shell in the foreground and no command, editor or
agent running in it. There is no flag that makes it split for you. Hop 1 is not a convenience; it is
a precondition, and skipping it is the most likely way to get this wrong on the first attempt.

**A successful start returns only after Herdr has detected the expected agent in that same pane and
considers it ready for interactive input.** The call is therefore slow by design, and its return is
a meaningful readiness signal rather than a fire-and-forget. Startup defaults to a 30-second
timeout, adjustable with `--timeout`.

Names must match `[a-z][a-z0-9_-]{0,31}` and be unique among live agents. A name follows the pane's
current occupant and is **cleared when that agent exits, is released, or is replaced** — so a name
is a handle on a live process, not a durable identifier you can persist across a plan.

What it can refuse: a kind the binary does not support, a pane that is not available, and startup
that does not reach ready — the last of which is `agent_not_ready` (section 5).

### Hop 3 — `herdr agent prompt`

```bash
herdr agent prompt <name> "<text>" --wait --timeout 120000
```

Returns an `agent_prompted` result carrying `.result.agent`. The command honours the pane's live
bracketed-paste mode and sends the text followed by an encoded Enter after a short delay.

**`--wait` alone is the right call for ordinary work.** It waits for the first settled `idle`,
`done` or `blocked`. Do not restate those three with `--until`; `--until` exists for the different
job of waiting on a *specific* state, such as `herdr agent wait <name> --until blocked` to catch an
already-running agent that is about to ask for input.

What it can refuse: an agent sitting at an approval or question dialog, rejected as `agent_blocked`
**before any input is written**; and a prompt that produces no observed lifecycle change within five
seconds, returned as `agent_prompt_stalled`.

### Hop 4 — `herdr agent read`

```bash
herdr agent read <name> --source recent-unwrapped --lines 120
```

Four sources, and the choice is not cosmetic. `visible` is the rendered viewport; `recent` is recent
rendered output including soft wraps; `recent-unwrapped` joins soft wraps and is the right one for
logs and transcripts; `detection` is the plain-text bottom-buffer snapshot Herdr itself uses to
classify the agent. Use `--format ansi` only when colour is evidence.

What it can refuse — and this is the failure that matters — is *most of the answer*. See section 5.

Targets throughout hops 2 to 4 accept a unique live agent name or the pane ID currently hosting that
agent. They do **not** accept terminal IDs or bare kind labels.

## 3. The three-layer kind check

This is the section that decides whether a configured pairing partner can run at all. A kind named
in `.jdi/config.yml` must clear **three independent layers, in order**, and clearing one says
nothing about the next.

### Layer 1 — kinds the binary supports

`herdr agent` prints them. On herdr 0.8.2 there are **22**:

```
pi claude codex gemini cursor devin agy cline omp mastracode opencode
copilot kimi kiro droid amp grok hermes kilo qodercli qwen maki
```

A kind outside this list is rejected by `agent start` outright. This layer is a property of the
binary and moves with a Herdr upgrade.

### Layer 2 — installable integrations

`herdr integration` lists **17** integrations that can be installed, and `herdr integration status`
reports what is installed here and now. The two lists are not the same set. Comparing them:

- Six kinds have **no same-named integration** to install: `agy`, `amp`, `cline`, `gemini`, `kiro`,
  `maki`.
- One integration has **no same-named kind**: `antigravity-cli`. Whether it corresponds to some
  kind under a different label is not answerable from either list; do not assume a mapping.

**A snapshot, dated 2026-09-03, from `herdr integration status` on this machine.** It is evidence,
not a permanent fact — a `herdr update` or an integration install changes it, and the numbers below
should be re-measured, not quoted:

| Integration | State |
|---|---|
| `pi` | current (v8) |
| `opencode` | current (v10) |
| `claude` | **outdated (v7 < v8)** |
| `codex` | **outdated (v7 < v8)** |
| the other 13 | not installed |

**Versions are per-integration, not global.** `pi` is current at v8 while `opencode` is current at
v10. "v8" alone means nothing; only "v7 < v8, for `claude`" does.

### Layer 3 — the binary actually on `PATH`

Herdr starting an agent means Herdr running a command. Of the 22 supported kinds, **8** resolved via
`command -v` in this environment on 2026-09-03: `pi`, `claude`, `codex`, `gemini`, `omp`,
`opencode`, `copilot`, `grok`. The other 14 did not.

**Intersect all three as stated and four kinds clear them** — `pi`, `opencode`, `claude` and
`codex` — of which two carry an outdated integration. Four more (`gemini`, `omp`, `copilot`,
`grok`) are supported and on `PATH` with layer 2 either uninstalled or, for `gemini`, nonexistent.
That does not necessarily disqualify them: as the next subsection shows, a kind can be classified
by a detection manifest with no integration involved. Whether Herdr can classify any of those four
is the `herdr agent explain` question below, and it was not measured.

Two warnings about this layer. It is the layer most likely to differ between the machine a plan was
written on and the machine it runs on, so it must be checked at run time and never inherited from a
plan. And it is measured *in the environment you measure it from*: a `command -v` in the
coordinator's shell is not proof about a pane started with a different environment, and neither is
proof about a container or a remote host. Say which environment you measured.

### Why layer 2 matters — and what it actually does

The naive story is that the integration hook reports lifecycle state, so a missing hook means state
reads `unknown`. **That story is wrong for at least one kind, and getting it wrong will cost you a
day.** Herdr has *two* lifecycle sources, and which one applies depends on the kind.

`herdr agent explain <pane> --verbose` reports which one classified a live pane. Measured on
2026-09-03:

- The **OpenCode** pane reported `manifest: none`, `rule: none`, and
  `screen_detection_skip_reason: full_lifecycle_hook_authority`. Its plugin
  (`~/.config/opencode/plugins/herdr-agent-state.js`, v10) calls `pane.report_agent` and maps the
  agent's own events onto `working`, `blocked` and `idle`. The integration *is* the state, and
  Herdr does not look at the screen at all — visible in `agent list` as
  `screen_detection_skipped: true`. The reported `manifest: none` suggests there is no detection
  fallback behind the plugin, but what Herdr displays when a plugin fails to load was not
  measured.
- The **Claude Code** pane reported a detection manifest
  (`remote:~/.local/state/herdr/agent-detection/remote/claude.toml`, version `2026.08.31.1`) and a
  winning rule `osc_title_working (region=osc_title priority=1100)`, whose evidence was the
  terminal title string. State came from pattern-matching the screen.

The installed Claude integration explains why. `~/.claude/hooks/herdr-agent-state.sh` (v7) calls
exactly one socket method, `pane.report_agent_session`, reporting the session id and transcript
path; it never calls `pane.report_agent`, and `~/.claude/settings.json` registers it on
`SessionStart` only. So for `claude` the integration supplies **session identity, not lifecycle
state**.

**Therefore: an installed integration does not imply the integration reports state, and a missing
one does not imply state is unavailable.** The practical consequences differ by source:

- Where a **plugin holds authority** (OpenCode), state is as reliable as the agent's own event
  stream, and a plugin that fails to load sends no reports at all.
- Where a **detection manifest** classifies (Claude Code), state is a screen-scrape of a third-party
  TUI, driven by a remotely-updated ruleset. A redesigned prompt box, a new spinner glyph, or an
  unrecognised overlay yields `unknown` — an agent that is present but could not be classified.
  **`unknown` explicitly does not prove completion.** A coordinator that treats it as "turn over"
  will read a half-written report and hand the turn back.

For the six kinds with no integration at all, a detection manifest is the only possible source.
Whether one ships for a given kind is answerable **without a pane**, and this document originally
said otherwise. `herdr agent explain --file <any path> --agent <kind> --verbose` reports the
manifest that would classify a kind with no pane and no running agent; the pane-bound form answers
the different question of which source classified *that* pane. Measured 2026-09-03 with the
file form, **seven** kinds have a manifest here — `pi`, `opencode`, `claude`, `codex`, `gemini`,
`copilot`, `grok` — not the four an integration-only reading suggests, because a detection manifest
classifies a kind whose integration is not installed at all.

**So the check before honouring a configured kind is: in the supported list, then classifiable —
by an authoritative hook or by a detection manifest, an outdated integration being a warning and
not a refusal — then resolvable on `PATH`.** `reference/pairing.md`'s P1 rung 4 is the normative
statement of it; this section is the measurement behind it.

## 4. The five lifecycle states

`herdr api schema --json` types `AgentStatus` as exactly five values:

```
idle  working  blocked  done  unknown
```

**`idle` and `done` are the same underlying state, distinguished only by whether a human has looked
at it.** `idle` means the agent is ready for input *and* its tab has been seen in the focused Herdr
UI. `done` is that same ready state after unseen background work finished. Focusing the tab, or
targeting the pane or agent with a focus command, marks it seen.

**CLI reads do not mark a tab seen.** This is the distinction that bites, and it follows directly:
an agent driven entirely from a background loop is never seen, so its finished turns settle on
`done`, not `idle`. A coordinator that waits for `idle` alone waits forever on work it is itself
driving. **Treat `idle` and `done` as one condition — "the turn is over" — and never branch on the
difference.** `agent prompt --wait` already does exactly this; hand-rolled polling is where the bug
gets introduced.

Confirmation that `done` is derived rather than reported: `herdr pane report-agent` accepts
`--state idle|working|blocked|unknown` and **not** `done`. No integration can ever send it. Herdr
computes it from ready-plus-unseen. (Two panes were observed at `done` in this session's snapshots,
which is consistent with that account but is not a controlled transition — the panes were listed
minutes apart, not watched changing.)

**`blocked` means Herdr recognised an approval or question UI.** It is a state, not an error, and
the correct response is to look, not to type. See section 5.

**`unknown` means an agent is present that Herdr could not classify confidently.** It is not
proof of completion, not proof of failure, and not a licence to send the next prompt.

**On the pane and workspace surfaces, `unknown` is weaker still.** Enumerating all 22 panes in this
session with `herdr pane list --workspace <id>`: 11 hosted a recognised agent and 11 did not, and
**every one of the 11 agentless panes reported `agent_status: unknown`**. `herdr workspace list`
rolls the same value up to the workspace. So on those surfaces `unknown` cannot distinguish "no
agent here at all" from "an agent Herdr cannot read" — a caller must check the `agent` field, which
is absent when there is none. `herdr agent list` and `herdr agent get` do not have this ambiguity;
they only return recognised agents.

## 5. The four failure modes

Three are named error codes; the fourth is silent, which is what makes it dangerous.

A note on how solid the names are. Server errors arrive as JSON on stderr with exit status 1 —
observed live, `herdr agent get <nonexistent>` returned
`{"error":{"code":"agent_not_found","message":"agent target ... not found"}}`. But `herdr api
schema --json` types `ErrorBody.code` as a bare `string` with **no enumeration**, so the code list
below comes from `herdr --skill` and is not machine-checkable. Match on codes, and also handle
codes you have never seen.

### `agent_not_ready` — start returned, the agent did not

`agent start` normally returns only once Herdr sees the agent ready. If the agent is **blocked
during startup** — a trust prompt, a login, an update notice — the command returns `agent_not_ready`
immediately instead of waiting out the 30-second timeout.

What the caller must do: **do not retry the start, and do not treat the pane as dead.** The name is
still bound and still works for `herdr agent read` and `herdr agent send-keys`. Read the pane, find
out what it is asking, and wait for `idle` before prompting. Restarting throws away a live process
that is merely waiting.

### `agent_blocked` — the prompt refused, before writing anything

`agent prompt` rejects an agent already sitting at an approval or question dialog, and it does so
**before sending any input**. That ordering is the whole value of the error: your prompt text was
not typed into somebody's yes/no dialog and did not answer it by accident.

What the caller must do: inspect with `agent get` and `agent read`, then **ask the user**. **Never
answer another agent's approval dialog.** The dialog exists because that agent's own permission
system decided a human should decide; a coordinating agent that clicks through it has silently
removed a control the user chose to have. It is also not a decision the coordinator has the context
to make — it is being asked about an action it did not propose.

### `agent_prompt_stalled` — no lifecycle change in five seconds

A prompt sent from a non-working state must produce an observed lifecycle change within five
seconds; otherwise Herdr returns `agent_prompt_stalled` rather than waiting indefinitely.

**The subtle part is what the wait actually tracks: lifecycle STATE, not an individual turn.** If
the agent was **already working** when the prompt arrived, completion of the *active* turn can
satisfy the wait. The coordinator then sees a settled state, concludes its own prompt is done, and
reads a transcript belonging to the previous turn. This is a real source of false "turn done", and
it is not detectable from the return value.

What the caller must do: **only prompt an agent observed at `idle`, `done` or `blocked`** — check
with `agent get` first, or `herdr agent wait`. Turn-taking protocols must serialise on the
coordinator's side; `--wait` is not a mutex.

### The alternate screen — the read that silently truncates

`--lines` asks for more rows from the pane's screen and the host's scrollback. **When rows have
left the alternate screen they never enter host scrollback, so no value of `--lines` can recover
them.** The output is not an error and not marked as missing; it is simply short.

Measured on 2026-09-03, from `herdr pane list --workspace <id>` across all 22 panes in this session:
**all 11 panes hosting an agent reported `scroll.max_offset_from_bottom: 0`** — zero rows of host
scrollback — while of the 11 agentless panes, one had accumulated 54. That is consistent with agent
TUIs running on the alternate screen and ordinary shells not doing so. Both Claude Code and OpenCode
are alternate-screen TUIs, so both are subject to this.

What the caller must do: **stop treating `agent read` as a transport for anything long.** Raising
`--lines` and getting no more text is the diagnostic, not the fix. `PaneReadResult` carries a
`truncated` field worth checking, but the absence of the earlier rows is not something a flag can
undo. The fix is section 6.

## 6. Why a coordination protocol designates a shared file up front

`herdr --skill` is explicit that requesting file output is a **fallback**: try the read, and only
after it comes up short ask the agent to write its full response to a temporary file and reply with
the path. It also says, in as many words, not to request file output in the initial prompt.

**For a one-off read that advice is right, and JDI's pairing protocol is a deliberate exception to
it.** The reason is that the two situations are not the same situation:

- The skill's case is an *ad hoc* read of unknown size. Asking for a file first would add a round
  trip and a temp file to every short answer, most of which fit on screen.
- JDI's case is a *designed, repeating* hand-off whose payload size is known in advance and is
  large. `agents/executor.md:84-94` fixes the shape of a turn's report: a summary of the changes,
  verification results (test output, lint output), and under TDD the **red run** — the exact
  command, the failing output captured before the implementation existed, and the assertion line
  showing it failed for the intended reason — followed by the same command's green output. That is
  two full test transcripts plus prose, produced on **every task of every plan**.

Section 5 established that rows leaving the alternate screen are unrecoverable. So the fallback
would fire on essentially every turn, and each firing costs a wasted read, a wasted prompt, and a
round trip. Worse, the fallback only triggers when the caller *notices* the truncation — and a
truncated transcript still parses as a report. The failure is silent, and it lands precisely on the
evidence `reference/testing.md:140-147` says is the only thing making "the test was written first"
falsifiable.

**So state the exception in the protocol, and justify it there rather than contradicting the skill
by omission.** The rule: the first prompt of a paired session names an absolute path for the turn
report; every turn writes its report to that path and replies with the path only; the coordinator
reads the file. `agent read` is kept for what it is good at — seeing what a pane is doing right now,
and inspecting a `blocked` dialog.

### Prompt text must carry resolved absolute paths

JDI's command files refer to reference files as `${CLAUDE_PLUGIN_ROOT}/reference/config.md`, and
`AGENTS.md:46-50` states the constraint plainly: **that variable only resolves inside Claude Code.**
Anywhere else the files are wherever the repository was cloned, and the fix is to tell the agent the
real path once, at the start.

A Herdr pane makes this sharper than the general case, for two reasons. The prompt text is
delivered as **keystrokes into another process's TUI**, so nothing in it is expanded by a shell the
coordinator controls — `${CLAUDE_PLUGIN_ROOT}`, `$PWD` and `~` all arrive as literal characters and
are interpreted, if at all, by the receiving agent. And the receiving agent may be a different kind
entirely, with **no JDI synced at all**: `bin/sync-opencode.sh` exists precisely because OpenCode
needs its own copy, and the six kinds with no integration have no JDI installation implied by
anything.

**Every path in a prompt sent through `agent prompt` must be resolved and absolute before it is
sent** — the report path, the plan file, the task file, any role file the partner is expected to
read. Resolve them in the coordinator, where `${CLAUDE_PLUGIN_ROOT}` and `$PWD` mean something, and
send the results. This is the same instinct `docs/config-key-lifecycle.md` records for roles:
prefer passing an already-resolved value over passing the key that would have to be resolved again
somewhere with less context.

## 7. Two agents, one working tree

`agents/executor.md:96-122` is a staging discipline written for **a single writer**, and every rule
in it assumes that:

- Stage immediately after every edit (`:103`), so the index always matches intent.
- Before reporting, run `git status --short` and read **column 2**; anything but `??` there is
  unstaged work (`:106-108`).
- Never `git stash` (`:109-117`) — it breaks the index, and in a repository sharing a stash stack
  across worktrees you can pop someone else's work.
- Do not commit and do not push; the orchestrator does both (`:118-119`).

Two agents editing the same checkout break all four at once. Column 2 stops being a statement about
*your* work — the partner's unstaged edit is indistinguishable from your own. `git add <path>` may
stage a file the partner is mid-edit in. The single commit the orchestrator then makes contains both
agents' work with no way to attribute or separate it.

**The rule is single-writer: only the agent holding the turn edits files or touches the index. The
other agent reads, reviews and advises, and never runs `git add`, `git rm`, `git mv`, `git commit`
or `git stash`.** The turn is the write lock, and it is held by exactly one agent at a time. This
has to be stated in the prompt sent to the partner, because a partner running the Executor role has
`agents/executor.md`'s "stage after every edit" as a standing instruction and will follow it.

**`herdr worktree` exists, and it is the wrong answer here.** `herdr worktree create` and
`herdr worktree open` will give each agent its own checkout of its own branch, and for two agents
working *different* tasks that is exactly right. For pairing it defeats the point: driver and
navigator are working the same task on the same code, and the value is in the second pair of eyes on
the change as it is written. Separate worktrees turn the pair into two solo sessions plus a merge.
It also breaks JDI's one-commit-per-task rhythm (`AGENTS.md:55-57` — "JDI creates branches, commits
per task, and opens a pull request"), since the task's work would land as two commits on two
branches that then need reconciling. Reach for a worktree when the topology is parallel tasks, not
when it is a pair.

## 8. What is unverified

Two questions bear on the design and could not be settled from inside this session. They are
labelled by *why* they are open, because that determines who can close them.

**UNVERIFIED-EXTERNAL — the practical `herdr agent prompt` payload size before a paste degrades.**
Nothing in `herdr --skill`, in `herdr agent`'s usage output, or in `herdr api schema --json` states
a maximum, a chunking behaviour, or a documented degradation. The transport is keystrokes into a
TUI honouring bracketed-paste, so the ceiling plausibly belongs to the receiving agent's input
widget rather than to Herdr, and would differ by kind. **Do not guess it.** Settling it needs a
runtime probe: send prompts of increasing size to a live pane of each kind JDI intends to support
and read back what arrived. Until that is done, keep prompts short and put the payload in the
designated file (section 6) in *both* directions, not only the reply direction.

**UNVERIFIED-EXTERNAL — whether an outdated integration hook changes `--wait` or lifecycle
reporting.** This one is *partly* closed, and the closed part is worth recording. The installed
`claude` hook is v7 against the binary's v8. Extracting the v8 script embedded in `/usr/bin/herdr`
and diffing it against the installed v7 file shows the **bodies are identical** apart from the
version marker — identical line for line after dropping lines shorter than eight characters, which
the `strings` extraction cannot see. v8 sends the same single `pane.report_agent_session` call, and
the installed
`~/.claude/settings.json` registers it on `SessionStart` only. So the v7→v8 bump does not change
what the hook *reports*. What remains open is the installer side: whether `herdr integration install
claude` at v8 registers a different set of hook events. Answering that requires running the install,
which is mutating and out of scope here. Since section 3 established that Claude Code's lifecycle
state comes from a detection manifest and not from this hook at all, the expected impact is low —
but "expected" is not "measured", and a pairing mode should not depend on the difference until
someone installs v8 and re-runs `herdr agent explain`.

Two smaller gaps, for completeness. Whether `antigravity-cli` corresponds to the `agy` kind is not
answerable from the two lists. And whether the six kinds with no integration have detection
manifests is answerable only by `herdr agent explain` against a live pane of each, which needs those
binaries installed.

## Checklist

Before wiring a second agent:

- [ ] `test "${HERDR_ENV:-}" = 1` passes; if not, stop and say so.
- [ ] The configured kind clears all three layers — `herdr agent`'s list, `herdr integration
      status` (installed and current), and `command -v <kind>` — checked **now**, not inherited
      from the plan.
- [ ] The environment those checks were run in is the environment the pane will run in.
- [ ] An absolute path for the turn report is chosen, and it is in the **first** prompt.
- [ ] Every path in every prompt is resolved and absolute; no `${CLAUDE_PLUGIN_ROOT}`, no `$PWD`,
      no `~`.
- [ ] The partner's prompt states the single-writer rule explicitly.

Wiring it:

- [ ] `herdr pane split --current --direction <from layout> --cwd "$PWD" --no-focus`; take
      `.result.pane.pane_id`.
- [ ] `herdr agent start <name> --kind <kind> --pane <that id>`; take `.result.agent.name`.
- [ ] `herdr agent explain <pane> --verbose` once, to learn whether lifecycle state comes from a
      hook or a detection manifest — and record which.
- [ ] `herdr agent prompt <name> "<short text with absolute paths>" --wait --timeout <ms>`.

Every turn:

- [ ] The agent was observed at `idle`, `done` or `blocked` **before** the prompt was sent.
- [ ] `idle` and `done` are treated as one condition; nothing branches on the difference.
- [ ] `unknown` is never treated as "turn over".
- [ ] The report was read from the designated file, not scraped out of `agent read`.
- [ ] Only the agent holding the turn edited files or ran `git add`.

On failure:

- [ ] `agent_not_ready` → read the pane, wait for ready; do not restart.
- [ ] `agent_blocked` → inspect, then **ask the user**; never answer the dialog.
- [ ] `agent_prompt_stalled` → assume nothing about whose turn completed; re-check state.
- [ ] A short read → do not raise `--lines` and hope; the rows are gone.
- [ ] Any unrecognised error code → handle it; the schema does not enumerate them.
