"""Guards the enumerations that are maintained by hand and notice nothing on their own.

Adding a file to `reference/`, `commands/`, or `agents/` needs no adapter change —
`bin/sync-opencode.sh` is glob-driven and copies whole directories. Four lists are
not glob-driven, and they are in the documents a newcomer reads first:

- `README.md`'s "How it is put together" table, one row per reference file
- `AGENTS.md`'s "Reference files." paragraph, which names them in a sentence
- `reference/delegation.md`'s roles table, one row per `agents/*.md`
- `AGENTS.md`'s command table, one row per `commands/*.md`

Plus two counts written out in prose in the README table — "The 16 workflow
commands", "The 7 delegatable roles". `docs/config-key-lifecycle.md` section 4
says it plainly: counts in prose are citations too, and adding a file without
editing both enumerations leaves the repo describing itself incorrectly.

Every check here is bidirectional. A stale row naming a file that no longer
exists is the same class of wrong as a missing one.
"""

import re
import unittest

import jdi_files


def backticked(lines, prefix):
    """Every `` `<prefix>...md` `` mention across a set of lines."""
    found = set()
    for line in lines:
        found.update(re.findall(r"`(%s[^`]+\.md)`" % re.escape(prefix), line))
    return found


def table_rows(lines):
    """Only the markdown table rows.

    Scoping the scans to rows keeps a passing *prose* mention of a file from
    standing in for the table row the enumeration actually owes it.
    """
    return [line for line in lines if line.startswith("|")]


class ReferenceFileEnumerationTest(unittest.TestCase):
    def setUp(self):
        self.actual = set(jdi_files.markdown_files("reference"))
        self.assertTrue(self.actual, "no reference/*.md found; the check would be vacuous")

    def test_reference_files_are_enumerated_in_readme_and_agents_md(self):
        enumerations = {
            "README.md's `## How it is put together` table": backticked(
                table_rows(
                    jdi_files.section(
                        jdi_files.read("README.md"), "## How it is put together"
                    )
                ),
                "reference/",
            ),
            "AGENTS.md's `**Reference files.**` paragraph": backticked(
                jdi_files.paragraph_starting_with(
                    jdi_files.read("AGENTS.md"), "**Reference files.**"
                ),
                "reference/",
            ),
        }
        for document, listed in enumerations.items():
            with self.subTest(document=document):
                missing = sorted(self.actual - listed)
                self.assertEqual(
                    missing,
                    [],
                    "%s does not name %s. Both enumerations are maintained by hand."
                    % (document, ", ".join(missing)),
                )
                stale = sorted(listed - self.actual)
                self.assertEqual(
                    stale,
                    [],
                    "%s names %s, which does not exist"
                    % (document, ", ".join(stale)),
                )


class DelegationTableTest(unittest.TestCase):
    def test_every_agent_file_has_a_row_in_the_delegation_roles_table(self):
        actual = set(jdi_files.markdown_files("agents"))
        listed = backticked(
            table_rows(
                jdi_files.section(jdi_files.read("reference/delegation.md"), "## Roles")
            ),
            "agents/",
        )
        self.assertTrue(listed, "no `agents/*.md` rows found in reference/delegation.md's roles table")

        missing = sorted(actual - listed)
        self.assertEqual(
            missing,
            [],
            "reference/delegation.md's roles table does not name %s" % ", ".join(missing),
        )
        stale = sorted(listed - actual)
        self.assertEqual(
            stale,
            [],
            "reference/delegation.md's roles table names %s, which does not exist"
            % ", ".join(stale),
        )


class CommandTableTest(unittest.TestCase):
    def test_every_command_file_has_a_row_in_the_agents_md_command_table(self):
        actual = set(jdi_files.markdown_files("commands"))
        listed = backticked(
            table_rows(
                jdi_files.section(jdi_files.read("AGENTS.md"), "## The manual invocation")
            ),
            "commands/",
        )
        self.assertTrue(listed, "no `commands/*.md` rows found in AGENTS.md's command table")

        missing = sorted(actual - listed)
        self.assertEqual(
            missing,
            [],
            "AGENTS.md's command table does not name %s" % ", ".join(missing),
        )
        stale = sorted(listed - actual)
        self.assertEqual(
            stale,
            [],
            "AGENTS.md's command table names %s, which does not exist" % ", ".join(stale),
        )


class ReadmeCountTest(unittest.TestCase):
    """The digits in README.md's `## How it is put together` table."""

    def counted(self, row_prefix, pattern):
        lines = jdi_files.section(jdi_files.read("README.md"), "## How it is put together")
        rows = [line for line in table_rows(lines) if line.startswith(row_prefix)]
        self.assertEqual(
            len(rows),
            1,
            "expected exactly one README.md row starting %r, found %d"
            % (row_prefix, len(rows)),
        )
        match = re.search(pattern, rows[0])
        self.assertIsNotNone(
            match,
            "README.md's row %r no longer matches %r, so its count cannot be checked"
            % (rows[0], pattern),
        )
        return int(match.group(1))

    def test_the_readme_command_count_matches_the_commands_directory(self):
        stated = self.counted("| `commands/` |", r"The (\d+) workflow commands")
        actual = len(jdi_files.markdown_files("commands"))
        self.assertEqual(
            stated,
            actual,
            "README.md says %d workflow commands; commands/ holds %d" % (stated, actual),
        )

    def test_the_readme_role_count_matches_the_agents_directory(self):
        stated = self.counted("| `agents/` |", r"The (\d+) delegatable roles")
        actual = len(jdi_files.markdown_files("agents"))
        self.assertEqual(
            stated,
            actual,
            "README.md says %d delegatable roles; agents/ holds %d" % (stated, actual),
        )


if __name__ == "__main__":
    unittest.main()
