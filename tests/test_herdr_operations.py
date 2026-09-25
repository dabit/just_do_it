"""Guards `reference/herdr.md`, the one file that names Herdr subcommands.

The transport in `reference/delegation.md` and the herd command call the Herdr
operations (H1-H8) by name, so this file checks that each operation exists under
its exact heading and still states the rules the callers rely on: detection is
observed and never repaired, the result arrives through a file, a settled state
is not proof of success, and every pane JDI opens is closed on every exit.
"""

import re
import unittest

import jdi_files


PATH = "reference/herdr.md"

HEADINGS = (
    "# Herdr operations",
    "## The universal rules",
    "## Scope",
    "## H1 - Detect Herdr",
    "## H2 - Check the worker kind",
    "## H3 - Prepare the run",
    "## H4 - Start the worker",
    "## H5 - Prompt and wait",
    "## H6 - Handle a blocked worker",
    "## H7 - Validate the result",
    "## H8 - Close the pane and record the outcome",
    "## When a step fails",
    "## Why the agent surface, not pane run",
    "## Waves",
)


def normalized(text):
    return " ".join(text.split())


class HerdrOperationsTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(
            (jdi_files.ROOT / PATH).is_file(),
            "%s is missing; there are no Herdr operations to inspect" % PATH,
        )
        self.text = jdi_files.read(PATH)

    def section_lines(self, heading):
        return jdi_files.section(self.text, heading)

    def section_text(self, heading):
        return normalized("\n".join(self.section_lines(heading)))

    def assertSectionContains(self, heading, *fragments):
        body = self.section_text(heading)
        for fragment in fragments:
            with self.subTest(heading=heading, fragment=fragment):
                self.assertIn(normalized(fragment), body)

    def test_exact_headings_exist(self):
        lines = self.text.split("\n")
        for heading in HEADINGS:
            with self.subTest(heading=heading):
                self.assertIn(heading, lines)

    def test_superseded_design_is_gone(self):
        body = normalized(self.text)
        for fragment in (
            "## Extending to waves",
            "One active delegated role per Butler",
            "Single-instance roles",
        ):
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, body)

    def test_no_em_dash(self):
        self.assertNotIn("—", self.text)

    def test_universal_rules(self):
        self.assertSectionContains(
            "## The universal rules",
            "A Butler runs one phase at a time",
            "only a wave runs several workers at once",
        )

    def test_scope(self):
        self.assertSectionContains("## Scope", "never runs under Herdr")

    def test_h1_detect(self):
        self.assertSectionContains(
            "## H1 - Detect Herdr",
            "HERDR_ENV",
            "HERDR_BIN_PATH",
            "`herdr status`",
            "`compatible: yes`",
            "never from the harness name",
            "Detect, never repair",
        )

    def test_h2_kind(self):
        self.assertSectionContains(
            "## H2 - Check the worker kind",
            "lists the kinds Herdr supports",
            "`command -v <kind>`",
            "`herdr integration status`",
        )
        # The kind comes from models.<role>.harness only, never from the Butler's pane.
        self.assertNotIn('herdr agent get "$HERDR_PANE_ID"', self.text)

    def test_h3_prepare(self):
        heading = "## H3 - Prepare the run"
        self.assertSectionContains(
            heading,
            "`git rev-parse --absolute-git-dir`",
            "jdi/runs/<run-id>/",
            "`manifest.json`",
            "`prompt.md`",
            "`report.md`",
            "`result.json`",
            "`outcome.json`",
            '"needs_input"',
        )
        for key in (
            "run_id",
            "role",
            "plan",
            "ticket",
            "base_commit",
            "head_commit",
            "cwd",
            "workspace_id",
            "pane_id",
            "agent_name",
            "expected",
            "allowed_writes",
        ):
            self.assertSectionContains(heading, '"%s"' % key)

    def test_h4_start(self):
        self.assertSectionContains(
            "## H4 - Start the worker",
            "herdr pane split --current",
            "--env",
            "--no-focus",
            "herdr agent start",
            "`agent_not_ready`",
        )

    def test_h4_opens_with_the_spawn_line(self):
        lines = self.section_lines("## H4 - Start the worker")
        first_step = next((line for line in lines if re.match(r"\d+\. ", line)), "")
        self.assertTrue(
            first_step.startswith("1. **Print the spawn line.**"),
            "H4's first numbered step is %r, not the spawn line" % first_step,
        )
        self.assertSectionContains(
            "## H4 - Start the worker",
            "`JDI spawn` line",
            "`reference/delegation.md`, *Where a role runs*",
            "agent: <agent name>",
        )
        self.assertNotIn("**Print first.**", self.text)

    def test_manifest_is_written_after_the_pane_exists(self):
        body = self.section_text("## H4 - Start the worker")
        for marker in ("herdr pane split --current", "**Write the run files.**", "herdr agent start <name>"):
            self.assertIn(marker, body, "H4 lacks %r" % marker)
        split = body.index("herdr pane split --current")
        write = body.index("**Write the run files.**")
        start = body.index("herdr agent start <name>")
        self.assertLess(split, write, "H4 writes the run files before the pane split")
        self.assertLess(write, start, "H4 starts the agent before writing the run files")
        self.assertSectionContains(
            "## H3 - Prepare the run",
            "| `manifest.json` | the Butler | in H4, after the pane split and before `agent start`; never edited afterward |",
        )
        self.assertNotIn("before the spawn, never edited afterward", self.text)

    def test_h5_prompt_and_wait(self):
        heading = "## H5 - Prompt and wait"
        self.assertSectionContains(
            heading,
            "herdr agent prompt",
            "--wait --timeout",
            "herdr agent wait",
            "which pane",
        )
        lines = self.section_lines(heading)
        for row in (
            "| `working`",
            "| `blocked`",
            "| `idle`",
            # `done` shares its row with `idle`, as in PLAN.md's state table; this
            # prefix is the row that states what `done` means.
            "| `idle` or `done` |",
            "| `unknown`",
            "| `timeout`",
            "| `agent_blocked`",
            "| `agent_prompt_stalled`",
            "| `idle` or `done` with no `result.json`",
        ):
            with self.subTest(row=row):
                self.assertTrue(
                    any(line.startswith(row) for line in lines),
                    "H5's state table has no row starting with %r" % row,
                )

    def test_waves(self):
        self.assertSectionContains(
            "## Waves",
            "at most 4",
            "one pane per task",
            "herdr tab create",
            "jdi-wave-<first run id>",
            "is not cancelled",
            "the union of the wave's `## Files` lists",
            "cannot be attributed to one task",
        )

    def test_h6_blocked(self):
        self.assertSectionContains(
            "## H6 - Handle a blocked worker",
            "Never `send-keys` into",
            "herdr agent read <name> --source detection",
        )

    def test_h1_native_runs_no_herdr_command(self):
        self.assertSectionContains(
            "## H1 - Detect Herdr",
            "Under `native`, or with no `delegation` key, H1 does not run",
            "no Herdr command runs at step 0",
            "summaries included",
        )

    def test_wave_tab_close_may_find_the_tab_gone(self):
        self.assertSectionContains(
            "## H8 - Close the pane and record the outcome", "`tab_not_found`"
        )

    def test_h7_validate(self):
        self.assertSectionContains(
            "## H7 - Validate the result",
            "`idle` or `done` is not proof of success",
            "`JDI-RESULT-UNWRITABLE`",
        )

    def test_h8_close(self):
        self.assertSectionContains(
            "## H8 - Close the pane and record the outcome",
            "herdr pane close",
            "every exit",
        )

    def test_result_channel_rules(self):
        body = normalized(self.text)
        for fragment in (
            "`agent read` is for inspection only",
            "never counts as success",
            "never resubmit",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, body)


if __name__ == "__main__":
    unittest.main()
