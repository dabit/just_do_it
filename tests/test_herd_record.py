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


if __name__ == "__main__":
    unittest.main()
