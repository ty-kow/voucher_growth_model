# Research Log

Project: forecast Arizona ESA (voucher) enrolment and program cost from quarterly state reports (FY21Q2-FY26Q4). Modelling method not yet chosen.

## Data extraction

**Source.** Quarterly ESA reports (PDF) from the Arizona Department of Education, stored in `data/raw/voucher_reports/` (FY21Q2-FY26Q4, 23 quarters). Raw files are not edited.

**Tool.** `src/voucher_growth_model/extract_esa.py` reads each PDF with pypdf and parses metrics with regular expressions. Run on a folder, it writes one row per quarter to `data/processed/voucher_metrics_raw.csv`.

**Metrics extracted.**
- Mean voucher
- Total cost (annualized scholarship total)
- Total enrolment
- Universal count
- Total disability/special needs (SN) count
- K-12 disability/SN count
- Military with disability/SN count
- Preschool count
- Universal with disability/SN count

**Handling of format differences.**
- Each metric has ordered fallback patterns because report layout changes across years (e.g., narrative sentence, then table row).
- Mean voucher has three fallback sources: narrative sentence, table row, then student-weighted mean of the appendix "Exact Award Amounts" table.
- Total cost is parsed from the key-points sentence, which appears only in later reports (FY25+ pattern; some earlier quarters also matched).
- Legacy reports (FY21Q2-FY23Q3) list a single disability row covering all students. The extractor assigns it to total SN and leaves K-12 SN blank (`legacy_sn` flag).
- Tables with an "Active Students / Exited Students" layout take the active (first) column.
- FY24 quarters have both `SBE` and non-`SBE` PDFs. The extractor merges them by filling blanks per quarter.

**Rule.** Values not found stay blank. No imputation at the extraction stage.

**Known gaps in raw output.** Total cost blank for FY21Q2-FY24Q1 (as of the raw CSV); K-12 SN blank for legacy quarters; universal counts blank before universal eligibility began; military SN sparse.

## Data cleaning

Cleaned file: `data/processed/voucher_metrics_clean.csv` (renamed columns: `quarter, mean_voucher, total_cost, total_enroll, total_universal, total_sn, total_k12_sn, total_mil_sn, total_pre, total_universal_sn`). Every change is recorded in `decisions.md`. Filled values are marked `*` there. Steps 1, 2, 4, and 5 were explicit user instructions that override the project no-imputation rule.

1. **Total cost.** Blank `total_cost` filled with `total_enroll * mean_voucher` for FY21Q2-FY24Q1 (13 quarters). FY24Q2 onward were reported directly.
2. **Mean voucher.** Blank `mean_voucher` filled with `total_cost / total_enroll` for FY25Q1-FY26Q4 (8 quarters), where cost is reported but no average is stated.
3. **Universal counts.** `total_universal` and `total_universal_sn` set to 0 for FY21Q2-FY22Q4 (7 quarters). Universal vouchers began in FY23Q1, so these are structural zeros, not estimates.
4. **K-12 SN.** Blank `total_k12_sn` filled with `total_sn - total_pre` for FY21Q2-FY23Q3 (10 quarters). Basis: total SN = K-12 SN + preschool, and all preschool students are SN.
5. **Total SN.** Blank `total_sn` filled with `total_k12_sn + total_pre` for FY23Q4 and FY24Q1 (reverse of step 4).
6. **Remaining blanks.** All other blank cells set to `N/A` (data not available). Affects `total_mil_sn` and `total_universal_sn`; counts in `decisions.md`.

**Caveats.**
- Filled `total_cost` for FY21Q2-FY24Q1 is an estimate (enrolment times mean voucher), not a reported figure. Reported cost uses an annualized basis; the identity is approximate.
- Filled `mean_voucher` for FY25+ is an implied average from reported cost, so cost and mean voucher are not independent for those quarters.
- **FLAG: duplicate `total_k12_sn`.** FY23Q4 and FY24Q1 report the same value (10409). The duplicate does not follow the trend of the series. Likely cause: a reporting error by the agency, but this cannot be verified. The `total_sn` fills for FY23Q4 (11180) and FY24Q1 (11029) derive from these values (step 5) and inherit the uncertainty. Treat both quarters with caution in modelling.
- Quarters before FY25Q1 vs. after use different cost sources, which matters for any model that uses cost as a target.

## Model Building

### Exploration

**Question.** Which aspects drive enrolment and cost in the program?

**Enrolment.**
- First-order driver: incoming students (kindergarten) minus outgoing students (grade 12).
- In practice more complicated. Students tend to leave the program before grade 9. This is a qualitative claim, not yet checked against data.

**Cost.**
- Special needs cost is driven in large part by autism, which carries the highest award value.

**New decision.** Bring in grade-level data. Other modelling decisions (method, targets, cost structure) are deferred until this has been explored.
