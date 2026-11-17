status: pending
# 21 — H9: modes, the herd clause, single quoting, untracked tasks, the record

Depends on: None

## Why
H9 in `reference/herdr.md` defines what every herd agent is handed, so it must carry the invocation table by kind and `herd.mode` (`/jdi:do` or `/jdi:prep`), the fixed clause that tells `/jdi:do` and `/jdi:prep` a herd started them, the single-quoting that keeps typed task text literal on both surfaces, the untracked task's label and its lack of a `jdi-herd-<issue>` fallback, and the record's `task` key with `issue` allowed to be `null`. Every later task in #38 reads these strings from H9. Rests on: U1, U2, E1, E4, E5, M1, M2, M6, M7.

## Description
Planner's Task 21. Edit **only `## H9 - Give a Butler its own worktree` and its subsections**
(`### H9 on the app`, `### The herd record`, `### Cleanup from the herd record`) in
`reference/herdr.md`, and pin the edits in `tests/test_herd.py` and `tests/test_herd_record.py`.

**Rules for `reference/herdr.md`:** no em dash anywhere (the file has none); placeholders only, no
`/home/`; keep every fragment the existing tests pin (listed in Verification step 4). The section's
rules are called by name from `commands/herd.md` (Task 23) and read by `tests/test_herd_handoff.py`
(Task 22), so the two clauses must be spelt exactly `(started by /jdi:herd)` and
`(untracked, started by /jdi:herd)`, each in backticks.

TDD is on: write the tests first and watch them fail on their own assertions.

### 1. Tests first

**`tests/test_herd.py`**
- Replace `INVOCATION_ROWS` with these four lines (the M-B header and three rows, byte for byte):
  ```text
  | Kind | `herd.mode: do` | `herd.mode: prep` |
  | `claude` | `/jdi:do <WORK>` | `/jdi:prep <WORK>` |
  | `codex` | `$jdi:run do <WORK>` | `$jdi:run prep <WORK>` |
  | `opencode` | `/jdi-do <WORK>` | `/jdi-prep <WORK>` |
  ```
  `test_h9_exists_with_the_invocation_table` keeps checking each is a whole line of the H9 section.
- `test_h9_app_hands_off_by_send`: the fragment `'hc send <terminal> "<invocation>" --if idle'`
  becomes `"hc send <terminal> '<invocation>' --if idle"`.
- `test_h9_uses_the_title_name_suffix_match_and_title_label`: the fragment `'--label "<SHORT-ID> <TITLE>"'`
  becomes `"--label '<SHORT-ID> <TITLE>'"`, and add `self.assertNotIn('--label "', h9)`.
- New `test_h9_invocation_by_mode_and_clause`: the normalized H9 section
  (`normalized("\n".join(self.h9_lines()))`) contains, one `subTest` each: `` `herd.mode` ``,
  `` `(started by /jdi:herd)` ``, `` `(untracked, started by /jdi:herd)` ``,
  `it is not part of the work`, `collapsed to one space`.
- New `test_h9_invocation_is_single_quoted`: normalized H9 contains
  `` `herdr agent prompt <name> '<invocation>'` `` and `single-quoted, never double-quoted`, and
  does **not** contain `"<invocation>"`.
- New `test_h9_untracked_task_label_and_no_fallback`: normalized H9 contains `` `<suffix> <task text>` ``
  and ``has no `jdi-herd-<issue>` fallback``.

**`tests/test_herd_record.py`**
- `test_record_shape_matches_appendix_c`: the entry key set gains `"task"`.
- New `HerdRecordTest.test_record_untracked_entry`: the record section contains
  `` `null` for an untracked task ``, `` `schema` stays `1` ``, `` a missing `task` as `null` ``.
- New `HerdCleanupFromRecordTest.test_cleanup_reports_tasks_by_name`: the cleanup section contains
  `` reported by its `name` and its task text ``.
- New `HerdCleanupFromRecordTest.test_scratch_branch_reason_names_do`: the cleanup section contains
  `` `/jdi:do` and `/jdi:prep` both leave the scratch branch behind ``.

### 2. Edits to `reference/herdr.md`, H9 only

1. **Intro** (first paragraph under the `## H9` heading): each issue **or untracked task** gets its
   own worktree, workspace, pane and agent, and the agent is a whole Butler "running the herd's
   command, `/jdi:do` or `/jdi:prep` by `herd.mode`".
2. **Names.** "The caller supplies one name per issue or task, `<slug>-<suffix>` …" (keep the rest:
   the issue-title rule, the `jdi-herd-<issue>` fallback for an issue, the `herdr agent list` check),
   then append M-C:
   > An untracked task's suffix is built as `commands/herd.md` step 5 says. An untracked task has no `jdi-herd-<issue>` fallback. Its label, the TUI's `--label` and the app's space name, is `<suffix> <task text>`.
