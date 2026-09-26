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


if __name__ == "__main__":
    unittest.main()
