# Research Log

Project: forecast Arizona ESA (voucher) enrollment and program cost from quarterly state reports (FY21Q2-FY26Q4). Method chosen: logistic take-up scenarios on the population aged 5-19 (see "Report (2026-11-01)" below and `decisions.md`).

## Data extraction

**Source.** Quarterly ESA reports (PDF) from the Arizona Department of Education, stored in `data/raw/voucher_reports/` (FY21Q2-FY26Q4, 23 quarters). Raw files are not edited.

**Tool.** `src/voucher_growth_model/data_cleaning/extract_esa.py` reads each PDF with pypdf and parses metrics with regular expressions. Run on a folder, it writes one row per quarter to `data/processed/extracted/voucher_metrics_extracted.csv`.

**Metrics extracted.**
- Mean voucher
- Total cost (annualized scholarship total)
- Total enrollment
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

Cleaned file: `data/processed/clean/voucher_metrics_clean.csv` (renamed columns: `quarter, mean_voucher, total_cost, total_enroll, total_universal, total_sn, total_k12_sn, total_mil_sn, total_pre, total_universal_sn`). Every change is recorded in `decisions.md` (same folder). Filled values are marked `*` there. Steps 1, 2, 4, and 5 were explicit user instructions that override the project no-imputation rule.

1. **Total cost.** Blank `total_cost` filled with `total_enroll * mean_voucher` for FY21Q2-FY24Q1 (13 quarters). FY24Q2 onward were reported directly.
2. **Mean voucher.** Blank `mean_voucher` filled with `total_cost / total_enroll` for FY25Q1-FY26Q4 (8 quarters), where cost is reported but no average is stated.
3. **Universal counts.** `total_universal` and `total_universal_sn` set to 0 for FY21Q2-FY22Q4 (7 quarters). Universal vouchers began in FY23Q1, so these are structural zeros, not estimates.
4. **K-12 SN.** Blank `total_k12_sn` filled with `total_sn - total_pre` for FY21Q2-FY23Q3 (10 quarters). Basis: total SN = K-12 SN + preschool, and all preschool students are SN.
5. **Total SN.** Blank `total_sn` filled with `total_k12_sn + total_pre` for FY23Q4 and FY24Q1 (reverse of step 4).
6. **Remaining blanks.** All other blank cells set to `N/A` (data not available). Affects `total_mil_sn` and `total_universal_sn`; counts in `decisions.md`.

**Caveats.**
- Filled `total_cost` for FY21Q2-FY24Q1 is an estimate (enrollment times mean voucher), not a reported figure. Reported cost uses an annualized basis; the identity is approximate.
- Filled `mean_voucher` for FY25+ is an implied average from reported cost, so cost and mean voucher are not independent for those quarters.
- **FLAG: duplicate `total_k12_sn`.** FY23Q4 and FY24Q1 report the same value (10409). The duplicate does not follow the trend of the series. Likely cause: a reporting error by the agency, but this cannot be verified. The `total_sn` fills for FY23Q4 (11180) and FY24Q1 (11029) derive from these values (step 5) and inherit the uncertainty. Treat both quarters with caution in modelling.
- **FLAG: FY24Q1 `kinder`.** Possible data error. The value (5,148) falls sharply after FY23Q4 (about 7,750), while grades 3, 6, 8 and 12 rise smoothly over the same quarters. Could not be validated. Treat FY23Q4-FY24Q1 kindergarten counts with caution in modelling.
- Quarters before FY25Q1 vs. after use different cost sources, which matters for any model that uses cost as a target.

## Model Building

### Exploration

**Question.** Which aspects drive enrollment and cost in the program?

**enrollment.**
- First-order driver: incoming students (kindergarten) minus outgoing students (grade 12).
- In practice more complicated. Students tend to leave the program before grade 9. This is a qualitative claim, not yet checked against data.

**Naive program growth.**
- 4.08% per quarter in total enrollment (FY24Q1-FY26Q4, n = 12). Source: log-linear trend with quarter effects (`plots_drafts/plot_enrollment_seasonal_model.py`, `outputs/draft/enrollment/enrollment_seasonal_model.png`); SE 0.0010 log points.
- Seasonal factors: Q1 0.999, Q2 1.019, Q3 1.022, Q4 0.961.
- Caveat: 12 points, 5 parameters; each factor rests on three observations. Baseline for later models, not a forecast method.

