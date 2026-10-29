import pandas as pd

from voucher_growth_model.data_cleaning.clean_population_proj import clean


def test_pop_5_19_is_sum_of_age_groups(tmp_path):
    raw = tmp_path / "raw.csv"
    pd.DataFrame(
        {"year": [2026], "pop_total": [100.0], "pop_5_9": [1.0],
         "pop_10_14": [2.0], "pop_15_19": [4.0]}
    ).to_csv(raw, index=False)
    out = clean(raw, tmp_path / "clean.csv")
    assert out["pop_5_19"].tolist() == [7.0]
    assert pd.read_csv(tmp_path / "clean.csv")["pop_5_19"].tolist() == [7.0]
