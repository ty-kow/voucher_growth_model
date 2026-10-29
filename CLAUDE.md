# Voucher Growth Model

Forecast Arizona ESA (voucher) enrollment and program cost from quarterly state reports. enrollment drivers feed a cost projection. Modelling method is undecided; validate extraction first.

## Layout
- `data/raw/voucher_reports/`: source PDFs (FY21Q2-FY26Q4), tracked in git
- `data/processed/`: generated, tracked in git; changes logged in `decisions.md`
  - `raw/`: extractor output (`voucher_metrics_raw.csv`, `az_pop_proj_raw.csv`, `az_pop_real_raw.csv`)
  - `clean/`: cleaned files (`voucher_metrics_clean.csv`, `az_pop_real_clean.csv`)
- `outputs/`: generated files (graphs, analysis), no scripts, tracked in git (`draft/`, `final/`)
- `src/voucher_growth_model/`: all code, including scripts that create graphs
  - `extract_esa.py`: PDF to CSV extractor
  - `clean_esa.py`: raw to clean CSV
  - `plots/plot_*.py`: graph scripts; run from the repo root, write to `outputs/`
- `tests/`: pytest tests
- Root docs: `decisions.md`, `research_log.md`, `README.md`

## Commands
- `uv sync`
- `uv run python -m voucher_growth_model.data_cleaning.extract_esa data/raw/voucher_reports data/processed/raw/voucher_metrics_raw.csv`

## Conventions
- Use uv only; no pip.
- Scripts go in `src/voucher_growth_model/`, not `outputs/`.
- Add tests for any extraction change (pytest, text fixtures from PDFs).
- Never edit files in `data/raw/`; confirm before touching them.
- Missing values stay blank/N/A. Never impute or guess.

## Data caveats
- FY21Q2-FY23Q3 reports are a legacy format: a single disability row covers all students (`legacy_sn` flag).
- FY24 quarters have both `SBE` and non-`SBE` PDFs; the extractor merges them by filling blanks per quarter.
- Mean voucher has three fallback sources: narrative sentence, table row, appendix student-weighted mean.
- Quarters are labelled `FYxxQn`.
