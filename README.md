# Voucher Growth Model

Forecasts enrollment and program cost for Arizona's Empowerment Scholarship Account (ESA) voucher program from quarterly state reports. Enrollment drivers feed a cost projection. The forecast method is logistic take-up scenarios on the population aged 5-19 (see `docs/decisions.md`). Generated figures are written to `outputs/report/`.

## Data

Quarterly ESA reports, FY21Q2-FY26Q4, in `data/raw/voucher_reports/`.
Source: Arizona Department of Education (ADE), ESA Program quarterly reports, published at [azed.gov](https://www.azed.gov). Earlier reports (FY21-FY24) were addressed to the State Board of Education; later ones are "Executive & Legislative" reports. TODO: add retrieval date.

FY24 quarters appear in two variants (`SBE` and non-`SBE`); the extractor merges them.

Population: Arizona Office of Economic Opportunity (OEO), [population projections](https://oeo.az.gov/population/projections), 2025-2060 Medium Series, plus 2023-2025 estimates, in `data/raw/population/`.

## Usage

Rebuild every generated file from `data/raw/` (uses the exact versions in `uv.lock`):

```
uv sync --locked
uv run --locked python -m voucher_growth_model.run_all
```

Individual steps:

```
uv run python -m voucher_growth_model.data_cleaning.extract_esa data/raw/voucher_reports data/processed/extracted/voucher_metrics_extracted.csv
```

Single report: `uv run python -m voucher_growth_model.data_cleaning.extract_esa "<file>.pdf"`

Other pipeline steps (`src/voucher_growth_model/data_cleaning/`):

```
uv run python -m voucher_growth_model.data_cleaning.clean_esa <raw_csv> <clean_csv>
uv run python -m voucher_growth_model.data_cleaning.extract_population <xlsx> <out_csv>
uv run python -m voucher_growth_model.data_cleaning.extract_population_real <out_csv> <xlsx> [<xlsx> ...]
uv run python -m voucher_growth_model.data_cleaning.clean_population_proj <raw_csv> <clean_csv>
uv run python -m voucher_growth_model.data_cleaning.clean_population_real <raw_csv> <clean_csv>
uv run python -m voucher_growth_model.data_cleaning.merge_population <real_clean> <proj_clean> <out_csv>
uv run python -m voucher_growth_model.data_cleaning.make_report_data
```

Forecast (FY26-FY46 enrollment and cost, population aged 5-19):

```
uv run python -m voucher_growth_model.forecast outputs/report/report_data.csv outputs/report/forecast.csv
```

Report figures (run from the repo root; write to `outputs/report/`):

```
uv run python -m voucher_growth_model.plots_report.plot_forecast_slide outputs/report/report_data.csv outputs/report/forecast.csv outputs/report/forecast_slide_report.png --table
uv run python -m voucher_growth_model.plots_report.plot_enrollment_actual outputs/report/report_data.csv outputs/report/enrollment_actual.png
uv run python -m voucher_growth_model.plots_report.plot_forecast_enrollment outputs/report/report_data.csv outputs/report/forecast.csv outputs/report/forecast_enrollment_report.png
uv run python -m voucher_growth_model.plots_report.plot_forecast_cost_table outputs/report/forecast.csv outputs/report/forecast_cost_table.png
```

## Layout

```
data/raw/voucher_reports/                    source PDFs
data/raw/population/                         OEO population workbooks
data/processed/                              generated: extracted/ and clean/ CSVs (git-ignored)
outputs/                                     generated: report data, forecast, figures (git-ignored)
src/voucher_growth_model/run_all.py          rebuilds all generated files from data/raw/
src/voucher_growth_model/data_cleaning/      extract, clean, and merge scripts
src/voucher_growth_model/forecast.py         forecast
src/voucher_growth_model/plots_report/       report figure scripts (fonts/ holds bundled Montserrat)
docs/                                        decisions.md, research_log.md, data_dictionary.md
tests/                                       pytest tests
```

Local-only, git-ignored: `src/voucher_growth_model/plots_drafts/` and `docs/report_*.md`.

## Tests

```
uv run pytest
```

## Methodology

Text is extracted with pypdf, and metrics are parsed with regular expressions: mean voucher, total cost, total enrollment, and counts by eligibility category (universal, disability/special needs, military, preschool). Each metric has fallback patterns to handle format changes between reports.

Forecast (`forecast.py`): enrollment = take-up x population aged 5-19. Take-up follows a logistic path to a ceiling (9.9%, 20%, 30% or 40%), passing through FY26 actual take-up at the FY23-FY26 growth rate. Cost = enrollment x mean voucher, with mean voucher grown from FY26 at 2% inflation or the FY24-FY26 historical rate; real values are in FY26 dollars (2% deflator). Choices are recorded in `docs/decisions.md`.

## Limitations

- FY21Q2-FY23Q3 use a legacy format with one disability row for all students.
- Regex parsing is sensitive to report layout changes; unmatched values are left blank at extraction.
- Some values were filled during cleaning on explicit instruction (e.g. FY21-FY24 total cost, FY25+ mean voucher); every fill is listed in `docs/decisions.md`.
- Mean voucher falls back to a student-weighted appendix mean when no stated average exists.
- Take-up growth rests on four annual post-expansion observations; ceilings are scenarios, not estimates.
