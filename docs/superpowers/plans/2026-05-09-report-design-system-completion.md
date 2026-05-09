# Report Design System Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish standardising the ReportLab-generated DEWR report so repeated typography, colour, card, chart, table, note, spacing and page-rhythm decisions are controlled by `report_design_system.py`.

**Architecture:** Keep the current two-file architecture. `report_design_system.py` owns tokens, ParagraphStyle factories, table-style factories, visual text helpers, Flowable spacing helpers and reusable measurement helpers. `generate_report.py` remains the report assembly and custom visual implementation layer, but should consume named design-system APIs instead of creating one-off visual styles, line widths, padding values, notes, or story gaps.

**Tech Stack:** Python 3.9, ReportLab 4.5 Platypus, custom Flowables, macOS PDFKit screenshot rendering, Pillow contact sheets.

**Audit Evidence:** Current 12-page screenshots rendered to `/private/tmp/report-audit/pages`; contact sheet at `/private/tmp/report-audit/contact-sheet.png`. ReportLab user guide research highlights Chapter 5 Flowables/PageTemplates, Chapter 6 ParagraphStyles/spacing, Chapter 7 TableStyles, Chapter 9 `CondPageBreak`/`KeepTogether`, and Chapter 10 custom Flowables.

---

## File Structure

- Modify: `report_design_system.py`
  - Add reusable visual paragraph-style builders.
  - Add table-style factories.
  - Add named story-rhythm helpers and Flowable spacing support.
  - Add text measurement/drawing helpers for custom Canvas Flowables.

- Modify: `generate_report.py`
  - Replace local visual `ParagraphStyle(...)` creation with design-system style factories.
  - Replace fixed visual component spacing with named tokens.
  - Use table-style factories for evidence tables.
  - Use explicit story rhythm helpers for paragraph, visual, note and section gaps.
  - Add `CondPageBreak` before predictable exhibit blocks where `KeepTogether` is too blunt.

- Generated output: `Outputs/DEWR_Public_AI_B.pdf`
  - Regenerated after implementation and visually checked.

---

### Task 1: Design-System API Completion

**Files:**
- Modify: `report_design_system.py`

- [ ] Add `StoryRhythmSpec` with named gaps: `heading_gap=2`, `paragraph_gap=8`, `tight_gap=4`, `visual_gap=12`, `note_gap=5`, `after_note_gap=10`, `section_gap=14`.
- [ ] Add `FlowableSpacingMixin` implementing `getSpaceBefore()` and `getSpaceAfter()` from `space_before` and `space_after` attributes.
- [ ] Add `visual_paragraph_style(name, fonts, role, alignment=TA_LEFT, bold=False, italic=False, text_color=None)` for common visual roles: `panel_header`, `panel_header_small`, `card_title`, `card_body`, `kpi_caption`, `chart_label`, `table_header`, `table_label`, `table_value`, `stacked_row_label`, `theme_title`, `theme_body`, `safeguard_title`, `safeguard_body`, `model_body`, `note`.
- [ ] Add `make_visual_styles(fonts)` returning a dictionary of these reusable styles.
- [ ] Add `draw_wrapped_text(canvas, text, style, x, y_top, width, max_height)` to centralise the repeated `Paragraph(...).wrap(...).drawOn(...)` pattern in custom Flowables.
- [ ] Add `evidence_table_style()` and `access_evidence_table_style()` factories that encode background, divider, padding, alignment and vertical alignment tokens.
- [ ] Compile with `PYTHONPYCACHEPREFIX=/private/tmp/python-idiomatic-pycache python3 -m py_compile report_design_system.py`.

### Task 2: KPI, Card And Callout Flowables

**Files:**
- Modify: `generate_report.py`

