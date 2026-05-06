# DEWR Public AI Trial Report Visual Style Guide

Use this guide when creating or refining future pages in the report. The goal is a clean, executive-report style that is consistent with the current PDF treatment: structured, readable, and lightly analytical without looking over-designed.

## Core Principle

Lead with the takeaway in the paragraph, then let the visual prove it.

Visuals should not carry long explanatory titles inside the box. Put the strategic message immediately before the visual, then use the visual for compact evidence: labels, values, rows, columns and notes.

## Callouts

Use callouts for section-level takeaways only.

Keep callouts rounded, as they were before:

- Background: soft green tint
- Left accent bar: green
- Corners: rounded
- Text: bold, dark grey
- Width: align to the main content column

Do not square off the callout boxes. The rounded shape helps distinguish narrative callouts from evidence visuals.

## Evidence Cards And Visual Panels

Cards and evidence visuals should be square, not rounded.

Use square corners for:

- Usefulness and frequency metric cards
- Task type visual panels
- Any compact data evidence panel

Avoid nested card effects. If a parent panel has a grey background, inner cards should not draw their own background rectangles unless there is a clear reason. This prevents small visual overhangs and uneven edges.

## Width And Alignment

All major visual blocks should align to the same content width as nearby callouts.

For the usefulness and frequency visual:

- The outer grey panel should span the full report content width.
- The internal metric cards should sit inside that panel with consistent left and right padding.
- The right edge of the grey panel should align with the callout and surrounding text column.
- Avoid inner blocks protruding beyond the parent panel.

For the task types visual:

- Use the same visual width as the surrounding content.
- Remove unnecessary outer borders when the grey background already defines the visual area.
- Keep internal dividers for structure.

## Background Colour

Use the same soft grey background for related evidence visuals.

Recommended grey:

```text
#F7F8FA
```

Use this for:

- Usefulness and frequency visual background
- Task types visual background

This helps the visuals feel like one family across the page.

## Header Labels

Header labels should use the same colour treatment across visuals.

Labels such as:

- `RATED VERY USEFUL OR BETTER`
- `USED DAILY OR MOST OF DAY`
- `AVERAGE TASK BREADTH`
- `LARGEST ACCESS-TYPE GAPS`
- `M365`
- `CHAT`

should use the same dark grey label colour, not a lighter grey.

Recommended:

```text
Dark grey: #404246
```

Use uppercase labels for compact evidence visuals. Keep label size small, bold, and consistent.

## Task Types Visual

For the task types visual, keep the structure simple:

- Left side: average task breadth
- Right side: largest access-type gaps
- No outer border if the grey panel background is visible
- No green left accent strip
- No `+0.8 task types per user` badge inside the visual
- Put the interpretation in the paragraph before the visual

Alignment rules:

- `AVERAGE TASK BREADTH` should align vertically with `LARGEST ACCESS-TYPE GAPS`, `M365`, and `CHAT`.
- `4.0` and `3.2` should sit on the same baseline.
- The spacing between `4.0` and `3.2` should be balanced and close, but not overlapping.
- Their labels (`M365 Copilot`, `Copilot Chat`) should be centred underneath each value.

## Usefulness And Frequency Visual

Use the two-card layout unless there is a strong reason to switch to a table.

Current preferred structure:

- Card 1: `Rated very useful or better`
- Card 2: `Used daily or most of day`

Each card should have:

- Square corners
- Shared grey parent background
- A top label
- A thin horizontal divider
- Two centred value columns
- A thin vertical divider between M365 and Chat

Alignment rules:

- Card titles should align to the same y-position.
- Horizontal divider lines should align across both cards.
- Values should share the same baseline.
- Labels under values should share the same baseline.
- Vertical dividers should be the same height and start/end points.
- Internal left and right padding should be even.

Avoid placing an additional grey card background inside a grey parent panel, because this can create uneven edges or a visible protruding block.

## Comparison Metric Panels

Use this pattern when comparing two or three respondent groups on one headline measure, such as:

- Copilot Chat vs M365 Copilot
- Prior Gen AI experience groups
- APS vs EL, if a compact comparison is needed

The current preferred structure is a single full-width soft grey panel with equal-width columns. Do not include a separate title inside the visual if the section heading and paragraph already explain the measure.

Each column should have:

- A centred group label at the top
- A large centred percentage
- A short centred supporting label below the percentage
- No inner card background

Spacing rules:

- Use the same vertical rhythm across all columns in the panel.
- Group labels should share the same baseline.
- Percentages should share the same baseline.
- Supporting labels should share the same baseline.
- Leave visible space between the group label and the percentage.
- Leave visible space between the percentage and the supporting label.
- If a comparison note is used, place it at the bottom of the panel and leave extra breathing room above it.
- If the note is not necessary, omit it rather than adding a generic title or caption inside the visual.

Current ReportLab positioning standard for these panels:

```text
panel height: 104 pt
group label baseline: h - 24
percentage baseline: h - 56
supporting-label vertical centre: around y = 34
optional bottom note baseline: y = 6
```

Use thin light-grey internal dividers only:

- Two-column panels: one vertical divider between the columns.
- Three-column panels: two vertical dividers between the columns.
- Divider colour: `#D7D8D8`
- Divider weight: `0.5`
- Divider start/end should be consistent within the panel.

Colour treatment:

- Primary or higher-value result: DEWR green
- Comparison values: dark grey
- Group labels and supporting text: dark grey
- Panel background: `#F7F8FA`

Example two-column access panel:

```text
Copilot Chat                 M365 Copilot
79%                          63%
reported public tools        reported public tools
added value beyond Copilot   added value beyond Copilot

+16 pts higher among Copilot Chat users
```

Example three-column prior-experience panel:

```text
Experienced/highly experienced   Some prior experience   No/basic experience
91%                              73%                     62%
reported significant             reported significant    reported significant
added value                      added value             added value
```

## Colour Use

Use the DEWR green for the stronger M365 value where it supports the story.

Recommended treatment:

- M365 value: DEWR green
- Chat value: dark grey/black
- Header labels: dark grey
- Internal dividers: light grey
- Background: soft grey

Do not introduce a separate blue/McKinsey palette unless the whole report is being restyled. For this report, consistency with the existing DEWR palette matters more than switching palettes mid-document.

## Notes And Sources

Keep notes directly under the visual.

Notes should:

- Be italic
- Use small grey text
- Align to the same content width
- Include sample sizes and source where relevant

Example:

```text
Note: M365 Copilot n=30; Copilot Chat n=41. Source: DEWR Public Generative AI Trial survey, 2026.
```

## What To Avoid

Avoid:

- Rounded metric cards
- Nested cards inside cards
- Extra badges inside visuals when the paragraph can explain the insight
- Outer borders around grey evidence panels unless needed for readability
- Header labels in inconsistent colours
- Uneven right edges or panels that do not align with callouts
- Long descriptive titles inside visuals

## Reusable Pattern

For each future evidence visual:

1. Write the key takeaway in the paragraph before the visual.
2. Use a square grey evidence panel.
3. Align the panel width to the main content/callout width.
4. Use dark grey uppercase labels.
5. Use green for the primary/high-performing value and dark grey for the comparison value.
6. Keep dividers thin and internal.
7. Put notes immediately below the visual.
