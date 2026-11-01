# Data dictionary

Every column in the project's CSV files, in pipeline order. Blank/`N/A` means the value was not available; it is never imputed except where noted (see `decisions.md`).

Conventions
- Quarter labels are `FYxxQn` (e.g. `FY26Q3`). Fiscal year `FYxx` is paired with calendar year `20xx` when joining population data.
- `N/A` is the missing-value marker in clean and final files. Extracted files leave cells blank.
- "SN" = special needs / disability.

## Pipeline overview

| Stage | File | Grain |
|---|---|---|
| Extracted | `data/processed/extracted/voucher_metrics_extracted.csv` | quarter |
| Clean | `data/processed/clean/voucher_metrics_clean.csv` | quarter |
| Extracted | `data/processed/extracted/az_pop_proj_extracted.csv` | year (2026-2046) |
| Extracted | `data/processed/extracted/az_pop_real_extracted.csv` | year x age group |
| Clean | `data/processed/clean/az_pop_proj_clean.csv` | year |
| Clean | `data/processed/clean/az_pop_real_clean.csv` | year |
| Clean | `data/processed/clean/az_pop_all_clean.csv` | year |
| Report | `outputs/report/report_data.csv` | fiscal year (Q3 values) |
| Forecast | `outputs/report/forecast.csv` (draft copy: `outputs/draft/forecast/csv/forecast_draft.csv`) | fiscal year x scenario |

## Voucher metrics (`voucher_metrics_extracted.csv`, `voucher_metrics_clean.csv`)

One row per quarterly report, FY21Q2-FY26Q4. Source: ADE ESA quarterly PDFs. The extracted file uses the display names in the first column below; the clean file renames them.

| Clean column | Extracted column | Type | Meaning |
|---|---|---|---|
| `quarter` | `Quarter` | text | Report quarter, `FYxxQn`. |
| `mean_voucher` | `Mean Voucher` | dollars | Average award per student. Extracted from the report narrative, a table row, or the student-weighted mean of the appendix award table. FY25Q1-FY26Q4 blanks are filled as `total_cost / total_enroll`, so cost and mean are not independent there. |
| `total_cost` | `Total Cost` | dollars | Annualized scholarship total as reported (later reports only). Blank FY21Q2-FY24Q1 values are filled as `total_enroll x mean_voucher`, an estimate. |
| `total_enroll` | `Total Enrollment` | students | All ESA students in the quarter. Equals `total_pre` + `kinder` + `grade_1`..`grade_12`. |
| `total_universal` | `Universal Count` | students | Students enrolled under universal eligibility (programme began FY23Q1). Set to 0 before FY23Q1. |
| `total_sn` | `Total Disability/SN Count` | students | All students with a disability/special need. Equals `total_k12_sn` + `total_pre`. In legacy reports (FY21Q2-FY23Q3) this is the single disability row covering all students. |
| `total_k12_sn` | `K-12 Disability/SN Count` | students | K-12 students with a disability/special need. Blank in legacy quarters in the raw file; filled as `total_sn - total_pre`. |
| `total_mil_sn` | `Military with Disability/SN Count` | students | Military-family students with a disability/special need. Sparse; `N/A` where not reported. |
| `total_pre` | `Preschool Count` | students | Preschool students (all are special needs). Taken from the grade-level table for every quarter. |
| `total_universal_sn` | `Universal w/ Disability/SN Count` | students | Universal-eligibility students who also have a disability/special need. 0 before FY23Q1; `N/A` otherwise where not reported. |
| `kinder` | `kinder` | students | Kindergarten enrollment. FY23Q4-FY24Q1 flagged as possibly erroneous (`research_log.md`). |
| `grade_1` ... `grade_12` | same | students | Enrollment in each grade, 1 to 12. FY23Q4 values were read from a bar chart. |

## Population, extracted

### `az_pop_proj_extracted.csv`: projections, 2026-2046
Source: Arizona Office of Economic Opportunity (OEO) workbook, tab "Pop By Age Group & Sex", both-sexes Total row.

