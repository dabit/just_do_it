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

import re
import subprocess
import unittest

import jdi_files

HERD_COMMAND = "commands/herd.md"
HERDR_REFERENCE = "reference/herdr.md"
H9_HEADING = "## H9 - Give a Butler its own worktree"
H9_APP_HEADING = "### H9 on the app"

INVOCATION_ROWS = (
    "| Kind | `herd.mode: do` | `herd.mode: prep` |",
    "| `claude` | `/jdi:do <WORK>` | `/jdi:prep <WORK>` |",
    "| `codex` | `$jdi:run do <WORK>` | `$jdi:run prep <WORK>` |",
    "| `opencode` | `/jdi-do <WORK>` | `/jdi-prep <WORK>` |",
)


def normalized(text):
    return " ".join(text.split())


def step_text(text, n):
    """Step n of commands/herd.md: from its first line to the next numbered step or `## ` heading."""
    lines = text.split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith("%d. **" % n))
    collected = [lines[start]]
    for line in lines[start + 1 :]:
        if re.match(r"^\d+\. \*\*", line) or line.startswith("## "):
            break
        collected.append(line)
    return normalized("\n".join(collected))


class HerdCommandTest(unittest.TestCase):
    longMessage = False

    def herd_text(self):
        path = jdi_files.ROOT / HERD_COMMAND
        self.assertTrue(path.is_file(), "%s does not exist" % HERD_COMMAND)
        return jdi_files.read(HERD_COMMAND)

    def h9_lines(self):
        return jdi_files.section(jdi_files.read(HERDR_REFERENCE), H9_HEADING)

    def h9_app_lines(self):
        return jdi_files.section(jdi_files.read(HERDR_REFERENCE), H9_APP_HEADING)

    def h9_app_text(self):
        return normalized("\n".join(self.h9_app_lines()))

    def assertH9AppContains(self, *fragments):
        h9_app = self.h9_app_text()
        for fragment in fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, h9_app, "H9 on the app lacks %r" % fragment)

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
            "`herd`, `herdr`, `harnesses`",
            "H1 settles which Herdr",
            "On the app, the space is opened in step 8",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, herd, "%s lacks %r" % (HERD_COMMAND, fragment))

    def test_herd_drops_the_superseded_keys_and_tools(self):
        herd = self.herd_text()
        # #31 banned a *resume* record (its D12), so "--resume" stays banned. #37's
        # herd record is for cleanup only, so "herd record" is no longer banned here.
        for fragment in ("herd.args", "herd.env", "AskUserQuestion", "--resume"):
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

    def test_herd_cleanup_mode(self):
        """`--cleanup` calls H9's record sections by name and restates none of their rules (C11)."""
        herd = normalized(self.herd_text())
        for fragment in (
            "`--cleanup`",
            "`/jdi:herd --cleanup <herd-id>`",
            "*The herd record*",
            "*Cleanup from the herd record*",
            "asks once",
            "Never guess from folder names",
            "never names or resumes a session",
            "cleanup never stops on H1's answer",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, herd, "%s lacks %r" % (HERD_COMMAND, fragment))

    def test_argument_hint_names_cleanup(self):
        frontmatter = jdi_files.split_frontmatter(self.herd_text())
        self.assertIsNotNone(frontmatter, "%s has no frontmatter" % HERD_COMMAND)
        hint = jdi_files.frontmatter_scalars(frontmatter[0]).get("argument-hint", "")
        self.assertIn(
            "--cleanup [<herd-id>]",
            hint,
            "%s's argument-hint does not name the cleanup mode: %r" % (HERD_COMMAND, hint),
        )

    def assertStepContains(self, n, *fragments):
        step = step_text(self.herd_text(), n)
        for fragment in fragments:
            with self.subTest(step=n, fragment=fragment):
                self.assertIn(
                    fragment, step, "%s step %d lacks %r" % (HERD_COMMAND, n, fragment)
                )

    def test_herd_reads_the_mode(self):
        """M3: `herd.mode`, and an invalid value runs as the mode with less authority."""
        self.assertStepContains(
            1, "`herd.mode`", "announced once and runs as `prep`"
        )

    def test_herd_parses_issues_and_tasks(self):
        """E3: a quoted argument is a task; nothing is guessed."""
        self.assertStepContains(
            3,
            "A quoted argument is always a task",
            "an issue ID only when a tracker is configured",
            "`tracker.id_prefix`",
            "With no tracker configured, no argument is an issue ID",
            "ask once",
            "Never guess",
            "start nothing before the answer",
        )

    def test_tasks_skip_the_tracker(self):
        """E5: no tracker work for an untracked task."""
        self.assertStepContains(
            3,
            "Tasks skip **T2** and every other tracker step",
            "nothing is read from or posted to a tracker for a task",
        )

    def test_task_suffix_is_a_stable_hash(self):
        """E4: the task suffix is a hash of its text, never an index."""
        self.assertStepContains(
            5,
            "printf '%s' '<normalised task>' | git hash-object --stdin",
            "`t96ae2d`",
            "`fix-typo-signup-email-t96ae2d`",
            "an index in the herd would give every herd's first task the same suffix",
        )

    def test_task_suffix_example_is_reproducible(self):
        """The documented command, run on the worked example, gives the documented suffix."""
        lines = [
            line.strip()
            for line in self.herd_text().split("\n")
            if line.strip().startswith("printf '%s' '<normalised task>'")
        ]
        self.assertTrue(
            lines, "%s has no `printf '%%s' '<normalised task>'` line" % HERD_COMMAND
        )
        cmd = lines[0].replace("<normalised task>", "fix the typo in the signup email")
        result = subprocess.run(
            ["sh", "-c", cmd], cwd=jdi_files.ROOT, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip()[:6],
            "96ae2d",
            "%r gives %r, not the documented `96ae2d...`" % (cmd, result.stdout.strip()),
        )

    def test_mode_announced_before_start(self):
        """M5: step 8 says which mode runs before the first start."""
        self.assertStepContains(
            8, "opens and merges its own pull request", "`herd.mode: prep`"
        )

    def test_mode_announcement_is_quoted(self):
        """F-i (#38 UAT): step 8 quotes the line to say, naming `herd.mode: prep` as the way back."""
        self.assertStepContains(
            8,
            '"Mode `do`: each agent opens and merges its own pull request, unattended and in '
            'parallel with the others; `herd.mode: prep` stops each at a plan instead."',
            "a line of its own",
        )

    def test_report_names_do_mode_stops(self):
        """E2: a stopped `do` agent waits in its space, and the sidebar shows `done`."""
        self.assertStepContains(
            10, "a `do` agent that stopped", "the sidebar shows `done` for it"
        )

    def test_cleanup_refuses_tasks_alongside(self):
        herd = normalized(self.herd_text())
        self.assertIn(
            "Issue IDs, tasks or `--kind`",
            herd,
            "%s's cleanup does not refuse tasks alongside `--cleanup`" % HERD_COMMAND,
        )

    def test_argument_hint_names_tasks(self):
        frontmatter = jdi_files.split_frontmatter(self.herd_text())
        self.assertIsNotNone(frontmatter, "%s has no frontmatter" % HERD_COMMAND)
        hint = jdi_files.frontmatter_scalars(frontmatter[0]).get("argument-hint", "")
        for fragment in ("'task text'", "--cleanup [<herd-id>]"):
            with self.subTest(fragment=fragment):
                self.assertIn(
                    fragment,
                    hint,
                    "%s's argument-hint lacks %r: %r" % (HERD_COMMAND, fragment, hint),
                )

    def test_step_eleven_points_at_cleanup(self):
        """C8: a normal herd's step 11 names the cleanup mode, in its first paragraph."""
        paragraph = normalized(
            "\n".join(
                jdi_files.paragraph_starting_with(
                    self.herd_text(), "11. **Say how to clean up"
                )
            )
        )
        self.assertIn(
            "`/jdi:herd --cleanup <herd-id>`",
            paragraph,
            "step 11's first paragraph does not name `/jdi:herd --cleanup <herd-id>`",
        )

    def test_prep_leaves_the_scratch_branch_behind(self):
        """C4's correction: `/jdi:prep` switches to a branch of its own; it renames nothing."""
        herd = normalized(self.herd_text())
        self.assertIn(
            "leaves the scratch branch behind",
            herd,
            "%s does not say prep leaves the scratch branch behind" % HERD_COMMAND,
        )
        self.assertNotIn(
            "`/jdi:prep` renames the branch",
            herd,
            "%s still says `/jdi:prep` renames the branch" % HERD_COMMAND,
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
            "--label '<SHORT-ID> <TITLE>'",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, h9, "H9 lacks %r" % fragment)
        self.assertNotIn('--label "', h9, "H9 still double-quotes the TUI --label")
        self.assertNotIn(
            "--path <worktrees dir>/<repo>/jdi-herd-<issue>",
            h9,
            "H9 still creates the worktree at `jdi-herd-<issue>`",
        )

    def test_h9_invocation_by_mode_and_clause(self):
        """M-B: the command follows `herd.mode`, and a fixed clause says a herd started it."""
        h9 = normalized("\n".join(self.h9_lines()))
        for fragment in (
            "`herd.mode`",
            "`(started by /jdi:herd)`",
            "`(untracked, started by /jdi:herd)`",
            "it is not part of the work",
            "collapsed to one space",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, h9, "H9 lacks %r" % fragment)

    def test_h9_invocation_is_single_quoted(self):
        """M-B: typed task text stays literal, so the invocation is never double-quoted."""
        h9 = normalized("\n".join(self.h9_lines()))
        for fragment in (
            "`herdr agent prompt <name> '<invocation>'`",
            "single-quoted, never double-quoted",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, h9, "H9 lacks %r" % fragment)
        self.assertNotIn('"<invocation>"', h9, "H9 still double-quotes an invocation")

    def test_h9_untracked_task_label_and_no_fallback(self):
        """M-C: an untracked task is labelled by its suffix and text, with no issue fallback."""
        h9 = normalized("\n".join(self.h9_lines()))
        for fragment in (
            "`<suffix> <task text>`",
            "has no `jdi-herd-<issue>` fallback",
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

    def test_h9_app_folder_matches_the_app_dialog(self):
        self.assertH9AppContains(
            "${HERDR_APP_HOME:-~/.config/herdr-app}/settings.json",
            "worktrees.directory",
            "~/.herdr/worktrees",
            "--git-common-dir",
            "<worktrees dir>/<repo>/<name>",
        )

    def test_h9_app_branches_from_the_default_branch(self):
        self.assertH9AppContains(
            "git worktree add -b jdi-herd-scratch-<herd-id>-<N> <path> origin/<default>",
        )

    def test_h9_app_opens_the_space_after_seeding(self):
        self.assertH9AppContains(
            "herdr-app do space.new --name",
            "--folder <path> --tab <name>",
            "--focus false",
            "after `herd.seed`",
        )

    def test_h9_app_hands_off_by_send(self):
        """Type only into an idle agent; a trust dialog reports no status and is the user's."""
        self.assertH9AppContains(
            "hc wait <terminal> --timeout 120",
            "status: idle",
            "hc send <terminal> '<invocation>' --if idle",
            "Never `--task`",
            "blocked at startup",
        )

    def test_h9_app_hands_off_untagged(self):
        """Task 27, R7: from an agent's terminal hc wraps a send in an `<hc from>` tag, and a
        tagged `/jdi:do` is not a slash command (F-h). Dropping only `HC_TERMINAL_ID` for the one
        handoff sends it untagged to the same core, and `--if idle` still holds."""
        self.assertH9AppContains(
            "env -u HC_TERMINAL_ID hc send <terminal> '<invocation>' --if idle",
            "`<hc from=",
            "a real slash command",
            "only `HC_TERMINAL_ID`",
            "never `HC_SESSION`",
            "(R7)",
        )
        self.assertNotRegex(
            self.h9_app_text(),
            r"(?<!HC_TERMINAL_ID )hc send <terminal> '<invocation>'",
            "H9 on the app still hands off with a tagged `hc send` somewhere",
        )

    def test_h9_app_cleanup_order(self):
        h9_app = self.h9_app_text()
        steps = (
            "git -C <worktree> status --porcelain -- <plans.path>",
            "herdr-app do space.close --id <space> --confirmed true",
            "worktree remove",
        )
        positions = []
        for step in steps:
            self.assertIn(step, h9_app, "H9 on the app lacks %r" % step)
            positions.append(h9_app.index(step))
        self.assertEqual(
            positions,
            sorted(positions),
            "H9 on the app must check the plan files, then close the space, then remove "
            "the worktree; found them at %r" % (positions,),
        )
        self.assertEqual(len(set(positions)), len(positions))

    def test_h9_app_reattach_and_list(self):
        self.assertH9AppContains(
            "herdr-app do space.select --id <space>",
            "git worktree list --porcelain",
        )

    def test_surfaces_no_longer_calls_h9_tui_only(self):
        reference = normalized(jdi_files.read(HERDR_REFERENCE))
        self.assertNotIn(
            "H9 does not have its app subsection yet",
            reference,
            "`## Surfaces` still says H9 has only its TUI text",
        )

    def test_h9_app_trust_is_inherited_from_the_main_checkout(self):
        """F4: a linked worktree takes Claude's folder trust from its main checkout."""
        h9_app = self.h9_app_text()
        self.assertNotIn("has not seen", h9_app, "H9 on the app still says every new worktree is unseen")
        self.assertNotIn("have not seen", h9_app, "H9 on the app still says every new worktree is unseen")
        self.assertH9AppContains(
            "takes Claude's folder trust from its main checkout",
            "can open a folder-trust dialog",
            "an untrusted main checkout",
        )

    def test_h9_app_space_name_is_single_quoted(self):
        """F7: a literal single-quoted example, and why (A17)."""
        lines = self.h9_app_lines()
        examples = [
            line
            for line in lines
            if line.strip().startswith("herdr-app do space.new --name 'f4960613 Seam 1 - ")
        ]
        self.assertTrue(examples, "H9 on the app has no literal single-quoted --name example line")
        self.assertH9AppContains("A17", "'\\''", "never double quotes")
        self.assertNotIn('--name "', self.h9_app_text(), "H9 on the app double-quotes --name")


if __name__ == "__main__":
    unittest.main()