**Naive mean voucher growth.**
- 1.1% per quarter (FY24Q1-FY26Q4, n = 12). Source: OLS linear trend (`plots_drafts/plot_mean_voucher_ols.py`, `outputs/draft/mean_voucher/mean_voucher_ols.png`): slope $115.52 per quarter (SE $7.27, R² = 0.962), about 1.1% of the series mean ($10,266).
- Caveat: 12 points. FY25+ values are implied averages (cost / enrollment), not reported (see Data cleaning, step 2). Baseline for later models, not a forecast method.

**Mean voucher seasonality.**
- Decision: no seasonal adjustment of `mean_voucher`.
- Rationale: mean voucher is driven by the composition of enrolled students. Entry and exit at the start or end of the year show no pattern in who joins or leaves, so there is no mechanism for a seasonal effect.
- Check: log-linear trend with quarter effects (FY24Q1-FY26Q4, n = 12; `plots_drafts/plot_mean_voucher_seasonal_model.py`, `outputs/draft/mean_voucher/mean_voucher_seasonal_model.png`) gives factors Q1 0.9998, Q2 1.0061, Q3 0.9990, Q4 0.9951, all within 0.6% of 1. Trend 1.15% per quarter (SE 0.0007 log points). Consistent with the rationale, though 12 points give little power.

**Cost.**
- Special needs cost is driven in large part by autism, which carries the highest award value.

