"""Guards the step-0 transport line and the hand-off sites that depend on it.

Every command that loads the config and delegates resolves
`delegation.transport` once, at step 0, the way it already resolves Jev: H1 runs
there and nowhere else, so no role re-probes mid-command and gets a different
answer than its siblings. The three wave commands carry the line too, because a
wave's Executors use the transport. These tests pin the line in each command,
the block-name lists that name `delegation`, the wave sentence (whose step stays
provider-neutral), and the Researcher result gate in `prep` and `research`.
"""

import re
import unittest

import jdi_files

STEP_ZERO_COMMANDS = tuple(
    "commands/%s.md" % name
    for name in ("prep", "research", "plan", "split", "feedback", "pr", "execute", "next", "yolo")
)
WAVE_COMMANDS = ("commands/execute.md", "commands/next.md", "commands/yolo.md")
STEP_ZERO_FRAGMENTS = (
    "**Then resolve the delegation transport, once**",
    "perform **H1** from JDI's `reference/herdr.md`",
    "With `delegation.transport` `native` or absent, say nothing at all",
)


def normalized(path):
    return " ".join(jdi_files.read(path).split())


def executor_hand_off(path):
    """The numbered step that hands the wave to the Executors.

    The step-0 transport line names Herdr in every command, because it tells the
    Butler when H1 applies. The wave site is where the command body must stay
    provider-neutral, so the Herdr check reads only that step.
    """
    text = jdi_files.read(path)
    start = text.index("**Delegate to the Executor, once per task, all at once**")
    following = re.search(r"\n\d+\. \*\*", text[start:])
    end = start + following.start() if following else len(text)
    return text[start:end]


class StepZeroTransportTest(unittest.TestCase):
    longMessage = False

    def test_every_delegating_command_resolves_the_transport_at_step_zero(self):
        for path in STEP_ZERO_COMMANDS:
            text = normalized(path)
            for fragment in STEP_ZERO_FRAGMENTS:
                with self.subTest(path=path, fragment=fragment):
                    self.assertIn(fragment, text, "%s lacks %r" % (path, fragment))

    def test_block_name_lists_include_delegation(self):
        expected = (
            ("commands/prep.md", "`models`, `harnesses`, and `delegation` from it"),
            ("commands/research.md", "`models`, `harnesses`, and `delegation` from that config"),
        )
        for path, fragment in expected:
            with self.subTest(path=path):
                self.assertIn(fragment, normalized(path), "%s lacks %r" % (path, fragment))


class WaveTransportTest(unittest.TestCase):
    longMessage = False

    def test_wave_commands_resolve_each_executor_with_the_transport(self):
        for path in WAVE_COMMANDS:
            text = normalized(path)
            with self.subTest(path=path, check="sentence"):
                self.assertIn(
                    "including the transport `delegation.transport` selects",
                    text,
                    "%s lacks the per-Executor transport sentence" % path,
                )
            with self.subTest(path=path, check="superseded"):
                self.assertNotIn(
                    "does not apply to a wave", text, "%s still exempts waves" % path
                )
            with self.subTest(path=path, check="provider-neutral"):
                self.assertIsNone(
                    re.search(r"\bHerdr\b", executor_hand_off(path)),
                    "%s names Herdr in its Executor hand-off step; the wave site must "
                    "stay provider-neutral" % path,
                )


class ValidationGateTest(unittest.TestCase):
    longMessage = False

    def test_researcher_findings_come_from_the_validated_result_file(self):
        for path in ("commands/prep.md", "commands/research.md"):
            with self.subTest(path=path):
                self.assertIn(
                    "the result file the transport validated",
                    normalized(path),
                    "%s lacks 'the result file the transport validated'" % path,
                )


if __name__ == "__main__":
    unittest.main()
