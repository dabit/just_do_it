"""Guards the version that lives in three places and must be identical in all of them.

`README.md:151-154` is the reason this matters more than it looks: `claude plugin
update` compares **versions, not content**. A prompt edit shipped without a bump
reports "already at the latest version" and reaches nobody. A bump applied to
`.claude-plugin/plugin.json` and forgotten in `.claude-plugin/marketplace.json`
is the same failure with an extra step, and `docs/config-key-lifecycle.md`
section 6 records that a release here is exactly two JSON edits plus a CHANGELOG
entry — there are no git tags to fall back on.
"""

import unittest

import jdi_files


class VersionTest(unittest.TestCase):
    def test_plugin_and_marketplace_versions_match(self):
        plugin = jdi_files.plugin_version()
        marketplace = jdi_files.marketplace_version()
        self.assertEqual(
            plugin,
            marketplace,
            ".claude-plugin/plugin.json says %r and .claude-plugin/marketplace.json "
            "says %r; both must carry the same version or `claude plugin update` "
            "ships nothing" % (plugin, marketplace),
        )

    def test_the_changelog_leads_with_the_shipped_version(self):
        plugin = jdi_files.plugin_version()
        changelog = jdi_files.changelog_version()
        self.assertEqual(
            plugin,
            changelog,
            ".claude-plugin/plugin.json says %r but CHANGELOG.md's newest entry is "
            "`## %s`; a release is two JSON edits and a CHANGELOG entry, and this one "
            "is incomplete" % (plugin, changelog),
        )


if __name__ == "__main__":
    unittest.main()