3. **An existing folder is not overwritten.** "…any folder whose name ends in `-<suffix>`, or, for an
   issue, is named `jdi-herd-<issue>` from an older herd." You may say "issue or task" where the
   paragraph says a herd has run for this issue before; keep `` ends in `-<suffix>` `` and
   `` `jdi-herd-<issue>` from an older herd ``.
4. **TUI create fence**: `--label "<SHORT-ID> <TITLE>"` becomes `--label '<SHORT-ID> <TITLE>'` (the
   rest of the fence unchanged). In the paragraph after it, "When no title was read, it is
   `"<ISSUE-ID>"`" becomes `'<ISSUE-ID>'`, and the quoting sentence becomes: "Pass the label as one
   shell argument, single-quoted, with a `'` written as `'\''`, so that a quote, `$` or backtick in
   a title arrives literally."
5. **The invocation table.** Replace the line `**The invocation table.** The command each herd Butler
   receives, by kind:` and the three-row table with the M-B block below. The table lines and the
   header line are exact; the two prose paragraphs may be rewrapped at the file's width but not
   reworded. Then keep the existing paragraph "These spellings come from the README install table …"
   unchanged, directly after the M-B block.

   ```text
   **The invocation table.** The command each herd Butler receives, by kind and `herd.mode`:

   | Kind | `herd.mode: do` | `herd.mode: prep` |
   |---|---|---|
   | `claude` | `/jdi:do <WORK>` | `/jdi:prep <WORK>` |
   | `codex` | `$jdi:run do <WORK>` | `$jdi:run prep <WORK>` |
   | `opencode` | `/jdi-do <WORK>` | `/jdi-prep <WORK>` |

   `<WORK>` is the issue ID followed by `(started by /jdi:herd)`, or, for an untracked task, the task text followed by `(untracked, started by /jdi:herd)`, with one space between. The clause tells `/jdi:do` and `/jdi:prep` that a herd started them; it is not part of the work. The task text is one line: every run of whitespace, line breaks included, is collapsed to one space, because a line break typed into an agent can submit it early. For example, `/jdi:do ENG-12 (started by /jdi:herd)` and `/jdi:do fix the typo in the signup email (untracked, started by /jdi:herd)`.

   Pass the invocation as one shell argument, single-quoted, never double-quoted, with a `'` inside written as `'\''`: a task is text a person typed, and inside double quotes the shell expands `$` and backticks first.
   ```
   (This fence is indented only as part of this list; in the file the table rows start at column 0.)
6. **TUI handoff**: "**Hand it the work.** `herdr agent prompt <name> '<invocation>'`, with no `--wait`. …"
7. **App handoff** (`### H9 on the app`): the fence line becomes `hc send <terminal> '<invocation>' --if idle`;
   "The invocation comes from the invocation table above, with the issue ID filled in" becomes "…
   with `<WORK>` filled in"; "the prep command must arrive typed into a ready agent" becomes "the
   herd's command must arrive typed into a ready agent".
8. **App space name** bullet (`- **The name** is the label the TUI passes to `--label`: …`): add "or
   `<suffix> <task text>` for an untracked task" after "the issue ID when no title was read". Keep
   "**Single-quote it, never double quotes**", `A17` and `'\''` (pinned).
