"""Guards the herd record: the file `/jdi:herd` writes so a later cleanup can find its worktrees.

Issue #37 adds `/jdi:herd --cleanup`, and cleanup reads a record, never folder
names: a folder name is a guess, and a guess is how the wrong worktree gets
removed. So H9 writes one record per herd, under git's own directory, and every
rule about it (where it lives, its shape, when it is written, what its state
means) lives in `reference/herdr.md`, in `### The herd record`. This module pins
those rules there; the command only calls them by name.
"""

import json
import unittest

import jdi_files

HERDR_REFERENCE = "reference/herdr.md"
H9_HEADING = "## H9 - Give a Butler its own worktree"
H9_APP_HEADING = "### H9 on the app"
RECORD_HEADING = "### The herd record"
CLEANUP_HEADING = "### Cleanup from the herd record"
REMOVAL_MARKER = "**The removal, per entry, in this order:**"


def normalized(text):
    return " ".join(text.split())


class HerdRecordTest(unittest.TestCase):
    longMessage = False

    def reference_text(self):
        return jdi_files.read(HERDR_REFERENCE)

    def record_lines(self):
        return jdi_files.section(self.reference_text(), RECORD_HEADING)

    def record_text(self):
        return normalized("\n".join(self.record_lines()))

    def assertRecordContains(self, *fragments):
        record = self.record_text()
        for fragment in fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, record, "The herd record lacks %r" % fragment)

    def test_record_shape_matches_appendix_c(self):
        lines = self.record_lines()
        self.assertIn("```json", lines, "The herd record has no ```json fence at column 0")
        start = lines.index("```json") + 1
        end = next(
            (index for index in range(start, len(lines)) if lines[index].startswith("```")),
            None,
        )
        self.assertIsNotNone(end, "The herd record's ```json fence is never closed")
        record = json.loads("\n".join(lines[start:end]))
        self.assertEqual(
            set(record),
            {"schema", "herd_id", "created", "surface", "state", "issues"},
        )
        entry = record["issues"][0]
        self.assertEqual(
            set(entry),
            {
                "n",
                "issue",
                "task",
                "name",
                "worktree",
                "scratch_branch",
                "base_commit",
                "seeded",
                "created",
                "herdr",
            },
        )
        self.assertEqual(
            set(entry["herdr"]),
            {"workspace_id", "space_id", "tab_id", "pane_id", "terminal_id", "agent_name"},
        )

    def test_record_untracked_entry(self):
        """M-D: an untracked task's entry has a `null` issue and its `task` text."""
        self.assertRecordContains(
            "`null` for an untracked task",
            "`schema` stays `1`",
            "a missing `task` as `null`",
        )

    def test_record_heading_is_inside_h9(self):
        text = self.reference_text()
        lines = text.split("\n")
        self.assertIn(RECORD_HEADING, lines, "heading %r not found" % RECORD_HEADING)
        record_index = lines.index(RECORD_HEADING)
        self.assertGreater(record_index, lines.index(H9_HEADING))
        self.assertGreater(record_index, lines.index(H9_APP_HEADING))
        self.assertIn(
            RECORD_HEADING,
            jdi_files.section(text, H9_HEADING),
            "%r is not inside %r" % (RECORD_HEADING, H9_HEADING),
        )

    def test_record_location_and_lifecycle(self):
        self.assertRecordContains(
            "git rev-parse --path-format=absolute --git-common-dir",
            "<git-common-dir>/jdi/herds/<herd-id>.json",
            "never committed",
            "one file per herd",
            "mv -f",
            "never edited in place",
            "names no session and no app home",
        )

    def test_record_write_points(self):
        self.assertRecordContains(
            "step 6",
            "step 7",
            "step 8",
            "step 10",
            "`creating`",
            "`handed_off`",
            "git worktree list --porcelain",
            "refs/heads/<scratch branch>",
            "git -C <path> rev-parse HEAD",
            "the herd continues",
        )

    def test_create_steps_point_at_the_record(self):
        text = self.reference_text()
        h9 = jdi_files.section(text, H9_HEADING)
        self.assertIn(H9_APP_HEADING, h9, "%r is not inside %r" % (H9_APP_HEADING, H9_HEADING))
        tui = normalized("\n".join(h9[: h9.index(H9_APP_HEADING)]))
        app = normalized("\n".join(jdi_files.section(text, H9_APP_HEADING)))
        for label, body in (("H9 on the TUI", tui), ("H9 on the app", app)):
            with self.subTest(surface=label):
                self.assertIn(
                    "*The herd record*", body, "%s lacks '*The herd record*'" % label
                )


