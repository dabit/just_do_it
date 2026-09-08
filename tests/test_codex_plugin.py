"""Guards the native Codex package and its natural-language dispatcher contract."""

import json
import pathlib
import unittest

import jdi_files


SKILL_PATH = "skills/run/SKILL.md"
ALLOWLIST_HEADING = "## Exact command allowlist"


class DispatcherTestCase(unittest.TestCase):
    def dispatcher(self):
        self.assertIn(
            SKILL_PATH,
            jdi_files.skill_files(),
            "%s is missing; there is no dispatcher contract to inspect" % SKILL_PATH,
        )
        return jdi_files.read(SKILL_PATH)

    def dispatcher_body(self):
        split = jdi_files.split_frontmatter(self.dispatcher())
        self.assertIsNotNone(split, "%s has no well-formed frontmatter" % SKILL_PATH)
        return split[1]

    def allowlist(self):
        lines = jdi_files.section(self.dispatcher(), ALLOWLIST_HEADING)
        try:
            start = lines.index("```text")
            end = lines.index("```", start + 1)
        except ValueError:
            self.fail("%s needs one parseable fenced text allowlist" % SKILL_PATH)
        commands = [line for line in lines[start + 1 : end] if line]
        self.assertTrue(commands, "dispatcher allowlist is empty")
        self.assertEqual(len(commands), len(set(commands)), "dispatcher allowlist has duplicates")
        for command in commands:
            self.assertRegex(command, r"^[a-z]+$", "invalid allowlist token %r" % command)
        return commands

    def assertBodyContains(self, *fragments):
        body = " ".join(self.dispatcher_body().split())
        for fragment in fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(" ".join(fragment.split()), body)


class CodexManifestTest(unittest.TestCase):
    def manifest(self):
        path = jdi_files.ROOT / ".codex-plugin" / "plugin.json"
        self.assertTrue(path.is_file(), "%s is missing" % path.relative_to(jdi_files.ROOT))
        return jdi_files.codex_manifest()

    def test_manifest_is_native_minimal_and_portable(self):
        manifest = self.manifest()
        self.assertEqual(
            set(manifest),
            {"name", "version", "description", "author", "skills"},
            "the native manifest should contain identity metadata and the skills path only",
        )
        self.assertEqual(manifest["name"], "jdi")
        self.assertEqual(manifest["version"], jdi_files.plugin_version())
        claude = json.loads(jdi_files.read(".claude-plugin/plugin.json"))
        self.assertEqual(manifest["description"], claude["description"])
        self.assertEqual(manifest["author"], claude["author"])
        self.assertEqual(manifest["skills"], "./skills/")
        skills = pathlib.PurePosixPath(manifest["skills"])
        self.assertFalse(skills.is_absolute())
        self.assertNotIn("..", skills.parts)
        for forbidden in ("mcpServers", "hooks", "apps", "assets"):
            self.assertNotIn(forbidden, manifest)

    def test_manifest_and_skill_form_jdi_run(self):
        manifest = self.manifest()
        self.assertIn(
            SKILL_PATH,
            jdi_files.skill_files(),
            "%s is missing; manifest cannot expose jdi:run" % SKILL_PATH,
        )
        frontmatter, _ = jdi_files.split_frontmatter(jdi_files.read(SKILL_PATH))
        skill = jdi_files.frontmatter_scalars(frontmatter)
        self.assertEqual("%s:%s" % (manifest["name"], skill["name"]), "jdi:run")
        self.assertEqual(manifest["skills"], "./skills/")


class DispatcherContractTest(DispatcherTestCase):
    def test_allowlist_matches_commands_in_both_directions(self):
        allowlisted = set(self.allowlist())
        commands = {
            pathlib.PurePosixPath(path).stem
            for path in jdi_files.markdown_files("commands")
        }
        self.assertEqual(
            sorted(commands - allowlisted),
            [],
            "commands missing from dispatcher allowlist",
        )
        self.assertEqual(
            sorted(allowlisted - commands),
            [],
            "dispatcher exposes tokens without canonical command files",
        )

    def test_empty_input_defaults_to_allowlisted_help(self):
        self.assertIn("help", self.allowlist())
        self.assertBodyContains(
            "Absent or whitespace-only input selects `help` with an empty payload.",
            "Only absent or whitespace-only input defaults to `help`",
        )

    def test_matching_is_exact_and_rejects_unknown_or_path_like_tokens_before_paths(self):
        self.assertBodyContains(
            "Match the token exactly and case-sensitively",
            "Do not lowercase, alias, abbreviate, fuzzy-match, or probe for a file.",
            "Unknown tokens, including path-like tokens such as `../help`, `/tmp/help`, and `commands/help.md`, must be rejected",
            "before constructing a command path, reading any command file, or mutating the user's repository",
            "Report the complete supported-command list",
        )

    def test_remainder_is_opaque_and_preserved_verbatim(self):
        self.assertBodyContains(
            "The payload is the exact substring after the first whitespace separator that ends the command token.",
            "Preserve that substring verbatim, including additional whitespace, punctuation, quotes, and `$ARGUMENTS` text.",
            "Do not parse quoting, trim or normalize whitespace, expand variables, resolve paths, execute the payload, or serialize it through an argument list.",
        )

    def test_every_original_argument_placeholder_is_replaced_globally_once(self):
        self.assertBodyContains(
            "Replace every literal `$ARGUMENTS` occurrence in the original command body exactly once.",
            "The replacement is global, literal, and single-pass.",
            "Do not rescan replacement text",
            "An empty payload replaces each occurrence with the empty string.",
        )

    def test_feedback_keeps_the_multiple_placeholder_probe_non_vacuous(self):
        self.assertEqual(
            jdi_files.read("commands/feedback.md").count("$ARGUMENTS"),
            2,
            "feedback.md must retain two placeholders so global replacement is tested",
        )

    def test_butler_and_validated_command_are_read_completely(self):
        self.assertBodyContains(
            "Read `<plugin-root>/roles/butler.md` completely.",
            "Read `<plugin-root>/commands/<validated-command>.md` completely.",
            "Run the selected canonical command in this main session as the Butler",
            "Never spawn the Butler.",
        )

    def test_dependencies_resolve_only_from_the_installed_skill_root(self):
        self.assertBodyContains(
            "derive `<plugin-root>` from this loaded file's installed location",
            "Resolve every later `reference/`, `roles/`, and `agents/` dependency against that same `<plugin-root>`.",
            "Do not use the process working directory, the user's repository, the original marketplace checkout, or an ancestor search to locate JDI support files.",
            "If an installed support file is missing, report its expected installed path and stop; do not search for another copy.",
        )

    def test_dispatcher_has_no_checkout_path_or_claude_root_variable(self):
        dispatcher = self.dispatcher()
        self.assertNotIn(str(jdi_files.ROOT), dispatcher)
        self.assertNotIn("/home/", dispatcher)
        self.assertNotIn("CLAUDE_PLUGIN_ROOT", dispatcher)

    def test_dispatch_preserves_sandbox_approval_and_authorization_boundaries(self):
        self.assertBodyContains(
            "Follow the installed `reference/delegation.md` contract",
            "Preserve the active sandbox, approval policy, and authorization boundaries",
            "Neither dispatch nor delegation grants additional authority.",
        )


if __name__ == "__main__":
    unittest.main()
