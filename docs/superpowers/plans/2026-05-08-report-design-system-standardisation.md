# Report Design System Standardisation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Standardise the ReportLab-generated DEWR Public Generative AI Trial report around a reusable OCE/DEWR design system, then apply it across headers, typography, colours, panels, charts, tables, notes, and page rhythm.

**Architecture:** Add a small design-system module that owns palette, typography, spacing, line, radius, page, and chart tokens; then migrate `generate_report.py` to consume those tokens instead of scattered literal values. Keep the existing content and custom Flowable structure, but make each component use shared helpers for panel surfaces, dividers, labels, notes, chart scales, and story spacing.

**Tech Stack:** Python 3, ReportLab 4.5, Platypus Flowables, generated A4 PDF, macOS PDF rendering for visual verification.

**Evidence Sources:** `docs/Formatting Guidelines/OCE data viz guidelines (1).pdf`, `docs/Formatting Guidelines/report_visual_style_guide.md`, rendered pages from `Outputs/DEWR_Public_AI_B.pdf`, and the current `generate_report.py` inventory.

---

### Task 1: Design System Module

**Files:**
- Create: `report_design_system.py`
- Modify: `generate_report.py`

- [ ] **Step 1: Create central palette and semantic tokens**

Create `report_design_system.py` with official DEWR palette names from the OCE guideline:

```python
from dataclasses import dataclass
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


DEWR_GRAPHITE = HexColor("#404246")
DEWR_MID_GREY = HexColor("#D7D8D8")
DEWR_GREY = HexColor("#A4A7A9")
DEWR_EUCALYPTUS = HexColor("#719F4C")
DEWR_DARK_EUCALYPTUS = HexColor("#5D7A38")
DEWR_PLUM = HexColor("#62165C")
DEWR_LIME = HexColor("#B5C427")
DEWR_TEAL = HexColor("#009B9F")
DEWR_NAVY = HexColor("#0D2C6C")
DEWR_BLUE = HexColor("#287DB2")
DEWR_YELLOW = HexColor("#E9A913")
DEWR_RED = HexColor("#91040D")
DEWR_PINK = HexColor("#D37190")
DEWR_COBALT = HexColor("#004F9D")
DEWR_MINT = HexColor("#47BFAF")
DEWR_PURPLE = HexColor("#573393")
DEWR_ORANGE = HexColor("#F26322")

OCE_TEXT = DEWR_GRAPHITE
OCE_SECONDARY_TEXT = HexColor("#6B6E70")
OCE_NOTE_TEXT = DEWR_GRAPHITE
OCE_MUTED_TEXT = DEWR_GREY
OCE_PANEL_BG = HexColor("#F7F8FA")
OCE_KEY_FINDING_BG = HexColor("#EFF4E8")
OCE_DIVIDER = DEWR_MID_GREY
OCE_SOFT_DIVIDER = HexColor("#E1E3DF")
OCE_TRACK = HexColor("#E1E5E2")
OCE_TRACK_ALT = HexColor("#E3E6E4")
OCE_PRIMARY = DEWR_DARK_EUCALYPTUS
OCE_PRIMARY_LIGHT = DEWR_EUCALYPTUS
OCE_NEGATIVE = DEWR_RED
OCE_WHITE = white

OCE_DEFAULT_SERIES = [
    DEWR_DARK_EUCALYPTUS,
    DEWR_GRAPHITE,
    DEWR_LIME,
    DEWR_TEAL,
    DEWR_BLUE,
    DEWR_PLUM,
]
```

Add backwards-compatible aliases used by existing code:

```python
DEWR_GREEN = DEWR_EUCALYPTUS
DEWR_DARK_GREEN = DEWR_DARK_EUCALYPTUS
DEWR_DARK_GREY = DEWR_GRAPHITE
DEWR_LIGHT_GREY = DEWR_MID_GREY
DEWR_OFF_WHITE = OCE_PANEL_BG
DEWR_SOFT_LINE = OCE_SOFT_DIVIDER
DEWR_TEXT_GREY = OCE_SECONDARY_TEXT
DEWR_MUTED_GREY = HexColor("#B8BBBD")
```

