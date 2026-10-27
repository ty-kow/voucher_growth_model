"""Extract ESA program metrics from an Arizona ESA quarterly report PDF.

Usage: python extract_esa.py "FY21Q2 SBE.pdf"
Requires: pip install pypdf
"""
import re
import sys

NA = "N/A"
NUM = r"\$?([\d,]+(?:\.\d+)?)"


def clean(v):
    return v.replace(",", "") if v else None


def find(text, pattern):
    """Return the first captured group of pattern, or None."""
    m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    return clean(m.group(1)) if m else None


def fmt(v, money=False):
    if v is None:
        return NA
    return f"${float(v):,.2f}" if money else f"{int(float(v)):,}"


def parse(text):
    text = re.sub(r"[ \t]+", " ", text)

    mean_voucher = (
        find(text, r"average annual award amount[^$]*" + NUM)
        or find(text, r"^\s*Average\s+" + NUM)
    )
    total = (
        find(text, r"Total Active ESA Students\s+" + NUM)
        or find(text, r"there are " + NUM + r" (?:active )?students")
        or find(text, r"^\s*Total\s+" + NUM + r"\s*$")
    )

    # Eligibility rows: "<label> <count>" at the start of a line.
    def row_ml(label):
        m = re.search(r"^\s*" + label + r"\s+([\d,]+)\s*$", text, re.IGNORECASE | re.MULTILINE)
        return clean(m.group(1)) if m else None

    dash = r"[—–-]"
    special = row_ml(r"Special Needs") or row_ml(r"K-12" + dash + r"Disability")
    mil_sn = row_ml(r"Military with Special Needs")
    preschool = row_ml(r"Preschool(?:" + dash + r"disability)?")
    universal = row_ml(r"Universal") or row_ml(r"K-12" + dash + r"Universal")
    universal_sn = row_ml(r"Universal (?:w/|with) Special Needs")

    return {
        "Mean Voucher": fmt(mean_voucher, money=True),
        "Cost": NA,  # no separate cost figure is reported
        "Total Enrollment": fmt(total),
        "Universal Count": fmt(universal),
        "Total Disability/Special Needs Count": NA,  # not reported as a separate figure
        "Disability/Special Needs Count": fmt(special),
        "Military with Special Needs Count": fmt(mil_sn),
        "Preschool Count": fmt(preschool),
        "Universal w/ Special Needs Count": fmt(universal_sn),
    }


def main(path):
    from pypdf import PdfReader

    reader = PdfReader(path)
    text = "\n".join(p.extract_text() or "" for p in reader.pages)
    for k, v in parse(text).items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
