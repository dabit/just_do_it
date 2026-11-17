"""Guards how `/jdi:do` and `/jdi:prep` take work that `/jdi:herd` started.

`/jdi:herd` hands each agent its work with a clause appended, `(started by
/jdi:herd)` or `(untracked, started by /jdi:herd)`, and both clauses are defined
in `reference/herdr.md` H9. This module pins four rules that hang off them:

- a herd-started `/jdi:do` that finds the work too big for one session, before
  step 6 has changed anything, says so in one line and continues with
  `/jdi:prep` in the same session, pushing nothing, instead of handing back
  (standalone `/jdi:do` still recommends `/jdi:prep` and hands back);
- a herd-started `/jdi:prep` takes the herd's tracking answer and asks no
  tracking question;
- both commands leave the clause out of the work, and both quote the clauses
  exactly as H9 defines them;
- `/jdi:do` step 10 updates a branch the default branch moved under, on every
  run, herd-started or not.

Deviation from `DoPlanShapeTest`: that class's `step()` helper lives in
`tests/test_structural_checks.py`, and importing it would make unittest collect
that module's classes a second time. So this module reads paragraphs with
`jdi_files.paragraph_starting_with`, which stops at the first blank line; every
sentence it pins must therefore stay inside its paragraph.
"""

import unittest

import jdi_files

DO = "commands/do.md"
PREP = "commands/prep.md"
HERDR_REFERENCE = "reference/herdr.md"
H9_HEADING = "## H9 - Give a Butler its own worktree"

CLAUSES = ("`(started by /jdi:herd)`", "`(untracked, started by /jdi:herd)`")


def normalized(text):
    return " ".join(text.split())


def paragraph(path, prefix):
    return normalized(
        " ".join(jdi_files.paragraph_starting_with(jdi_files.read(path), prefix))
    )


def too_big_bullet():
    p = paragraph(DO, "   - **Too big for one session.**")
    return p[
        p.index("**Too big for one session.**") : p.index(
            "**A product decision outside the request.**"
        )
    ]


class HerdHandoffTest(unittest.TestCase):
    def test_too_big_in_a_herd_continues_with_prep(self):
        bullet = too_big_bullet()
        fragments = CLAUSES + (
            "before step 6 has changed anything",
            "do not hand back",
            "Say in one line that the work is too big for one session",
            "continue with `/jdi:prep`",
            "in this session",
            "Push nothing",
            "prep's step 6 keeps the branch step 2 created",
        )
        for fragment in fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, bullet)

    def test_standalone_too_big_still_hands_back(self):
        self.assertIn("Recommend `/jdi:prep` with what you learned", too_big_bullet())

    def test_clause_is_not_part_of_the_work(self):
        self.assertIn(
            "that clause is not part of the work",
            paragraph(DO, "1. **Identify the work**"),
        )

    def test_merge_updates_a_branch_the_default_moved_under(self):
        text = paragraph(DO, "10. **Merge**")
        for fragment in (
            "a parallel change merged first",
            "run step 7's gates again",
            "a step-5 stop",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_prep_takes_the_herds_tracking_answer(self):
        text = paragraph(PREP, "2. **Determine the tracking context**")
        for fragment in CLAUSES + ("Ask neither", "The clause is not part of the work"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_clauses_match_h9(self):
        sources = {
            HERDR_REFERENCE + " H9": normalized(
                "\n".join(
                    jdi_files.section(jdi_files.read(HERDR_REFERENCE), H9_HEADING)
                )
            ),
            DO: normalized(jdi_files.read(DO)),
            PREP: normalized(jdi_files.read(PREP)),
        }
        for clause in CLAUSES:
            for source, text in sources.items():
                with self.subTest(clause=clause, source=source):
                    self.assertIn(clause, text)


if __name__ == "__main__":
    unittest.main()
