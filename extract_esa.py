"""Extract ESA program metrics from an Arizona ESA quarterly report PDF.

Usage: python extract_esa.py "FY21Q2 SBE.pdf"
       python extract_esa.py "Voucher Reports" output.csv   (one row per quarter)
Requires: pip install pypdf
"""
import os
import re
import sys

NA = "N/A"
NUM = r"\$?\s*([\d,]+(?:\.\d+)?)"


def clean(v):
    return v.replace(",", "") if v else None


def find(text, pattern):
    """Return the first captured group of pattern, or None."""
    m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    return clean(m.group(1)) if m else None


def fmt(v, money=False):
    """Return a raw number (float for money, int for counts), or None if missing."""
    if v is None:
        return None
    return round(float(v), 2) if money else int(float(v))


def appendix_mean(text):
    """Student-weighted mean of the "Exact Award Amounts" appendix table, or None."""
    i = text.find("Exact Award Amounts for all")
    if i < 0:
        return None
    rows = re.findall(r"^\s*\$\s*([\d,]+\.\d+)\s+([\d,]+)\s*$", text[i:], re.MULTILINE)
    n = sum(int(c.replace(",", "")) for _, c in rows)
    if not n:
        return None
    return str(sum(float(a.replace(",", "")) * int(c.replace(",", "")) for a, c in rows) / n)


def is_legacy(label):
    """True for quarters FY21Q2 through FY23Q3 (label like "FY23Q3")."""
    m = re.search(r"FY(\d\d)Q(\d)", label or "")
    return bool(m) and (int(m.group(1)), int(m.group(2))) <= (23, 3)


def parse(text, legacy_sn=False):
    text = re.sub(r"[ \t]+", " ", text)

    mean_voucher = (
        find(text, r"average\s+annual\s+award\s+amount[^$]*" + NUM)
        or find(text, r"^\s*Average:?\s+" + NUM)
        or appendix_mean(text)
    )
    # FY25+ reports: annualized scholarship total in the key points, and total
    # students directly after the "K-12 universal" row of Table 1.
    cost = find(text, r"annualized\s+basis,?\s+is\s+" + NUM)
    total_sn = find(text, r"of\s+the\s+" + NUM + r"\s+ESA\s+students\s+with\s+a\s+disability")
    total = (
        find(text, r"K-12\W+universal\s+[\d,]+\s*\n\s*Total\s+" + NUM + r"\s*$")
        # Narrative sentence first: some reports add an "Exited" column after the active count.
        or find(text, r"there\s+(?:are|were)\s+" + NUM + r"\s+(?:active\s+)?students")
        or find(text, r"Total Active ESA Students(?: [\d,]+)*? " + NUM + r"[ \t]*$")
        or find(text, r"^\s*Total(?: [\d,]+)*? " + NUM + r"\s*$")
    )

    # Eligibility rows: "<label> <count>" at the start of a line.
    def row_ml(label):
        # Multi-quarter tables list several columns; the last is the current quarter.
        # "Active Students Exited Students" tables put the active count first, exited last.
        if re.search(r"Active Students Exited Students", text):
            m = re.search(r"^\s*" + label + r" ([\d,]+) [\d,]+\s*$", text, re.IGNORECASE | re.MULTILINE)
        else:
            m = re.search(r"^\s*" + label + r"(?: [\d,]+)*? ([\d,]+)\s*$", text, re.IGNORECASE | re.MULTILINE)
        return clean(m.group(1)) if m else None

    dash = r"\s*[—–-]?\s*"
    special = row_ml(r"Special Needs") or row_ml(r"Disabilities") or row_ml(r"K-12" + dash + r"Disability")
    mil_sn = row_ml(r"Military with (?:Special Needs|Disabilities)")
    preschool = row_ml(r"Preschool(?:" + dash + r"disability)?")
    universal = row_ml(r"Universal") or row_ml(r"K-12" + dash + r"Universal")
    universal_sn = row_ml(r"Universal (?:w/|with) (?:Special Needs|Disabilities)")

    if legacy_sn:
        # FY21Q2-FY23Q3 reports list a single disability row covering all students.
        total_sn, special = special, None

    return {
        "Mean Voucher": fmt(mean_voucher, money=True),
        "Total Cost": fmt(cost, money=True),
        "Total Enrollment": fmt(total),
        "Universal Count": fmt(universal),
        "Total Disability/SN Count": fmt(total_sn),
        "K-12 Disability/SN Count": fmt(special),
        "Military with Disability/SN Count": fmt(mil_sn),
        "Preschool Count": fmt(preschool),
        "Universal w/ Disability/SN Count": fmt(universal_sn),
    }


def read_text(path):
    from pypdf import PdfReader

    return "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)


def main(path):
    for k, v in parse(read_text(path), is_legacy(os.path.basename(path))).items():
        print(f"{k}: {NA if v is None else v}")


def main_folder(folder, out_csv):
    """Write one CSV row per quarter for every PDF in folder; missing values are blank."""
    import csv
    import glob

    def quarter(p):
        m = re.search(r"FY(\d\d)Q(\d)", os.path.basename(p))
        return (int(m.group(1)), int(m.group(2)), m.group(0)) if m else (99, 9, p)

    rows = []
    for p in sorted(glob.glob(os.path.join(folder, "*.pdf")), key=quarter):
        q = quarter(p)[2]
        rows.append({"Quarter": q, **parse(read_text(p), is_legacy(q))})
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: "" if v is None else v for k, v in r.items()})
    print(f"Wrote {len(rows)} rows to {out_csv}")


if __name__ == "__main__":
    if len(sys.argv) == 3 and os.path.isdir(sys.argv[1]):
        main_folder(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        sys.exit(__doc__)
