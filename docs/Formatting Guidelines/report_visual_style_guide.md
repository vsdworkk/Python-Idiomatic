# DEWR Public AI Trial Report Design System

This design system defines the visual language for the DEWR Public AI Trial report. It is intended for ReportLab/PDF production and should be used when creating, refining, or reviewing report pages, callouts, evidence panels, charts, tables, notes, and page-level layout.

The goal is a clean executive-report style: structured, readable, analytical, and consistent with DEWR colours. The report should feel authoritative without looking over-designed.

## Design Principles

### 1. Narrative First, Visual Second

Lead with the takeaway in the paragraph immediately before a visual. The visual should then prove the point with compact evidence.

Do:

- Put interpretation in the body copy.
- Use the visual for facts: labels, values, rows, columns, comparisons, and source notes.
- Keep visual headings short.

Avoid:

- Long explanatory visual titles.
- Extra badges or callouts inside the visual when the paragraph can carry the message.
- Visuals that require the reader to infer what decision or implication matters.

### 2. One Visual, One Job

Each evidence visual should answer one analytical question.

Good examples:

- "How much time did M365 Copilot users report saving?"
- "How does coverage differ by classification and group?"
- "Which tools were most used for each task type?"

Avoid mixing unrelated cuts unless the design clearly separates them with structure, labels, and notes.

### 3. OCE-Aligned Clarity

Visuals should be easy to read at report scale and should not rely on decorative complexity.

Use:

- Square evidence panels.
- Thin internal dividers.
- Direct labels on values.
- Sorted rows where rank matters.
- Notes directly below visuals.

Avoid:

- Rounded metric cards inside evidence panels.
- Outer borders when the panel background already defines the block.
- Nested grey cards inside grey panels.
- Decorative icons.
- Inconsistent label colour or spacing.

## Core Tokens

Use these tokens consistently in ReportLab code.

### Colour

| Token | Hex | Use |
| --- | --- | --- |
| `DEWR_GREEN` | `#719F4C` | Primary positive value, key highlight, strong result |
| `DEWR_DARK_GREEN` | `#5D7A38` | Primary chart fill, strongest value, emphasis in evidence panels |
| `DEWR_DARK_GREY` | `#404246` | Primary text, headings, comparison values, labels |
| `DEWR_TEXT_GREY` | `#6B6E70` | Secondary explanatory text |
| `DEWR_GREY` | `#A4A7A9` | Muted labels, secondary notes, subdued markers |
| `DEWR_MUTED_GREY` | `#B8BBBD` | Low-priority secondary information |
| `DEWR_LIGHT_GREY` | `#D7D8D8` | Internal dividers, hairlines |
| `DEWR_SOFT_LINE` | `#E1E3DF` | Very soft panel separators |
| `DEWR_OFF_WHITE` | `#F7F8FA` | Evidence panel background |
| `DEWR_TEAL` | `#009B9F` | Secondary data series only when needed |
| `DEWR_LIME` | `#B5C427` | Tertiary data series only when needed |
| `DEWR_RED` | `#91040D` | Caution, negative, changed or exception values |
| `white` | `#FFFFFF` | Cover text, callout text, rare internal contrast |

Colour rules:

- Use `DEWR_OFF_WHITE` for evidence panels.
- Use `DEWR_DARK_GREY` for most labels and comparison values.
- Use `DEWR_DARK_GREEN` or `DEWR_GREEN` for the primary or strongest value.
- Use `DEWR_LIGHT_GREY` or `DEWR_SOFT_LINE` for dividers and tracks.
- Do not introduce a McKinsey blue palette unless the whole report is being restyled.
- Do not use gradients in content visuals.

### Typography

The report uses standard PDF-safe Helvetica styles.

