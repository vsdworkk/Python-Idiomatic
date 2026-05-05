# Task-Range Visual Redesign

Date: 2026-05-04  
Report: `Outputs/live_report/index.html` and `Outputs/DEWR_Public_AI_B.pdf`

## Goal

Replace the current clunky task-range visual under the Copilot usage section with a cleaner executive-style exhibit that makes the key finding obvious:

> M365 Copilot users applied Copilot across a wider range of tasks than Copilot Chat users.

## Approved Direction

Use Option B from the visual companion:

**Dense consulting panel: metric tiles + gap callouts**

The visual should lead with the average number of task types selected:

- M365 Copilot: `4.0 task types`
- Copilot Chat: `3.2 task types`
- Difference: `+0.8 task types per user`

Then show the two largest task gaps:

- Research, problem solving or generating ideas: `67%` M365 Copilot vs `44%` Copilot Chat
- Planning or meeting preparation: `33%` M365 Copilot vs `15%` Copilot Chat

## Layout

Create a compact 2 by 2 exhibit:

- Top-left tile: M365 Copilot breadth, `4.0`.
- Top-right tile: Copilot Chat breadth, `3.2`.
- Bottom-left tile: research/problem solving gap, `+23 pts`.
- Bottom-right tile: planning/meeting preparation gap, `+18 pts`.

The visual should sit after the task-types explanatory paragraph and before the supporting bullets/key finding.

## Style

Use the report's existing DEWR style:

- Eucalyptus green for M365 Copilot emphasis.
- Graphite/dark grey for Copilot Chat comparison.
- White or very light grey panel background.
- Thin, precise rules and minimal borders.
- No decorative icons.
- Clear data labels beside bars.

The tone should be McKinsey-style in structure: insight-led, high-density, clean, and executive-readable, while preserving the DEWR colour palette.

## Acceptance Criteria

- The first thing a skimmer sees is the `4.0` vs `3.2` breadth comparison.
- The two bottom tiles clearly show the largest task gaps driving the broader footprint.
- The exhibit fits comfortably inside the existing A4 report page without crowding nearby sections.
- The same treatment is implemented in the live HTML and the PDF generation source.
- The final PDF regenerates successfully.
