status: pending
# 01 — Make the new command and config key falsifiable

Depends on: None

## Why
`/jdi:pair` and the `pair` config key are about to add rows to two hand-maintained lists —
`commands/help.md`'s command table and `roles/butler.md`'s ownership table — that nothing today
checks. Without a guard on each, a future edit can silently drop the new command from either list
and the suite stays green. Landing the guards first, and fixing what they immediately find, is
what keeps every later task in this plan falsifiable at the moment it adds a file.

## Description
Add two bidirectional enumeration checks, following the shape of the existing
`CommandTableTest` and `ReferenceFileEnumerationTest` in `tests/test_enumerations.py`:

1. **A guard on `commands/help.md`'s command table** — the table a user actually sees when they run
   `/jdi:help` — checking it names every file in `commands/`, and names nothing that is not a file
   in `commands/`. Add a `command_slugs()` helper to `tests/jdi_files.py` (every `` /jdi:<name> ``
   derivable from `commands/*.md`'s filenames) and a `slash_commands(lines)` extractor (every
   `` `/jdi:<name>` `` mention across a set of lines), scoped to table rows with the existing
   `table_rows()` helper.
2. **A guard on `roles/butler.md`'s ownership table**, using the same two helpers. This table's
   rows *group* commands — one row can name three commands separated by commas — so the guard must
   extract every `` `/jdi:<name>` `` mention from the table's rows rather than expect one row per
   command, the way the help.md guard can.

**This task's red is real and pre-existing, and it must be fixed, not accommodated.**
`commands/help.md`'s table currently names 15 commands for 16 files in `commands/`: `/jdi:help` is
missing from its own table, so a user who runs `/jdi:help` never learns the command exists. Once
the new guard is in place it will fail naming `help`. **The fix is to add the missing `/jdi:help`
row to the table — never to exempt `help` from the check.** Exempting it would be the tempting
green, and it would neuter the guard at the exact moment `/jdi:pair` needs it to catch a missing
row of its own.

The `roles/butler.md` guard is different: it is **green the day it is added**, because
`roles/butler.md`'s ownership table, taken as a whole across its grouped rows, already names all 16
commands — `/jdi:help` among them, in the row it shares with `/jdi:done` and `/jdi:status`. Its red
must be produced deliberately, once, to prove the guard actually catches an omission: remove one
`` `/jdi:<name>` `` mention from one grouped row, run the suite and capture the failure, then
restore the line exactly as it was.

**The report for this task must say, explicitly, which red was real and pre-existing (help.md's)
and which was induced and then reverted (butler.md's).** Conflating the two would misrepresent
what this task actually found versus what it manufactured to prove a negative.

## Files
- `tests/jdi_files.py` — add `command_slugs()` and `slash_commands(lines)`.
- `tests/test_enumerations.py` — add the two new bidirectional guards.
- `commands/help.md` — add the missing `/jdi:help` row to the command table.

## Verification
- `python3 -m unittest discover -s tests -v` before any change — expect `Ran 15 tests ... OK`
  (today's baseline; not proof of anything this task adds).
- Add the two new guards, before touching `commands/help.md` — expect **one new failure**, naming
  `help` as absent from `commands/help.md`'s table, and the new butler guard passing.
- Add the `/jdi:help` row to `commands/help.md` — expect `Ran 17 tests ... OK`.
- Induce the butler guard's red: delete one `` `/jdi:<name>` `` mention from one grouped row in
  `roles/butler.md`, run the suite — expect the new butler guard to fail, naming the removed
  command as absent from the ownership table. Restore the line — expect `Ran 17 tests ... OK`
  again.
