# Voucher Growth Model

Forecasts enrollment and program cost for Arizona's Empowerment Scholarship Account (ESA) voucher program from quarterly state reports. enrollment drivers feed a cost projection. The forecasting method is not yet chosen; the current stage is data extraction.

## Data

Quarterly ESA reports, FY21Q2-FY26Q4, in `data/raw/voucher_reports/`.
Source: Arizona Department of Education (ADE), ESA Program quarterly reports, published at [azed.gov](https://www.azed.gov). Earlier reports (FY21-FY24) were addressed to the State Board of Education; later ones are "Executive & Legislative" reports. TODO: add retrieval date.

FY24 quarters appear in two variants (`SBE` and non-`SBE`); the extractor merges them.

## Usage

```
uv sync
uv run python -m voucher_growth_model.extract_esa data/raw/voucher_reports data/processed/voucher_metrics.csv
```

Single report: `uv run python -m voucher_growth_model.extract_esa "<file>.pdf"`

## Layout

```
data/raw/voucher_reports/   source PDFs (tracked)
data/processed/             extracted CSVs (gitignored)
outputs/                    figures and results (gitignored)
src/voucher_growth_model/   extraction code
```

## Methodology

Text is extracted with pypdf, and metrics are parsed with regular expressions: mean voucher, total cost, total enrollment, and counts by eligibility category (universal, disability/special needs, military, preschool). Each metric has fallback patterns to handle format changes between reports.

## Limitations

- FY21Q2-FY23Q3 use a legacy format with one disability row for all students.
- Regex parsing is sensitive to report layout changes; unmatched values are left blank, not imputed.
- Mean voucher falls back to a student-weighted appendix mean when no stated average exists.
- Forecasting model not yet implemented.
