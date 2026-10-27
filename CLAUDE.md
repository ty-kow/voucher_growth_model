# Voucher Growth Model

Forecast Arizona ESA (voucher) enrolment and program cost from quarterly state reports. Enrolment drivers feed a cost projection. Modelling method is undecided; validate extraction first.

## Layout
- `data/raw/voucher_reports/`: source PDFs (FY21Q2-FY26Q4), tracked in git
- `data/processed/`, `outputs/`: generated, gitignored
- `src/voucher_growth_model/extract_esa.py`: PDF to CSV extractor

## Commands
- `uv sync`
- `uv run python -m voucher_growth_model.extract_esa data/raw/voucher_reports data/processed/voucher_metrics.csv`

## Conventions
- Use uv only; no pip.
- Add tests for any extraction change (pytest, text fixtures from PDFs).
- Never edit files in `data/raw/`; confirm before touching them.
- Missing values stay blank/N/A. Never impute or guess.

## Data caveats
- FY21Q2-FY23Q3 reports are a legacy format: a single disability row covers all students (`legacy_sn` flag).
- FY24 quarters have both `SBE` and non-`SBE` PDFs; the extractor merges them by filling blanks per quarter.
- Mean voucher has three fallback sources: narrative sentence, table row, appendix student-weighted mean.
- Quarters are labelled `FYxxQn`.
