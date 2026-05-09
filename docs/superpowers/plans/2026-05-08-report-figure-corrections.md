# Report Figure Corrections Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update every report figure that conflicts with the validated Section 1, Section 2, and Section 3 markdown tables.

**Architecture:** The report is generated from literal values embedded in `generate_report.py`; the markdown tables in `docs/Report Analysis /` are the source of truth. Corrections should update prose, custom visual data arrays, and evidence tables together so the generated PDF is internally consistent.

**Tech Stack:** Python, ReportLab, markdown source tables, generated PDF output.

**Change-marking requirement:** Every corrected report-facing value must be rendered in red and include the old value in brackets immediately next to it, using the pattern `new (old)`. This applies to prose, evidence tables, and custom ReportLab visuals. Values used only for layout, axis ticks, colour constants, date/page metadata, or calculations behind unchanged displayed text do not need marking.

---

### Task 1: Section 1 Copilot Figures

**Files:**
- Modify: `generate_report.py`

- [ ] **Step 1: Update Copilot baseline ratios**

Change the Section 1 `ValueSignalsPanel` values from `2.0x`, `1.8x`, `1.4x` to `2.0x`, `1.9x`, `1.5x`, matching Section 1 rows 1-3.

Render corrected ratios as red `1.9x (1.8x)` and `1.5x (1.4x)`.

- [ ] **Step 2: Update time-savings visual and prose**

Change `TimeSavingsPanel.rows` from `68.7` and `33.8` to `67.9` and `33.5`. Keep weekly equivalents as `5.7 hours per week` and `2.8 hours per week`. Change the prose reference from `69 minutes per day` to `68 minutes per day`.

Render corrected daily-minute values as red `67.9 (68.7) minutes per day`, `33.5 (33.8) minutes per day`, and prose as red `68 minutes per day (69 minutes per day)`.

- [ ] **Step 3: Update Copilot engagement visual**

Change `CopilotEngagementDeltaPanel.rows` to `68% vs 35%`, `81% vs 55%`, and `65% vs 25%`, matching Section 1 rows 5-7.

Render all six corrected percentages in red with their old values in brackets: `68% (67%)`, `35% (37%)`, `81% (80%)`, `55% (56%)`, `65% (63%)`, and `25% (27%)`.

- [ ] **Step 4: Update Copilot task-footprint visual**

Change `TaskFootprintExhibit.rows` to:

```python
[
    ("Summarising", 83.9, 74.4, False),
    ("Editing and revision", 71.0, 64.1, False),
    ("Drafting", 71.0, 66.7, False),
    ("Research, problem solving or generating ideas", 67.7, 43.6, True),
    ("General administrative tasks", 48.4, 41.0, False),
    ("Planning or meeting preparation", 35.5, 12.8, True),
    ("Coding or data work", 22.6, 20.5, False),
]
```

Render corrected task-footprint values in red with old values in brackets where displayed. If the visual previously displayed only highlighted-row labels, add compact labels for corrected values so the old/new values are visible in the generated report.

### Task 2: Section 2 Public-Tool and Access Figures

**Files:**
- Modify: `generate_report.py`

- [ ] **Step 1: Update unused access summary panels for consistency**

Where present, update access-comparison figures to Section 2 rows 26-29 and Section 1 rows 2-3: public-tool usefulness `81.8% vs 78.6%`, public-tool weekly use `54.5% vs 50.0%`, public-tool added value `78.8% vs 64.3%`, Copilot high usefulness `35.0% vs 67.7%`, and Copilot weekly use `55.0% vs 80.6%`.

- [ ] **Step 2: Update `access_evidence_table`**

Replace the old access evidence table values with the validated values:

```text
Public AI rated at least moderately useful: 81.8%, 78.6%
Copilot rated very or extremely useful: 35.0%, 67.7%
Public AI used weekly or more: 54.5%, 50.0%
Copilot used weekly or more: 55.0%, 80.6%
Public AI added value beyond Copilot: 78.8%, 64.3%
```

Render each corrected evidence-table value in red with its old value in brackets.

- [ ] **Step 3: Update Productivity from Public Gen AI prose**

Replace unsupported old values `82.4%`, `70.6%`, `92.6%`, `77.8%`, `52.9%`, `51.9%`, `58.8%`, and `85.2%` with the validated values above. Update the note to use `M365 Copilot n=28` and `Copilot Chat/basic n=33` for Section 2 measures and explain that Copilot engagement rows use their valid Section 1 populations.

Render each corrected prose value and sample size in red with the old value in brackets.

- [ ] **Step 4: Correct the prior-experience comparison sentence**

Change `86% vs 69% for both lower-experience groups` to `86% vs 69% and 75% for lower-experience groups`, matching Section 2 row 32.

Render the corrected `75%` in red with the old implied value in brackets, e.g. `75% (69%)`.

### Task 3: Section 3 Concerns, Risks and Safeguards

**Files:**
- Modify: `generate_report.py`

- [ ] **Step 1: Update ethical-concern values**

Change Section 3 value-signal and prose references from `11%` to `12%`, matching Section 3 row 3.

Render corrected ethical-concern values as red `12% (11%)`.

- [ ] **Step 2: Update communications-comfort comparison**

Change the not-both-effective comparison from `61.9%` to `60.0%`, matching Section 3 row 5.

Render corrected communications-comfort value as red `60.0% (61.9%)`.

### Task 4: Verification

**Files:**
- Verify: `generate_report.py`
- Verify: `Outputs/DEWR_Public_AI_B.pdf`

- [ ] **Step 1: Generate the report**

Run: `python3 generate_report.py`

Expected: command completes and prints `Report generated: /Users/aristotle/Projects/Python-Idiomatic/Outputs/DEWR_Public_AI_B.pdf`.

- [ ] **Step 2: Inspect remaining numeric references**

Run: `rg -n "\\b[0-9]+(?:\\.[0-9]+)?%|\\b[0-9]+(?:\\.[0-9]+)?x|hours per week|minutes per day|n=" generate_report.py`

Expected: report-facing values match the Section 1, Section 2, and Section 3 markdown tables, excluding layout constants, page furniture, source notes, and external benchmark context.
