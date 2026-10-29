# Voucher Growth Model

Forecasts enrollment and program cost for Arizona's Empowerment Scholarship Account (ESA) voucher program from quarterly state reports. enrollment drivers feed a cost projection. The forecasting method is not yet chosen; the current stage is data extraction, cleaning, and exploratory forecasts (drafts in `outputs/draft/`).

## Data

Quarterly ESA reports, FY21Q2-FY26Q4, in `data/raw/voucher_reports/`.
Source: Arizona Department of Education (ADE), ESA Program quarterly reports, published at [azed.gov](https://www.azed.gov). Earlier reports (FY21-FY24) were addressed to the State Board of Education; later ones are "Executive & Legislative" reports. TODO: add retrieval date.

FY24 quarters appear in two variants (`SBE` and non-`SBE`); the extractor merges them.

## Usage

```
uv sync
uv run python -m voucher_growth_model.data_cleaning.extract_esa data/raw/voucher_reports data/processed/raw/voucher_metrics_raw.csv
```

Single report: `uv run python -m voucher_growth_model.data_cleaning.extract_esa "<file>.pdf"`

Other pipeline steps (`src/voucher_growth_model/data_cleaning/`):

```
uv run python -m voucher_growth_model.data_cleaning.clean_esa <raw_csv> <clean_csv>
uv run python -m voucher_growth_model.data_cleaning.extract_population <xlsx> <out_csv>
uv run python -m voucher_growth_model.data_cleaning.clean_population_proj <raw_csv> <clean_csv>
uv run python -m voucher_growth_model.data_cleaning.clean_population_real <raw_csv> <clean_csv>
uv run python -m voucher_growth_model.data_cleaning.merge_population <real_clean> <proj_clean> <out_csv>
```

Forecast (FY26-FY46 enrollment and cost; `total` is the default population base):

```
uv run python -m voucher_growth_model.forecast <voucher_clean> <pop_all_clean> <out_csv> [total|5_19]
```

Plots: run `plots/plot_*.py` from the repo root; they write to `outputs/`.

## Layout

```
data/raw/voucher_reports/             source PDFs (tracked)
data/processed/raw/                   extractor output (tracked)
data/processed/clean/                 cleaned CSVs (tracked)
outputs/draft/                        exploratory graphs and forecasts (tracked)
outputs/final/                        final results (tracked)
src/voucher_growth_model/data_cleaning/   extract, clean, and merge scripts
src/voucher_growth_model/plots/       graph scripts
src/voucher_growth_model/forecast.py  forecast
tests/                                pytest tests
```

## Methodology

Text is extracted with pypdf, and metrics are parsed with regular expressions: mean voucher, total cost, total enrollment, and counts by eligibility category (universal, disability/special needs, military, preschool). Each metric has fallback patterns to handle format changes between reports.

Forecast (`forecast.py`): enrollment = take-up x population (total or ages 5-19). Take-up follows a logistic path to a ceiling, passing through FY26 actual take-up at the FY23-FY26 growth rate. Cost = enrollment x mean voucher, with mean voucher grown from FY26 at 2% inflation or the FY24-FY26 historical rate; real values are in FY26 dollars (2% deflator). Choices are recorded in `decisions.md`.

## Limitations

- FY21Q2-FY23Q3 use a legacy format with one disability row for all students.
- Regex parsing is sensitive to report layout changes; unmatched values are left blank, not imputed.
- Mean voucher falls back to a student-weighted appendix mean when no stated average exists.
- Forecasting model not finalized; current forecasts are drafts.