class HerdCleanupFromRecordTest(unittest.TestCase):
    """Guards `### Cleanup from the herd record`: how `/jdi:herd --cleanup` cleans a herd.

    The rules live only in `reference/herdr.md`; `commands/herd.md` calls them by
    name. Fragments follow the #37 probe gate (PLAN.md, `## Probe log (#37)`).
    """

    longMessage = False

    def cleanup_text(self):
        return normalized(
            "\n".join(jdi_files.section(jdi_files.read(HERDR_REFERENCE), CLEANUP_HEADING))
        )

    def assertCleanupContains(self, *fragments):
        cleanup = self.cleanup_text()
        for fragment in fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(
                    fragment, cleanup, "Cleanup from the herd record lacks %r" % fragment
                )

    def test_selects_records_safely(self):
        self.assertCleanupContains(
            "`^[0-9]{8}T[0-9]{6}$`",
            "never builds a path from",
            "`creating`",
            "Never guess from folder names",
            "git worktree list",
        )

    def test_resolves_by_worktree_path(self):
        """Every ID is re-found by worktree path.

        Gate amendments from `## Probe log (#37)`: G1 (a TUI worktree with no open
        workspace has no `open_workspace_id` key, so absent or `null` both mean
        none), G2 (the app's busy check reads each terminal's `status` string from
        `hc ls --json`, never its `state`), G3 (the app's space `folder` is resolved
        with `pwd -P` before it is compared with git's path).
        """
        self.assertCleanupContains(
            "never by a recorded ID alone",
            "herdr-app ls",
            "pwd -P",
            "hc ls --json --label herdr.space=<space>",
            "the `status` of every terminal",
            "herdr worktree list --cwd <main checkout>",
            "open_workspace_id",
            "absent or `null` means no open workspace",
            "herdr workspace get <workspace_id>",
        )

    def test_skips(self):
        self.assertCleanupContains(
            "`working` or `blocked`",
            "not reachable from here",
            "agent state unknown",
            "the session running the cleanup",
            "prunable",
            "git worktree prune",
        )

    def test_guards_and_force(self):
        self.assertCleanupContains(
            "git -C <worktree> status --porcelain -- <plans.path>",
            "git -C <worktree> status --porcelain",
            "the whole tree",
            "`--force` only when the entry's `seeded` is true",
            "uncommitted changes",
            "one list",
            "asks once",
            "its own yes",
            "ignored files",
        )

    def test_scratch_branch_rule(self):
        self.assertCleanupContains(
            "jdi-herd-scratch-<herd-id>-<N>",
            "git show-ref --verify --quiet refs/heads/<scratch branch>",
            "git rev-list --count <base_commit>..refs/heads/<scratch branch>",
            "git branch -D <scratch branch>",
            "Never delete any other branch",
        )

    def test_cleanup_reports_tasks_by_name(self):
        """M-D: an untracked entry has no issue ID, so the report names it otherwise."""
        self.assertCleanupContains("reported by its `name` and its task text")

    def test_scratch_branch_reason_names_do(self):
        """M-D: either mode leaves the scratch branch behind, so the deletion rule holds."""
        self.assertCleanupContains(
            "`/jdi:do` and `/jdi:prep` both leave the scratch branch behind"
        )

    def test_record_upkeep(self):
        self.assertCleanupContains("removes the entry", "deletes the record file")

    def test_removal_order(self):
        cleanup = self.cleanup_text()
        self.assertIn(
            REMOVAL_MARKER, cleanup, "Cleanup from the herd record lacks %r" % REMOVAL_MARKER
        )
        removal = cleanup[cleanup.index(REMOVAL_MARKER) + len(REMOVAL_MARKER) :]
        steps = (
            "git -C <worktree> status --porcelain -- <plans.path>",
            "herdr-app do space.close --id <space> --confirmed true",
            "git -C <main checkout> worktree remove",
            "git branch -D <scratch branch>",
            "removes the entry",
        )
        positions = []
        for step in steps:
            self.assertIn(step, removal, "The removal lacks %r" % step)
            positions.append(removal.index(step))
        self.assertEqual(
            positions,
            sorted(positions),
            "The removal must re-check the plan files, close, remove the worktree, delete "
            "the scratch branch, then update the record; found them at %r" % (positions,),
        )
        self.assertEqual(len(set(positions)), len(positions))


if __name__ == "__main__":
    unittest.main()
