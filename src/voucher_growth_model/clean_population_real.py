"""Raw actual population CSV (long format) to clean CSV (wide format).

Pivots to one row per year with columns 5-9, 10-14, 15-19, total_pop, and adds
`5-19` (sum of the three age groups) and `school_aged_ratio` (5-19 / total_pop,
rounded to 6 decimals). Both added columns are derived, not reported.

Usage (from the repo root):
    uv run python -m voucher_growth_model.clean_population_real <raw_csv> <clean_csv>
"""
import sys

import pandas as pd

AGE_GROUPS = ["5-9", "10-14", "15-19"]


def clean(raw_path, out_path) -> pd.DataFrame:
    raw = pd.read_csv(raw_path)
    df = raw.pivot(index="year", columns="age_group", values="population")
    df["5-19"] = df[AGE_GROUPS].sum(axis=1)
    df["school_aged_ratio"] = (df["5-19"] / df["total_pop"]).round(6)
    df = df[AGE_GROUPS + ["5-19", "total_pop", "school_aged_ratio"]].reset_index()
    df.columns.name = None
    df.to_csv(out_path, index=False)
    return df


if __name__ == "__main__":
    clean(sys.argv[1], sys.argv[2])
