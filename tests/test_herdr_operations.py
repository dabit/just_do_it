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
    "## Surfaces",
    "## H1 - Detect Herdr",
    "### Choosing the surface",
    "### H1 on the TUI",
    "### H1 on the app",
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
    "### H2 on the TUI",
    "### H2 on the app",
    "### H3 on the app",
    "### H4 on the TUI",
    "### H4 on the app",
    "#### H4b on the app",
    "### H5 on the TUI",
    "### H5 on the app",
    "### H6 on the TUI",
    "### H6 on the app",
    "### H8 on the TUI",
    "### H8 on the app",
    "### Waves on the app",
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

    def test_surfaces_section(self):
        self.assertSectionContains(
            "## Surfaces",
            "`herdr.surface`",
            "Inherit, never set",
            "`HC_SESSION`",
            "`HERDR_APP_HOME`",
            "Never run bare `herdr-app` or bare `hc`",
            "`hc server`",
            "seconds",
        )

    def test_choosing_the_surface(self):
        self.assertSectionContains(
            "### Choosing the surface",
            "innermost surface wins",
            "`foreground`",
            "says so once and uses the TUI",
            "never falls to the other surface",
        )

    def test_h1_app_checks_in_order(self):
        body = self.section_text("### H1 on the app")
        previous = -1
        for marker in (
            "HC_TERMINAL_ID",
            "command -v hc",
            'test -S "$HC_TERMINAL_SOCKET"',
            'hc get "$HC_TERMINAL_ID" --json',
            "herdr.space",
            "herdr-app status",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, body, "H1 on the app lacks %r" % marker)
                position = body.index(marker)
                self.assertGreater(
                    position, previous, "H1 on the app names %r out of order" % marker
                )
                previous = position
        self.assertIn("before any `hc` command", body)

    def test_no_personal_values(self):
        # A `${HERDR_APP_HOME:-...}` default does not contain `HERDR_APP_HOME=`.
        for fragment in ("/home/", "/Users/", "jdiprobe", "HC_SESSION=", "HERDR_APP_HOME="):
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, self.text)

    def test_failure_patterns_name_the_surface(self):
        self.assertSectionContains("## When a step fails", "Herdr (<surface>)")

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
            "spawn_line",
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

    def test_h4_spawn_line_and_pane_split_are_one_command(self):
        lines = self.section_lines("## H4 - Start the worker")
        start = next(i for i, line in enumerate(lines) if line.startswith("1. "))
        end = next(i for i, line in enumerate(lines) if line.startswith("2. "))
        step = lines[start:end]
        fence = [i for i, line in enumerate(step) if line.strip().startswith("```")]
        self.assertGreaterEqual(len(fence), 2, "H4 step 1 has no code block")
        block = step[fence[0] + 1 : fence[1]]
        joined = [
            line
            for line in block
            if "printf '%s\\n' \"JDI spawn" in line and "&& herdr pane split --current" in line
        ]
        self.assertTrue(
            joined,
            "H4 step 1's code block has no line that prints the spawn line and splits the pane",
        )
        self.assertSectionContains(
            "## H4 - Start the worker",
            "the same shell command",
            "`\"spawn_line\"`",
        )

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

    def test_h2_app(self):
        self.assertSectionContains(
            "### H2 on the app",
            "`command -v <kind>`",
            "absolute path",
            "no kinds list",
            "not ready",
            "`--no-daemon`",
            "`harnesses.codex.args`",
        )

    def test_h3_app(self):
        self.assertSectionContains(
            "### H3 on the app",
            "`hc ls --json --label jdi.agent=<name>`",
            "`herdr-app ls`",
            '"surface"',
            '"space_id"',
            '"terminal_id"',
        )

    def test_h4_app_spawn_line_and_split_are_one_command(self):
        lines = self.section_lines("### H4 on the app")
        start = next(i for i, line in enumerate(lines) if line.startswith("1. "))
        end = next(i for i, line in enumerate(lines) if line.startswith("2. "))
        self.assertTrue(
            lines[start].startswith("1. **Print the spawn line.**"),
            "H4 on the app's first numbered step is %r, not the spawn line" % lines[start],
        )
        step = lines[start:end]
        fence = [i for i, line in enumerate(step) if line.strip().startswith("```")]
        self.assertGreaterEqual(len(fence), 2, "H4 on the app step 1 has no code block")
        block = step[fence[0] + 1 : fence[1]]
        joined = [
            line
            for line in block
            if "printf '%s\\n' \"JDI spawn" in line
            and "&& herdr-app do pane.split --pane <butler pane> --direction right --argv" in line
        ]
        self.assertTrue(
            joined,
            "H4 on the app step 1's code block has no line that prints the spawn line and splits the pane",
        )

    def test_h4_app_order(self):
        body = self.section_text("### H4 on the app")
        previous = -1
        for marker in (
            "pane.split",
            "hc label <terminal> jdi.agent=<agent name>",
            "**Write the run files.**",
            "hc wait <terminal> --timeout 120",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, body, "H4 on the app lacks %r" % marker)
                position = body.index(marker)
                self.assertGreater(
                    position, previous, "H4 on the app names %r out of order" % marker
                )
                previous = position

    def test_h4_app_argv(self):
        self.assertSectionContains(
            "### H4 on the app",
            'cd -- "$1"',
            "env KEY=VALUE",
            "Expand every path",
        )

    def test_h4b_app(self):
        self.assertSectionContains(
            "#### H4b on the app",
            "hc label",
            "hc wait <terminal> --timeout 120",
        )

    def test_h5_app(self):
        heading = "### H5 on the app"
        self.assertSectionContains(
            heading,
            'hc send <terminal> "<short prompt>" --if idle --wait --timeout 300',
            "`--if idle`",
            "hc wait <terminal> --timeout 300",
            "seconds, not milliseconds",
        )
        lines = self.section_lines(heading)
        for row in (
            "| `working`",
            "| `blocked`",
            "| `idle` or `done` |",
            "| `idle` or `done` with no `result.json`",
            "| `error`",
            "| no status",
            "| overall timeout",
            "| refused as blocked",
            "| `not_started`",
            "| `reason: message`",
            "| finished",
        ):
            with self.subTest(row=row):
                self.assertTrue(
                    any(line.startswith(row) for line in lines),
                    "H5 on the app's state table has no row starting with %r" % row,
                )

    def test_h6_app(self):
        self.assertSectionContains(
            "### H6 on the app",
            "never `hc keys`",
            "never `hc send --force`",
            "never `hc interrupt`",
            "hc read <terminal> --lines 80",
            "herdr-app do agent.focus --terminal <terminal>",
        )

    def test_h8_app(self):
        self.assertSectionContains(
            "### H8 on the app",
            "herdr-app do pane.close --pane <pane_id>",
            "herdr-app do tab.close --id <tab_id> --confirmed true",
            "already gone",
        )

    def test_waves_app(self):
        self.assertSectionContains(
            "### Waves on the app",
            "herdr-app do tab.new --name jdi-wave-<first run id>",
            "--focus false",
            "hc wait <terminal> --timeout 30",
        )

    # Task 11, the UAT follow-ups (F2, F3, F5).

    def test_h1_auto_silence_covers_summaries_and_a_pinned_surface(self):
        """F5: under `auto`, silence means no mention of Herdr or H1 anywhere, summaries too."""
        self.assertSectionContains(
            "## H1 - Detect Herdr",
            "Silent means the run never mentions Herdr or H1 at all, summaries included",
            "A pinned surface whose first check fails under `auto` is silent too",
            "No check runs after the first failure",
        )

    def test_h1_quotes_the_step_zero_note(self):
        """F5: the one-time note is quoted from `## When a step fails`, naming the surface."""
        self.assertSectionContains(
            "## H1 - Detect Herdr",
            "`delegation.transport is herdr, but Herdr (<surface>) is not usable here: "
            "<failed check> returned <what came back>. Delegating natively for this run.`",
            "Copy this note; do not paraphrase it",
        )

    def test_app_wave_tab_closes_with_its_last_pane(self):
        """F3: on the app the wave tab goes when H8 closes its last pane; tab.close may find it gone."""
        self.assertNotIn("does not close itself", self.text)
        self.assertSectionContains(
            "### H8 on the app",
            "closing its last pane closes the tab with it",
            '{"error": "no tab \\"<tab_id>\\""}',
            "expected and harmless",
        )
        self.assertSectionContains(
            "### Waves on the app",
            "closing its last pane closes the tab with it",
        )

    def test_app_manifest_drops_status_reported(self):
        """F2: written before the readiness wait, `status_reported` was always false."""
        self.assertNotIn("status_reported", self.text)


if __name__ == "__main__":
    unittest.main()
