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

import pathlib
import re
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


class ModelsBlockTest(unittest.TestCase):
    """The `models:` block names roles, one per `agents/*.md`, each with a shape.

    `reference/config.md` is the only place a role's model is named, so the block
    has to stay in step with the set of roles that exist. A role that gains a
    definition and never gains a key is a role nobody can configure; a key left
    behind by a role that was renamed or removed is a key nobody can use.
    """

    def setUp(self):
        self.schema_keys = jdi_files.key_paths(jdi_files.schema_block())
        self.role_stems = {
            pathlib.Path(path).stem for path in jdi_files.markdown_files("agents")
        }
        self.assertTrue(self.schema_keys, "no keys parsed out of reference/config.md's schema")
        self.assertTrue(self.role_stems, "no role definitions found under agents/")

    def test_models_names_exactly_the_agent_roles(self):
        configured = {
            key.split(".")[1]
            for key in self.schema_keys
            if key.startswith("models.") and key.count(".") == 1
        }
        self.assertEqual(
            configured,
            self.role_stems,
            "reference/config.md's `models:` block and agents/ disagree about which "
            "roles exist. Only in the schema: %s. Only in agents/: %s. There is "
            "deliberately no `models.butler` — the Butler is the session you are "
            "already in and is never spawned."
            % (
                ", ".join(sorted(configured - self.role_stems)) or "none",
                ", ".join(sorted(self.role_stems - configured)) or "none",
            ),
        )

    def test_every_role_carries_a_model_and_a_harness(self):
        for stem in sorted(self.role_stems):
            with self.subTest(role=stem):
                expected = {"models.%s.model" % stem, "models.%s.harness" % stem}
                missing = sorted(expected - self.schema_keys)
                self.assertEqual(
                    missing,
                    [],
                    "reference/config.md's `models.%s` entry is missing %s. Every "
                    "role carries both keys: `model` is what it runs on, `harness` "
                    "is the agent CLI it runs in. Write them as a two-space-indented "
                    "block, not a flow mapping — a flow mapping loses its children "
                    "silently." % (stem, ", ".join(missing)),
                )


class DelegationBlockTest(unittest.TestCase):
    """The `delegation:` block has one key, `transport`, defaulting to `native`.

    Every later step that resolves a transport reads `delegation.transport`, so
    the key has to exist in the schema, the example, and the defaults table, and
    the schema has to say what each value does and that a role on this session's
    own CLI is never affected. The example deliberately shows a non-default value,
    per `docs/config-key-lifecycle.md`.
    """

    def setUp(self):
        self.schema = jdi_files.schema_block()
        self.schema_comments = [
            line for line in self.schema if line.lstrip().startswith("#")
        ]
        self.example = jdi_files.read("jdi.config.example.yml").split("\n")
        self.config_text = jdi_files.read("reference/config.md")

    def test_transport_is_a_schema_key(self):
        self.assertIn("delegation.transport", jdi_files.key_paths(self.schema))

    def test_schema_default_is_native(self):
        self.assertTrue(
            any(re.match(r"^  transport: native$", line) for line in self.schema),
            "reference/config.md's schema has no `  transport: native` line",
        )

    def test_schema_comment_lists_the_values(self):
        self.assertTrue(
            any("native | auto | herdr" in line for line in self.schema_comments),
            "no schema comment lists `native | auto | herdr`",
        )

    def test_schema_comment_says_own_cli_is_unaffected(self):
        self.assertTrue(
            any(
                "A role on this session's own CLI is never affected" in line
                for line in self.schema_comments
            ),
            "no schema comment says a role on this session's own CLI is never affected",
        )

    def test_notes_say_transport_only_changes_another_cli(self):
        notes = "\n".join(jdi_files.section(self.config_text, "## Notes"))
        self.assertIn("The transport only changes how a role on another CLI runs", notes)

    def test_example_value_is_not_the_default(self):
        self.assertTrue(
            any(re.match(r"^  transport: (auto|herdr)$", line) for line in self.example),
            "jdi.config.example.yml has no `  transport: auto` or `  transport: herdr` "
            "line; the example shows a configured repo, so it uses a non-default value",
        )

    def test_defaults_table_has_a_native_row(self):
        rows = jdi_files.section(self.config_text, "## Defaults when nothing is configured")
        self.assertTrue(
            any(row.startswith("| `delegation.transport` | `native`") for row in rows),
            "the defaults table has no `delegation.transport` row defaulting to `native`",
        )


class HerdBlockTest(unittest.TestCase):
    """The `herd:` block carries `kind`, `max_parallel` and `seed`, and nothing else.

    `/jdi:herd` reads those three keys. PR #5 also added `herd.args` and
    `herd.env`, which duplicated `harnesses.<kind>.{args,env}`; herd agents take
    their arguments and environment from `harnesses.<herd.kind>` instead, so the
    two keys must not come back.
    """

    def setUp(self):
        self.schema_keys = jdi_files.key_paths(jdi_files.schema_block())
        self.config_text = jdi_files.read("reference/config.md")

    def test_herd_keys_are_schema_keys(self):
        for key in ("herd.kind", "herd.max_parallel", "herd.seed"):
            with self.subTest(key=key):
                self.assertIn(key, self.schema_keys)

    def test_herd_args_and_env_are_not_schema_keys(self):
        for key in ("herd.args", "herd.env"):
            with self.subTest(key=key):
                self.assertNotIn(
                    key,
                    self.schema_keys,
                    "`%s` duplicates `harnesses.<kind>`; herd agents take their "
                    "arguments and environment from `harnesses.<herd.kind>`" % key,
                )

    def test_defaults_table_covers_herd(self):
        rows = jdi_files.section(self.config_text, "## Defaults when nothing is configured")
        for key, default in (
            ("herd.kind", "`claude`"),
            ("herd.max_parallel", "`5`"),
            ("herd.seed", "empty"),
        ):
            with self.subTest(key=key):
                self.assertTrue(
                    any(row.startswith("| `%s` | %s" % (key, default)) for row in rows),
                    "the defaults table has no `%s` row defaulting to %s" % (key, default),
                )


if __name__ == "__main__":
    unittest.main()
