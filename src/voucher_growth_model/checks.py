"""Robustness checks on the forecast (see docs/decisions.md, "Forecast checks").

1. Hold-out: fit r on FY23-FY25, anchor at FY25 take-up, project FY26 enrollment per ceiling,
   and compare with the FY26 Q3 actual.
2. Population sensitivity: treat the 2025 -> 2026 drop in pop_5_19 as a series difference,
   scaling every projected year (FY26 on) by pop(FY25) / pop(FY26), then rerun the forecast.

Usage (from the repo root):
    uv run python -m voucher_growth_model.checks <report_data> <holdout_csv> <sensitivity_csv>
"""
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd

from voucher_growth_model.forecast import BASE_FY, BASES, GROWTH_START_FY, forecast, takeup_path


def holdout(report_path, out_path, base="5_19") -> pd.DataFrame:
    cfg = BASES[base]
    v = pd.read_csv(report_path)
    v.index = 2000 + v["year"].str[2:4].astype(int)
    takeup = v["total_enroll"] / v[cfg["pop_col"]]
    fit_end = BASE_FY - 1
    window = takeup.loc[GROWTH_START_FY:fit_end]
    r = np.polyfit(window.index, np.log(window), 1)[0]
    actual = v.loc[BASE_FY, "total_enroll"]
    rows = []
    for k_name, k in cfg["ceilings"].items():
        pred = takeup_path(takeup[fit_end], k, r, 1) * v.loc[BASE_FY, cfg["pop_col"]]
        rows.append({"takeup_scenario": k_name, "r_fit": r, "pred_enroll": pred,
                     "actual_enroll": actual, "error_pct": (pred / actual - 1) * 100})
    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False)
    return df


def pop_sensitivity(report_path, out_path, base="5_19") -> pd.DataFrame:
    col = BASES[base]["pop_col"]
    v = pd.read_csv(report_path)
    v[col] = v[col].astype(float)
    fy = 2000 + v["year"].str[2:4].astype(int)
    scale = v.loc[fy == BASE_FY - 1, col].iloc[0] / v.loc[fy == BASE_FY, col].iloc[0]
    v.loc[fy >= BASE_FY, col] *= scale
    with TemporaryDirectory() as tmp:
        scaled = Path(tmp) / "report_data_scaled.csv"
        v.to_csv(scaled, index=False, na_rep="N/A")
        return forecast(scaled, out_path, base)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: python -m voucher_growth_model.checks REPORT_DATA HOLDOUT_CSV SENSITIVITY_CSV")
    print(holdout(sys.argv[1], sys.argv[2]).to_string(index=False))
    s = pop_sensitivity(sys.argv[1], sys.argv[3])
    fy46 = s[s.fy == "FY46"]
    print(f"r = {s.r.iloc[0]:.3f}; FY26 take-up = {s[s.fy == 'FY26'].takeup.iloc[0]:.4f}; "
          f"FY46 real cost ${fy46.cost_real_fy26.min() / 1e9:.2f}-{fy46.cost_real_fy26.max() / 1e9:.2f}B")
