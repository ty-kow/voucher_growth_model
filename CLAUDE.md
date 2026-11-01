# Voucher Growth Model

Forecast Arizona ESA (voucher) enrollment and program cost from quarterly state reports. enrollment drivers feed a cost projection. Modelling method is undecided; validate extraction first.

## Layout
- `data/raw/voucher_reports/`: source PDFs (FY21Q2-FY26Q4), tracked in git
- `data/processed/`: generated, tracked in git; changes logged in `docs/decisions.md`
  - `extracted/`: extractor output (`voucher_metrics_extracted.csv`, `az_pop_proj_extracted.csv`, `az_pop_real_extracted.csv`)
  - `clean/`: cleaned files (`voucher_metrics_clean.csv`, `az_pop_real_clean.csv`)
- `outputs/`: generated files (graphs, analysis), no scripts; `report/` tracked in git, `draft/` git-ignored
- `src/voucher_growth_model/`: all code, including scripts that create graphs
  - `data_cleaning/`: `extract_esa.py` (PDF to CSV), `clean_esa.py` (raw to clean CSV), `extract_population.py`, `clean_population_proj.py`, `clean_population_real.py`, `merge_population.py`, `make_report_data.py`
  - `forecast.py`: enrollment and cost forecast
  - `plots_drafts/plot_*.py` (git-ignored): draft graph scripts; run from the repo root, write to `outputs/`
  - `plots_report/fonts/`: bundled Montserrat (OFL), loaded by the forecast plots
  - `plots_report/plot_*.py`: scripts for the `outputs/report/` report figures (`plot_forecast_slide --table --panels`, `plot_enrollment_actual`)
- `tests/`: pytest tests
- `docs/`: `decisions.md`, `research_log.md`
- Root docs: `README.md`

## Commands
- `uv sync`
- `uv run python -m voucher_growth_model.data_cleaning.extract_esa data/raw/voucher_reports data/processed/extracted/voucher_metrics_extracted.csv`

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
