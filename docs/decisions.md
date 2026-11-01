# Decisions

## Current forecast specification (summary, 2026-11-01)

Detail and history are in the entries below; entries marked "superseded" are kept as a record.

- Inputs: `outputs/report/report_data.csv` (Q3 value per fiscal year, FY21-FY26; population aged 5-19 from 2023).
- Enrollment = take-up x population aged 5-19. Take-up follows a logistic path to a ceiling of 9.9% (best fit), 20%, 30% or 40%, anchored at FY26 actual take-up (7.49%).
- Shared rate r = 0.246: slope of log take-up on year, FY23-FY26.
- Mean voucher grows from FY26 ($10,837.68) at 2%/yr or the FY24-FY26 rate (about 5.1%/yr).
- Cost = enrollment x mean voucher; real values in FY26 dollars (2%/yr deflator).
- Horizon FY26-FY46, annual; 4 x 2 = 8 scenarios. Output: `outputs/report/forecast.csv`.

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

Decision: add grade-level enrollment data to the project. Explanation: enrollment is driven first by incoming (kindergarten) and outgoing (grade 12) students, and students tend to leave the program before grade 9 (qualitative claim, not yet checked against data). Grade-level counts are needed to test this and to model enrollment flows.

All other modelling decisions (method, targets, cost structure) are deferred until the grade-level data has been explored. No changes to `data/processed/` files yet.

## Grade-level data brought in

Grade-level enrollment (`kinder`, `grade_1` to `grade_12`) extracted from all quarterly PDFs and added to `voucher_metrics_extracted.csv` and `voucher_metrics_clean.csv`. Preschool was already present (`Preschool Count` / `total_pre`). No values imputed.

- FY23Q4: the PDF has only a bar chart for total enrollment by grade; counts were read from the chart and accepted because preschool plus grades 1 to 12 sums to total enrollment (61,689).
- All 23 quarters: preschool + `kinder` + `grade_1` to `grade_12` equals total enrollment.

## FY25Q3 preschool: grade-level table used

Flag: FY25Q3 preschool is 1,340 (grade-level table), not 1,346 (eligibility table). Grade-level table chosen for consistency with the other grade data; with it, preschool plus grades sums to total enrollment (87,602). The extractor now takes preschool from the grade-level table for all quarters; no other quarter changed. `total_pre` in `voucher_metrics_clean.csv` updated to 1340.

## Population projections

