"""Line graph of ESA enrollment per cohort (kinder-entry year), by fiscal year.

Uses the Q3 snapshot of each fiscal year from FY23, so each cohort advances one grade per year.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

GRADE_COLS = ["kinder"] + [f"grade_{n}" for n in range(1, 13)]
START_FY = 23


def plot_cohorts(csv_path: Path, out_path: Path) -> None:
    df = pd.read_csv(csv_path, na_values=["N/A"])
    df = df[df["quarter"].str.endswith("Q3")].copy()
    df["fy"] = df["quarter"].str[2:4].astype(int)
    df = df[df["fy"] >= START_FY]

    # cohort id = fiscal year the cohort is/was in kinder
    cohorts: dict[int, dict[int, float]] = {}
    for _, row in df.iterrows():
        for grade, col in enumerate(GRADE_COLS):
            if pd.notna(row[col]):
                cohorts.setdefault(row["fy"] - grade, {})[row["fy"]] = row[col]

    fig, ax = plt.subplots(figsize=(12, 6))
    cmap = plt.get_cmap("viridis", len(cohorts))
    for i, cohort in enumerate(sorted(cohorts)):
        pts = sorted(cohorts[cohort].items())
        ax.plot(
            [fy for fy, _ in pts], [v for _, v in pts],
            marker="o", markersize=4, color=cmap(i), label=f"12 in FY{cohort + 12:02d}",
        )
    fys = sorted(df["fy"])
    ax.set_xticks(fys, [f"FY{fy:02d}" for fy in fys])
    ax.set_xlabel("Fiscal year (Q3)")
    ax.set_ylabel("Students enrolled")
    ax.set_title("Arizona ESA enrollment by cohort (grade 12 fiscal year)")
    ax.grid(alpha=0.3)
    ax.set_ylim(bottom=0)
    ax.legend(ncol=2, fontsize=8, loc="center left", bbox_to_anchor=(1.01, 0.5))
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)


if __name__ == "__main__":
    plot_cohorts(Path(sys.argv[1]), Path(sys.argv[2]))
