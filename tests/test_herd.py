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

    def test_herd_offers_no_watch_loop(self):
        """The Herdr sidebar shows blocked and done per pane; the herd starts no poll."""
        herd = normalized(self.herd_text())
        for fragment in ("watch loop", "loop facility", "Every 5 minutes"):
            with self.subTest(fragment=fragment):
                self.assertNotIn(
                    fragment, herd, "%s still offers a loop: %r" % (HERD_COMMAND, fragment)
                )
        self.assertIn(
            "the Herdr sidebar shows `blocked` and `done` per pane",
            herd,
            "%s does not point at the Herdr sidebar" % HERD_COMMAND,
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
            "<worktrees dir>/<repo>/<name>",
            "[worktrees] directory",
            "~/.herdr/worktrees",
            "jdi-herd-scratch-<herd-id>-<N>",
            "herdr worktree open",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, h9, "H9 lacks %r" % fragment)

    def test_herd_names_each_agent_from_the_issue_title(self):
        """A readable `<slug>-<suffix>` name from the title, with the old name as the fallback."""
        herd = normalized(self.herd_text())
        for fragment in (
            "perform **T2**",
            "`<slug>-<suffix>`",
            "**T6**",
            "`[a-z][a-z0-9_-]{0,31}`",
            "keep the suffix whole",
            "falls back to the old name `jdi-herd-<issue>` for that issue and says so once",
            "any folder whose name ends in `-<suffix>`",
            "The workspace label is the issue title",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, herd, "%s lacks %r" % (HERD_COMMAND, fragment))
        self.assertNotIn(
            "The name is `jdi-herd-<issue>`",
            herd,
            "%s still builds every name as `jdi-herd-<issue>`" % HERD_COMMAND,
        )

    def test_h9_uses_the_title_name_suffix_match_and_title_label(self):
        h9 = normalized("\n".join(self.h9_lines()))
        for fragment in (
            "`<slug>-<suffix>`",
            "ends in `-<suffix>`",
            "`jdi-herd-<issue>` from an older herd",
            '--label "<SHORT-ID> <TITLE>"',
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, h9, "H9 lacks %r" % fragment)
        self.assertNotIn(
            "--path <worktrees dir>/<repo>/jdi-herd-<issue>",
            h9,
            "H9 still creates the worktree at `jdi-herd-<issue>`",
        )

    def test_h9_drops_the_collision_prone_scratch_branch(self):
        h9 = normalized("\n".join(self.h9_lines()))
        self.assertNotIn(
            "--branch jdi-herd-scratch-<N> ",
            h9,
            "H9 still creates PR #5's collision-prone `jdi-herd-scratch-<N>` branch",
        )


if __name__ == "__main__":
    unittest.main()
