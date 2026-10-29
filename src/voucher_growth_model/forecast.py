"""Forecast ESA enrollment and cost, FY26-FY46 (see decisions.md for every choice).
The FY26 row (t = 0) reproduces the FY26 Q3 actuals.

Enrollment = take-up x population aged 5-19 (pop_5_19; see BASES). Take-up follows a logistic path to each ceiling,
re-centred to pass through FY26 actual take-up, at the FY23-FY26 growth rate of take-up
(the same for every ceiling in a base). Cost = enrollment x mean voucher, with mean voucher grown from FY26 at each scenario rate.
Annual values come from each fiscal year's Q3 report; FYxx pairs with year 20xx.

Usage (from the repo root):
    uv run python -m voucher_growth_model.forecast <final_data> <out_csv>
"""
import math
import sys

import pandas as pd

BASE_FY = 2026
END_FY = 2046
GROWTH_START_FY = 2023  # take-up growth measured FY23-FY26 (population data starts in 2023)
# Per population base: take-up ceilings. All ceilings share the approach rate r, the
# continuous annual growth rate of take-up over FY23-FY26.
BASES = {
    "5_19": {
        "pop_col": "pop_5_19",
        "ceilings": {"k9.9": 0.0990, "k20": 0.20, "k30": 0.30, "k40": 0.40},
    },
}
BASE_VOUCHER_FY = 2024  # historical growth measured FY24-FY26
DEFLATOR = 0.02  # real dollars in FY26 terms


def takeup_path(y0, ceiling, r, t):
    """Logistic value t years after the base year, equal to y0 at t = 0."""
    return ceiling / (1 + (ceiling / y0 - 1) * math.exp(-r * t))


def forecast(final_path, out_path, base="5_19") -> pd.DataFrame:
    cfg = BASES[base]
    v = pd.read_csv(final_path)
    v["year"] = 2000 + v["year"].str[2:4].astype(int)
    v = v.set_index("year")
    pop = v[cfg["pop_col"]]

    takeup = v["total_enroll"] / pop
    y0 = takeup[BASE_FY]
    r = math.log(y0 / takeup[GROWTH_START_FY]) / (BASE_FY - GROWTH_START_FY)
    m0 = v.loc[BASE_FY, "mean_voucher"]
    hist = (m0 / v.loc[BASE_VOUCHER_FY, "mean_voucher"]) ** (1 / (BASE_FY - BASE_VOUCHER_FY)) - 1
    rates = {"infl2": 0.02, "hist": hist}

    rows = []
    for year in range(BASE_FY, END_FY + 1):
        t = year - BASE_FY
        for k_name, k in cfg["ceilings"].items():
            rate = takeup_path(y0, k, r, t)
            enroll = rate * pop[year]
            for g_name, g in rates.items():
                mean_voucher = m0 * (1 + g) ** t
                cost = enroll * mean_voucher
                rows.append({
                    "fy": f"FY{year % 100:02d}",
                    "takeup_scenario": k_name,
                    "voucher_scenario": g_name,
                    "pop_base": base,
                    "pop": pop[year],
                    "takeup": rate,
                    "r": r,
                    "enroll": enroll,
                    "mean_voucher": mean_voucher,
                    "cost_nominal": cost,
                    "cost_real_fy26": cost / (1 + DEFLATOR) ** t,
                })
    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False)
    return df


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python -m voucher_growth_model.forecast FINAL_DATA OUT_CSV")
    forecast(*sys.argv[1:])
