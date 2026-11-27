import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "claimset-code", "claimset-vs-pdf"))
import mask  # noqa: E402

CASES = [
    ("No. Limitation L2 states that x.", "No. [location] states that x."),
    ("claims C3, C5 and C7 hold", "[location] hold"),
    ("the evidence (E1, E2) shows x (see Table 2).", "the evidence shows x."),
    ("as Table 2 shows", "as [location] shows"),
    ("Table E8.T1 shows", "[location] shows"),
    ("(E3.T1 r4: 0.894/0.9)", "(0.894/0.9)"),
    ("see Appendix A and Table 3a.", "see [location]."),
    ("in Section 3.2, p. 14", "in [location]"),
    ("from §2.1 and Eq. (12)", "from [location]"),
    ("in figure 2(b)", "in [location]"),
    ("[p3.2] says", "[location] says"),
    ("The PDF says", "The paper says"),
    ("the .txt file states", "the paper states"),
    ("this claimset does not", "this paper does not"),
    ("the claimset (reading view) says", "the paper says"),
    ("a plain-text file", "a paper"),
    ("the EVIDENCE tables", "the evidence tables"),
    ("- **L1:** under", "- under"),
    ("(0.99 + 0.98i, E4.T1); and", "(0.99 + 0.98i); and"),
    ("the formula (entrylib:2026.000003@v4#C12) holds", "the formula holds"),
    ("From `multi-step-estimators.pdf` [file: multi-step-estimators.pdf], x", "From, x"),
    ('It says so. <FileCite ref_id="turn0file0" line_range_start={1}/>', "It says so."),
]
KEPT = ["the figures 0.812 and 0.9", "the M3 and M4 competitions, series N2703", "ETS(A,N,N) and AR(1), MA(2)",
        "the text of the paper", "Page's CUSUM", "Theorem-like results"]


class MaskTest(unittest.TestCase):
    def test_identifiers_locators_form_words_and_files(self):
        for text, want in CASES:
            self.assertEqual(mask.mask(text).strip(), want, text)

    def test_names_and_numbers_are_kept(self):
        for text in KEPT:
            self.assertEqual(mask.mask(text), text)

    def test_leaks_lists_what_may_still_tell(self):
        found = [w for w, _ in mask.leaks("The claimset row C3 and the record say so.")]
        self.assertIn("claimset", found)
        self.assertIn("C3", found)


if __name__ == "__main__":
    unittest.main()
