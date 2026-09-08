"""Guards the YAML frontmatter every command and role file opens with.

`bin/sync-opencode.sh`'s `convert()` splits these files on their `---`
delimiters and rewrites the frontmatter for the target harness. A file with a
missing delimiter, an absent `description`, or an empty body still looks fine in
a diff and still gets copied — it just ships a broken command to every OpenCode
user, and nothing in this repository notices today.

The block scalar is the trap worth naming. `agents/*.md` write
`description: |` and put the prose on the following indented lines, so a
`^description:\\s*\\S` regex matches the pipe character and proves only that a
pipe is present. Where the value is `|` or `>`, this module asserts the next
line instead.
"""

import re
import unittest

import jdi_files

BLOCK_SCALAR = ("|", ">")


class FrontmatterTest(unittest.TestCase):
    def files(self):
        return jdi_files.markdown_files("commands") + jdi_files.markdown_files("agents")

    def test_there_are_command_and_agent_files_to_check(self):
        commands = jdi_files.markdown_files("commands")
        agents = jdi_files.markdown_files("agents")
        self.assertTrue(commands, "no commands/*.md found; the suite would pass vacuously")
        self.assertTrue(agents, "no agents/*.md found; the suite would pass vacuously")

    def test_every_command_and_agent_has_frontmatter_with_a_description(self):
        for path in self.files():
            with self.subTest(path=path):
                split = jdi_files.split_frontmatter(jdi_files.read(path))
                self.assertIsNotNone(
                    split,
                    "%s has no well-formed `---` frontmatter; "
                    "bin/sync-opencode.sh's convert() splits on those delimiters" % path,
                )
                frontmatter, _ = split
                described = [
                    index
                    for index, line in enumerate(frontmatter)
                    if line.startswith("description:")
                ]
                self.assertEqual(
                    len(described),
                    1,
                    "%s has %d top-level `description:` keys in its frontmatter, expected 1"
                    % (path, len(described)),
                )
                index = described[0]
                value = frontmatter[index][len("description:") :].strip()

                if value in BLOCK_SCALAR or value[:1] in BLOCK_SCALAR:
                    self.assertLess(
                        index + 1,
                        len(frontmatter),
                        "%s ends its frontmatter immediately after `description: %s`, "
                        "so the block scalar is empty" % (path, value),
                    )
                    following = frontmatter[index + 1]
                    self.assertTrue(
                        following.strip(),
                        "%s follows `description: %s` with a blank line, "
                        "so the block scalar is empty" % (path, value),
                    )
                    self.assertTrue(
                        following.startswith(" ") or following.startswith("\t"),
                        "%s follows `description: %s` with an unindented line (%r), "
                        "so the block scalar is empty and that line is a sibling key"
                        % (path, value, following),
                    )
                else:
                    unquoted = value
                    if len(unquoted) >= 2 and unquoted[0] == unquoted[-1] and unquoted[0] in "\"'":
                        unquoted = unquoted[1:-1]
                    self.assertTrue(
                        unquoted.strip(),
                        "%s has an empty `description:` value (%r)" % (path, value),
                    )

    def test_every_command_and_agent_has_a_non_empty_body(self):
        for path in self.files():
            with self.subTest(path=path):
                split = jdi_files.split_frontmatter(jdi_files.read(path))
                self.assertIsNotNone(
                    split, "%s has no well-formed `---` frontmatter" % path
                )
                _, body = split
                self.assertTrue(
                    body.strip(),
                    "%s has frontmatter but no body; there is nothing for an agent to follow"
                    % path,
                )


class SkillFrontmatterTest(unittest.TestCase):
    def test_run_is_the_only_bundled_skill(self):
        self.assertEqual(
            jdi_files.skill_files(),
            ["skills/run/SKILL.md"],
            "the Codex package must expose exactly one bundled dispatcher skill",
        )

    def test_run_skill_has_valid_matching_frontmatter_and_body(self):
        path = "skills/run/SKILL.md"
        self.assertIn(
            path,
            jdi_files.skill_files(),
            "%s is missing; the jdi:run dispatcher cannot be discovered" % path,
        )
        split = jdi_files.split_frontmatter(jdi_files.read(path))
        self.assertIsNotNone(split, "%s has no well-formed frontmatter" % path)
        frontmatter, body = split
        scalars = jdi_files.frontmatter_scalars(frontmatter)
        self.assertEqual(
            set(scalars),
            {"name", "description"},
            "%s should use only the required Agent Skills frontmatter" % path,
        )
        name = scalars["name"]
        self.assertEqual(name, "run")
        self.assertEqual(name, path.split("/")[-2], "skill name must match its directory")
        self.assertRegex(name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(name), 64)
        description = scalars["description"]
        self.assertTrue(description.strip(), "skill description is empty")
        self.assertLessEqual(len(description), 1024)
        self.assertRegex(description, re.compile(r"\bJDI\b", re.IGNORECASE))
        self.assertRegex(description, re.compile(r"\bworkflow\b", re.IGNORECASE))
        self.assertRegex(description, re.compile(r"\bdispatch", re.IGNORECASE))
        self.assertTrue(body.strip(), "%s has no dispatcher instructions" % path)


if __name__ == "__main__":
    unittest.main()
