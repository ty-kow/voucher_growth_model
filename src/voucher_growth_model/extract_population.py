"""Extract Arizona population projections (2026-2046) from the OEO workbook to CSV.

Usage (from the repo root):
    uv run python -m voucher_growth_model.extract_population <xlsx> <out_csv>
"""
import sys

import openpyxl
import pandas as pd

YEARS = range(2026, 2047)


def pop_0_4(ws) -> dict[int, float]:
    """Tab 2: the 'Total' (both sexes) row of each year block, column '0-4'."""
    header = next(r for r in ws.iter_rows(values_only=True) if r[0] == "Year")
    col = header.index("0-4")
    out, year = {}, None
    for row in ws.iter_rows(values_only=True):
        if isinstance(row[0], int):
            year = row[0]
        if row[1] == "Total" and year in YEARS:
            out[year] = row[col]
    return out


def tab3_total(ws, column: str) -> dict[int, float]:
    """Tab 3: one total column (e.g. '18 and Over: Total'), one row per year."""
    header = next(r for r in ws.iter_rows(values_only=True) if r[0] == "Year")
    col = header.index(column)
    return {
        row[0]: row[col]
        for row in ws.iter_rows(values_only=True)
        if isinstance(row[0], int) and row[0] in YEARS
    }


def extract(xlsx_path: str) -> pd.DataFrame:
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    young = pop_0_4(wb.worksheets[1])
    adult = tab3_total(wb.worksheets[2], "18 and Over: Total")
    everyone = tab3_total(wb.worksheets[2], "All Ages: Total")
    return pd.DataFrame(
        {
            "year": list(YEARS),
            "pop_0_4": [young.get(y) for y in YEARS],
            "pop_18_plus": [adult.get(y) for y in YEARS],
            "pop_total": [everyone.get(y) for y in YEARS],
        }
    )


if __name__ == "__main__":
    extract(sys.argv[1]).to_csv(sys.argv[2], index=False)
