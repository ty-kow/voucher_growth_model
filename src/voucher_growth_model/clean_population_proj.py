"""Raw population projection CSV to clean CSV.

Adds `pop_5_19 = pop_5_9 + pop_10_14 + pop_15_19` (derived, not reported).

Usage (from the repo root):
    uv run python -m voucher_growth_model.clean_population_proj <raw_csv> <clean_csv>
"""
import sys

import pandas as pd


def clean(raw_path, out_path) -> pd.DataFrame:
    df = pd.read_csv(raw_path)
    df["pop_5_19"] = df["pop_5_9"] + df["pop_10_14"] + df["pop_15_19"]
    df.to_csv(out_path, index=False)
    return df


if __name__ == "__main__":
    clean(sys.argv[1], sys.argv[2])
