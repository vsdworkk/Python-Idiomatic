# Report Visual Design System Next Pass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Centralise visual-level styling for every custom ReportLab visual so headers, card titles, KPI values, labels, legends, axis ticks, bar heights, dot sizes, dividers and inner padding are controlled by named design-system tokens.

**Architecture:** Keep the current report generator structure stable. Add second-layer visual spec dataclasses to `report_design_system.py`, instantiate them once in `generate_report.py`, and replace repeated local visual constants inside Flowables with named spec fields. This is a tokenisation pass, not a module-splitting pass.

**Tech Stack:** Python 3, ReportLab, local PDFKit renderer at `/private/tmp/render_pdf_pages`, Pillow for contact sheet generation.

---

## File Structure

- Modify: `report_design_system.py`
  - Add visual spec dataclasses: `VisualTextSpec`, `PanelSpec`, `KpiSpec`, `ChartLayoutSpec`, `TableSpec`, `PageChromeSpec`, `CoverSpec`.
  - Keep existing palette, font, paragraph and drawing helpers unchanged unless needed for imports.

- Modify: `generate_report.py`
  - Import and instantiate new visual spec dataclasses.
  - Refactor Flowables to use `VISUAL_TEXT`, `PANEL`, `KPI`, `CHART_LAYOUT`, `TABLE_SPEC`, `PAGE_CHROME`, and `COVER`.
  - Preserve current visual layout unless a token makes the existing value explicit.

- Generated output: `Outputs/DEWR_Public_AI_B.pdf`
  - Regenerated as verification output.

---

### Task 1: Add Visual Spec Dataclasses

**Files:**
- Modify: `report_design_system.py`

- [ ] **Step 1: Add dataclasses below `ChartSpec`**

Add this code immediately after `ChartSpec`:

```python
@dataclass(frozen=True)
class VisualTextSpec:
    panel_header: float = 7.5
    panel_header_small: float = 7.2
    card_title: float = 8.5
    card_body: float = 8.0
    card_body_leading: float = 9.5
    chart_label: float = 7.5
    chart_label_leading: float = 8.6
    chart_tick: float = 7.0
    chart_legend: float = 7.2
    chart_legend_compact: float = 6.6
    chart_value_label: float = 7.0
    chart_value_label_compact: float = 6.8
    table_header: float = 6.5
    table_header_leading: float = 7.5
    table_label: float = 7.6
    table_label_leading: float = 8.6
    table_value: float = 11.0
    table_value_leading: float = 12.0
    kpi_value: float = 24.0
    kpi_value_medium: float = 22.0
    kpi_value_compact: float = 17.0
    kpi_caption: float = 7.4
    kpi_caption_leading: float = 8.4
    note: float = 8.0
```

- [ ] **Step 2: Add layout spec dataclasses below `VisualTextSpec`**

Add this code:

```python
@dataclass(frozen=True)
class PanelSpec:
    padding: float = 16.0
    padding_large: float = 20.0
    padding_callout: float = 12.0
    inner_padding: float = 12.0
    gutter: float = 10.0
    title_y_offset: float = 20.0
    divider_y_offset: float = 36.0
    divider_inset: float = 16.0
    section_divider_width: float = 0.5
    hairline_width: float = 0.35


@dataclass(frozen=True)
class KpiSpec:
    panel_height: float = 74.0
    strip_height: float = 96.0
    value_y_without_title: float = 52.0
    value_y_with_title: float = 42.0
    label_gap: float = 16.0
    divider_top_inset: float = 12.0
    divider_bottom_inset: float = 12.0
    stat_box_height: float = 55.0
    stat_box_radius: float = 4.0


@dataclass(frozen=True)
class ChartLayoutSpec:
    row_height: float = 23.0
    row_height_compact: float = 19.0
    row_height_dense: float = 13.0
    bar_height: float = 7.0
    bar_height_compact: float = 6.0
    bar_height_large: float = 14.0
    dot_radius: float = 3.0
    dot_radius_small: float = 2.6
    dot_radius_compact: float = 2.4
    dot_radius_highlight: float = 3.8
    legend_marker_radius: float = 2.6
    legend_marker_radius_compact: float = 2.4
    axis_top_gap: float = 42.0
    label_width_ratio: float = 0.35
```

- [ ] **Step 3: Add table/chrome specs**

Add this code:

```python
@dataclass(frozen=True)
class TableSpec:
    matrix_row_height: float = 26.0
    matrix_header_height: float = 44.0
    matrix_header_height_single: float = 50.0
    access_header_height: float = 28.0
    access_row_height: float = 31.0
    cell_padding_x: float = 16.0
    cell_padding_y: float = 5.0
    section_row_value: float = 8.0


@dataclass(frozen=True)
class PageChromeSpec:
    header_line_y: float = 20 * mm
    header_text_y: float = 18 * mm
    footer_line_y: float = 18 * mm
    footer_text_y: float = 13 * mm
    header_text_size: float = 8.0
    footer_text_size: float = 8.0
    header_line_width: float = 2.0
    footer_line_width: float = 0.5


@dataclass(frozen=True)
class CoverSpec:
    left: float = 64.0
    logo_width: float = 196.0
    logo_height: float = 61.0
    title_size: float = 26.0
    title_leading: float = 34.0
    subtitle_size: float = 17.0
    subtitle_leading: float = 25.0
    date_size: float = 16.0
    bottom_bar_height: float = 10 * mm
```