- [ ] **Step 2: Add typography, spacing, and layout scales**

Add dataclasses and constants:

```python
@dataclass(frozen=True)
class FontSet:
    regular: str
    bold: str
    italic: str
    bold_italic: str


@dataclass(frozen=True)
class Spacing:
    xxs: int = 2
    xs: int = 4
    sm: int = 6
    md: int = 8
    lg: int = 12
    xl: int = 16
    xxl: int = 20
    section: int = 28
    paragraph_gap: int = 8
    paragraph_to_visual: int = 12
    visual_to_note: int = 5
    note_to_text: int = 10


@dataclass(frozen=True)
class TypeScale:
    body: float = 10.5
    body_leading: float = 14.5
    body_bold: float = 10.5
    h1: float = 18
    h1_leading: float = 24
    h2: float = 14
    h2_leading: float = 18
    h3: float = 11.8
    h3_leading: float = 15.5
    h4: float = 10.5
    h4_leading: float = 13.5
    visual_title: float = 10.8
    visual_header: float = 7.6
    row_label: float = 8.2
    data_label: float = 8.2
    support_label: float = 7.8
    note: float = 8.2
    note_leading: float = 10.2
    kpi_large: float = 24
    kpi_medium: float = 16


@dataclass(frozen=True)
class Lines:
    hairline: float = 0.5
    gridline: float = 0.6
    strong: float = 2.0
    max_oce_gridline: float = 0.75


@dataclass(frozen=True)
class Radii:
    square: int = 0
    callout: int = 3
    small: int = 3


@dataclass(frozen=True)
class PageSpec:
    left_margin = 25 * mm
    right_margin = 25 * mm
    top_margin = 28 * mm
    bottom_margin = 25 * mm
    header_y = 20 * mm
    footer_rule_y = 18 * mm
    footer_text_y = 13 * mm
```

- [ ] **Step 3: Add font registration with Aptos fallback**

Add a `register_fonts()` helper that checks common system font paths for Aptos and falls back to Helvetica:

```python
APTOS_CANDIDATES = [
    Path("/Library/Fonts/Aptos.ttf"),
    Path("/Library/Fonts/Aptos-Bold.ttf"),
    Path("/System/Library/Fonts/Aptos.ttf"),
    Path.home() / "Library/Fonts/Aptos.ttf",
]


def register_fonts() -> FontSet:
    regular = next((p for p in APTOS_CANDIDATES if p.exists() and "Bold" not in p.name), None)
    bold = next((p for p in APTOS_CANDIDATES if p.exists() and "Bold" in p.name), None)
    if regular and bold:
        pdfmetrics.registerFont(TTFont("Aptos", str(regular)))
        pdfmetrics.registerFont(TTFont("Aptos-Bold", str(bold)))
        return FontSet("Aptos", "Aptos-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique")
    return FontSet("Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique")
```

- [ ] **Step 4: Import design tokens in generator**

In `generate_report.py`, import the module and replace top-level colour literals with aliases from `report_design_system.py`:

```python
from report_design_system import (
    DEWR_BLUE,
    DEWR_COBALT,
    DEWR_DARK_GREEN,
    DEWR_DARK_GREY,
    DEWR_GREEN,
    DEWR_GREY,
    DEWR_LIGHT_GREY,
    DEWR_LIME,
    DEWR_MUTED_GREY,
    DEWR_NAVY,
    DEWR_OFF_WHITE,
    DEWR_RED,
    DEWR_SOFT_LINE,
    DEWR_TEAL,
    DEWR_TEXT_GREY,
    OCE_DEFAULT_SERIES,
    OCE_DIVIDER,
    OCE_KEY_FINDING_BG,
    OCE_NOTE_TEXT,
    OCE_PANEL_BG,
    OCE_PRIMARY,
    OCE_SECONDARY_TEXT,
    OCE_SOFT_DIVIDER,
    OCE_TRACK,
    PageSpec,
    Radii,
    Spacing,
    TypeScale,
    register_fonts,
)
```

Expected after Step 4: `python3 -m py_compile report_design_system.py generate_report.py` exits 0.

### Task 2: Paragraph Styles And Story Rhythm

