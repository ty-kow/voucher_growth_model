"""Extract Arizona population projections (2026-2046) from the OEO workbook to CSV.

All columns come from tab 2 ("Pop By Age Group & Sex"), both-sexes "Total" row of
each year block. No derived columns.

Usage (from the repo root):
    uv run python -m voucher_growth_model.extract_population <xlsx> <out_csv>
"""
import sys

import openpyxl
import pandas as pd

YEARS = range(2026, 2047)
AGE_COLUMNS = {
    "pop_total": "Total",
    "pop_5_9": "5-9",
    "pop_10_14": "10-14",
    "pop_15_19": "15-19",
}


def total_rows(ws) -> dict[int, dict[str, float]]:
    """Tab 2: for each year, the both-sexes 'Total' row keyed by column header."""
    header = next(r for r in ws.iter_rows(values_only=True) if r[0] == "Year")
    out, year = {}, None
    for row in ws.iter_rows(values_only=True):
        if isinstance(row[0], int):
            year = row[0]
        if row[1] == "Total" and year in YEARS:
            out[year] = dict(zip(header, row))
    return out


def extract(xlsx_path: str) -> pd.DataFrame:
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    rows = total_rows(wb.worksheets[1])
    df = pd.DataFrame(
        {
            "year": list(YEARS),
            **{
                name: [rows[y][col] for y in YEARS]
                for name, col in AGE_COLUMNS.items()
            },
        }
    )
    return df


if __name__ == "__main__":
    extract(sys.argv[1]).to_csv(sys.argv[2], index=False)