- [ ] Import `StoryRhythmSpec`, `make_visual_styles`, `draw_wrapped_text`, and the table-style factories.
- [ ] Instantiate `VISUAL_STYLES = make_visual_styles(REPORT_FONTS)` and `RHYTHM = StoryRhythmSpec()`.
- [ ] Refactor `CalloutBox`, `ValueSignalsPanel`, `CalloutSignalsPanel`, `ComparisonCard`, `TwoEvidenceCardsPanel`, `HorizontalEvidenceCallout`, and `KeyFindingBar` to reuse `VISUAL_STYLES` and `draw_wrapped_text`.
- [ ] Replace hard-coded callout leading formulas with `VISUAL_TEXT.callout_text_leading`.
- [ ] Wrap each `draw()` body touched in `saveState()` / `restoreState()` so visual components do not leak canvas state.
- [ ] Compile `generate_report.py`.

### Task 3: Tables, Matrices And Qualitative Panels

**Files:**
- Modify: `generate_report.py`

- [ ] Refactor `EvidenceMatrixPanel`, `CopilotEngagementDeltaPanel`, `M365ValueAndReachTable`, `PriorExperienceComparisonPanel`, `SafeguardPrioritiesPanel`, `UncertaintyAreasPanel`, `SafeguardModelPanel`, `ConcernClusterMap`, and `DataHandlingCrosstabPanel` to use `VISUAL_STYLES`.
- [ ] Replace `access_evidence_table()` local `TableStyle` commands with `access_evidence_table_style()`.
- [ ] Use `draw_wrapped_text()` for repeated row labels and body blocks.
- [ ] Keep fixed widths where the report depends on designed comparison columns; remove fixed row heights only where Paragraph content would otherwise risk clipping.
- [ ] Compile `generate_report.py`.

### Task 4: Charts And Appendix Visuals

**Files:**
- Modify: `generate_report.py`

- [ ] Refactor `HorizontalBarPanel`, `ComfortDataHandlingPanel`, `PublicToolTaskProfilePanel`, `AllToolTaskProfilePanel`, `GroupedBarChart`, and `TaskFootprintExhibit` to use common chart label, legend, tick and value styles.
- [ ] Ensure all chart tracks, dividers, gridlines, value labels, row labels and series colours map to existing design-system tokens.
- [ ] Keep the appendix label as `Appendix A. All-tool task footprint` and preserve the five-series palette documented in the current visual style guide.
- [ ] Compile `generate_report.py`.

### Task 5: Story Rhythm And Pagination

**Files:**
- Modify: `generate_report.py`

- [ ] Replace `sp()` and `visual_spacer()` defaults with `RHYTHM` tokens.
- [ ] Add helper functions: `para_gap()`, `tight_gap()`, `visual_gap()`, `note_gap()`, `after_note_gap()`, and `section_gap()`.
- [ ] Replace obvious `sp(4)`, `sp(6)`, `sp(8)`, `sp(10)`, `sp(12)`, `sp(14)` calls with semantic helpers where the relationship is clear.
- [ ] Import and use `CondPageBreak` before major heading + exhibit blocks on pages currently prone to awkward breaks.
- [ ] Regenerate the PDF and confirm page count remains 12 unless a more professional page break clearly requires 13.

### Task 6: Verification And Visual QA

**Files:**
- Verify: `report_design_system.py`
- Verify: `generate_report.py`
- Verify: `Outputs/DEWR_Public_AI_B.pdf`

- [ ] Run `PYTHONPYCACHEPREFIX=/private/tmp/python-idiomatic-pycache python3 -m py_compile report_design_system.py generate_report.py`.
- [ ] Run `PYTHONPYCACHEPREFIX=/private/tmp/python-idiomatic-pycache python3 generate_report.py`.
- [ ] Render pages with Swift/PDFKit to `/private/tmp/report-audit-after/pages`.
- [ ] Create `/private/tmp/report-audit-after/contact-sheet.png`.
- [ ] Visually inspect the contact sheet plus pages 2, 6, 10, 11 and 12.
- [ ] Scan remaining `ParagraphStyle(`, `setFont(`, `Spacer(` and `sp(` usages and verify any survivors are either central factories, direct Canvas drawing that must set a font, or data/layout coordinates rather than reusable design decisions.
