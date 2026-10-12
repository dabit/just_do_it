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


def step(text, number, title=""):
    """The lines of a numbered command step, up to the next one.

    `title` picks between steps that share a number, as yolo's nested loops do.
    """
    lines = text.split("\n")
    start = next(
        (
            i
            for i, line in enumerate(lines)
            if line.startswith("%d. " % number) and title in line
        ),
        None,
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
    """The Splitter's task-template fields ⇔ the probe in split step 6."""

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
        for field in ("red when:", "control:", "at base:", "compliant hits:"):
            with self.subTest(field=field):
                self.assertIn(field, self.template)
                self.assertIn(field, self.split_step)

    def test_prep_runs_the_same_probe(self):
        prep = flat(step(jdi_files.read("commands/prep.md"), 16))
        for field in ("red when:", "at base:"):
            with self.subTest(field=field):
                self.assertIn(field, prep)

    def test_the_probe_refuses_a_step_without_the_field_and_is_never_silent(self):
        good = (
            "## Verification\n1. `make` — expected: ok\n   red when: build breaks\n"
            "2. `grep -c x f` — expected: 1\n   red when: x gone\n   at base: 1\n"
        )
        bad = "## Verification\n1. `make` — expected: ok\n2. `grep x f` — expected: a\n"
        with tempfile.TemporaryDirectory() as folder:
            for name, body in (("01-good.md", good), ("02-bad.md", bad)):
                (pathlib.Path(folder) / name).write_text(body, encoding="utf-8")
            out = subprocess.run(
                ["bash", "-c", self.probe()], cwd=folder, capture_output=True, text=True
            ).stdout.split("\n")
        self.assertIn(
            "01-good.md: steps 2, missing red when: none / missing at base: none", out
        )
        self.assertIn("02-bad.md: steps 2, missing red when: 1. 2. / missing at base: 2.", out)


class RefusedFormsTest(unittest.TestCase):
    """The Splitter's refused-forms list ⇔ the grep split step 6 runs for it."""

    def test_the_list_exists_and_both_commands_cite_it(self):
        splitter = jdi_files.read("agents/splitter.md").split("\n")
        self.assertIn("### Refused in a Verification step", splitter)
        for path, number in (("commands/split.md", 6), ("commands/prep.md", 16)):
            with self.subTest(path=path):
                text = flat(step(jdi_files.read(path), number))
                self.assertIn("*Refused in a Verification step*", text)

    def test_the_grep_reaches_every_greppable_form(self):
        text = step(jdi_files.read("commands/split.md"), 6)
        match = re.search(r"`grep -cE '([^']+)' \[0-9\]\*\.md`", text)
        self.assertIsNotNone(match, "split step 6 no longer greps for the refused forms")
        pattern = re.compile(match.group(1))  # this ERE is also a Python regex
        for line in ("1. `git diff -- a.rb`", "2. `git diff $(git merge-base a b)..HEAD`",
                     "3. `git status --short`", "4. `sed -n 1p app/x.rb:42`"):
            with self.subTest(line=line):
                self.assertRegex(line, pattern)


class TestingStrategyFieldsTest(unittest.TestCase):
    """The Planner's per-case fields ⇔ the Butler's check in plan step 7 and prep step 15."""

    FIELDS = ("at HEAD:", "reddened by:", "reaches the guard:")

    def test_every_end_names_every_field(self):
        ends = (
            ("agents/planner.md", flat(jdi_files.read("agents/planner.md"))),
            ("commands/plan.md", flat(step(jdi_files.read("commands/plan.md"), 7))),
            ("commands/prep.md", flat(step(jdi_files.read("commands/prep.md"), 15))),
        )
        for path, text in ends:
            for field in self.FIELDS:
                with self.subTest(path=path, field=field):
                    self.assertIn(field, text)

    def test_the_check_counts_only_the_testing_strategy(self):
        text = step(jdi_files.read("commands/plan.md"), 7)
        match = re.search(r"```sh\n(.*?)\n\s*```", text, re.S)
        self.assertIsNotNone(match, "plan step 7 no longer carries its check")
        probe = "\n".join(line[3:] for line in match.group(1).split("\n"))
        plan = (
            "## Testing Strategy\n- a — at HEAD: red; reddened by: m; reaches the guard: s\n"
            "- b — at HEAD: green\n## Risks\n- at HEAD: not a case\n"
        )
        with tempfile.TemporaryDirectory() as folder:
            (pathlib.Path(folder) / "PLAN.md").write_text(plan, encoding="utf-8")
            out = subprocess.run(
                ["bash", "-c", probe], cwd=folder, capture_output=True, text=True
            ).stdout.split("\n")
        for line in ("at HEAD: 2", "reddened by: 1", "reaches the guard: 1"):
            with self.subTest(line=line):
                self.assertIn(line, out)


class CollectedCountTest(unittest.TestCase):
    """The Executor's collected-count receipt is a duty and a return, not one without the other."""

    def test_the_duty_and_the_return_both_stand(self):
        text = jdi_files.read("agents/executor.md")
        self.assertIn("more collected than its baseline", flat(text))
        returns = flat("\n".join(jdi_files.section(text, "## What it returns")))
        self.assertIn("collected count before and after", returns)
        self.assertIn("`control:`", returns)


class PremisesSlotTest(unittest.TestCase):
    """The premise tags in delegation.md ⇔ every role's inputs ⇔ every brief that fills them."""

    BRIEFS = (
        ("commands/prep.md", 8, ""),
        ("commands/prep.md", 13, ""),
        ("commands/plan.md", 6, ""),
        ("commands/research.md", 3, ""),
        ("commands/execute.md", 5, ""),
        ("commands/next.md", 7, ""),
        ("commands/yolo.md", 3, "Delegate to the Executor"),
    )

    def test_the_slot_is_defined_with_both_tags(self):
        section = flat("\n".join(
            jdi_files.section(jdi_files.read("reference/delegation.md"), "## Premises in a brief")
        ))
        tags = ("`VERIFIED (<command or file:line>)`", "`ASSUMED`", "cites; it does not restate")
        for tag in tags:
            with self.subTest(tag=tag):
                self.assertIn(tag, section)

    def test_every_role_receives_the_slot(self):
        for path in jdi_files.markdown_files("agents"):
            with self.subTest(path=path):
                receives = flat("\n".join(
                    jdi_files.section(jdi_files.read(path), "## What it receives")
                ))
                self.assertIn("Premises in a brief", receives)
                self.assertIn("`ASSUMED`", receives)

    def test_every_brief_points_at_the_slot(self):
        for path, number, title in self.BRIEFS:
            with self.subTest(path=path, step=number):
                text = flat(step(jdi_files.read(path), number, title))
                self.assertIn("Premises in a brief", text)


class PremisePassTest(unittest.TestCase):
    """The Researcher's `§0 Premises` return ⇔ the Butler's check before relaying findings."""

    def test_the_return_opens_with_the_premise_pass(self):
        returns = jdi_files.section(jdi_files.read("agents/researcher.md"), "## What it returns")
        first = flat("\n".join(returns)).split(" - ")[0]
        self.assertIn("`§0 Premises`", first)
        self.assertIn("`REFUTED: none — checked: <list>`", flat("\n".join(returns)))

    def test_every_receiving_step_checks_for_it(self):
        for path, number in (
            ("commands/research.md", 3),
            ("commands/research.md", 4),
            ("commands/prep.md", 8),
            ("commands/prep.md", 9),
        ):
            with self.subTest(path=path, step=number):
                self.assertIn("§0 Premises", flat(step(jdi_files.read(path), number)))


class BlockerRecordTest(unittest.TestCase):
    """The blocker-record fields ⇔ every role and rule that writes or relays a blocker."""

    FIELDS = ("Tried:", "Message:", "Arguments checked against the schema: yes", "Per target:",
              "Observed:")
    CITERS = ("agents/researcher.md", "agents/planner.md", "agents/executor.md",
              "roles/butler.md", "reference/tracker.md")

    def test_the_record_names_every_field(self):
        section = "\n".join(
            jdi_files.section(jdi_files.read("reference/delegation.md"), "## Blocker records")
        )
        for field in self.FIELDS:
            with self.subTest(field=field):
                self.assertIn(field, section)

    def test_every_writer_cites_the_record(self):
        for path in self.CITERS:
            with self.subTest(path=path):
                self.assertIn("*Blocker record*", flat(jdi_files.read(path)))


if __name__ == "__main__":
    unittest.main()
