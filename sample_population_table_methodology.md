# Sample Population Table Methodology

## Purpose

Create an appendix table that makes the sample base for every reported statistic transparent. The table should let a reviewer trace each statistic in the report to the population used to calculate it.

The table is intended to be granular and audit-ready. It should not group multiple statistics into broad visual-level rows when those statistics can be described separately.

## Table Columns

Use the following columns:

| Section / visual | Measure | Population used | Population size |
|---|---|---|---|

### Section / visual

Use the report section or subsection where the statistic first appears.

If a statistic appears in a section-level summary before the first subsection, use the parent section number.

Examples:

| Statistic location | Section / visual value |
|---|---|
| Appears in the section 3 opening panel before 3.1 | `3 Concerns, risks and safeguards` |
| Appears first in subsection 3.1 | `3.1 Most respondents were comfortable; security concerns were rare` |
| Appears first in subsection 3.3 | `3.3 Respondents were more likely to copy/paste information than upload documents` |

### Measure

Use the exact statistic or a close plain-English version of the statistic.

Examples:

- `Comfortable or very comfortable using public tools`
- `Uncomfortable using public tools`
- `Ethical concerns encountered`
- `Specific security concerns encountered`
- `Lack of integration with internal systems or Microsoft 365 products`
- `Free prompt/request limits`
- `Average workday time saved`

### Population used

Describe the group used to calculate the statistic in a complete, reader-friendly way. Avoid terse labels such as `valid users` unless they are explained in the same phrase.

Examples:

- `Respondents with known Copilot access and valid Q17 response`
- `Respondents with known Copilot access and valid Copilot usefulness response`
- `Respondents who used at least one public Gen AI tool and provided a valid limitations response for at least one tool`
- `Respondents who used ChatGPT during the trial and provided a valid usefulness response`
- `Respondents who used at least one public Gen AI tool and provided a valid comfort response`

### Population size

State the relevant population size in a polished, readable format. Use `n=` where the statistic is based on a population. Use `x of y` where numerator detail is important for interpretation.

Examples:

- `M365 n=30; Copilot Chat/basic n=41`
- `Valid public-tool users n=61`
- `ChatGPT users n=56; Claude users n=41; Gemini users n=37`
- `33 of 40 respondents who rated both communications channels effective; 13 of 21 comparison respondents`

## Row Granularity

Create one row per unique statistic.

If a visual contains five different bars, create five rows. If it contains six bars and a headline statistic, create seven rows.

Do not create a single broad row such as `3.x Safety/risk measures` or `2.6 Limitations reported`. Instead, list each unique measure separately.

## Repeated Populations

It is acceptable for multiple rows to repeat the same `Population used` and `Population size` when several measures share the same base.

The repetition is intentional. It makes the appendix easy to audit because each statistic can be read independently.

## Mixed Populations

If one visual contains statistics with different bases, split them into separate rows with distinct population descriptions.

Example:

| Section / visual | Measure | Population used | Population size |
|---|---|---|---|
| 2.1 Tool comparison | Used ChatGPT during trial | Respondents who used at least one public Gen AI tool and provided valid tool-use responses | Valid public-tool users n=61 |
| 2.1 Tool comparison | Rated ChatGPT at least moderately useful | Respondents who used ChatGPT during the trial and provided a valid ChatGPT usefulness response | ChatGPT users n=56 |
| 2.1 Tool comparison | Rated Claude at least moderately useful | Respondents who used Claude during the trial and provided a valid Claude usefulness response | Claude users n=41 |

## Example: Limitations Visual

For the `2.6 Limitations reported by respondents` visual, create one row for each unique statistic.

| Section / visual | Measure | Population used | Population size |
|---|---|---|---|
| 2.6 Limitations reported by respondents | Reported at least one limitation with at least one public AI tool | Respondents who used at least one public Gen AI tool and provided a valid limitations response for at least one tool | Valid public-tool users n=61 |
| 2.6 Limitations reported by respondents | Lack of integration with internal systems or Microsoft 365 products | Respondents who used at least one public Gen AI tool and provided a valid limitations response for at least one tool | Valid public-tool users n=61 |
| 2.6 Limitations reported by respondents | Free prompt/request limits | Respondents who used at least one public Gen AI tool and provided a valid limitations response for at least one tool | Valid public-tool users n=61 |
| 2.6 Limitations reported by respondents | Misinterpreted prompts | Respondents who used at least one public Gen AI tool and provided a valid limitations response for at least one tool | Valid public-tool users n=61 |
| 2.6 Limitations reported by respondents | Difficulty with specialised topics | Respondents who used at least one public Gen AI tool and provided a valid limitations response for at least one tool | Valid public-tool users n=61 |
| 2.6 Limitations reported by respondents | Slow responses | Respondents who used at least one public Gen AI tool and provided a valid limitations response for at least one tool | Valid public-tool users n=61 |
| 2.6 Limitations reported by respondents | Fabricated content or hallucinations | Respondents who used at least one public Gen AI tool and provided a valid limitations response for at least one tool | Valid public-tool users n=61 |

## Implementation Rules

1. Scan the current PDF/report script in report order.
2. Record each unique statistic the first time it appears.
3. Assign the section or subsection where it first appears.
4. Use the exact measure wording where possible.
5. Describe the population in full, using the relevant survey condition and valid-response rule.
6. Use `Population size`, not `Denominator`, as the fourth column heading.
7. Repeat population details where needed rather than merging rows.
8. Add caveats in the population wording where a statistic excludes unknown access type, non-users, low sample groups, or item non-response.

## Preferred Style

Write rows in the same style as:

| Section / visual | Measure | Population used | Population size |
|---|---|---|---|
| 1.1 Time saved by Copilot access | Average workday time saved | Respondents with known Copilot access and valid Q17 response | M365 n=30; Copilot Chat/basic n=41 |
| 1.2 Copilot usefulness/frequency | Rated Copilot very or extremely useful | Respondents with known Copilot access and valid Copilot usefulness response | M365 n=30; Copilot Chat/basic n=41 |
| 1.2 Copilot usefulness/frequency | Used Copilot weekly or more | Respondents with known Copilot access and valid Copilot frequency response | M365 n=30; Copilot Chat/basic n=41 |
