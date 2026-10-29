import pandas as pd

from voucher_growth_model.merge_population import merge


def test_merge_real_then_proj(tmp_path):
    real = tmp_path / "real.csv"
    proj = tmp_path / "proj.csv"
    real.write_text("year,5-9,10-14,15-19,5-19,total_pop,school_aged_ratio\n2025,1,2,3,6,100,0.06\n")
    proj.write_text(
        "year,pop_total,pop_5_9,pop_10_14,pop_15_19,pop_5_19\n"
        "2025,999,1,1,1,3\n2026,110,1,2,3,6.5\n"
    )
    out = tmp_path / "out.csv"
    df = merge(real, proj, out)
    assert list(df.columns) == ["year", "pop_total", "pop_5_19", "source"]
    assert df["year"].tolist() == [2025, 2026]
    assert df["source"].tolist() == ["real", "proj"]
    assert df["pop_total"].tolist() == [100, 110]
    assert pd.read_csv(out).equals(df)
