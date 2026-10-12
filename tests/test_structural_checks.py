"""Pins both ends of every required field that a Butler probe checks.

Since 1.0.11 a few properties of JDI's artefacts are no longer advice but fields:
a role writes them into a template, and the Butler refuses a hand-back that lacks
them. Each one has two ends in two files — the field in a role's template and the
check in a command — and either end can be dropped by a later edit with nothing
noticing: a field nobody checks decays back into advice, and a check for a field
the template no longer names refuses every correct hand-back. These tests hold
the pairs together.
"""

import pathlib
import re
import subprocess
import tempfile
import unittest

import jdi_files


def step(text, number):
    """The lines of a top-level numbered command step, up to the next one."""
    lines = text.split("\n")
    start = next(
        (i for i, line in enumerate(lines) if line.startswith("%d. " % number)), None
    )
    if start is None:
        raise AssertionError("step %d not found" % number)
    collected = [lines[start]]
    for line in lines[start + 1 :]:
        if re.match(r"^\d+\. ", line) or line.startswith("#"):
            break
        collected.append(line)
    return "\n".join(collected)


def flat(text):
    return " ".join(text.split())


class VerificationProbeTest(unittest.TestCase):
    """`red when:` in the Splitter's task template ⇔ the probe in split step 6."""

    def setUp(self):
        self.template = "\n".join(
            jdi_files.section(jdi_files.read("agents/splitter.md"), "## Task file shape")
        )
        self.split_step = step(jdi_files.read("commands/split.md"), 6)

    def probe(self):
        match = re.search(r"```sh\n(.*?)\n\s*```", self.split_step, re.S)
        self.assertIsNotNone(match, "split step 6 no longer carries its probe")
        return "\n".join(line[3:] for line in match.group(1).split("\n"))

    def test_the_template_and_the_probe_name_the_same_field(self):
        for field in ("red when:", "control:"):
            with self.subTest(field=field):
                self.assertIn(field, self.template)
                self.assertIn(field, self.split_step)

    def test_prep_runs_the_same_probe(self):
        self.assertIn("red when:", flat(step(jdi_files.read("commands/prep.md"), 16)))

    def test_the_probe_refuses_a_step_without_the_field_and_is_never_silent(self):
        good = "## Verification\n1. `make` — expected: ok\n   red when: build breaks\n"
        bad = "## Verification\n1. `make` — expected: ok\n2. `ls` — expected: a\n"
        with tempfile.TemporaryDirectory() as folder:
            for name, body in (("01-good.md", good), ("02-bad.md", bad)):
                (pathlib.Path(folder) / name).write_text(body, encoding="utf-8")
            out = subprocess.run(
                ["bash", "-c", self.probe()], cwd=folder, capture_output=True, text=True
            ).stdout.split("\n")
        self.assertIn("01-good.md: steps 1, missing red when: none", out)
        self.assertIn("02-bad.md: steps 2, missing red when: 1. 2.", out)


if __name__ == "__main__":
    unittest.main()
