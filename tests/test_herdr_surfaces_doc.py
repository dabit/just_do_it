"""The surfaces architecture doc records the design as decided and probed, not as proposed.

`docs/herdr-surfaces-architecture.md` began as a proposal with open decisions and a probe list
that ran in the user's own window. Once the plan settled every decision and the probe gate ran,
it must record those decisions, keep its structural sections, and say that probes run only in a
throwaway session. It must carry no personal path. The transport architecture doc's detection
section must point at it and name the key that picks the surface.
"""

import re
import unittest

import jdi_files

SURFACES_DOC = "docs/herdr-surfaces-architecture.md"
TRANSPORT_DOC = "docs/delegation-transport-architecture.md"

PRESENT_HEADINGS = (
    "## Detection",
    "## Operation map",
    "## The app's worktree layout",
    "## Decisions",
    "## App-side live probes",
    "## The herd record",
)


class HerdrSurfacesDocTest(unittest.TestCase):
    longMessage = False

    def setUp(self):
        self.text = jdi_files.read(SURFACES_DOC)
        self.lines = self.text.split("\n")
        # Prose wraps at any word, so phrase checks read the text as one line.
        self.flat = re.sub(r"\s+", " ", self.text)

    def test_headings_present(self):
        for heading in PRESENT_HEADINGS:
            with self.subTest(heading=heading):
                self.assertIn(
                    heading, self.lines, "%s lacks the heading %r" % (SURFACES_DOC, heading)
                )

    def test_no_open_decisions_heading(self):
        self.assertNotIn(
            "## Open decisions",
            self.lines,
            "%s still has an `## Open decisions` heading" % SURFACES_DOC,
        )

    def test_not_described_as_unimplemented(self):
        self.assertNotIn(
            "Nothing here is implemented yet",
            self.flat,
            "%s still says nothing is implemented" % SURFACES_DOC,
        )

    def test_probes_never_run_in_the_users_window(self):
        self.assertNotIn(
            "in an app terminal of the user's normal window",
            self.flat,
            "%s still runs probes in the user's normal window" % SURFACES_DOC,
        )

    def test_probes_run_in_a_throwaway_session(self):
        body = "\n".join(jdi_files.section(self.text, "## App-side live probes"))
        self.assertIn(
            "throwaway",
            body,
            "`## App-side live probes` does not require a throwaway session",
        )

    def test_no_personal_paths(self):
        self.assertNotIn("/home/", self.text, "%s contains a `/home/` path" % SURFACES_DOC)

    # Task 11, the UAT follow-ups (F3, F4, F7).

    def test_app_wave_tab_closes_with_its_last_pane(self):
        self.assertNotIn("does not close itself", self.flat)
        self.assertIn("closing its last pane closes the tab with it", self.flat)

    def test_trust_is_inherited_not_always_a_dialog(self):
        self.assertNotIn("always a new folder", self.flat)
        self.assertIn("takes Claude's folder trust from its main checkout", self.flat)

    def test_operation_map_single_quotes_the_space_name(self):
        operation_map = " ".join(jdi_files.section(self.text, "## Operation map"))
        self.assertNotIn('--name "<label>"', operation_map)
        self.assertIn("--name '<label>'", operation_map)

    # Task 17, the herd record and cleanup from it (#37).

    def test_herd_record_section(self):
        body = re.sub(r"\s+", " ", " ".join(jdi_files.section(self.text, "## The herd record")))
        for fragment in (
            "`jdi/herds/<herd-id>.json`",
            "`--git-common-dir`",
            "never by a recorded ID alone",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, body, "`## The herd record` lacks %s" % fragment)

    def test_operation_map_has_record_rows(self):
        rows = jdi_files.section(self.text, "## Operation map")
        for prefix in ("| H9 Herd record |", "| H9 Cleanup from the record |"):
            with self.subTest(row=prefix):
                self.assertTrue(
                    any(line.startswith(prefix) for line in rows),
                    "`## Operation map` has no row starting %r" % prefix,
                )

    # Task 25, herd modes and untracked tasks (#38).

    def test_operation_map_single_quotes_the_invocation(self):
        rows = jdi_files.section(self.text, "## Operation map")
        row = next((line for line in rows if line.startswith("| H9 Hand it the work |")), None)
        self.assertIsNotNone(row, "`## Operation map` has no row starting `| H9 Hand it the work |`")
        for fragment in (
            "`herdr agent prompt <name> '<invocation>'`",
            "`hc send <terminal> '<invocation>' --if idle`",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, row, "`| H9 Hand it the work |` lacks %s" % fragment)
        self.assertNotIn(
            '"<invocation>"', row, "`| H9 Hand it the work |` still double-quotes the invocation"
        )

    # Task 27, the untagged app handoff (R7).

    def test_operation_map_hands_off_untagged(self):
        rows = jdi_files.section(self.text, "## Operation map")
        row = next((line for line in rows if line.startswith("| H9 Hand it the work |")), None)
        self.assertIsNotNone(row, "`## Operation map` has no row starting `| H9 Hand it the work |`")
        for fragment in ("`env -u HC_TERMINAL_ID hc send <terminal> '<invocation>' --if idle`", "R7"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, row, "`| H9 Hand it the work |` lacks %s" % fragment)

    def test_r7_note(self):
        body = re.sub(r"\s+", " ", " ".join(jdi_files.section(self.text, "### What the probes showed")))
        for fragment in ("**R7, the app handoff.**", "`<hc from=", "HC_TERMINAL_ID"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, body, "the R7 note lacks %s" % fragment)

    def test_herd_record_section_names_task(self):
        body = re.sub(r"\s+", " ", " ".join(jdi_files.section(self.text, "## The herd record")))
        for fragment in ("`task`", "`/jdi:do`"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, body, "`## The herd record` lacks %s" % fragment)


