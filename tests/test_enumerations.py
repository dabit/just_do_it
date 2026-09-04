"""Guards the enumerations that are maintained by hand and notice nothing on their own.

Adding a file to `reference/`, `commands/`, or `agents/` needs no adapter change —
`bin/sync-opencode.sh` is glob-driven and copies whole directories. Six lists are
not glob-driven, and they are in the documents a newcomer reads first:

- `README.md`'s "How it is put together" table, one row per reference file
- `AGENTS.md`'s "Reference files." paragraph, which names them in a sentence
- `reference/delegation.md`'s roles table, one row per `agents/*.md`
- `AGENTS.md`'s command table, one row per `commands/*.md`
- `commands/help.md`'s command table, one row per `commands/*.md` — the list a
  user actually sees when they run `/jdi:help`
- `roles/butler.md`'s ownership table, whose rows *group* commands — one row can
  name three, so it is every mention across the rows that must add up, not one
  row per command

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


def slash_commands(lines):
    """Every `` `/jdi:<name>` `` mention across a set of lines.

    A mention, not a row: the tables these guard do not agree on how many
    commands a row may name, and counting mentions is the only reading that
    works for both.
    """
    found = set()
    for line in lines:
        found.update(re.findall(r"`(/jdi:[A-Za-z0-9_-]+)`", line))
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


class HelpCommandTableTest(unittest.TestCase):
    """The table a user actually sees when they run `/jdi:help`.

    Scoped to the table rows, so the `**On the Feedbacker:**` prose in the same
    section — which mentions `/jdi:feedback` — cannot stand in for the row the
    enumeration owes it.
    """

    def test_every_command_file_has_a_row_in_the_help_command_table(self):
        actual = jdi_files.command_slugs()
        listed = slash_commands(
            table_rows(jdi_files.section(jdi_files.read("commands/help.md"), "### Commands"))
        )
        self.assertTrue(listed, "no `/jdi:...` mentions found in commands/help.md's command table")

        missing = sorted(actual - listed)
        self.assertEqual(
            missing,
            [],
            "commands/help.md's command table does not name %s" % ", ".join(missing),
        )
        stale = sorted(listed - actual)
        self.assertEqual(
            stale,
            [],
            "commands/help.md's command table names %s, which does not exist"
            % ", ".join(stale),
        )


class ButlerOwnershipTableTest(unittest.TestCase):
    """`roles/butler.md`'s table of what the Butler owns, command by command.

    Its rows *group* commands — one row names `/jdi:done`, `/jdi:status` and
    `/jdi:help` together — so what must add up is every mention across the rows,
    not one row per command.
    """

    def test_every_command_file_is_named_in_the_butler_ownership_table(self):
        actual = jdi_files.command_slugs()
        listed = slash_commands(
            table_rows(
                jdi_files.section(jdi_files.read("roles/butler.md"), "## What the Butler owns")
            )
        )
        self.assertTrue(
            listed, "no `/jdi:...` mentions found in roles/butler.md's ownership table"
        )

        missing = sorted(actual - listed)
        self.assertEqual(
            missing,
            [],
            "roles/butler.md's ownership table does not name %s" % ", ".join(missing),
        )
        stale = sorted(listed - actual)
        self.assertEqual(
            stale,
            [],
            "roles/butler.md's ownership table names %s, which does not exist"
            % ", ".join(stale),
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
