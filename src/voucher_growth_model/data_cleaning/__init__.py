"""Merge real and projected population clean CSVs into one year series.

Keeps `pop_total` and `pop_5_19`; `source` is `real` or `proj`. Real values take
precedence if a year appears in both.

Usage (from the repo root):
    uv run python -m voucher_growth_model.data_cleaning.merge_population <real_clean> <proj_clean> <out_csv>
"""
import sys

import pandas as pd


def merge(real_path, proj_path, out_path) -> pd.DataFrame:
    real = pd.read_csv(real_path).rename(columns={"total_pop": "pop_total", "5-19": "pop_5_19"})
    real["source"] = "real"
    proj = pd.read_csv(proj_path)
    proj["source"] = "proj"
    cols = ["year", "pop_total", "pop_5_19", "source"]
    df = (
        pd.concat([real[cols], proj[cols]])
        .drop_duplicates("year", keep="first")
        .sort_values("year")
        .reset_index(drop=True)
    )
    df.to_csv(out_path, index=False)
    return df


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: python -m voucher_growth_model.data_cleaning.merge_population REAL_CLEAN PROJ_CLEAN OUT_CSV")
    merge(*sys.argv[1:])
