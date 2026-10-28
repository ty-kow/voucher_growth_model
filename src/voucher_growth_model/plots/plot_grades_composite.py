"""Composite (stacked) line graph of ESA enrollment by grade: grade lines stack to the grade-sum aggregate."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

GRADE_COLS = ["kinder"] + [f"grade_{n}" for n in range(1, 13)]


def plot_grades_composite(csv_path: Path, out_path: Path) -> None:
    df = pd.read_csv(csv_path, na_values=["N/A"])
    # Quarters with any blank grade are dropped: a partial stack would misstate the aggregate.
    df = df.dropna(subset=GRADE_COLS)
    cum = df[GRADE_COLS].cumsum(axis=1)
    x = range(len(df))
    fig, ax = plt.subplots(figsize=(12, 6))
    cmap = plt.get_cmap("turbo", len(GRADE_COLS))
    lower = pd.Series(0.0, index=df.index)
    for i, col in enumerate(GRADE_COLS):
        label = "K" if col == "kinder" else col.replace("grade_", "Grade ")
        ax.fill_between(x, lower, cum[col], color=cmap(i), alpha=0.35, linewidth=0)
        ax.plot(x, cum[col], color=cmap(i), linewidth=1.2, label=label)
        lower = cum[col]
    ax.plot(x, cum[GRADE_COLS[-1]], color="black", linewidth=2.5, label="Sum of grades")
    ax.plot(x, df["total_enroll"], color="black", linewidth=1.5, linestyle="--", label="Reported total")
    ax.set_xticks(list(x))
    ax.set_xticklabels(df["quarter"], rotation=60)
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Students enrolled (cumulative across grades)")
    ax.set_title("Arizona ESA enrollment by grade (stacked to aggregate)")
    ax.grid(alpha=0.3)
    ax.set_ylim(bottom=0)
    ax.legend(ncol=2, fontsize=8, loc="center left", bbox_to_anchor=(1.01, 0.5))
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)


if __name__ == "__main__":
    plot_grades_composite(Path(sys.argv[1]), Path(sys.argv[2]))