| Role | Font | Size | Leading | Colour | Notes |
| --- | --- | ---: | ---: | --- | --- |
| Section heading | Helvetica-Bold | 14-18 | 18-24 | `DEWR_DARK_GREY` | Use outside visuals |
| Subsection heading | Helvetica-Bold | 11.5-14 | 15-18 | `DEWR_DARK_GREY` | Use outside visuals |
| Body text | Helvetica | 10 | 14 | `DEWR_DARK_GREY` | Justified in narrative paragraphs |
| Body emphasis | Helvetica-Bold | 10 | 14 | `DEWR_DARK_GREY` | For key facts in paragraphs |
| Visual title | Helvetica-Bold | 10-11 | n/a | `DEWR_DARK_GREY` | Short only, not a sentence |
| Visual header label | Helvetica-Bold | 7-8 | n/a | `DEWR_DARK_GREY` | Uppercase for compact evidence visuals |
| Large KPI | Helvetica-Bold | 20-26 | n/a | Green or dark grey | Use sparingly |
| Medium KPI | Helvetica-Bold | 13-18 | n/a | Green or dark grey | Use in compact panels |
| Row label | Helvetica-Bold | 7.5-9 | n/a | `DEWR_DARK_GREY` | Directly label rows |
| Data label | Helvetica-Bold | 7-9 | n/a | Data-series colour | Label bars/dots directly |
| Supporting label | Helvetica or Helvetica-Bold | 6.8-8 | n/a | `DEWR_DARK_GREY` | Under KPI values |
| Source note | Helvetica-Oblique | 8-8.5 | 10-11 | `DEWR_GREY` | Immediately below visual |

Typography rules:

- Keep visual labels small, bold, and consistent.
- Use uppercase labels for visual headers.
- Use sentence case for respondent group names and supporting labels.
- Avoid long headings inside panels.
- If a label must wrap, use a `Paragraph` with controlled width and leading.

## Spacing System

Use a small set of spacing values so visuals feel related.

| Token | Points | Use |
| --- | ---: | --- |
| `xs` | 4 | Tight label/value spacing |
| `sm` | 6 | Between compact text elements |
| `md` | 8 | Standard internal breathing room |
| `lg` | 12 | Between visual components |
| `xl` | 16 | Standard panel padding |
| `2xl` | 18-20 | Large panel padding and page visual inset |
| `section` | 24-34 | Between major rows or grouped chart rows |

ReportLab standards:

- Standard evidence panel padding: `16 pt` or `18 pt`.
- Larger analytical panels: `20 pt`.
- Hairline divider below title/header: title baseline at `h - 22`, divider at `h - 32` to `h - 34`.
- Compact chart header row: header label baseline at `h - 20`, legend baseline aligned to the same row, divider at `h - 28`.
- In compact chart headers, right-align the legend to the divider or plot boundary. Position the legend from right to left so the final character of the final legend label ends exactly where the divider line ends.
- Compact chart tick row: tick-label baseline around `h - 42`, with gridlines starting around `tick_y - 4`.
- First chart row should sit close to the tick row. For dot plots/dumbbells, place the first row around `h - 49`, so the first row is almost tucked under the 0/25/50/75/100 labels.
- Evidence panel bottom padding: minimum `14-16 pt`.
- Visual-to-note spacing: `4-6 pt`.
- Paragraph-to-visual spacing: `12 pt`. This is the default "two spaces, then visual" rhythm for evidence panels after explanatory text.
- Visual-to-next-paragraph spacing: `6-12 pt`, depending on page density.

### Narrative Text Rhythm

Narrative spacing should make the argument easy to scan before the reader reaches the evidence visual.

Recommended defaults:

| Relationship | Spacing |
| --- | ---: |
| Heading to first paragraph | heading style `spaceAfter` plus `2 pt` explicit spacer |
| Paragraph to paragraph | `6-8 pt` |
| Paragraph to bullet list | `6 pt` |
| Bullet to bullet | `4-5 pt` |
| Bullet list to visual | `10-12 pt` |
| Paragraph to visual | `12 pt` |
| Visual to source note | `4-6 pt` |
| Source note to next paragraph | `8-12 pt` |

Text settings:

- Body text: `10 pt` Helvetica, `14 pt` leading.
- Bullet text: `9.5-10 pt` Helvetica, `13.5-14 pt` leading.
- Bullet indentation: left indent around `18 pt`, bullet indent around `6 pt`.
- For subsection headings in dense report pages, keep the heading style's normal `spaceAfter` and add a `2 pt` spacer before the first paragraph when the section starts to feel cramped.
- Keep bullets short enough to wrap cleanly over no more than two lines where possible.
- Do not place dense bullets immediately against a visual; leave at least `10 pt` before the panel.
- Avoid widowed one-line paragraphs immediately above a visual.

Alignment rules:

- Panel left/right edges must align to the report content width.
- Internal elements should align to a shared x-start unless intentionally centred.
- Related values should share the same baseline.
- Divider start/end points should be consistent within the panel.
- Bars should end on the same right edge as the visual's internal content area.

## Layout System

### Page And Content Width

The report uses A4 pages with margins set in `generate_report.py`.

