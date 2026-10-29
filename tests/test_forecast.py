import math

import pytest

from voucher_growth_model.forecast import forecast, takeup_path


def test_takeup_path_anchored_and_bounded():
    assert takeup_path(0.0132, 0.05, 0.3, 0) == pytest.approx(0.0132)
    assert 0.0132 < takeup_path(0.0132, 0.05, 0.3, 5) < 0.05
    assert takeup_path(0.0132, 0.05, 0.3, 200) == pytest.approx(0.05)


def test_forecast_grid(tmp_path):
    v = tmp_path / "v.csv"
    v.write_text(
        "quarter,mean_voucher,total_enroll\n"
        "FY23Q3,8000,50000\nFY24Q3,9000,70000\nFY25Q3,9500,88000\nFY26Q3,10000,100000\nFY26Q4,11000,105000\n"
    )
    p = tmp_path / "p.csv"
    p.write_text("year,pop_total\n" + "".join(f"{y},{8_000_000}\n" for y in range(2023, 2047)))
    df = forecast(v, p, tmp_path / "out.csv")
    r = math.log(2) / 3  # take-up doubles FY23-FY26 (0.625% to 1.25%)
    assert len(df) == 21 * 4 * 2
    base = df[(df.fy == "FY26") & (df.voucher_scenario == "infl2")]
    assert base.enroll.tolist() == pytest.approx([100000] * 4)
    assert base.mean_voucher.tolist() == pytest.approx([10000] * 4)
    assert base.cost_nominal.tolist() == pytest.approx(base.cost_real_fy26.tolist())
    row = df[(df.fy == "FY27") & (df.voucher_scenario == "infl2") & (df.takeup_scenario == "k5")].iloc[0]
    assert row.enroll == pytest.approx(8_000_000 * takeup_path(0.0125, 0.05, r, 1))
    assert row.mean_voucher == pytest.approx(10200)
    assert row.cost_nominal == pytest.approx(row.enroll * 10200)
    assert row.cost_real_fy26 == pytest.approx(row.cost_nominal / 1.02)
    assert df.r.tolist() == pytest.approx([r] * len(df))
    fy27 = df[(df.fy == "FY27") & (df.voucher_scenario == "infl2")].takeup
    assert fy27.is_monotonic_increasing and fy27.nunique() == 4
    assert (df.pop_base == "total").all()
    hist = df[(df.fy == "FY27") & (df.voucher_scenario == "hist")].mean_voucher.iloc[0]
    assert hist == pytest.approx(10000 * (10000 / 9000) ** 0.5)


def test_forecast_5_19_base(tmp_path):
    v = tmp_path / "v.csv"
    v.write_text(
        "quarter,mean_voucher,total_enroll\n"
        "FY23Q3,8000,50000\nFY24Q3,9000,70000\nFY25Q3,9500,88000\nFY26Q3,10000,100000\n"
    )
    p = tmp_path / "p.csv"
    p.write_text("year,pop_total,pop_5_19\n" + "".join(f"{y},8000000,1400000\n" for y in range(2023, 2047)))
    r = math.log(2) / 3
    df = forecast(v, p, tmp_path / "out.csv", base="5_19")
    assert set(df.takeup_scenario) == {"k9.9", "k20", "k30", "k40"}
    assert (df["pop"] == 1400000).all()
    row = df[(df.fy == "FY27") & (df.takeup_scenario == "k20")].iloc[0]
    assert row.enroll == pytest.approx(1_400_000 * takeup_path(100000 / 1_400_000, 0.20, r, 1))
    assert df.r.tolist() == pytest.approx([r] * len(df))
