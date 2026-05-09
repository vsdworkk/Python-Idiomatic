# reportlab-docs-cli

A small terminal companion for `docs.reportlab.com` and the ReportLab API reference.

It works offline against the installed `reportlab` package, and can optionally search a local copy of the ReportLab API reference PDF when `pypdf` is installed.

## Install

```bash
python3 -m pip install -e .
```

For PDF reference search:

```bash
python3 -m pip install -e ".[pdf]"
```

## Commands

```bash
reportlab-docs info
reportlab-docs docs
reportlab-docs inspect Canvas
reportlab-docs search table
reportlab-docs search bookmark --pdf /Users/aristotle/Downloads/reportlab-reference.pdf
reportlab-docs critique Outputs/DEWR_Public_AI_B.pdf
reportlab-docs critique Outputs/DEWR_Public_AI_B.pdf --standard bain-editorial --json
reportlab-docs render Outputs/DEWR_Public_AI_B.pdf --pages 2,5,6,8,10-12 --output-dir /private/tmp/dewr-renders
reportlab-docs example hello --output hello.pdf
reportlab-docs example table --output table.pdf
```

## What It Covers

- Installed ReportLab package metadata.
- Official topic links for `docs.reportlab.com`.
- Runtime introspection for key APIs from the attached API reference, including `pdfgen.canvas.Canvas`, `platypus`, `colors`, `pagesizes`, `units`, and styles.
- Optional local PDF search across the ReportLab API reference.
- Detailed generated-PDF critique for font hierarchy, table header/body styling, nearby titles, and legend/caption consistency.
- Optional Bain-style editorial standard checks for figure labels, pre-visual spacing, visual titles, and notes/source formatting.
- PDF page rendering to PNG for visual QA of tables, charts, legends, page flow, clipping, and repeated component consistency.
- Runnable PDF examples for canvas drawing, Platypus flowables, and tables.