Current page setup:

```python
doc = SimpleDocTemplate(
    OUTPUT_PATH,
    pagesize=A4,
    leftMargin=25*mm,
    rightMargin=25*mm,
    topMargin=28*mm,
    bottomMargin=25*mm,
)
```

All major visuals should use the calculated `width`:

```python
width = A4[0] - doc.leftMargin - doc.rightMargin
```

Do not create visuals that protrude beyond this content width.

### Evidence Panel Anatomy

Default evidence panel:

```text
Soft grey background (#F7F8FA)
20 pt horizontal padding
Short visual title or compact header label, if needed
Thin horizontal divider (#D7D8D8, 0.5 pt)
Evidence area: values, rows, bars, columns, dots or comparison blocks
Optional internal dividers only
No outer border
No rounded corners
```

### Titles Inside Visuals

Use a visual title only when it helps navigation. If the preceding paragraph already frames the insight, omit the title or use a very short label.

Good:

- `M365 COPILOT LICENCE COVERAGE`
- `MEASURE`
- `DATA HANDLING BY COMFORT USING PUBLIC TOOLS`

Avoid:

- Full-sentence titles.
- Titles that repeat the paragraph.
- Titles that combine too many analytical dimensions.

## Component Patterns

### 1. Narrative Callout

Use callouts for section-level takeaways only.

Style:

- Rounded corners.
- Soft green background or dark green fill depending on emphasis.
- Bold text.
- Width aligned to content column.
- Use enough padding for wrapped text.

Callouts are the exception to the square-corner rule. Their rounded shape distinguishes narrative emphasis from evidence panels.

### 2. Evidence Panel

Use for compact proof points, metric summaries, visual comparisons, and small charts.

Style:

- Square corners.
- `DEWR_OFF_WHITE` background.
- No outer border.
- Thin internal dividers only.
- Values and labels directly visible.

Avoid:

- White cards inside grey panels unless needed for legibility.
- Nested card effects.
- Decorative shadows or rounded corners.

### 3. Comparison Metric Panel

Use when comparing two or three groups on one headline measure.

Structure:

- Equal-width columns.
- Group label at top.
- Large percentage centred below.
- Short supporting label below percentage.
- Thin vertical dividers between columns.

Recommended dimensions:

```text
Panel height: 90-110 pt
Top label baseline: h - 24
Percentage baseline: h - 52 to h - 58
Supporting label baseline: h - 70 to h - 78
Vertical dividers: y = 14 to h - 42
```

### 4. Bar Panel

Use horizontal bars for ranked percentages, adoption, coverage, limitations, and task prevalence.

Structure:

- Optional compact header label.
- Sorted rows if ranking matters.
- Direct row label above or left of each bar.
- Light grey track.
- Green fill for primary/highest value.
- Dark grey fill for comparison values.
- Percentage label directly after fill.

Recommended dimensions:

```text
Bar height: 7-14 pt
Row gap: 19-34 pt depending on label density
Track colour: #E1E5E2 or #E3E6E4
Fill scale: 0-100% unless the visual explicitly states another scale
```

Scale rule:

- Use a 0-100% scale when the point is absolute coverage or prevalence.
- Use an indexed scale, dot plot, or variance view when small differences matter more than absolute magnitude.

### 5. Dot Plot Or Dumbbell

Use when comparing multiple tools or groups across tasks and bars would be too dense.

Structure:

- Shared horizontal axis.
- Light vertical gridlines.
- Direct labels for highest or key values.
- Legend inside the visual only if necessary.
- Highlight the analytical focus with green or dark grey.

Rules:

- Keep dots large enough to read at PDF scale.
- Avoid over-labelling every point.
- Resolve near-overlaps manually by nudging labels.
- Put the category header, such as `TASK`, above the divider line.
- Keep the tick labels close to the divider line and the first row close to the tick labels. The chart should feel compact vertically, not like the first row is floating too low.
- Use `row_gap` around `23 pt` for seven task rows.
- Use subdued or "fogged" versions of the series colours for non-highlight rows, preserving the same green/black identity without competing with highlighted rows.

### 6. Evidence Matrix

Use for compact multi-metric comparison across groups or tools.

Structure:

- First column: measure labels.
- Remaining columns: groups/tools.
- Hairline dividers.
- Section separator rows only if needed.
- Highlight strongest values in green.

Rules:

- Numeric values should be centred.
- Measure labels should be left aligned.
- Keep row heights consistent.
- Use section rows sparingly.

