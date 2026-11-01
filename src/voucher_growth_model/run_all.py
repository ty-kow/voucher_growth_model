"""Rebuild every generated file from data/raw/, in pipeline order.

Usage (from the repo root):
    uv run python -m voucher_growth_model.run_all
"""
import subprocess
import sys
from pathlib import Path

POP = Path("data/raw/population")
EXT = "data/processed/extracted"
CLEAN = "data/processed/clean"
REP = "outputs/report"

STEPS = [
    ["data_cleaning.extract_esa", "data/raw/voucher_reports", f"{EXT}/voucher_metrics_extracted.csv"],
    ["data_cleaning.clean_esa", f"{EXT}/voucher_metrics_extracted.csv", f"{CLEAN}/voucher_metrics_clean.csv"],
    ["data_cleaning.extract_population", str(POP / "az_population_growth.xlsx"), f"{EXT}/az_pop_proj_extracted.csv"],
    ["data_cleaning.clean_population_proj", f"{EXT}/az_pop_proj_extracted.csv", f"{CLEAN}/az_pop_proj_clean.csv"],
    ["data_cleaning.extract_population_real", f"{EXT}/az_pop_real_extracted.csv",
     *sorted(str(p) for p in POP.glob("20* - 5 year*.xlsx"))],
    ["data_cleaning.clean_population_real", f"{EXT}/az_pop_real_extracted.csv", f"{CLEAN}/az_pop_real_clean.csv"],
    ["data_cleaning.merge_population", f"{CLEAN}/az_pop_real_clean.csv", f"{CLEAN}/az_pop_proj_clean.csv",
     f"{CLEAN}/az_pop_all_clean.csv"],
    ["data_cleaning.make_report_data"],
    ["forecast", f"{REP}/report_data.csv", f"{REP}/forecast.csv"],
    ["plots_report.plot_forecast_slide", f"{REP}/report_data.csv", f"{REP}/forecast.csv",
     f"{REP}/forecast_slide_report.png"],
    ["plots_report.plot_enrollment_actual", f"{REP}/report_data.csv", f"{REP}/enrollment_actual.png"],
    ["plots_report.plot_forecast_enrollment", f"{REP}/report_data.csv", f"{REP}/forecast.csv",
     f"{REP}/forecast_enrollment_report.png"],
    ["plots_report.plot_forecast_cost_table", f"{REP}/forecast.csv", f"{REP}/forecast_cost_table.png"],
]

if __name__ == "__main__":
    for module, *args in STEPS:
        print(f"> {module}", flush=True)
        subprocess.run([sys.executable, "-m", f"voucher_growth_model.{module}", *args], check=True)
