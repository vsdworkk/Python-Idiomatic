# Report Visual Design System Next Pass Design

## Goal

Standardise the custom ReportLab visuals in `generate_report.py` so chart headers, card titles, KPI values, labels, legends, axis ticks, dot sizes, bar heights, inner padding, dividers and visual spacing all come from named design-system tokens rather than local magic numbers.

## Context

The first pass added `report_design_system.py` with official OCE/DEWR colours, paragraph styles, page specs, font registration and shared drawing helpers. That improved global styling, but many custom Flowables still define their own visual constants directly inside `draw()` methods.

The next pass should keep the current file structure stable and avoid a large component split. It should centralise visual detail first, then wire each Flowable to the shared specs.

## Recommended Architecture

Add a second layer of visual tokens to `report_design_system.py`:

- `VisualTextSpec`: small visual type sizes for panel headers, card titles, chart labels, legends, axis ticks, table headers, table body labels, table values, KPI values, KPI captions and notes.
- `PanelSpec`: standard panel padding, large panel padding, inner padding, divider insets, header baseline, header divider offset and default panel height rhythm values.
- `KpiSpec`: KPI value sizes, compact KPI value size, KPI caption size/leading, default column divider insets and KPI panel height.
- `ChartLayoutSpec`: bar heights, compact bar heights, row heights, dot radii, highlighted dot radii, legend marker radii, axis tick text size and value label sizes.
- `TableSpec`: matrix header height, row height, section row text size, header text size, body label size, value size and cell padding.

Keep existing palette and font tokens intact. `generate_report.py` should instantiate these specs once near the existing `PAGE_SPEC`, `SPACING`, `LINES`, `RADII` and `CHART` constants.

## Component Scope

Refactor custom visuals in four groups:

1. KPI/card components:
   `ValueSignalsPanel`, `CalloutSignalsPanel`, `StatBox`, `ComparisonCard`, `TwoEvidenceCardsPanel`, `HorizontalEvidenceCallout`, `KeyFindingBar`.

2. Tables and evidence matrices:
   `EvidenceMatrixPanel`, `access_evidence_table`, `CopilotEngagementDeltaPanel`, `PriorExperienceComparisonPanel`.

3. Charts:
   `HorizontalBarPanel`, `ComfortDataHandlingPanel`, `PublicToolTaskProfilePanel`, `AllToolTaskProfilePanel`, `TaskFootprintExhibit`, `GroupedBarChart`.

4. Page chrome:
   `header_footer`, `cover_page`.

## Design Rules

- Preserve the current visual hierarchy and page count unless visual verification shows a clear layout problem.
- Do not introduce a new colour palette. Continue to use OCE/DEWR palette tokens already in `report_design_system.py`.
- Keep body/report paragraph styles in `build_paragraph_styles()`.
- Put component-level visual numbers in spec dataclasses rather than scattering them through Flowables.
- Use readable token names, not generic names such as `small`, `large`, or `number_1`.
- Avoid splitting `generate_report.py` into many modules in this pass; this keeps the diff focused on standardisation.

## Verification

Fresh verification must include:

- `PYTHONPYCACHEPREFIX=/private/tmp/python-idiomatic-pycache python3 -m py_compile report_design_system.py generate_report.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/python-idiomatic-pycache python3 generate_report.py`
- Render all PDF pages with `/private/tmp/render_pdf_pages`.
- Inspect a contact sheet plus pages 2, 6, 10, 11 and 12.
- Run a literal scan for remaining local visual constants in `generate_report.py`; any remaining numeric values should be layout coordinates or data-driven dimensions, not reusable typography/chrome tokens.
