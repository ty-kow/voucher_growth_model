"""Extract Arizona population estimates from the OEO five-year-group workbooks to CSV.

Each workbook holds one year (read from the title row, e.g. "..., ARIZONA, 2024").
Values come from the first sheet, first "Arizona" row (state total, both sexes). Output is long format:
age groups for every year, then total_pop for every year. No derived columns.

Usage (from the repo root):
    uv run python -m voucher_growth_model.data_cleaning.extract_population_real <out_csv> <xlsx> [<xlsx> ...]
"""
import re
import sys

import openpyxl
import pandas as pd

AGE_GROUPS = ["5-9", "10-14", "15-19"]


def extract_one(xlsx_path) -> tuple[int, dict[str, int]]:
    """Year and {age group or 'total_pop': population} from one workbook."""
    ws = openpyxl.load_workbook(xlsx_path, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    title = next(r[0] for r in rows if isinstance(r[0], str) and "ARIZONA" in r[0])
    year = int(re.search(r"(\d{4})\s*$", title).group(1))
    header = next(r for r in rows if "Total" in r and "5-9" in r)
    # First "Arizona" row is the state total (2023 adds an "All groups" race column).
    total = next(r for r in rows if r[0] == "Arizona")
    values = dict(zip(header, total))
    out = {g: values[g] for g in AGE_GROUPS}
    out["total_pop"] = values["Total"]
    return year, out


def extract(xlsx_paths) -> pd.DataFrame:
    by_year = dict(sorted(extract_one(p) for p in xlsx_paths))
    records = [(y, g, v[g]) for y, v in by_year.items() for g in AGE_GROUPS]
    records += [(y, "total_pop", v["total_pop"]) for y, v in by_year.items()]
    return pd.DataFrame(records, columns=["year", "age_group", "population"])


if __name__ == "__main__":
    extract(sys.argv[2:]).to_csv(sys.argv[1], index=False)
