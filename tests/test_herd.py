"""Guards `/jdi:herd`: the command that preps several issues at once, one worktree each.

`commands/herd.md` sets work up and hands it off. It reaches Herdr only through
the named operations in `reference/herdr.md` (H1, H2, H4b and H9), so the
command body stays free of raw `herdr` invocations, and every Herdr detail it
depends on is pinned here in the reference instead.

Two decisions travel with it. A herd validates Herdr and stops on the first
failure; it never falls back to a sequential `/jdi:prep`, because a herd that
quietly became one prep looks exactly like a herd that worked. And a herd
worktree is named for its issue and never removed while its plan folder holds
uncommitted files, because the plan on the branch is the only durable state.
"""

import unittest

import jdi_files

HERD_COMMAND = "commands/herd.md"
HERDR_REFERENCE = "reference/herdr.md"
H9_HEADING = "## H9 - Give a Butler its own worktree"

INVOCATION_ROWS = (
    "| `claude` | `/jdi:prep <ISSUE-ID>` |",
    "| `codex` | `$jdi:run prep <ISSUE-ID>` |",
    "| `opencode` | `/jdi-prep <ISSUE-ID>` |",
)


def normalized(text):
    return " ".join(text.split())


class HerdCommandTest(unittest.TestCase):
    longMessage = False

    def herd_text(self):
        path = jdi_files.ROOT / HERD_COMMAND
        self.assertTrue(path.is_file(), "%s does not exist" % HERD_COMMAND)
        return jdi_files.read(HERD_COMMAND)

    def h9_lines(self):
        return jdi_files.section(jdi_files.read(HERDR_REFERENCE), H9_HEADING)

    def test_herd_names_the_shared_operations_and_the_config_load(self):
        herd = normalized(self.herd_text())
        for fragment in (
            "perform **H1**",
            "**H2**",
            "**H4b**",
            "**H9**",
            "`reference/herdr.md`",
            "Validate, never repair",
            "never fall back to a sequential `/jdi:prep`",
            "`jdi-herd-<issue",
            "`.jdi/config.local.yml`",
            "one name per issue",
            "Worktree",
            "uncommitted plan files",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, herd, "%s lacks %r" % (HERD_COMMAND, fragment))

    def test_herd_drops_the_superseded_keys_and_tools(self):
        herd = self.herd_text()
        for fragment in ("herd.args", "herd.env", "AskUserQuestion", "herd record", "--resume"):
            with self.subTest(fragment=fragment):
                self.assertNotIn(
                    fragment, herd, "%s still says %r" % (HERD_COMMAND, fragment)
                )

    def test_h9_exists_with_the_invocation_table(self):
        lines = self.h9_lines()
        for row in INVOCATION_ROWS:
            with self.subTest(row=row):
                self.assertIn(row, lines, "H9 lacks the invocation row %r" % row)

    def test_h9_names_the_worktree_commands_and_paths(self):
        h9 = normalized("\n".join(self.h9_lines()))
        for fragment in (
            "herdr worktree create",
            "herdr tab rename",
            "git -C <worktree> status --porcelain",
            "--path",
            "<worktrees dir>/<repo>/jdi-herd-<issue>",
            "[worktrees] directory",
            "~/.herdr/worktrees",
            "jdi-herd-scratch-<herd-id>-<N>",
            "herdr worktree open",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, h9, "H9 lacks %r" % fragment)

    def test_h9_drops_the_collision_prone_scratch_branch(self):
        h9 = normalized("\n".join(self.h9_lines()))
        self.assertNotIn(
            "--branch jdi-herd-scratch-<N> ",
            h9,
            "H9 still creates PR #5's collision-prone `jdi-herd-scratch-<N>` branch",
        )


if __name__ == "__main__":
    unittest.main()
