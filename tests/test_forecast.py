import math

import numpy as np
import pytest

from voucher_growth_model.checks import holdout, pop_sensitivity
from voucher_growth_model.forecast import forecast, takeup_path


def report_data(tmp_path, pop_5_19):
    """report_data.csv fixture: FY23-FY26 actuals, FY27-FY46 voucher values N/A."""
    actual = {2023: (8000, 50000), 2024: (9000, 70000), 2025: (9500, 88000), 2026: (10000, 100000)}
    rows = "".join(
        f"FY{y % 100:02d},{actual[y][0] if y in actual else 'N/A'},N/A,"
        f"{actual[y][1] if y in actual else 'N/A'},{pop_5_19}\n"
        for y in range(2023, 2047)
    )
    path = tmp_path / "report_data.csv"
    path.write_text("year,mean_voucher,total_cost,total_enroll,pop_5_19\n" + rows)
    return path

def test_takeup_path_anchored_and_bounded():
    assert takeup_path(0.0132, 0.05, 0.3, 0) == pytest.approx(0.0132)
    assert 0.0132 < takeup_path(0.0132, 0.05, 0.3, 5) < 0.05
    assert takeup_path(0.0132, 0.05, 0.3, 200) == pytest.approx(0.05)


def test_forecast_grid(tmp_path):
    v = report_data(tmp_path, pop_5_19=1_600_000)
    df = forecast(v, tmp_path / "out.csv")
    # Take-up 3.125%, 4.375%, 5.5%, 6.25% for FY23-FY26; r is the slope of log take-up on year
    r = np.polyfit([0, 1, 2, 3], np.log([50000, 70000, 88000, 100000]), 1)[0]
    assert r != pytest.approx(math.log(2) / 3)  # not the FY23-FY26 endpoint rate
    assert len(df) == 21 * 4 * 2
    assert set(df.takeup_scenario) == {"k9.9", "k20", "k30", "k40"}
    assert (df.pop_base == "5_19").all()
    assert (df["pop"] == 1_600_000).all()
    base = df[(df.fy == "FY26") & (df.voucher_scenario == "infl2")]
    assert base.enroll.tolist() == pytest.approx([100000] * 4)
    assert base.mean_voucher.tolist() == pytest.approx([10000] * 4)
    assert base.cost_nominal.tolist() == pytest.approx(base.cost_real_fy26.tolist())
    row = df[(df.fy == "FY27") & (df.voucher_scenario == "infl2") & (df.takeup_scenario == "k20")].iloc[0]
    assert row.enroll == pytest.approx(1_600_000 * takeup_path(0.0625, 0.20, r, 1))
    assert row.mean_voucher == pytest.approx(10200)
    assert row.cost_nominal == pytest.approx(row.enroll * 10200)
    assert row.cost_real_fy26 == pytest.approx(row.cost_nominal / 1.02)
    assert df.r.tolist() == pytest.approx([r] * len(df))
    fy27 = df[(df.fy == "FY27") & (df.voucher_scenario == "infl2")].takeup
    assert fy27.is_monotonic_increasing and fy27.nunique() == 4
    hist = df[(df.fy == "FY27") & (df.voucher_scenario == "hist")].mean_voucher.iloc[0]
    assert hist == pytest.approx(10000 * (10000 / 9000) ** 0.5)


def test_holdout_fits_fy23_fy25(tmp_path):
    v = report_data(tmp_path, pop_5_19=1_600_000)
    df = holdout(v, tmp_path / "holdout.csv")
    r = np.polyfit([0, 1, 2], np.log([50000, 70000, 88000]), 1)[0]
    assert df.r_fit.tolist() == pytest.approx([r] * 4)
    k20 = df[df.takeup_scenario == "k20"].iloc[0]
    assert k20.pred_enroll == pytest.approx(1_600_000 * takeup_path(0.055, 0.20, r, 1))
    assert k20.error_pct == pytest.approx((k20.pred_enroll / 100000 - 1) * 100)


def test_pop_sensitivity_scales_projection(tmp_path):
    v = report_data(tmp_path, pop_5_19=1_600_000)
    text = v.read_text().replace("FY26,10000,N/A,100000,1600000", "FY26,10000,N/A,100000,1500000")
    v.write_text(text)
    df = pop_sensitivity(v, tmp_path / "sens.csv")
    # FY26 population (and every year after) scaled by 1.6M / 1.5M
    assert df[df.fy == "FY26"]["pop"].iloc[0] == pytest.approx(1_600_000)
    assert df[df.fy == "FY27"]["pop"].iloc[0] == pytest.approx(1_600_000 * 1.6 / 1.5)
    assert df[df.fy == "FY26"].enroll.tolist() == pytest.approx([100000] * 8)