**Population baseline growth rate.**
- Purpose: bring in population data to create a baseline growth rate for the program.
- Data: observed population for 2023-2025; projections for 2026-2046.
- Caveat: 2026-2046 values are projections, not observations, so any baseline built on them inherits projection uncertainty.
- Source: Arizona Office of Economic Opportunity, Population Projections (https://oeo.az.gov/population/projections), "Arizona Population Projections: 2025 to 2060, Medium Series". Workbook: `data/raw/population/az_population_growth.xlsx`.
- Extracted (2026-2046) to `data/processed/extracted/az_pop_proj_extracted.csv` via `src/voucher_growth_model/data_cleaning/extract_population.py`: `pop_total`, `pop_5_9`, `pop_10_14`, `pop_15_19` (tab 2, both sexes, statewide Arizona). The 5-19 age groups match the age range of the actual population data in the `az_pop_real` CSVs.
- Scope note: ages 5-19 approximate the school-aged population, not ESA-eligible or enrolled students.

### Forecast (2026-10-29)

Full parameter choices are in `decisions.md` (sections "Forecast scope" to "School-age (5-19) population version").

**Data prep.**
- Reorganized `data/processed/` into `raw/` (since renamed `extracted/`) and `clean/`; added population cleaning scripts (`clean_population_proj.py`, `clean_population_real.py`) and `plots_drafts/plot_pop_proj.py`.
- Merged real (2023-2025) and projected (2026-2046) population into `data/processed/clean/az_pop_all_clean.csv` (`merge_population.py`), columns `pop_total`, `pop_5_19`, `source`. Caveat: sources differ, so a level shift at 2025/2026 is possible.

**Method.** `src/voucher_growth_model/forecast.py`, annual FY26-FY46 (the FY26 row reproduces actuals).
- Enrollment = take-up x population. Take-up = Q3 enrollment / population in the same calendar year (FY26Q3 pairs with 2026).
- Take-up follows a logistic path to a ceiling, re-centred through FY26 actual take-up. All ceilings in a base share r = continuous annual growth rate of take-up, fitted to FY23-FY26 (slope of log take-up on year, all four years; 5-19 r = 0.246). It was first the endpoint rate (superseded) ln(FY26 / FY23) / 3 (total r = 0.228; 5-19 r = 0.255), which ignored FY24 and FY25. Scenarios diverge from FY27. FY22 would need a 2022 population, which the data does not have.
- Cost = enrollment x mean voucher. Mean voucher grows from FY26 ($10,837.68) at 2% or the FY24-FY26 compound rate (about 5.1%/yr). Cost is reported in real FY26 dollars (2%/yr deflator) on the graph; the CSV also holds nominal.

**Scenarios.**
- Total population base (superseded: removed, only the 5-19 base is used; see `decisions.md`, "report_data.csv"): take-up 1.32% in FY26. Logistic fit to FY23-FY26 gives K = 1.44% (s.e. 0.16pp), r = 0.797. Ceilings 1.44%, 2%, 3%, 5% (10% dropped after the first graph, about 917k students by FY46).
- 5-19 population base (separate outputs `forecast_5_19.*`): take-up FY23 3.48%, FY24 5.15%, FY25 6.05%, FY26 7.49%. Logistic fit K = 9.9% (s.e. 3.5pp), r = 0.555. Ceilings 9.9%, 20%, 30%, 40%.
- Grid: 4 take-up paths x 2 mean-voucher rates = 8 per base.

**Caveats.**
- Logistic fits rest on 4 data points; ceilings from 1.5% to 10% fit almost as well, so ceilings are scenario choices, not estimates.
- FY25-FY26 take-up growth on the 5-19 base (23.8%) vs. total base (16.1%): part may reflect the 2025/2026 real-to-projected population shift.
- An earlier version solved r per ceiling to match FY25-FY26 growth, which made all FY27 values identical; replaced by the shared fitted r.
- 5-19 take-up growth was uneven (continuous rates 0.392 FY23-24, 0.161 FY24-25, 0.214 FY25-26), so r from four points is not statistically strong. FY46 enrollment with r = 0.246: 9.9% = 134,648; 20% = 269,365; 30% = 400,187; 40% = 528,533.
- Mean voucher for FY25+ is an implied average (see Data cleaning, step 2).

**New decision.** Bring in grade-level data. Other modelling decisions (method, targets, cost structure) are deferred until this has been explored.

### Grade-level vs. total enrollment trend (2026-10-29)

Question: which grade's enrollment trend matches total enrollment (`total_enroll`) most closely? Source: `data/processed/clean/voucher_metrics_clean.csv`, grade columns `kinder`, `grade_1`-`grade_12`. Metrics: Pearson r on levels, and on quarter-over-quarter growth rates (more discriminating, since levels share a trend). Ad hoc computation; no script saved.

**Full period (FY21Q2-FY26Q4, 23 quarters).**
- Closest by level: grade 9 (r = 0.9999). Closest by growth rate: grades 5, 6 and 4 (r = 0.998); grade 9 r = 0.996.
- Grade 9 share of total stable (6.2% to 6.3%).
- Most divergent: kinder (growth r = 0.93) and grade 12 (0.91). Grade 11 share rose 4.2% to 5.1%; grade 12 fell 5.6% to 4.8%.

**FY23Q1 onward (16 quarters, FY23Q1-FY26Q4).** Window read as fiscal-year labels, not calendar 2023.
- Closest: grade 9 (growth r = 0.996, level r = 0.9995, tied with grade 6). Cumulative growth 224.3% vs. 227.2% total.
- Second: grade 5 (growth r = 0.995, level r = 0.9994, cumulative 217.7%).
- Most divergent: kinder (growth r = 0.76, level r = 0.87) and grade 12 (growth r = 0.62).

**Caveats.**
- Confidence: high on computed values; differences among grades 5, 6 and 9 are small and not statistically distinguishable at n = 16.
- Correlations measure co-movement, not equal growth; cumulative growth differs by grade (grade 11 261%, grade 3 248%, grade 8 205% from FY23Q1).

## Report (2026-11-01)

**Final specification.** Population aged 5-19 base only; take-up ceilings 9.9% (logistic best fit), 20%, 30%, 40%; shared r = 0.246; mean voucher growth 2% or 5.1%/yr; FY26-FY46; cost in real FY26 dollars. Summary at the top of `decisions.md`.

**Headline results** (`outputs/report/forecast.csv`). FY46 enrollment 134,648 to 528,533. FY46 real cost $1.5B to $10.4B; FY36 $1.3B to $5.5B. The take-up ceiling drives more of the spread than voucher growth.

**Report materials.**
- Text: `docs/report_outline.md` (skeleton), `docs/report_draft.md` (draft, ~1,500 words).
- Figures in `outputs/report/`: `enrollment_actual.png`, `forecast_enrollment_report.png`, `forecast_cost_table.png`, `forecast_slide_report.png`; scripts in `src/voucher_growth_model/plots_report/`.

**Open items.**
- FLAG on the 9.9% ceiling line (its s.e. of 3.5pp rests on four points).
- Policy implications section flagged for revision.
- Note on the two report types (Executive & Legislative vs. SBE) still to write.
- Reference URLs for ADE reports and HB 2853; AI use statement.