Source: Arizona OEO population projections, 2025 to 2060, Medium Series (https://oeo.az.gov/population/projections). Statewide, both sexes, 2026-2046.

- `data/processed/extracted/az_pop_proj_extracted.csv`: extractor output (`extract_population.py`), all from tab 2 (both-sexes "Total" row): `pop_total`, `pop_5_9`, `pop_10_14`, `pop_15_19`. No values altered, nothing derived.
- `data/processed/clean/az_pop_proj_clean.csv`: copy of the raw file with `pop_5_19 = pop_5_9 + pop_10_14 + pop_15_19` added (derived, not reported), to match the 5-19 age range of `az_pop_real_clean.csv`.
- `data/processed/clean/az_pop_all_clean.csv`: real (2023-2025) and projected (2026-2046) population stacked by year (`merge_population.py`). Columns `year`, `pop_total`, `pop_5_19`, `source` (`real` or `proj`). No year overlaps; real wins if one does. Real `total_pop` renamed `pop_total`, `5-19` renamed `pop_5_19`. Real and projected come from different sources (see above), so a level shift at 2025/2026 is possible.

## Forecast scope

Decided by the user (2026-10-29):

- Horizon: through FY36 or later.
- Frequency: annual (fiscal year).
- Enrollment method: take-up rate x population.
- Cost method: enrollment x mean voucher, with mean voucher forecast separately.

Still open: how quarters become annual values, which population base to use, how take-up is forecast, how mean voucher is forecast.

## Forecast method details (partly superseded: take-up base is now pop_5_19, see "School-age (5-19) population version" and "report_data.csv")

Decided by the user (2026-10-29):

- Annual value: each fiscal year's Q3 report.
- Take-up rate: enrollment / `pop_total`.
- Take-up projection: scenario paths with a ceiling.
- Mean voucher projection: scenario rates, including 2% inflation and the historical growth rate; any further scenarios are still open.

## Forecast parameters (partly superseded: 3.5% scenario dropped, see "Take-up scenarios revised")

Decided by the user (2026-10-29):

- Population year: same calendar year as the Q3 report (FY26Q3 pairs with 2026).
- Historical mean-voucher growth: compound rate over FY24-FY26 only (about 5.1%/yr).
- Mean-voucher scenarios: 2% inflation, historical rate (FY24-FY26), high inflation (3.5%).
- Take-up ceilings: fit a logistic curve to FY23-FY26 as a reference, then the user picks the ceilings.

## Take-up scenarios (superseded: total-population base removed, see "report_data.csv")

Decided by the user (2026-10-29): take-up ceilings of 1.44% (logistic best fit to FY23-FY26), 3%, 5% and 10%. Each path approaches its ceiling at the fitted rate (r = 0.797/yr). Logistic fit: K = 0.0144 (s.e. 0.0016), r = 0.797, t0 = 0.146 (t = 0 at FY23); fixed ceilings from 1.5% to 10% fit almost as well (4 data points).

Anchor: each logistic path is re-centred (t0 solved) so it passes through FY26 actual take-up (1.32%), keeping its ceiling and r = 0.797.

## Forecast output

Decided by the user (2026-10-29): forecast runs FY27-FY46 (later changed to start at FY26, see "Forecast start year"); all 12 combinations (4 take-up paths x 3 mean-voucher rates); cost reported in nominal dollars and in real FY26 dollars (deflated at 2%/yr). Mean voucher grows from FY26 actual ($10,837.68). Cost = enrollment x mean voucher.

## Take-up scenarios revised (superseded: per-ceiling r replaced, see "Take-up rate (FY23-FY26 fit, all four years)")

Decided by the user (2026-10-29), after reviewing the first forecast graph:

- 10% ceiling dropped (about 917k students by FY46); replaced with 2%. Ceilings are now 1.44%, 2%, 3%, 5%.
- Approach rate: for each ceiling, r is solved so FY27 take-up grows by the FY25-FY26 take-up growth (16.1%). Resulting r: 2% = 0.520, 3% = 0.283, 5% = 0.208.
- 1.44% cannot grow 16.1% without passing its ceiling, so it keeps the fitted r = 0.797.

Forecast graph (2026-10-29, user): cost shown in real FY26 dollars only; Q3 actuals deflated at the same 2%/yr. `outputs/draft/forecast/csv/forecast_draft.csv` still holds both nominal and real cost.

Mean-voucher scenarios (2026-10-29, user): 3.5% high-inflation scenario dropped. Remaining: 2% inflation and historical FY24-FY26 rate; grid is now 4 x 2 = 8.

## School-age (5-19) population version

Decided by the user (2026-10-29): a second forecast using take-up = enrollment / `pop_5_19`, written to separate files (`outputs/forecast/csv/forecast_5_19.csv`, `outputs/forecast/forecast_5_19.png`); the total-population version is unchanged.

- Take-up (Q3): FY23 3.48%, FY24 5.15%, FY25 6.05%, FY26 7.49%. FY25-FY26 growth 23.8% (vs 16.1% on total population); 2025 is real and 2026 projected population, so part may be a source level shift.
- Logistic fit to FY23-FY26: K = 9.90% (s.e. 3.5pp), r = 0.555.
- Ceilings: 9.9% (fitted), 20%, 30%, 40%.
- Rates: same rule as the total version (match FY26 take-up growth). All four ceilings can match it, so none uses the fitted r.
- Forecast CSVs now carry `pop_base` and `pop` in place of `pop_total`.

## Project setup and plots (2026-10-29)

- `pyproject.toml`: added a hatchling build system with `src/voucher_growth_model` as the wheel package, so `uv run python -m voucher_growth_model.<module>` imports the package. `uv.lock` updated.
- `plots_drafts/plot_pop_proj.py`: y-axis now starts at 0 so population changes are not visually exaggerated.
- `plots_drafts/plot_pop_all.py` (`outputs/population/pop_all.png`): plots the merged real and projected series from `az_pop_all_clean.csv`.

## Forecast start year

Decided by the user (2026-10-29): forecast CSVs and graphs start at FY26 instead of FY27 (FY26-FY46, 21 years). The FY26 row is t = 0: take-up, enrollment and mean voucher equal the FY26 Q3 actuals, and cost is enrollment x mean voucher (not the reported FY26 cost). Applies to both population bases; all other choices unchanged.

## Take-up rate (common r) (superseded, see "Take-up rate (FY23-FY26 fit, all four years)")

Decided by the user (2026-10-29): all ceilings within a population base share the logistic rate fitted to FY23-FY26 take-up, so FY27 differs by scenario. Total population: r = 0.797. Ages 5-19: r = 0.555. This replaces the rule that solved r per ceiling to match FY25-FY26 take-up growth ("Take-up scenarios revised" and the 5-19 "Rates" line); ceilings and the FY26 anchor are unchanged. `rate_matching_growth` was removed from `forecast.py`.

## Take-up rate (FY23-FY26 growth) (superseded, see "Take-up rate (FY23-FY26 fit, all four years)")

Decided by the user (2026-10-29): the shared logistic rate r is now the continuous annual growth rate of take-up, r = ln(FY26 take-up / FY23 take-up) / 3, computed in `forecast.py` for each population base. Total population: r = 0.228. Ages 5-19: r = 0.255. This replaces the fixed fitted rates (0.797 / 0.555). The user asked for FY22-FY26, but population data starts in 2023, so FY22 take-up cannot be computed without imputing a 2022 population; FY23 was chosen as the start (user's choice). Ceilings, the FY26 anchor and mean-voucher scenarios are unchanged.

## Take-up rate (FY23-FY26 fit, all four years)

Decided by the user (2026-10-29): the shared logistic rate r is now the slope of log take-up on year over FY23-FY26 (least squares on all four years), replacing the FY23-FY26 endpoint rate ln(FY26 / FY23) / 3, which ignored FY24 and FY25. Ages 5-19: r = 0.246 (was 0.255). Ceilings, the FY26 anchor and mean-voucher scenarios are unchanged. `forecast.py` uses `numpy.polyfit`; the forecast CSV and `outputs/report/` graphs were regenerated. FY46 enrollment: 9.9% = 134,648; 20% = 269,365; 30% = 400,187; 40% = 528,533. Four data points, so r is not statistically strong. Earlier entries giving r = 0.255 are superseded.

## Extractor output renamed (2026-10-29)

Decided by the user (2026-10-29): `data/processed/raw/` renamed to `data/processed/extracted/`, and extractor files renamed from `*_raw.csv` to `*_extracted.csv` (`voucher_metrics_extracted.csv`, `az_pop_proj_extracted.csv`, `az_pop_real_extracted.csv`). Paths updated in code, tests and docs. File contents unchanged. Earlier entries above that name `*_raw.csv` or `data/processed/raw/` refer to these files.

## report_data.csv (2026-10-29)

Decided by the user (2026-10-29): `outputs/report/report_data.csv` is built by `data_cleaning/make_report_data.py` from `voucher_metrics_clean.csv`. It keeps `mean_voucher`, `total_cost` and `total_enroll` for the Q3 report of each fiscal year only (FY21Q3 to FY26Q3, 6 rows); the other quarters are dropped. The `quarter` column is renamed `year` and holds the fiscal year (`FY21` to `FY26`); each value is the Q3 value for that year. No values altered. `forecast.py` and `plots_drafts/plot_forecast.py` now read this file (column `year`) and no longer filter for Q3; the Q3 choice is unchanged from "Forecast method details" ("Annual value: each fiscal year's Q3 report") and now applies through this file. All forecast inputs from this file are Q3 values. They no longer accept `voucher_metrics_clean.csv`.

Updates (2026-10-29, user): the file was renamed from `final_data_voucher.csv` to `final_data.csv` (now `outputs/report/report_data.csv`). Population columns `pop_total` and `pop_5_19` were added, joined from `az_pop_all_clean.csv` by calendar year (FYxx pairs with 20xx; FY26 uses the projected value). FY21 and FY22 are `N/A` because population data starts in 2023; nothing was imputed. Rows FY27 to FY46 were added (26 rows in total) with `N/A` for `mean_voucher`, `total_cost` and `total_enroll`. `pop_total` was added because the forecast needs it and `forecast.py` now reads only `report_data.csv` (usage: `forecast FINAL_DATA OUT_CSV [total|5_19]`); it no longer reads `az_pop_all_clean.csv`. Forecast results are unchanged.

Update (2026-10-29, user): `pop_total` removed from `report_data.csv` (columns now `year`, `mean_voucher`, `total_cost`, `total_enroll`, `pop_5_19`), and the forecast now produces only the ages 5-19 base (`pop_base` = `5_19`; ceilings k9.9, k20, k30, k40; 21 years x 4 ceilings x 2 voucher scenarios = 168 rows). The total-population base (ceilings k1.44, k2, k3, k5) was removed from `forecast.py`, so `forecast` takes `FINAL_DATA OUT_CSV` only. Earlier entries that describe the total-population base are superseded. The 5-19 results are unchanged.

## Universal expansion timing and enrollment graphic (2026-10-29)

Decided by the user (2026-10-29): universal expansion began in Q1 2023 (FY23Q1). This confirms the "total_universal and total_universal_sn zero-fill" entry above (zeros through FY22Q4). `outputs/report/forecast_enrollment_report.png` was revised in the same session:

- The notes sentence about the FY23 expansion and FY21-FY22 take-up was removed. FY21-FY22 take-up is still absent from the forecast because population data starts in 2023.
- Scenario lines keep the original teal/orange/red/magenta colours and gain distinct dash patterns (dotted for 9.9%, dashed for 20%, dash-dot for 30%, long dash for 40%) so they stay separable in greyscale and for colour-blind readers. A blue ramp was tried and reverted. End values are labelled on each line.
- The notes no longer state the shared rate (r = 0.246) or the four-point fit; both are recorded in "Take-up rate (FY23-FY26 fit, all four years)" above.
- Other edits: title and subtitle reworded, the 9.9% scenario relabelled "Best-fit ceiling, 9.9%", legend order reversed, FY26 population-source flag added to the notes, x-axis labels shown as calendar years (2021, 2023, 2026, then every fifth year), x-axis title removed.

## Report outputs and repo restructure (2026-11-01)

Decided by the user (2026-11-01):

- `outputs/final/` renamed to `outputs/report/`. `final_data.csv` renamed to `report_data.csv` and moved into it (built by `make_report_data.py`, renamed from `make_final_data.py`); `forecast_final.csv` renamed to `forecast.csv`. The draft forecast CSV is `outputs/draft/forecast/csv/forecast_draft.csv`.
- Report figures in `outputs/report/`: `enrollment_actual.png` (FY21-FY26 Q3 actuals), `forecast_enrollment_report.png` and `forecast_cost_table.png` (standalone panels of the slide, with report titles and a sources line), `forecast_slide_report.png` (slide with the cost tables).
- Earlier final graphs (`forecast_cost_final`, `forecast_cost_scenarios_final`, `forecast_enrollment_final`, `forecast_table`, first slide) moved to `outputs/draft/forecast/`.
- Report figure scripts moved to `src/voucher_growth_model/plots_report/` and made self-contained (fonts and `plot_forecast_cost.py` moved in). Draft scripts folder renamed `plots/` to `plots_drafts/`.
- `outputs/draft/` and `plots_drafts/` are git-ignored and removed from the git index; files remain local.
- Report text: `docs/report_outline.md` (skeleton) and `docs/report_draft.md` (draft).

## Replication docs (2026-11-01)

Decided by the user (2026-11-01): run commands for `forecast_enrollment_report.png` and `forecast_cost_table.png` added to `README.md` and `CLAUDE.md`. `.python-version` added (`3.15`) to pin the interpreter used by uv. No data or outputs changed.

## Report figure scripts reproduce the report PNGs (2026-11-01)

Decided by the user (2026-11-01): the committed `forecast_enrollment_report.png` and `forecast_cost_table.png` could not be reproduced from their scripts. `plot_forecast_enrollment.py` now keeps the headline title (`Enrollment in Arizona's Private School Voucher Program Could Reach ...`) and its command line puts the notes before the sources line. `plot_forecast_cost_table.py` called from the command line now adds the `ESA Voucher Cost Forecasts` title and the sources line, centres the header on the figure, and uses a 6.5 x 8.05 in figure so the notes fit. The slide (`plot_forecast_slide.py`) still uses the function defaults and is unchanged. Both PNGs regenerated; values unchanged.
