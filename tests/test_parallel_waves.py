"""Guards the wave vocabulary that parallel execution hangs on.

Since 1.0.7 the Splitter cuts a plan for parallelism and `/jdi:execute`,
`/jdi:next` and `/jdi:yolo` run a **wave** — every task whose dependencies are
done — at once. The mechanics live in two reference sections and two role
sections, and six command files point at them by name. Nothing notices when a
heading is renamed under a command that still cites it, or when one command
quietly goes back to picking "the first unchecked task" while the others run the
whole wave — and a `/jdi:done` that marks one task after a wave of three leaves
two tasks' work staged with no commit of their own.
"""

import unittest

import jdi_files

WAVE_RUNNERS = ("commands/execute.md", "commands/next.md", "commands/yolo.md")
WAVE_READERS = WAVE_RUNNERS + ("commands/done.md", "commands/status.md")


class WaveSectionsTest(unittest.TestCase):
    def test_the_sections_the_commands_cite_exist(self):
        sections = (
            ("reference/plan-store.md", "## Waves"),
            ("reference/delegation.md", "## Delegating several roles at once"),
            ("agents/splitter.md", "## Analysing for parallelism"),
            ("agents/executor.md", "## Running alongside other Executors"),
        )
        for path, heading in sections:
            with self.subTest(path=path, heading=heading):
                self.assertIn(
                    heading,
                    jdi_files.read(path).split("\n"),
                    "%s no longer has a `%s` section, which the commands and the "
                    "Butler cite by name" % (path, heading),
                )

    def test_every_command_that_reads_a_wave_cites_the_definition(self):
        for path in WAVE_READERS:
            with self.subTest(path=path):
                text = jdi_files.read(path)
                self.assertIn("*Waves*", text, "%s never cites *Waves*" % path)
                self.assertIn("reference/plan-store.md", text)

    def test_every_command_that_runs_a_wave_cites_concurrent_delegation(self):
        for path in WAVE_RUNNERS:
            with self.subTest(path=path):
                self.assertIn(
                    "*Delegating several",
                    jdi_files.read(path),
                    "%s delegates a wave without pointing at how several roles are "
                    "run at once, or what to say when they cannot be" % path,
                )


class SingleTaskSelectionTest(unittest.TestCase):
    def test_no_command_still_picks_only_the_first_unchecked_task(self):
        for path in jdi_files.markdown_files("commands"):
            with self.subTest(path=path):
                self.assertNotIn(
                    "first unchecked task",
                    " ".join(jdi_files.read(path).split()),
                    "%s selects a single task; a wave is every unchecked task whose "
                    "dependencies are done" % path,
                )


class CommitByPathTest(unittest.TestCase):
    def test_every_command_that_marks_tasks_done_commits_by_path(self):
        for path in ("commands/done.md", "commands/next.md", "commands/yolo.md"):
            with self.subTest(path=path):
                text = " ".join(jdi_files.read(path).split())
                self.assertIn("by path", text)
                self.assertNotIn(
                    "Stage everything",
                    text,
                    "%s stages everything, which folds a whole wave into one commit" % path,
                )


if __name__ == "__main__":
    unittest.main()
