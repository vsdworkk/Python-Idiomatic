import json
import importlib.util
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from reportlab_docs_cli.cli import (
    load_symbol,
    main,
    parse_page_selection,
    search_everything,
)


class ReportLabDocsCliTests(unittest.TestCase):
    def test_loads_canvas_alias_target(self):
        canvas_class = load_symbol("reportlab.pdfgen.canvas.Canvas")

        self.assertEqual(canvas_class.__name__, "Canvas")

    def test_inspect_canvas_outputs_json_members(self):
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["inspect", "Canvas", "--json"])

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["kind"], "class")
        self.assertIn("drawString", payload["members"])

    def test_search_finds_table_symbol(self):
        hits = search_everything("Table", limit=5)

        self.assertTrue(any("Table" in hit.name for hit in hits))

    def test_parse_page_selection_accepts_ranges_and_all(self):
        self.assertEqual(parse_page_selection("2,5-7,3", page_count=10), [2, 3, 5, 6, 7])
        self.assertEqual(parse_page_selection("all", page_count=3), [1, 2, 3])

    def test_parse_page_selection_rejects_out_of_bounds(self):
        with self.assertRaisesRegex(Exception, "outside 1-3"):
            parse_page_selection("1,4", page_count=3)

    def test_example_generates_pdf(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "hello.pdf"
            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["example", "hello", "--output", str(output), "--json"])

            self.assertEqual(exit_code, 0)
            self.assertGreater(output.stat().st_size, 1000)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["output"], str(output))

    @unittest.skipIf(importlib.util.find_spec("pdfplumber") is None, "pdfplumber is not installed")
    def test_critique_reports_table_styles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "table.pdf"
            with redirect_stdout(StringIO()):
                main(["example", "table", "--output", str(output), "--json"])
            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["critique", str(output), "--json"])

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["pages"], 1)
            self.assertIn("detected_tables", payload["summary"])
            self.assertIn("hierarchy", payload)

    @unittest.skipIf(importlib.util.find_spec("pdfplumber") is None, "pdfplumber is not installed")
    def test_critique_can_apply_bain_editorial_standard(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "bainish.pdf"
            self._write_bainish_pdf(output)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["critique", str(output), "--standard", "bain-editorial", "--json"])

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["standard"], "bain-editorial")
            standard = payload["standards"]["bain_editorial"]
            self.assertEqual(standard["metrics"]["figure_label_count"], 1)
            self.assertEqual(standard["profile"]["figure_label_pattern"], "Figure N: title above visual")

    def _write_bainish_pdf(self, output):
        from reportlab.lib.colors import HexColor
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        pdf = canvas.Canvas(str(output), pagesize=letter)
        pdf.setFont("Times-Roman", 10)
        pdf.drawString(72, 700, "This is a paragraph before the exhibit.")
        pdf.drawString(72, 684, "It has room before the figure label.")
        pdf.setFillColor(HexColor("#CC0000"))
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(118, 635, "Figure 1:")
        pdf.setFillColor(HexColor("#000000"))
        pdf.setFont("Helvetica", 10)
        pdf.drawString(170, 635, "A compact editorial exhibit title")
        pdf.setFillColor(HexColor("#CCCCCC"))
        pdf.rect(118, 470, 260, 120, fill=1, stroke=0)
        pdf.setFillColor(HexColor("#666666"))
        pdf.setFont("Helvetica", 7)
        pdf.drawString(118, 450, "Notes: Example note text.")
        pdf.drawString(118, 440, "Source: Synthetic test fixture.")
        pdf.save()


if __name__ == "__main__":
    unittest.main()