class TransportDocPointsAtSurfacesTest(unittest.TestCase):
    longMessage = False

    def test_capability_detection_points_at_the_surfaces_doc(self):
        body = "\n".join(
            jdi_files.section(jdi_files.read(TRANSPORT_DOC), "## Capability detection")
        )
        for fragment in ("`docs/herdr-surfaces-architecture.md`", "`herdr.surface`"):
            with self.subTest(fragment=fragment):
                self.assertIn(
                    fragment,
                    body,
                    "`## Capability detection` in %s lacks %s" % (TRANSPORT_DOC, fragment),
                )

    # Task 17: the herd layer exists, and its outer layer names cleanup (#37).

    def test_transport_status_is_not_stale(self):
        flat = re.sub(r"\s+", " ", jdi_files.read(TRANSPORT_DOC))
        self.assertNotIn(
            "is planned in the same branch as a separable wave",
            flat,
            "%s still calls the `/jdi:herd` layer planned" % TRANSPORT_DOC,
        )

    def test_two_layers_names_cleanup(self):
        body = re.sub(
            r"\s+",
            " ",
            " ".join(jdi_files.section(jdi_files.read(TRANSPORT_DOC), "## Two layers")),
        )
        self.assertIn(
            "`/jdi:herd --cleanup`",
            body,
            "`## Two layers` in %s does not name `/jdi:herd --cleanup`" % TRANSPORT_DOC,
        )

    # Task 25, herd modes and untracked tasks (#38).

    def test_two_layers_names_herd_mode(self):
        body = re.sub(
            r"\s+",
            " ",
            " ".join(jdi_files.section(jdi_files.read(TRANSPORT_DOC), "## Two layers")),
        )
        for fragment in ("`herd.mode`", "`/jdi:do`"):
            with self.subTest(fragment=fragment):
                self.assertIn(
                    fragment,
                    body,
                    "`## Two layers` in %s lacks %s" % (TRANSPORT_DOC, fragment),
                )


if __name__ == "__main__":
    unittest.main()
