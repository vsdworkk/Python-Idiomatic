# reportlab-docs-cli

A small terminal companion for `docs.reportlab.com`, the installed ReportLab API, and generated PDF design QA.

It works offline against the local `reportlab` package. With the `pdf` extra installed, it can search a local ReportLab API reference PDF, critique generated PDF typography/layout, and render pages to PNG for visual QA.

## Install

From the repository:

```bash
python3 -m pip install -e ".[pdf]"
```

From GitHub after publishing:

```bash
python3 -m pip install "git+https://github.com/YOUR_ORG/reportlab-docs-cli.git[pdf]"
```

## Commands

```bash
reportlab-docs info
reportlab-docs docs
reportlab-docs inspect Canvas
reportlab-docs inspect reportlab.platypus.Table --json
reportlab-docs search table
reportlab-docs search bookmark --pdf /path/to/reportlab-reference.pdf
reportlab-docs critique /path/to/report.pdf
reportlab-docs critique /path/to/report.pdf --standard bain-editorial --json
reportlab-docs render /path/to/report.pdf --pages 2,5,6,8,10-12 --output-dir renders
reportlab-docs example hello --output hello.pdf
reportlab-docs example table --output table.pdf
```

## What It Covers

- Installed ReportLab package metadata.
- Official topic links for `docs.reportlab.com`.
- Runtime introspection for key APIs including `pdfgen.canvas.Canvas`, Platypus flowables, tables, colors, pagesizes, units, and styles.
- Optional local PDF search across a ReportLab API reference PDF.
- Generated-PDF critique for font hierarchy, table header/body styling, nearby titles, and legend/caption consistency.
- Optional Bain-style editorial standard checks for `Figure N:` labels, pre-visual spacing, figure title architecture, and notes/source formatting.
- PDF page rendering to PNG for visual QA of tables, charts, legends, page flow, clipping, and repeated component consistency.
- Runnable PDF examples for canvas drawing, Platypus flowables, and tables.

## Design Critique Workflow

Use extraction first:

```bash
reportlab-docs critique report.pdf --standard bain-editorial --json
```

Then render dense pages for visual inspection:

```bash
reportlab-docs render report.pdf --pages 2,5,6,8,10-12 --output-dir renders --json
```

The critique command is evidence-backed, but it is still heuristic. For final report QA, inspect the rendered PNGs and compare repeated component families such as tables, charts, legends, notes, callouts, and page breaks.

## Development

```bash
python3 -m pip install -e ".[dev]"
python3 -m unittest discover -s tests
python3 -m reportlab_docs_cli --help
```

## Notes

- `critique` requires `pdfplumber`.
- `render` uses PyMuPDF when available.
- `search --pdf` requires `pypdf`.
- The CLI does not mirror all of `docs.reportlab.com`; it provides curated docs links plus local runtime inspection.