**Files:**
- Modify: `report_design_system.py`
- Modify: `generate_report.py`

- [ ] **Step 1: Add a style factory**

Add `build_paragraph_styles(fonts: FontSet)` to `report_design_system.py` returning a dictionary with `title`, `subtitle`, `h1`, `evaluation_h1`, `h2`, `h3`, `h4`, `mini_heading`, `metric_context`, `body`, `section_intro`, `body_bold`, `bullet`, `evidence_bullet`, `quote`, `note`, and `chart_title`.

Use these exact defaults:

```python
"body": fontSize=10.5, leading=14.5, textColor=OCE_TEXT, spaceAfter=8
"note": fontSize=8.2, leading=10.2, textColor=OCE_NOTE_TEXT, spaceBefore=4, spaceAfter=6
"chart_title": fontSize=10.8, leading=13.2, textColor=OCE_TEXT, spaceBefore=4, spaceAfter=4
"h2": fontSize=14, leading=18, textColor=OCE_TEXT, spaceBefore=14, spaceAfter=8
"h3": fontSize=11.8, leading=15.5, textColor=OCE_TEXT, spaceBefore=10, spaceAfter=6
```

- [ ] **Step 2: Replace local `ParagraphStyle` block**

In `build_report()`, replace the current local style definitions with:

```python
    fonts = register_fonts()
    report_styles = build_paragraph_styles(fonts)
    title_style = report_styles["title"]
    subtitle_style = report_styles["subtitle"]
    h1 = report_styles["h1"]
    evaluation_h1 = report_styles["evaluation_h1"]
    h2 = report_styles["h2"]
    h3 = report_styles["h3"]
    h4 = report_styles["h4"]
    mini_heading = report_styles["mini_heading"]
    metric_context = report_styles["metric_context"]
    body = report_styles["body"]
    section_intro = report_styles["section_intro"]
    body_bold = report_styles["body_bold"]
    bullet_style = report_styles["bullet"]
    evidence_bullet_style = report_styles["evidence_bullet"]
    quote_style = report_styles["quote"]
    note_style = report_styles["note"]
    chart_title = report_styles["chart_title"]
```

- [ ] **Step 3: Standardise spacing helpers**

Replace `sp()` and `visual_spacer()` with token-driven helpers:

```python
    spacing = Spacing()

    def sp(h=Spacing.sm):
        return Spacer(1, h)

    def para_gap():
        return sp(spacing.paragraph_gap)

    def visual_spacer():
        return sp(spacing.paragraph_to_visual)

    def note_gap():
        return sp(spacing.visual_to_note)
```

Update obvious hard-coded story rhythm values:
- paragraph-to-visual spacing: `visual_spacer()`
- visual-to-note spacing: `sp(4)` or `sp(6)` becomes `note_gap()` where directly between visual and note
- source note to next subsection: `sp(10)` or `sp(12)` according to the next content density

- [ ] **Step 4: Add page-break rules for major transitions**

Make these content edits in `generate_report.py`:
- Start Section 3 on a new page instead of at the bottom of Page 9.
- Keep the Section 3 opener callout and KPI strip together.
- Prevent `3.3 Respondents were more likely...` from starting at the bottom of Page 10 by grouping the heading, paragraph, and first visual when possible.
- Rename the last page heading from `Visual Options` to `Appendix A. All-tool task footprint` so it reads as a finished appendix, not a prototype page.
- Replace the corrupted Section 3 intro paragraph with: `All respondents were asked about concerns, confidence and safeguards when using public generative AI tools during the trial. The results point to generally comfortable use, with specific concern signals concentrated around information handling and practical judgement.`

Expected after Task 2: `python3 -m py_compile report_design_system.py generate_report.py` exits 0.

### Task 3: Shared Panel And Table Styling

**Files:**
- Modify: `report_design_system.py`
- Modify: `generate_report.py`

- [ ] **Step 1: Add drawing helpers**

Add helpers to `report_design_system.py`:

