from pathlib import Path

from voucher_growth_model.data_cleaning.clean_esa import clean, clean_row

COLS = ["quarter", "mean_voucher", "total_cost", "total_enroll", "total_universal",
        "total_sn", "total_k12_sn", "total_mil_sn", "total_pre", "total_universal_sn"]


def row(**kw):
    r = dict.fromkeys(COLS, "")
    r.update(kw)
    return r


def test_cost_filled_from_mean_and_enrollment():
    r = clean_row(row(quarter="FY21Q4", mean_voucher="14543.0", total_enroll="9669"))
    assert r["total_cost"] == "140616267.00"


def test_mean_filled_from_cost():
    r = clean_row(row(quarter="FY25Q1", total_cost="795296542.0", total_enroll="79593"))
    assert r["mean_voucher"] == "9992.04"


def test_reported_values_untouched():
    r = clean_row(row(quarter="FY24Q2", mean_voucher="9769.0", total_cost="698626997.0",
                      total_enroll="71520"))
    assert r["total_cost"] == "698626997.0"


def test_universal_zero_only_before_fy23q1():
    assert clean_row(row(quarter="FY22Q4"))["total_universal"] == "0"
    assert clean_row(row(quarter="FY23Q4"))["total_universal"] == "N/A"


def test_sn_k12_derivations():
    assert clean_row(row(quarter="FY21Q2", total_sn="5707", total_pre="278"))["total_k12_sn"] == "5429"
    assert clean_row(row(quarter="FY23Q4", total_k12_sn="10409", total_pre="771"))["total_sn"] == "11180"


def test_missing_inputs_not_imputed():
    r = clean_row(row(quarter="FY25Q1", total_enroll="79593"))
    assert r["mean_voucher"] == r["total_cost"] == r["total_k12_sn"] == "N/A"


def test_matches_committed_clean_csv(tmp_path):
    root = Path(__file__).resolve().parents[1] / "data" / "processed"
    out = tmp_path / "clean.csv"
    clean(root / "raw" / "voucher_metrics_raw.csv", out)
    assert out.read_bytes() == (root / "clean" / "voucher_metrics_clean.csv").read_bytes()
