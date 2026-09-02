"""Guards the agreement between the config schema, the example, and the defaults table.

`docs/config-key-lifecycle.md` section 2 names the half-finish this catches: a key
is added to `reference/config.md`'s schema block and then never reaches
`jdi.config.example.yml`, or reaches both and never gets a row in
`## Defaults when nothing is configured`. Either way the key is documented, a
command asks "what is the default?", and the table does not say.

The example deliberately disagrees with the schema on *values* — the schema shows
the default, the example shows a configured repo — so this module compares only
the set of key paths, never a value.
"""

import unittest

import jdi_files

# `plans.service` and `plans.location` are external-mode-only, and
# `jdi.config.example.yml` ships them commented out (the example is in `repo`
# mode, where neither applies). They are therefore schema keys with no live
# counterpart in the example, by design rather than by omission.
KNOWN_OMISSIONS = {"plans.service", "plans.location"}


class ConfigSchemaTest(unittest.TestCase):
    def setUp(self):
        self.schema_keys = jdi_files.key_paths(jdi_files.schema_block())
        self.example_keys = jdi_files.key_paths(
            jdi_files.read("jdi.config.example.yml").split("\n")
        )
        self.defaults_keys = jdi_files.defaults_table_keys()
        self.assertTrue(self.schema_keys, "no keys parsed out of reference/config.md's schema")
        self.assertTrue(self.example_keys, "no keys parsed out of jdi.config.example.yml")

    def test_schema_keys_appear_in_the_example(self):
        missing = sorted(self.schema_keys - self.example_keys - KNOWN_OMISSIONS)
        self.assertEqual(
            missing,
            [],
            "these keys are in reference/config.md's schema but not in "
            "jdi.config.example.yml: %s. Add them to the example, or, if they are "
            "deliberately commented out there, to KNOWN_OMISSIONS with a reason."
            % ", ".join(missing),
        )

    def test_example_keys_appear_in_the_schema(self):
        missing = sorted(self.example_keys - self.schema_keys)
        self.assertEqual(
            missing,
            [],
            "these keys are in jdi.config.example.yml but not in "
            "reference/config.md's schema: %s" % ", ".join(missing),
        )

    def test_known_omissions_are_still_schema_keys(self):
        stale = sorted(KNOWN_OMISSIONS - self.schema_keys)
        self.assertEqual(
            stale,
            [],
            "KNOWN_OMISSIONS names keys that no longer exist in "
            "reference/config.md's schema: %s. Remove them from the constant."
            % ", ".join(stale),
        )

    def test_every_schema_block_has_a_defaults_row(self):
        blocks = sorted(key for key in self.schema_keys if "." not in key)
        for block in blocks:
            with self.subTest(block=block):
                covered = [
                    key
                    for key in self.defaults_keys
                    if key == block or key.startswith(block + ".")
                ]
                self.assertTrue(
                    covered,
                    "the `%s` block is in reference/config.md's schema but has no row "
                    "in its `## Defaults when nothing is configured` table" % block,
                )

    def test_every_defaults_row_names_a_real_schema_key(self):
        for key in self.defaults_keys:
            with self.subTest(key=key):
                if key.endswith(".*"):
                    prefix = key[: -len(".*")]
                    matched = any(
                        schema_key == prefix or schema_key.startswith(prefix + ".")
                        for schema_key in self.schema_keys
                    )
                    self.assertTrue(
                        matched,
                        "the defaults table row `%s` matches no key under `%s` in "
                        "reference/config.md's schema" % (key, prefix),
                    )
                else:
                    self.assertIn(
                        key,
                        self.schema_keys,
                        "the defaults table row `%s` names a key that is not in "
                        "reference/config.md's schema" % key,
                    )


if __name__ == "__main__":
    unittest.main()
