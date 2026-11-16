"""The user-facing docs describe `delegation.transport`: init asks, help and README explain.

`/jdi:init` asks the transport question only inside Herdr, so it must name the key and perform
H1 from `reference/herdr.md` rather than guess from the harness name. `/jdi:help` and the README
must say what `auto` and `herdr` change: a role on another CLI runs in its own pane, one pane per
task in a wave, while a role on this session's own CLI stays a subagent.
"""

import unittest

import jdi_files


class TransportDocumentationTest(unittest.TestCase):
    def test_init_description_names_the_transport_question(self):
        split = jdi_files.split_frontmatter(jdi_files.read("commands/init.md"))
        self.assertIsNotNone(split, "commands/init.md has no frontmatter")
        description = jdi_files.frontmatter_scalars(split[0])["description"]
        self.assertIn("how delegated roles reach their own process", description)
        self.assertIn("which Herdr they use", description)

    def test_init_asks_through_h1(self):
        text = jdi_files.read("commands/init.md")
        self.assertIn("`delegation.transport`", text)
        self.assertIn("perform **H1**", text)

    def test_help_has_a_separate_agent_processes_section(self):
        text = jdi_files.read("commands/help.md")
        jdi_files.section(text, "### Separate agent processes")
        opening = " ".join(
            jdi_files.paragraph_starting_with(text, "Explain the Just Do It")
        )
        self.assertIn("delegation transport", opening)

    def test_readme_has_a_herdr_section_naming_the_key(self):
        text = jdi_files.read("README.md")
        body = "\n".join(
            jdi_files.section(text, "### Separate agent processes under Herdr")
        )
        self.assertIn("`delegation.transport`", body)

    def test_readme_herdr_section_describes_waves_and_own_cli_roles(self):
        text = jdi_files.read("README.md")
        body = " ".join(
            jdi_files.section(text, "### Separate agent processes under Herdr")
        )
        self.assertIn("one pane per task", body)
        self.assertIn("stays a subagent", body)
        self.assertNotIn("waves unaffected", body)


class HerdrSurfaceDocumentationTest(unittest.TestCase):
    """`herdr.surface` is offered by init and explained by help and the README."""

    def test_init_offers_the_surface_key(self):
        text = jdi_files.read("commands/init.md")
        self.assertIn("offer `herdr.surface`", text)

    def test_help_opening_names_the_pinned_surface(self):
        text = jdi_files.read("commands/help.md")
        opening = " ".join(
            jdi_files.paragraph_starting_with(text, "Explain the Just Do It")
        )
        self.assertIn("which Herdr surface", opening)

    def test_help_separate_agent_processes_names_the_key(self):
        text = jdi_files.read("commands/help.md")
        body = " ".join(jdi_files.section(text, "### Separate agent processes"))
        self.assertIn("`herdr.surface`", body)

    def test_help_init_row_names_the_surface(self):
        text = jdi_files.read("commands/help.md")
        rows = [
            line
            for line in text.split("\n")
            if line.startswith("|") and "/jdi:init" in line
        ]
        self.assertTrue(rows, "no /jdi:init row in the help command table")
        self.assertIn("Herdr surface", rows[0])

    def test_readme_herdr_section_names_the_surface_key(self):
        text = jdi_files.read("README.md")
        body = " ".join(
            jdi_files.section(text, "### Separate agent processes under Herdr")
        )
        self.assertIn("`herdr.surface`", body)
        self.assertIn("the Herdr app", body)

    def test_readme_init_snippet_comment_names_which_herdr(self):
        text = jdi_files.read("README.md")
        comments = [
            line for line in text.split("\n") if line.startswith("/jdi:init") and "# asks about" in line
        ]
        self.assertTrue(comments, "no commented /jdi:init snippet in the README")
        self.assertIn("which Herdr", comments[0])

    def test_readme_init_prose_names_which_herdr(self):
        text = jdi_files.read("README.md")
        prose = " ".join(
            jdi_files.paragraph_starting_with(text, "`/jdi:init` asks about the tracker")
        )
        self.assertIn("which Herdr", prose)


def normalized(text):
    return " ".join(text.split())


class HerdCleanupDocumentationTest(unittest.TestCase):
    """`/jdi:herd --cleanup [<herd-id>]` is named by help, the README and the 1.0.13 CHANGELOG.

    The AGENTS.md row for `commands/herd.md` gains a matching clause too, but no test pins it.
    """

    def test_help_herd_row_names_cleanup(self):
        text = jdi_files.read("commands/help.md")
        rows = [line for line in text.split("\n") if line.startswith("| `/jdi:herd` |")]
        self.assertTrue(rows, "no /jdi:herd row in the help command table")
        self.assertIn("`--cleanup`", rows[0])

    def test_readme_cleanup_paragraph(self):
        text = jdi_files.read("README.md")
        paragraph = normalized(
            " ".join(jdi_files.paragraph_starting_with(text, "`/jdi:herd --cleanup "))
        )
        self.assertIn("herd record", paragraph)
        self.assertIn("never committed", paragraph)
        self.assertIn("asks once", paragraph)

    def test_changelog_names_cleanup(self):
        text = jdi_files.read("CHANGELOG.md")
        body = normalized("\n".join(jdi_files.section(text, "## 1.0.13")))
        self.assertIn("`/jdi:herd --cleanup [<herd-id>]`", body)


if __name__ == "__main__":
    unittest.main()