```python
def draw_panel_background(canvas, width, height):
    canvas.setFillColor(OCE_PANEL_BG)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)


def draw_divider(canvas, x1, y, x2):
    canvas.setStrokeColor(OCE_DIVIDER)
    canvas.setLineWidth(0.5)
    canvas.line(x1, y, x2, y)


def draw_vertical_divider(canvas, x, y1, y2):
    canvas.setStrokeColor(OCE_DIVIDER)
    canvas.setLineWidth(0.5)
    canvas.line(x, y1, x, y2)
```

- [ ] **Step 2: Migrate evidence surfaces**

Update every evidence panel to use `draw_panel_background()` rather than repeated `HexColor("#F7F8FA")`, including:
- `ValueSignalsPanel`
- `TimeSavingsPanel`
- `M365LicenceCoveragePanel`
- `CopilotEngagementDeltaPanel`
- `EvidenceMatrixPanel`
- `HorizontalEvidenceCallout`
- `PriorExperienceComparisonPanel`
- `HorizontalBarPanel`
- `ComfortDataHandlingPanel`
- `PublicToolTaskProfilePanel`
- `AllToolTaskProfilePanel`
- `SafeguardPrioritiesPanel`
- `UncertaintyAreasPanel`
- `SafeguardModelPanel`
- `ConcernClusterMap`
- `TaskFootprintExhibit`

- [ ] **Step 3: Standardise KPI/value strips**

Apply these rules to `ValueSignalsPanel` and `HorizontalEvidenceCallout`:
- panel padding: 16pt
- large KPI: 24pt, or downscale only when the value would overflow
- supporting label: 7.8pt, 9.0pt leading
- divider width: 0.5pt
- no rounded corners for evidence panels
- primary value uses eucalyptus/dark eucalyptus; comparison values use graphite; negative/caution values use red only when semantically cautionary

- [ ] **Step 4: Standardise matrix/table panels**

Update `EvidenceMatrixPanel` and `access_evidence_table()`:
- header label: 7.6pt bold uppercase
- row label: 8.2pt bold
- numeric values: 12pt bold for dense tables, 14-16pt where there are two columns
- internal lines: `OCE_SOFT_DIVIDER` or `OCE_DIVIDER`, 0.5pt
- left/right padding: 16pt
- no decorative borders
- strongest value highlighted in eucalyptus; all other values graphite

Expected after Task 3: generated PDF still has 12 or more valid pages and no `LayoutError`.

### Task 4: Chart Components And Colour Discipline

**Files:**
- Modify: `generate_report.py`

- [ ] **Step 1: Standardise bar charts**

Update `TimeSavingsPanel`, `HorizontalBarPanel`, `ComfortDataHandlingPanel`, and similar horizontal bar panels:
- use `OCE_TRACK` for tracks
- use `OCE_PRIMARY` for primary/highlighted values
- use graphite for comparison bars
- use 0-100 scale for percentage bars
- keep direct value labels at bar ends
- avoid redundant axis labels when bars are directly labelled

- [ ] **Step 2: Standardise dot plots**

Update `PublicToolTaskProfilePanel`, `AllToolTaskProfilePanel`, and `TaskFootprintExhibit`:
- x-axis ticks at 0, 25, 50, 75, 100 for percentage charts
- tick labels 7.2pt muted graphite/grey
- gridlines 0.5pt in `OCE_DIVIDER`
- row labels 7.8-8.2pt
- direct labels for the analytical focus/highest values
- use legend only where every series is not directly labelled; do not duplicate direct labels and legend labels for the same purpose
- use default series order from the OCE palette: dark eucalyptus, graphite, lime, teal, blue, plum

- [ ] **Step 3: Fix the five-series appendix palette**

Keep the appendix chart, but make it read as a finished appendix:
- `M365 Copilot`: dark eucalyptus
- `Copilot Chat`: graphite
- `ChatGPT`: grey
- `Gemini`: lime
- `Claude`: teal
- de-emphasise non-focus series where there are near-overlaps

- [ ] **Step 4: Standardise notes**

Update `source_note()` and all source notes:
- note text uses graphite, italic, 8.2pt, 10.2pt leading
- notes sit within 4-6pt of the relevant visual
- each chart/table keeps the note immediately below it

Expected after Task 4: all charts use official DEWR palette values only, except `OCE_PANEL_BG`, `OCE_TRACK`, `OCE_TRACK_ALT`, and `OCE_KEY_FINDING_BG` neutral support colours.