### 7. Notes And Sources

Notes should sit immediately below the visual and align to the same content width.

Style:

- Helvetica-Oblique.
- 8-8.5 pt.
- `DEWR_GREY`.
- Sentence case.

Use notes to clarify:

- Sample sizes.
- Separate cuts of the workforce.
- Directional interpretation.
- Source.

Example:

```text
Note: Licence coverage uses current M365 licence counts as a share of all staff in each group. Classification level and organisational group are separate cuts of the workforce and should not be summed.
```

## Visual-Specific Guidance

### M365 Licence Coverage

Purpose: show limited M365 Copilot licence coverage across classification level and organisational group without implying the two cuts can be summed.

Recommended structure:

- One soft grey panel.
- Short title: `M365 COPILOT LICENCE COVERAGE`.
- Left: classification-level KPI stack or compact three-column comparison.
- Right: organisational group bars sorted high-to-low.
- Thin vertical divider between classification and group areas.
- Note below clarifying that classification level and organisational group are separate cuts.

Use 0-100% bar scale if the message is limited absolute coverage. Consider a dot plot with an overall reference marker if the message is relative group variation.

### Time Savings

Purpose: compare M365 Copilot and Copilot Chat productivity signals.

Recommended structure:

- Two horizontal bars.
- M365 in green, Chat in dark grey.
- Weekly time saved as the right-aligned primary label.
- Daily time saved as smaller supporting label underneath.
- No excessive axis decoration.

### Task Footprint

Purpose: show where M365 Copilot and Copilot Chat differ in reported task use.

Recommended structure:

- Dumbbell or dot plot.
- Common percentage axis.
- Highlight largest access-type gaps.
- Use direct labels only for highlighted rows.

### Public Tool Task Profile

Purpose: compare ChatGPT, Gemini, and Claude by task type.

Recommended structure:

- Dot plot on 0-100% axis.
- Tool legend in compact header area.
- Highlight highest value per task with label.
- Keep axis ticks at 0%, 25%, 50%, 75%, 100%.

### Safety And Data Handling

Purpose: show comfort, concerns, copy/paste, upload, and safeguard signals.

Recommended structure:

- Use value-signal strips for headline results.
- Use paired/grouped bars for behavioural comparisons.
- Use three-column text panels only for qualitative themes.

## Implementation Checklist

Before delivering a visual:

- [ ] The preceding paragraph states the takeaway.
- [ ] The visual has one analytical job.
- [ ] Panel width aligns to the content column.
- [ ] Background uses `DEWR_OFF_WHITE`.
- [ ] Corners are square for evidence panels.
- [ ] No nested cards unless there is a clear purpose.
- [ ] Header labels are dark grey, small, bold, and consistent.
- [ ] Internal dividers are `DEWR_LIGHT_GREY` at `0.4-0.6 pt`.
- [ ] Primary/highest value uses green; comparisons use dark grey.
- [ ] Values and labels share baselines where comparable.
- [ ] Bars or rows are sorted when ranking matters.
- [ ] Any axis or scale choice is honest and interpretable.
- [ ] Notes sit directly below the visual.
- [ ] The visual does not rely on decorative elements.

## Common ReportLab Defaults

Use these defaults unless a visual has a specific reason to deviate.

```python
PANEL_BG = DEWR_OFF_WHITE       # #F7F8FA
TEXT = DEWR_DARK_GREY          # #404246
SECONDARY_TEXT = DEWR_TEXT_GREY
DIVIDER = DEWR_LIGHT_GREY      # #D7D8D8
TRACK = HexColor("#E1E5E2")
PRIMARY = DEWR_DARK_GREEN

PANEL_PAD = 16                 # compact panels
PANEL_PAD_LARGE = 20           # larger evidence panels
DIVIDER_WIDTH = 0.5
HEADER_SIZE = 7.2
VISUAL_TITLE_SIZE = 10.5
ROW_LABEL_SIZE = 8
DATA_LABEL_SIZE = 8
SOURCE_NOTE_SIZE = 8.5
```

## What To Avoid

Avoid:

- Long explanatory titles inside visuals.
- Decorative icons or chart junk.
- Rounded evidence panels.
- Nested grey cards.
- Unaligned right edges.
- Inconsistent padding across similar visuals.
- Different font sizes for equivalent labels.
- Green applied to too many values.
- Bars on a misleading truncated scale.
- Notes separated from the relevant visual.
