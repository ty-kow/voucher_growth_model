from pathlib import Path

from voucher_growth_model.data_cleaning.extract_population_real import extract

ROOT = Path(__file__).resolve().parents[1]


def test_matches_committed_extracted_csv():
    paths = sorted((ROOT / "data" / "raw" / "population").glob("20* - 5 year*.xlsx"))
    out = extract(paths)
    committed = (ROOT / "data" / "processed" / "extracted" / "az_pop_real_extracted.csv").read_text()
    assert out.to_csv(index=False, lineterminator="\n") == committed.replace("\r\n", "\n")