9. **The record fence** (`### The herd record`, column-0 ```` ```json ```` fence, must stay valid
   JSON): the entry's line `      "issue": "<ISSUE-ID>",` becomes
   `      "issue": "<ISSUE-ID, else null>",` and the next line is the new
   `      "task": "<task text, else null>",` (six-space indent, as its siblings). Then add this
   bullet (M-D) to **Write rules.**:
   > `issue` is the issue ID, or `null` for an untracked task; `task` is the task text as handed to the agent, without the clause, or `null` for an issue. `task` is additive, so `schema` stays `1`, and a reader treats a missing `task` as `null`.
10. **Cleanup step 4's reason** (`### Cleanup from the herd record`, under the removal marker): the
    sentence beginning "The reason: `/jdi:prep` leaves the scratch branch behind …" becomes (M-D):
    > The reason: `/jdi:do` and `/jdi:prep` both leave the scratch branch behind at its base and work on a branch of their own, so the scratch branch holds nothing, and any other branch may hold the work.
11. **The report** (same section): append (M-D) "An entry whose `issue` is `null` is reported by its
    `name` and its task text."

Nothing outside H9 changes. In particular the H6 and H5 text, and every other `hc send` in the file,
stay as they are.

## Files
- `reference/herdr.md`
- `tests/test_herd.py`
- `tests/test_herd_record.py`

## Verification
Run from the repository root.

1. **Red first.** After writing the tests, before editing `reference/herdr.md`:
   `python3 -m unittest discover -s tests -p 'test_herd.py' -v` — expected: `Ran 24 tests`, `FAILED`;
   failing methods exactly `test_h9_exists_with_the_invocation_table`, `test_h9_app_hands_off_by_send`,
   `test_h9_uses_the_title_name_suffix_match_and_title_label`, `test_h9_invocation_by_mode_and_clause`,
   `test_h9_invocation_is_single_quoted`, `test_h9_untracked_task_label_and_no_fallback`; the other 18 pass.
   Then `python3 -m unittest discover -s tests -p 'test_herd_record.py' -v` — expected: `Ran 15 tests`,
   `FAILED`; failing exactly `test_record_shape_matches_appendix_c`, `test_record_untracked_entry`,
   `test_cleanup_reports_tasks_by_name`, `test_scratch_branch_reason_names_do`; the other 11 pass.
   red when: a new or changed test passes before the edit, or any other method fails.
   at base: `Ran 21 tests`, `OK`; `Ran 12 tests`, `OK`.
2. **Green.** Both commands after the edit — expected: `Ran 24 tests`, `OK` and `Ran 15 tests`, `OK`.
   red when: any test fails.
   at base: `Ran 21 tests`, `OK`; `Ran 12 tests`, `OK` (the 6 new methods are written by this task).
3. **No double-quoted invocation or label is left.** `grep -n '"<invocation>"\|--label "' reference/herdr.md` — expected: no output, exit 1.
   red when: a line is printed (a TUI or app handoff, or the TUI label, is still double-quoted).
   control: `git show 2f30a283e56c0c4673b80519810ec314290f7cc7:reference/herdr.md | grep -c '"<invocation>"\|--label "'` prints `3`.
   at base: three lines: the TUI create fence (`--label "<SHORT-ID> <TITLE>"`), the TUI `**Hand it the work.**` line, and the app `hc send <terminal> "<invocation>" --if idle` fence line.
   compliant hits: none (the M-B prose names no double-quoted form; it says "never double-quoted").
4. **The pinned H9 fragments survive.** `python3 -m unittest discover -s tests -p 'test_herdr_operations.py' -v` and `python3 -m unittest discover -s tests -p 'test_herd.py' -k test_h9 -v` — expected: both `OK` (the second covers `test_h9_names_the_worktree_commands_and_paths`, `test_h9_app_space_name_is_single_quoted`, `test_h9_app_cleanup_order` and the rest).
   Counts after the edit: `Ran 40 tests`, `OK`; `Ran 15 tests`, `OK`.
   red when: any `test_h9*` or operations test fails.
   at base: `Ran 40 tests`, `OK`; `Ran 12 tests`, `OK`.
5. **The record fence is still valid JSON with the new key.** `python3 -c "import sys; sys.path.insert(0,'tests'); import jdi_files, json; l=jdi_files.section(jdi_files.read('reference/herdr.md'),'### The herd record'); s=l.index('\`\`\`json')+1; e=next(i for i in range(s,len(l)) if l[i].startswith('\`\`\`')); print(sorted(json.loads('\n'.join(l[s:e]))['issues'][0]))"` — expected: a list that includes `'task'` and `'issue'` (10 keys).
   red when: a `json.decoder.JSONDecodeError`, or `'task'` absent.
   at base: the same command prints 9 keys, without `'task'`.
6. **The tests bite.** In `reference/herdr.md`, the file that defines the handoff, change the TUI `**Hand it the work.**` line back to `herdr agent prompt <name> "<invocation>"` and rerun `test_herd.py` — expected: `test_h9_invocation_is_single_quoted` fails. Restore. Then in the same file delete the M-D sentence "An entry whose `issue` is `null` is reported by its `name` and its task text." and rerun `test_herd_record.py` — expected: `test_cleanup_reports_tasks_by_name` fails. Restore.
   red when: either mutation leaves its module green.
   at base: none — the mutated text is written by this task.
7. **No em dash, nothing outside H9 touched.** `grep -c '—' reference/herdr.md` — expected: `0`. And `git diff -U0 2f30a283e56c0c4673b80519810ec314290f7cc7 -- reference/herdr.md | awk '/^@@/{split($2,a,","); s=substr(a[1],2)+0; if (s<780) print}'` — expected: no output (every hunk starts at or after base line 780, the `## H9` heading).
   red when: the count is not `0`, or a hunk header is printed (a line before H9 changed).
   control: `grep -c '—' commands/do.md` prints `20`; `git diff -U0 cdd14046784af5ef7e58fe612067f17a2e5b60df 2f30a283e56c0c4673b80519810ec314290f7cc7 -- reference/herdr.md | awk '/^@@/{split($2,a,","); s=substr(a[1],2)+0; if (s<780) print}'` prints two hunk headers (`@@ -538,0 +539,4 @@ …` and `@@ -597,4 +601,17 @@ …`, Task 19's H5/H6 edit).
   at base: `0`; no output.
8. **Full suite.** `python3 -m unittest discover -s tests -v` — expected: every test passes. Task 20 runs beside this one; a failure in `tests/test_config_schema.py` belongs to it while it is unfinished.
   red when: a failure in `tests/test_herd.py`, `tests/test_herd_record.py`, `tests/test_herdr_operations.py`, `tests/test_delegation_transport.py`, or any module other than `tests/test_config_schema.py`.
   at base: `Ran 219 tests`, `OK`, no known reds.
