import unittest

from reportlab.platypus import KeepTogether, Table

from report_design_system import FontSpec, build_key_finding_matrix_exhibit


class KeyFindingMatrixExhibitTests(unittest.TestCase):
    def test_builds_integrated_key_finding_and_matrix_exhibit(self):
        exhibit = build_key_finding_matrix_exhibit(
            width=420,
            fonts=FontSpec(),
            key_finding_text=(
                "EL level users were more likely to report that public tools "
                "added value beyond Copilot."
            ),
            title="MEASURE",
            columns=["APS level", "EL level"],
            rows=[
                ("Public tools", None, None),
                ("Used weekly or more", ["51.5%", "53.6%"], 1),
                ("Rated at least moderately useful", ["87.9%", "71.4%"], 0),
                ("Copilot", None, None),
                ("Used weekly or more", ["72.7%", "67.9%"], 0),
            ],
            first_col_ratio=0.56,
        )

        self.assertIsInstance(exhibit, KeepTogether)
        self.assertEqual(len(exhibit._content), 1)
        table = exhibit._content[0]
        self.assertIsInstance(table, Table)
        self.assertEqual(table._colWidths, [235.20000000000002, 92.39999999999999, 92.39999999999999])
        self.assertIsNone(table._cellvalues[0][0].style.backColor)
        self.assertEqual(table._spanCmds, [
            ("SPAN", (0, 0), (-1, 0)),
            ("SPAN", (0, 2), (-1, 2)),
            ("SPAN", (0, 5), (-1, 5)),
        ])
        self.assertEqual(table._cellvalues[2][1], "")
        self.assertEqual(table._cellvalues[2][2], "")
        self.assertEqual(table._cellvalues[5][1], "")
        self.assertEqual(table._cellvalues[5][2], "")


if __name__ == "__main__":
    unittest.main()