| Column | Type | Meaning |
|---|---|---|
| `year` | calendar year | Projection year. |
| `pop_total` | persons | Total Arizona population. |
| `pop_5_9` | persons | Population aged 5-9. |
| `pop_10_14` | persons | Population aged 10-14. |
| `pop_15_19` | persons | Population aged 15-19. |

### `az_pop_real_extracted.csv`: actuals, long format
| Column | Type | Meaning |
|---|---|---|
| `year` | calendar year | Observation year (2023-2025). |
| `age_group` | text | `5-9`, `10-14`, `15-19`, or `total_pop` (all ages). |
| `population` | persons | Population for that year and age group. |

## Population, clean

### `az_pop_proj_clean.csv`
Same columns as `az_pop_proj_extracted.csv`, plus:

| Column | Type | Meaning |
|---|---|---|
| `pop_5_19` | persons | Derived: `pop_5_9 + pop_10_14 + pop_15_19`. |

### `az_pop_real_clean.csv`: wide format, one row per year
| Column | Type | Meaning |
|---|---|---|
| `year` | calendar year | Observation year. |
| `5-9`, `10-14`, `15-19` | persons | Population in each age group. |
| `5-19` | persons | Derived: sum of the three age groups. |
| `total_pop` | persons | Total Arizona population. |
| `school_aged_ratio` | ratio | Derived: `5-19 / total_pop`, rounded to 6 decimals. |

### `az_pop_all_clean.csv`: merged real and projected series
| Column | Type | Meaning |
|---|---|---|
| `year` | calendar year | 2023-2046. |
| `pop_total` | persons | Total Arizona population. |
| `pop_5_19` | persons | Population aged 5-19. |
| `source` | text | `real` (actual) or `proj` (OEO projection). Real values take precedence if a year appears in both. |

## Report data (`outputs/report/report_data.csv`)

One row per fiscal year, FY21-FY46. Voucher values are the Q3 report for each year (`FY26Q3` becomes `FY26`).

| Column | Type | Meaning |
|---|---|---|
| `year` | text | Fiscal year, `FYxx`. Despite the name it is not an integer. |
| `mean_voucher` | dollars | `mean_voucher` from the Q3 row. `N/A` after FY26. |
| `total_cost` | dollars | `total_cost` from the Q3 row. `N/A` after FY26. |
| `total_enroll` | students | `total_enroll` from the Q3 row. `N/A` after FY26. |
| `pop_5_19` | persons | Population aged 5-19 for calendar year `20xx`, from `az_pop_all_clean.csv`. `N/A` before 2023. FY26 onward is projected. |

## Forecast (`outputs/report/forecast.csv`)

One row per fiscal year (FY26-FY46) x take-up scenario x voucher scenario: 21 x 4 x 2 = 168 rows. FY26 (t = 0) reproduces FY26 Q3 actual take-up, enrollment and mean voucher.

| Column | Type | Meaning |
|---|---|---|
| `fy` | text | Fiscal year, `FYxx`. |
| `takeup_scenario` | text | Take-up ceiling: `k9.9` (9.9%), `k20` (20%), `k30` (30%), `k40` (40%). |
| `voucher_scenario` | text | Mean-voucher growth rate: `infl2` (2%/yr) or `hist` (FY24-FY26 compound rate, about 5.1%/yr). |
| `pop_base` | text | Population base. Only `5_19` (ages 5-19) is in use. |
| `pop` | persons | Population aged 5-19 in that year. |
| `takeup` | ratio | Enrolled share of `pop`. Logistic path toward the ceiling, passing through FY26 actual take-up. |
| `r` | per year | Continuous annual growth rate of take-up: slope of log take-up on year over FY23-FY26. Constant across rows. |
| `enroll` | students | `takeup x pop`. |
| `mean_voucher` | dollars | FY26 mean voucher grown at the scenario rate. |
| `cost_nominal` | dollars | `enroll x mean_voucher`. |
| `cost_real_fy26` | dollars | `cost_nominal` deflated to FY26 dollars at 2%/yr. |

The draft copy in `outputs/draft/forecast/csv/` may differ from the final file (e.g. a different `r`).