### Task 5: Page Chrome And Cover

**Files:**
- Modify: `generate_report.py`

- [ ] **Step 1: Page margins and chrome**

Use `PageSpec` for `SimpleDocTemplate` margins and header/footer positions:

```python
    page = PageSpec()
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=page.left_margin,
        rightMargin=page.right_margin,
        topMargin=page.top_margin,
        bottomMargin=page.bottom_margin,
    )
```

Update `header_footer()` to use graphite text and 0.75pt max line widths, with the header rule still strong enough to visually anchor pages.

- [ ] **Step 2: Cover tokens**

Use `DEWR_GRAPHITE` for the cover background, `DEWR_EUCALYPTUS` for the footer band, and `DEWR_EUCALYPTUS` or `DEWR_DARK_EUCALYPTUS` for subtitle/date text depending on contrast. Keep the current official lockup placement.

- [ ] **Step 3: Output metadata**

Set PDF title/author metadata through the document where practical:
- title: `Public Generative AI Trial Evaluation Report`
- author: `Department of Employment and Workplace Relations`

Expected after Task 5: cover remains dark and official-looking, and body page chrome remains consistent.

### Task 6: Verification And Visual QA

**Files:**
- Verify: `report_design_system.py`
- Verify: `generate_report.py`
- Verify: `Outputs/DEWR_Public_AI_B.pdf`

- [ ] **Step 1: Compile Python**

Run:

```bash
python3 -m py_compile report_design_system.py generate_report.py
```

Expected: exit 0.

- [ ] **Step 2: Generate report**

Run:

```bash
python3 generate_report.py
```

Expected: prints `Report generated: /Users/aristotle/Projects/Python-Idiomatic/Outputs/DEWR_Public_AI_B.pdf`.

- [ ] **Step 3: Render page images**

Run the temporary PDFKit renderer already proven in this session:

```bash
/private/tmp/render_pdf_pages /Users/aristotle/Projects/Python-Idiomatic/Outputs/DEWR_Public_AI_B.pdf /private/tmp/dewr_report_pages_after dewr-report-after
```

Expected: reports the generated page count and writes page PNGs.

- [ ] **Step 4: Create contact sheet**

Run:

```bash
python3 -c "from PIL import Image, ImageDraw; import glob, os, math; files=sorted(glob.glob('/private/tmp/dewr_report_pages_after/dewr-report-after-*.png')); thumbs=[]; w,h=280,396
for f in files:
    im=Image.open(f).convert('RGB'); im.thumbnail((w,h)); canvas=Image.new('RGB',(w,h+24),'white'); canvas.paste(im,((w-im.width)//2,0)); ImageDraw.Draw(canvas).text((8,h+6),os.path.basename(f),fill=(0,0,0)); thumbs.append(canvas)
cols=3; rows=math.ceil(len(thumbs)/cols); sheet=Image.new('RGB',(cols*w,rows*(h+24)),(245,245,245))
for i,t in enumerate(thumbs): sheet.paste(t,((i%cols)*w,(i//cols)*(h+24)))
sheet.save('/private/tmp/dewr_report_after_contact_sheet.png')"
```

Expected: `/private/tmp/dewr_report_after_contact_sheet.png` exists.

- [ ] **Step 5: Manual visual checks**

Inspect the contact sheet and at least pages 2, 3, 6, 9, 10, 11, and appendix page. Confirm:
- no headings orphaned at page bottoms
- no major section starts at the bottom of a page
- notes remain attached to visuals
- typography looks consistent across KPI strips, tables, bars, and dot plots
- charts use DEWR palette and no decorative colours
- Section 3 intro is corrected
- appendix no longer reads as a draft/prototype page

- [ ] **Step 6: Literal-value scan**

Run:

```bash
rg -n "HexColor\\(\"#|setFont\\(|fontSize=|leading=|roundRect|Spacer\\(1, [0-9]" generate_report.py report_design_system.py
```

Expected: remaining literals are either design-system tokens, content-specific layout inside a bespoke Flowable, or justified exceptions. No repeated `HexColor("#F7F8FA")` should remain in `generate_report.py`.
