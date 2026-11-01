"""Clean voucher metrics and population CSVs to report_data.csv.

Voucher columns: Q3 rows only, `quarter` renamed `year` with the Q3 suffix dropped, values unchanged.
`pop_5_19` is joined from az_pop_all_clean.csv by calendar year (FYxx pairs with 20xx); N/A where the
population file has no year (before 2023). Years after the last voucher year (2027-2046) are added with
N/A voucher values.

Usage (from the repo root):
    uv run python -m voucher_growth_model.data_cleaning.make_report_data
"""
import pandas as pd

CLEAN_PATH = "data/processed/clean/voucher_metrics_clean.csv"
POP_PATH = "data/processed/clean/az_pop_all_clean.csv"
OUT_PATH = "outputs/report/report_data.csv"
COLUMNS = ["quarter", "mean_voucher", "total_cost", "total_enroll"]
VOUCHER_COLUMNS = COLUMNS[1:]
POP_COLUMNS = ["pop_5_19"]


def make_final(clean_path=CLEAN_PATH, pop_path=POP_PATH, out_path=OUT_PATH) -> pd.DataFrame:
    df = pd.read_csv(clean_path, dtype=str, keep_default_na=False)[COLUMNS]
    df = df[df["quarter"].str.endswith("Q3")].copy()
    df["quarter"] = df["quarter"].str[:4]
    df = df.rename(columns={"quarter": "year"})

    pop = pd.read_csv(pop_path, dtype=str, keep_default_na=False)
    last_year = int(pop["year"].max())
    first_new = 2000 + int(df["year"].iloc[-1][2:]) + 1
    future = pd.DataFrame({"year": [f"FY{y % 100:02d}" for y in range(first_new, last_year + 1)]})
    for col in VOUCHER_COLUMNS:
        future[col] = "N/A"
    df = pd.concat([df, future], ignore_index=True)

    calendar_year = "20" + df["year"].str[2:]
    for col in POP_COLUMNS:
        df[col] = calendar_year.map(dict(zip(pop["year"], pop[col]))).fillna("N/A")
    df.to_csv(out_path, index=False)
    return df


if __name__ == "__main__":
    make_final()
