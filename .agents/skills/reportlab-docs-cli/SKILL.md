---
name: reportlab-docs-cli
description: "Use when an AI agent needs to explore ReportLab APIs, docs.reportlab.com links, critique generated ReportLab PDFs, or search a local ReportLab API reference PDF via the `reportlab-docs` CLI. Helps inspect symbols, audit PDF font hierarchy/table styling/legends/titles, search docs/PDF reference text, list installed modules, and generate sanity-check example PDFs before writing ReportLab code."
---

# ReportLab Docs CLI

Use this skill when you need fast, local ReportLab API context before writing or debugging ReportLab code.

The CLI lives in this repo as `reportlab_docs_cli` and can be run without installation:

```bash
python3 -m reportlab_docs_cli --help
```

If installed from the repo, the console script is:

```bash
reportlab-docs --help
```

## Core Workflow

1. Start with package facts:

```bash
python3 -m reportlab_docs_cli info --json
```

2. Inspect the API object you plan to use:

```bash
python3 -m reportlab_docs_cli inspect Canvas --json
python3 -m reportlab_docs_cli inspect reportlab.platypus.Table --json
python3 -m reportlab_docs_cli inspect reportlab.lib.styles.ParagraphStyle --json
```

3. Search before guessing names:

```bash
python3 -m reportlab_docs_cli search table --limit 10
python3 -m reportlab_docs_cli search bookmark --limit 10
```

4. If the user supplied the ReportLab API reference PDF, search it too:

```bash
python3 -m reportlab_docs_cli search bookmark --pdf /Users/aristotle/Downloads/reportlab-reference.pdf --limit 10
```

PDF search requires `pypdf`. If it is missing, tell the user or install it with approval according to the active environment policy.

5. Generate a small example PDF when validating the local ReportLab runtime:

```bash
python3 -m reportlab_docs_cli example hello --output /private/tmp/reportlab-hello.pdf --json
python3 -m reportlab_docs_cli example table --output /private/tmp/reportlab-table.pdf --json
```

6. Critique an existing generated PDF for design consistency:

```bash
python3 -m reportlab_docs_cli critique Outputs/DEWR_Public_AI_B.pdf --json
```

Use this for questions about font hierarchy, table header boldness, table body font/size, whether a title appears above a table or visual, and whether legend/caption-like text is consistently styled.

For Bain-style editorial report standards, add:

```bash
python3 -m reportlab_docs_cli critique Outputs/DEWR_Public_AI_B.pdf --standard bain-editorial --json
```

Use this when the desired report standard is closer to Bain & Company editorial reports: body paragraphs have modest paragraph gaps, exhibits have larger arrival space, visuals use explicit `Figure N:` labels above the exhibit, and notes/source text sits below the exhibit as small regular sans text.

7. Render important pages for visual inspection:

```bash
python3 -m reportlab_docs_cli render Outputs/DEWR_Public_AI_B.pdf --pages 2,5,6,8,10-12 --output-dir /private/tmp/dewr-renders --json
```

Use this after `critique` whenever layout quality matters. Inspect the generated PNGs directly and compare repeated visual families, especially tables, matrices, charts, callouts, legends, notes, and dense pages. The rendered review should catch visual-system issues that extraction cannot infer, such as two tables using different header architecture even when their extracted fonts are acceptable.

## Command Selection

- Use `info` to confirm installed ReportLab version and package path.
- Use `docs` to list canonical `docs.reportlab.com` topic URLs.
- Use `modules --prefix reportlab.pdfgen` or `modules --prefix reportlab.platypus` to discover installed modules.
- Use `inspect SYMBOL --json` for signatures, docstrings, and class members.
- Use `search QUERY` for known high-value symbols and docs topics.
- Use `search QUERY --pdf PATH` when the local API reference may contain details not exposed by runtime introspection.
- Use `critique PDF_PATH` when reviewing generated PDF design details: hierarchy, table header/body styles, titles above tables, and legend/caption consistency.
- Use `critique PDF_PATH --standard bain-editorial` when checking against the Bain-style editorial standard for figure labels, exhibit spacing, visual-title architecture, and note/source treatment.
- Use `render PDF_PATH --pages ...` when reviewing visual fidelity, repeated component consistency, clipping, overlap, chart legends, or page flow.
- Use `example NAME` for smoke tests and to create minimal working PDFs.

## Good Defaults

- Prefer `--json` when another tool or agent will consume output.
- Prefer aliases for common symbols: `Canvas`, `Paragraph`, `Table`, `TableStyle`, `SimpleDocTemplate`, `ParagraphStyle`, `colors`, `pagesizes`, and `units`.
- Prefer `Canvas` for coordinate-level drawing questions.
- Prefer `platypus` symbols for multi-page document layout, flowables, tables, paragraphs, and story building.
- Prefer `reportlab.lib` symbols for colors, units, page sizes, validators, and styles.

## Verification Expectations

Before claiming a ReportLab implementation is complete:

- Run the relevant unit tests if present.
- Generate at least one small PDF if the change affects PDF output.
- Inspect the API with this CLI when you are uncertain about signatures or class members.
- If layout matters, run `critique`, render the dense or changed pages, and visually review the PNGs.
- Treat `critique` findings as evidence-backed heuristics, then confirm visually when layout quality matters.
- For design critique, never rely only on JSON extraction. Compare rendered examples of each repeated component family and explicitly check whether similar tables/charts share the same title/header/legend/note architecture.

## Known Limits

- `docs` prints curated topic links, not a full mirror of the site.
- `search` over installed symbols is seeded with common public APIs; use `modules` plus `inspect` for deeper exploration.
- PDF extraction may emit encoding warnings from `pypdf`; useful text snippets can still be valid.
- `critique` requires `pdfplumber` and infers tables/visuals heuristically from PDF text and geometry. It is strongest for consistency auditing, not semantic judgment.
- `render` requires PyMuPDF or Poppler's `pdftoppm`; if neither is installed, install the `pdf` extra or ask the user to install Poppler.
