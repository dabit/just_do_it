"""Guards the four release authorities that must carry one shipped version.

`README.md:164-168` is the reason this matters more than it looks: cached plugin
updates compare **versions, not content**. A prompt edit shipped without a bump
reports "already at the latest version" and reaches nobody. A bump applied to
only one of `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and
`.claude-plugin/marketplace.json` is the same failure with an extra step, and
`docs/config-key-lifecycle.md` section 6 records that a release here is exactly
three JSON edits plus a CHANGELOG entry — there are no git tags to fall back on.
"""

import unittest

import jdi_files


class VersionTest(unittest.TestCase):
    def test_claude_codex_and_marketplace_versions_match(self):
        claude = jdi_files.plugin_version()
        codex = jdi_files.codex_plugin_version()
        marketplace = jdi_files.marketplace_version()
        self.assertEqual(
            (claude, claude),
            (codex, marketplace),
            ".claude-plugin/plugin.json says %r, .codex-plugin/plugin.json says %r, "
            "and .claude-plugin/marketplace.json says %r; all three JSON version "
            "authorities must match or cached plugin updates ship an incomplete "
            "release" % (claude, codex, marketplace),
        )

    def test_the_changelog_leads_with_the_shipped_version(self):
        plugin = jdi_files.plugin_version()
        changelog = jdi_files.changelog_version()
        self.assertEqual(
            plugin,
            changelog,
            ".claude-plugin/plugin.json says %r but CHANGELOG.md's newest entry is "
            "`## %s`; a release is three JSON edits and a CHANGELOG entry, and this "
            "one is incomplete" % (plugin, changelog),
        )


class ReleaseMetadataTest(unittest.TestCase):
    def test_marketplace_description_is_harness_neutral(self):
        marketplace = jdi_files.marketplace_manifest()
        descriptions = [marketplace["description"]]
        descriptions.extend(plugin["description"] for plugin in marketplace["plugins"])
        for description in descriptions:
            with self.subTest(description=description):
                self.assertNotIn(
                    "Claude Code",
                    description,
                    "marketplace descriptions must present JDI as a harness-neutral "
                    "workflow, not a Claude-only package",
                )


class ReleaseDocumentationTest(unittest.TestCase):
    def test_release_mechanics_names_all_version_authorities(self):
        release_mechanics = "\n".join(
            jdi_files.section(
                jdi_files.read("docs/config-key-lifecycle.md"),
                "## 6. Release mechanics",
            )
        )
        authorities = (
            ".claude-plugin/plugin.json",
            ".codex-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            "CHANGELOG.md",
        )
        for authority in authorities:
            with self.subTest(authority=authority):
                self.assertIn(
                    authority,
                    release_mechanics,
                    "release mechanics must name all four version authorities; "
                    "%s is missing" % authority,
                )

    def test_release_counts_and_checklist_include_the_codex_manifest(self):
        document = jdi_files.read("docs/config-key-lifecycle.md")
        expected_statements = (
            "Nine files are the **floor**",
            "three JSON version edits",
            "**Three version files, and they must match.**",
            "The nine mandatory files:",
            "- [ ] `.codex-plugin/plugin.json` — the **same** version.",
        )
        for statement in expected_statements:
            with self.subTest(statement=statement):
                self.assertIn(
                    statement,
                    document,
                    "release guidance must include the Codex manifest and use the "
                    "three-JSON/nine-file counts; missing %r" % statement,
                )


if __name__ == "__main__":
    unittest.main()
