from pathlib import Path

import pandas as pd

from voucher_growth_model.data_cleaning.clean_population_real import clean


def test_pivot_sum_and_ratio(tmp_path):
    raw = tmp_path / "raw.csv"
    pd.DataFrame(
        {
            "year": [2023] * 4,
            "age_group": ["5-9", "10-14", "15-19", "total_pop"],
            "population": [10, 20, 30, 600],
        }
    ).to_csv(raw, index=False)
    out = clean(raw, tmp_path / "clean.csv")
    assert out.columns.tolist() == [
        "year", "5-9", "10-14", "15-19", "5-19", "total_pop", "school_aged_ratio",
    ]
    assert out.loc[0, "5-19"] == 60
    assert out.loc[0, "school_aged_ratio"] == 0.1


def test_matches_committed_clean_csv(tmp_path):
    root = Path(__file__).resolve().parents[1] / "data" / "processed"
    out = tmp_path / "clean.csv"
    clean(root / "extracted" / "az_pop_real_extracted.csv", out)
    pd.testing.assert_frame_equal(
        pd.read_csv(out), pd.read_csv(root / "clean" / "az_pop_real_clean.csv")
    )
