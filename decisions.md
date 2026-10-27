# Decisions

## total_cost imputation

Blank `total_cost` filled with `total_enroll * mean_voucher` where both inputs exist (user instruction; overrides the project no-imputation rule). Rows without `mean_voucher` (FY25Q1 onward) are not fillable and stay blank. Filled values are marked `*`.

| quarter | mean_voucher | total_enroll | total_cost |
|---|---|---|---|
| FY21Q2 | 14373.69 | 9718 | 139683519.42* |
| FY21Q3 | 14441.39 | 9831 | 141973305.09* |
| FY21Q4 | 14543.0 | 9669 | 140616267.00* |
| FY22Q1 | 15189.0 | 10699 | 162507111.00* |
| FY22Q2 | 15242.12 | 11256 | 171565302.72* |
| FY22Q3 | 15225.39 | 11775 | 179278967.25* |
| FY22Q4 | 15565.52 | 12127 | 188763061.04* |
| FY23Q1 | 11332.11 | 30471 | 345300723.81* |
| FY23Q2 | 10004.21 | 44787 | 448058553.27* |
| FY23Q3 | 9882.59 | 50073 | 494850929.07* |
| FY23Q4 | 9523.0 | 61689 | 587464347.00* |
| FY24Q1 | 9782.11 | 66457 | 650089684.27* |
| FY24Q2 | 9769.0 | 71520 | 698626997.0 |
| FY24Q3 | 9818.0 | 74996 | 736351926.0 |
| FY24Q4 | 9896.0 | 74578 | 738002994.0 |
| FY25Q1 |  | 79593 | 795296542.0 |
| FY25Q2 |  | 83819 | 860077422.0 |
| FY25Q3 |  | 87602 | 901174756.0 |
| FY25Q4 |  | 85195 | 881662142.0 |
| FY26Q1 |  | 93993 | 985147916.0 |
| FY26Q2 |  | 99034 | 1067507825.0 |
| FY26Q3 |  | 102891 | 1115099565.0 |
| FY26Q4 |  | 99709 | 1090228062.0 |

## mean_voucher imputation

Blank `mean_voucher` filled with `total_cost / total_enroll` (user instruction; overrides the project no-imputation rule). Applies to FY25Q1 onward, where `total_cost` is reported.

| quarter | total_cost | total_enroll | mean_voucher |
|---|---|---|---|
| FY25Q1 | 795296542.0 | 79593 | 9992.04* |
| FY25Q2 | 860077422.0 | 83819 | 10261.13* |
| FY25Q3 | 901174756.0 | 87602 | 10287.15* |
| FY25Q4 | 881662142.0 | 85195 | 10348.75* |
| FY26Q1 | 985147916.0 | 93993 | 10481.08* |
| FY26Q2 | 1067507825.0 | 99034 | 10779.21* |
| FY26Q3 | 1115099565.0 | 102891 | 10837.68* |
| FY26Q4 | 1090228062.0 | 99709 | 10934.10* |

## total_universal and total_universal_sn zero-fill

`total_universal` and `total_universal_sn` set to 0 for FY21Q2-FY22Q4 (7 quarters). Explanation: the Universal Voucher program began in 2023Q1 (FY23Q1), so there was no universal enrollment before that quarter. These are structural zeros, not imputed estimates.

## total_k12_sn derivation

Blank `total_k12_sn` filled with `total_sn - total_pre` (user instruction). Explanation: `total_sn` is `total_k12_sn` plus `total_pre`, and all preschool students are special needs. Applies only where `total_sn` and `total_pre` are reported.

| quarter | total_sn | total_pre | total_k12_sn |
|---|---|---|---|
| FY21Q2 | 5707 | 278 | 5429* |
| FY21Q3 | 5854 | 296 | 5558* |
| FY21Q4 | 5773 | 289 | 5484* |
| FY22Q1 | 6379 | 224 | 6155* |
| FY22Q2 | 6732 | 262 | 6470* |
| FY22Q3 | 7094 | 352 | 6742* |
| FY22Q4 | 7291 | 421 | 6870* |
| FY23Q1 | 8028 | 411 | 7617* |
| FY23Q2 | 8253 | 509 | 7744* |
| FY23Q3 | 8545 | 641 | 7904* |

## total_sn derivation

Blank `total_sn` filled with `total_k12_sn + total_pre` (user instruction; reverse of the `total_k12_sn` fill). Explanation: `total_sn` is `total_k12_sn` plus `total_pre`, and all preschool students are special needs. Applies only where both inputs are reported.

| quarter | total_k12_sn | total_pre | total_sn |
|---|---|---|---|
| FY23Q4 | 10409 | 771 | 11180* |
| FY24Q1 | 10409 | 620 | 11029* |

## Remaining blanks set to N/A

All remaining blank cells set to `N/A` (user instruction). Reason: data not available.

| column | cells set to N/A |
|---|---|
| total_mil_sn | 19 |
| total_universal_sn | 13 |

## Bring in grade-level data

Decision: add grade-level enrolment data to the project. Explanation: enrolment is driven first by incoming (kindergarten) and outgoing (grade 12) students, and students tend to leave the program before grade 9 (qualitative claim, not yet checked against data). Grade-level counts are needed to test this and to model enrolment flows.

All other modelling decisions (method, targets, cost structure) are deferred until the grade-level data has been explored. No changes to `data/processed/` files yet.

## Grade-level data brought in

Grade-level enrolment (`kinder`, `grade_1` to `grade_12`) extracted from all quarterly PDFs and added to `voucher_metrics_raw.csv` and `voucher_metrics_clean.csv`. Preschool was already present (`Preschool Count` / `total_pre`). No values imputed.

- FY23Q4: the PDF has only a bar chart for total enrolment by grade; counts were read from the chart and accepted because preschool plus grades 1 to 12 sums to total enrolment (61,689).
- All 23 quarters: preschool + `kinder` + `grade_1` to `grade_12` equals total enrolment.

## FY25Q3 preschool: grade-level table used

Flag: FY25Q3 preschool is 1,340 (grade-level table), not 1,346 (eligibility table). Grade-level table chosen for consistency with the other grade data; with it, preschool plus grades sums to total enrolment (87,602). The extractor now takes preschool from the grade-level table for all quarters; no other quarter changed. `total_pre` in `voucher_metrics_clean.csv` updated to 1340.
