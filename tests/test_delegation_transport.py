"""Guards the delegation transport: how rung 2 reaches another CLI, and where Herdr is named.

`delegation.transport` (`native | auto | herdr`) changes how rung 2 of *How to
delegate* runs a role on another CLI: through that CLI's non-interactive mode,
or as its interactive agent in a Herdr pane. A role on this session's own CLI
never reaches Herdr. Every Herdr invocation lives in `reference/herdr.md` and
nowhere else, so a command or role file that grows its own `herdr pane ...`
line has forked the mechanism. These tests pin the selection rules, the
confinement, and the Butler's one-phase-at-a-time rule.
"""

import re
import unittest

import jdi_files

HERDR_REFERENCE = "reference/herdr.md"

HERDR_COMMAND = re.compile(
    r"\bherdr (agent|pane|workspace|worktree|tab|status|integration|server|session"
    r"|notification|terminal)\b"
)
CONFINED_PATTERNS = (HERDR_COMMAND, re.compile(r"HERDR_"), re.compile(r"AskUserQuestion"))


def normalized(path):
    return " ".join(jdi_files.read(path).split())


class TransportSelectionTest(unittest.TestCase):
    longMessage = False

    def guidance(self):
        return normalized("reference/delegation.md")

    def test_transport_section_and_selection_rules_are_present(self):
        guidance = self.guidance()
        for fragment in (
            "## Choosing the transport",
            "`delegation.transport`",
            "`reference/herdr.md`",
            "A role on this session's own CLI never runs under Herdr",
            "rung 2 runs the other CLI as its interactive agent in a Herdr pane",
            "one pane per task",
            "A Butler runs one phase at a time.",
            "Herdr's `kinds:` line lists the kinds it supports",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(
                    fragment, guidance, "reference/delegation.md lacks %r" % fragment
                )

    def test_the_three_rungs_keep_their_order(self):
        guidance = self.guidance()
        first = guidance.index("**1. The harness has first-class subagents**")
        second = guidance.index("**2. A second non-interactive session**")
        third = guidance.index("**3. Neither.**")
        self.assertLess(first, second)
        self.assertLess(second, third)

    def test_superseded_wording_is_gone(self):
        guidance = self.guidance()
        for fragment in (
            "**0. A separate agent",
            "asked to watch the run",
            "Herdr does not report the kind installed",
            "Not `herdr agent start`",
            "herdr pane run",
        ):
            with self.subTest(fragment=fragment):
                self.assertNotIn(
                    fragment, guidance, "reference/delegation.md still says %r" % fragment
                )


class HerdrConfinementTest(unittest.TestCase):
    def confined_files(self):
        files = []
        for directory in ("commands", "agents", "roles", "reference"):
            files.extend(jdi_files.markdown_files(directory))
        files.append("skills/run/SKILL.md")
        return [path for path in files if path != HERDR_REFERENCE]

    def test_no_herdr_command_variable_or_question_tool_outside_the_reference(self):
        for path in self.confined_files():
            for number, line in enumerate(jdi_files.read(path).split("\n"), start=1):
                for pattern in CONFINED_PATTERNS:
                    with self.subTest(path=path, line=number, pattern=pattern.pattern):
                        self.assertIsNone(
                            pattern.search(line),
                            "%s:%d names %r; every Herdr step belongs in %s"
                            % (path, number, line.strip(), HERDR_REFERENCE),
                        )


class ButlerSequentialTest(unittest.TestCase):
    longMessage = False

    def test_butler_runs_one_phase_at_a_time_and_resolves_the_transport(self):
        butler = normalized("roles/butler.md")
        for fragment in ("one phase at a time", "a delegation transport"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, butler, "roles/butler.md lacks %r" % fragment)


class FeedbackerIndependenceTest(unittest.TestCase):
    longMessage = False

    def test_reviewer_differs_in_model_and_harness(self):
        for path in ("agents/feedbacker.md", "reference/delegation.md"):
            with self.subTest(path=path):
                self.assertIn(
                    "same model and harness",
                    normalized(path),
                    "%s lacks 'same model and harness'" % path,
                )

    def test_feedback_command_picks_a_different_model_or_harness(self):
        self.assertIn(
            "a different model or a different harness",
            normalized("commands/feedback.md"),
            "commands/feedback.md lacks 'a different model or a different harness'",
        )


class ArchitectureDocTest(unittest.TestCase):
    longMessage = False

    ARCHITECTURE = "docs/delegation-transport-architecture.md"

    def architecture(self):
        self.assertTrue(
            (jdi_files.ROOT / self.ARCHITECTURE).is_file(),
            "%s does not exist" % self.ARCHITECTURE,
        )
        return jdi_files.read(self.ARCHITECTURE)

    def test_architecture_doc_has_the_pinned_headings(self):
        lines = self.architecture().split("\n")
        for heading in (
            "## Two layers",
            "## Result contract",
            "## Waves and other roles",
            "## Live validation matrix",
            "## Relationship to PR #5",
        ):
            with self.subTest(heading=heading):
                self.assertIn(
                    heading, lines, "%s lacks the heading %r" % (self.ARCHITECTURE, heading)
                )
        self.assertNotIn(
            "## Extending to other roles and waves",
            lines,
            "%s still has the superseded heading" % self.ARCHITECTURE,
        )

    def test_architecture_doc_states_the_backend_and_repair_rules(self):
        text = " ".join(self.architecture().split())
        for fragment in (
            "only when the harness differs",
            "same-harness control",
            "`reference/herdr.md`",
            "validate, never repair",
            "detect, never repair",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(
                    fragment, text, "%s lacks %r" % (self.ARCHITECTURE, fragment)
                )

    def test_adapter_doc_names_the_transport_in_capability_based_delegation(self):
        section = " ".join(
            jdi_files.section(
                jdi_files.read("docs/harness-adapter-architecture.md"),
                "## Capability-Based Delegation",
            )
        )
        self.assertIn(
            "`delegation.transport`",
            section,
            "docs/harness-adapter-architecture.md's Capability-Based Delegation "
            "section lacks `delegation.transport`",
        )

    def test_lifecycle_doc_citations_are_corrected(self):
        lifecycle = jdi_files.read("docs/config-key-lifecycle.md")
        self.assertIn(
            "`commands/prep.md:28-29`",
            lifecycle,
            "docs/config-key-lifecycle.md lacks `commands/prep.md:28-29`",
        )
        self.assertNotIn(
            "are all `1.0.6`",
            lifecycle,
            "docs/config-key-lifecycle.md still pins a literal version",
        )


if __name__ == "__main__":
    unittest.main()