- [ ] **Step 4: Compile**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/python-idiomatic-pycache python3 -m py_compile report_design_system.py
```

Expected: exit code 0.

---

### Task 2: Wire Specs Into Generator And Refactor KPI/Card Visuals

**Files:**
- Modify: `generate_report.py`

- [ ] **Step 1: Import and instantiate specs**

Update the existing import from `report_design_system` to include:

```python
VisualTextSpec,
PanelSpec,
KpiSpec,
ChartLayoutSpec,
TableSpec,
PageChromeSpec,
CoverSpec,
```

Add these constants after `CHART = ChartSpec()`:

```python
VISUAL_TEXT = VisualTextSpec()
PANEL = PanelSpec()
KPI = KpiSpec()
CHART_LAYOUT = ChartLayoutSpec()
TABLE_SPEC = TableSpec()
PAGE_CHROME = PageChromeSpec()
COVER = CoverSpec()
```

- [ ] **Step 2: Refactor KPI/card components**

For `ValueSignalsPanel`, `CalloutSignalsPanel`, `StatBox`, `ComparisonCard`, `TwoEvidenceCardsPanel`, `HorizontalEvidenceCallout`, and `KeyFindingBar`:

- Replace local panel padding values such as `pad = 16`, `self.padding = 12`, and `inner_pad = 12` with `PANEL.padding`, `PANEL.padding_callout`, or `PANEL.inner_padding`.
- Replace KPI value sizes `24`, `22`, and `17` with `VISUAL_TEXT.kpi_value`, `VISUAL_TEXT.kpi_value_medium`, and `VISUAL_TEXT.kpi_value_compact`.
- Replace KPI caption styles `7.4/8.2` and `7.4/8.4` with `VISUAL_TEXT.kpi_caption` and `VISUAL_TEXT.kpi_caption_leading`.
- Replace visual title/header sizes `7.2`, `7.5`, `8.5`, `10.5`, and `11` with named `VISUAL_TEXT` fields.
- Replace divider line widths `0.4`, `0.5`, and `0.6` with `LINES.hairline`, `LINES.fine`, or `LINES.regular`.

Example replacement in `ValueSignalsPanel`:

```python
pad = PANEL.padding
value_size = VISUAL_TEXT.kpi_value_medium if len(value) <= 8 else VISUAL_TEXT.kpi_value_compact
p = Paragraph(label, ParagraphStyle(
    "value_signal_label",
    fontName=FONT_REGULAR,
    fontSize=VISUAL_TEXT.kpi_caption,
    leading=VISUAL_TEXT.kpi_caption_leading,
    alignment=TA_CENTER,
    textColor=DEWR_DARK_GREY,
))
```

- [ ] **Step 3: Compile**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/python-idiomatic-pycache python3 -m py_compile generate_report.py
```

Expected: exit code 0.

---

### Task 3: Refactor Tables, Matrices, Charts And Page Chrome

**Files:**
- Modify: `generate_report.py`

- [ ] **Step 1: Refactor matrix and table visuals**

For `EvidenceMatrixPanel`, `access_evidence_table`, `CopilotEngagementDeltaPanel`, and `PriorExperienceComparisonPanel`:

- Replace matrix row/header heights with `TABLE_SPEC.matrix_row_height`, `TABLE_SPEC.matrix_header_height`, and `TABLE_SPEC.matrix_header_height_single`.
- Replace access table row heights with `TABLE_SPEC.access_header_height` and `TABLE_SPEC.access_row_height`.
- Replace table header sizes with `VISUAL_TEXT.table_header` and `VISUAL_TEXT.table_header_leading`.
- Replace table label/value sizes with `VISUAL_TEXT.table_label`, `VISUAL_TEXT.table_label_leading`, `VISUAL_TEXT.table_value`, and `VISUAL_TEXT.table_value_leading`.
- Replace `LEFTPADDING`, `RIGHTPADDING`, `TOPPADDING`, and `BOTTOMPADDING` values with `TABLE_SPEC.cell_padding_x` and `TABLE_SPEC.cell_padding_y`.

- [ ] **Step 2: Refactor chart visuals**

For `HorizontalBarPanel`, `ComfortDataHandlingPanel`, `PublicToolTaskProfilePanel`, `AllToolTaskProfilePanel`, `TaskFootprintExhibit`, and `GroupedBarChart`:

- Replace row heights with `CHART_LAYOUT.row_height`, `CHART_LAYOUT.row_height_compact`, or `CHART_LAYOUT.row_height_dense`.
- Replace bar heights with `CHART_LAYOUT.bar_height`, `CHART_LAYOUT.bar_height_compact`, or `CHART_LAYOUT.bar_height_large`.
- Replace dot and legend marker radii with `CHART_LAYOUT.dot_radius`, `CHART_LAYOUT.dot_radius_small`, `CHART_LAYOUT.dot_radius_compact`, `CHART_LAYOUT.dot_radius_highlight`, `CHART_LAYOUT.legend_marker_radius`, and `CHART_LAYOUT.legend_marker_radius_compact`.
- Replace tick, legend, chart label, and chart value-label font sizes with `VISUAL_TEXT.chart_tick`, `VISUAL_TEXT.chart_legend`, `VISUAL_TEXT.chart_legend_compact`, `VISUAL_TEXT.chart_label`, `VISUAL_TEXT.chart_label_leading`, `VISUAL_TEXT.chart_value_label`, and `VISUAL_TEXT.chart_value_label_compact`.
- Replace repeated `label_w = w * 0.35` with `label_w = w * CHART_LAYOUT.label_width_ratio` where the component uses the standard chart label width.

- [ ] **Step 3: Refactor page chrome**

Update `header_footer()` and `cover_page()`:

- Replace header/footer line positions and font sizes with `PAGE_CHROME`.
- Replace cover left offset, logo dimensions, title sizes, subtitle sizes, date size and bottom bar height with `COVER`.

- [ ] **Step 4: Compile**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/python-idiomatic-pycache python3 -m py_compile report_design_system.py generate_report.py
```

Expected: exit code 0.

---

### Task 4: Regenerate, Render And Inspect

**Files:**
- Generated: `Outputs/DEWR_Public_AI_B.pdf`
- Generated temp images: `/private/tmp/dewr_report_pages_visual_pass/`
- Generated temp contact sheet: `/private/tmp/dewr_report_contact_sheet_visual_pass.png`

- [ ] **Step 1: Generate PDF**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/python-idiomatic-pycache python3 generate_report.py
```

Expected: prints `Report generated: /Users/aristotle/Projects/Python-Idiomatic/Outputs/DEWR_Public_AI_B.pdf` and exits 0.

- [ ] **Step 2: Render PDF pages**

Run:

```bash
/private/tmp/render_pdf_pages /Users/aristotle/Projects/Python-Idiomatic/Outputs/DEWR_Public_AI_B.pdf /private/tmp/dewr_report_pages_visual_pass dewr-report
```

Expected: prints `pages=12` and writes page PNGs.

- [ ] **Step 3: Create contact sheet**

Run:

```bash
python3 -c 'from PIL import Image,ImageDraw; import pathlib, math; files=sorted(pathlib.Path("/private/tmp/dewr_report_pages_visual_pass").glob("dewr-report-*.png")); thumbs=[]; [thumbs.append((f, (lambda im: (im.thumbnail((230,325)), im.copy())[1])(Image.open(f).convert("RGB")))) for f in files]; w=4*260; h=math.ceil(len(thumbs)/4)*360; sheet=Image.new("RGB",(w,h),"white"); d=ImageDraw.Draw(sheet); [ (sheet.paste(im,((idx%4)*260+15,(idx//4)*360+25)), d.text(((idx%4)*260+15,(idx//4)*360+7), f.stem[-2:], fill=(64,66,70))) for idx,(f,im) in enumerate(thumbs) ]; sheet.save("/private/tmp/dewr_report_contact_sheet_visual_pass.png"); print("/private/tmp/dewr_report_contact_sheet_visual_pass.png")'
```

Expected: prints `/private/tmp/dewr_report_contact_sheet_visual_pass.png`.

- [ ] **Step 4: Scan remaining local visual constants**

Run:

```bash
rg -n "fontSize=[0-9]|leading=[0-9]|setFont\\(FONT_[A-Z_]+, [0-9]|circle\\([^\\n]*, [0-9]+\\.?[0-9]*|bar_h = [0-9]|row_h = [0-9]|pad = [0-9]|padding = [0-9]" generate_report.py
```

Expected: Remaining hits are either data/layout coordinates that are not reusable visual-system tokens, or are documented exceptions to be reported.

- [ ] **Step 5: Visual QA**

Inspect:

- `/private/tmp/dewr_report_contact_sheet_visual_pass.png`
- `/private/tmp/dewr_report_pages_visual_pass/dewr-report-02.png`
- `/private/tmp/dewr_report_pages_visual_pass/dewr-report-06.png`
- `/private/tmp/dewr_report_pages_visual_pass/dewr-report-10.png`
- `/private/tmp/dewr_report_pages_visual_pass/dewr-report-11.png`
- `/private/tmp/dewr_report_pages_visual_pass/dewr-report-12.png`

Expected: no overlapping text, no blank visuals, section/page rhythm remains professional, visual sizes remain comparable to the previous verified PDF.
