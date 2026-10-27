"""Clean extractor output: raw CSV to clean CSV, following decisions.md.

Steps 1, 2, 4 and 5 are user-instructed imputations that override the project
no-imputation rule. Reported values are never overwritten.
"""
import csv
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

RENAME = {
    "Quarter": "quarter",
    "Mean Voucher": "mean_voucher",
    "Total Cost": "total_cost",
    "Total Enrollment": "total_enroll",
    "Universal Count": "total_universal",
    "Total Disability/SN Count": "total_sn",
    "K-12 Disability/SN Count": "total_k12_sn",
    "Military with Disability/SN Count": "total_mil_sn",
    "Preschool Count": "total_pre",
    "Universal w/ Disability/SN Count": "total_universal_sn",
}
UNIVERSAL_START = "FY23Q1"
NA = "N/A"


def _num(v):
    v = (v or "").strip()
    return Decimal(v) if v and v != NA else None


def _fmt2(d):
    return str(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _blank(row, col):
    return not row[col].strip()


def clean_row(row):
    """Return a cleaned copy of one renamed row. Order of steps matters."""
    r = dict(row)
    cost, mean, enroll = _num(r["total_cost"]), _num(r["mean_voucher"]), _num(r["total_enroll"])

    # 1. total_cost = total_enroll * mean_voucher
    if cost is None and mean is not None and enroll is not None:
        r["total_cost"] = _fmt2(enroll * mean)
        cost = _num(r["total_cost"])
    # 2. mean_voucher = total_cost / total_enroll
    if mean is None and cost is not None and enroll:
        r["mean_voucher"] = _fmt2(cost / enroll)

    # 3. structural zeros: universal program began FY23Q1 (FYxxQn sorts lexically)
    if r["quarter"] < UNIVERSAL_START:
        for col in ("total_universal", "total_universal_sn"):
            if _blank(r, col):
                r[col] = "0"

    sn, k12, pre = _num(r["total_sn"]), _num(r["total_k12_sn"]), _num(r["total_pre"])
    # 4. total_k12_sn = total_sn - total_pre
    if k12 is None and sn is not None and pre is not None:
        r["total_k12_sn"] = str(int(sn - pre))
        k12 = _num(r["total_k12_sn"])
    # 5. total_sn = total_k12_sn + total_pre
    if sn is None and k12 is not None and pre is not None:
        r["total_sn"] = str(int(k12 + pre))

    # 6. remaining blanks
    return {k: (v if v.strip() else NA) for k, v in r.items()}


def clean(raw_path, clean_path):
    with open(raw_path, newline="", encoding="utf-8-sig") as f:
        rows = [{RENAME.get(k, k): v for k, v in row.items()} for row in csv.DictReader(f)]
    out = [clean_row(r) for r in rows]
    # BOM matches the committed file (Excel-friendly)
    with open(clean_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(out)
    return out


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python -m voucher_growth_model.clean_esa RAW_CSV CLEAN_CSV")
    clean(Path(sys.argv[1]), Path(sys.argv[2]))
