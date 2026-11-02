"""Line graph of ESA enrollment by grade, per quarter."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

GRADE_COLS = ["kinder"] + [f"grade_{n}" for n in range(1, 13)]


def plot_grades(csv_path: Path, out_path: Path, q3_from_fy23: bool = False) -> None:
    df = pd.read_csv(csv_path, na_values=["N/A"])
    if q3_from_fy23:
        df = df[df["quarter"].str.endswith("Q3") & (df["quarter"] >= "FY23Q3")]
    fig, ax = plt.subplots(figsize=(12, 6))
    cmap = plt.get_cmap("turbo", len(GRADE_COLS))
    for i, col in enumerate(GRADE_COLS):
        label = "K" if col == "kinder" else col.replace("grade_", "Grade ")
        ax.plot(df["quarter"], df[col], marker="o", markersize=3, color=cmap(i), label=label)
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Students enrolled (by grade)")
    ax.set_title("Arizona ESA enrollment by grade")
    ax.tick_params(axis="x", rotation=60)
    ax.grid(alpha=0.3)
    ax.set_ylim(bottom=0)
    ax2 = ax.twinx()
    (total,) = ax2.plot(
        df["quarter"], df["total_enroll"], color="black", linewidth=2.5, linestyle="--", label="Total"
    )
    ax2.set_ylabel("Total students enrolled")
    ax2.set_ylim(bottom=0)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles + [total], labels + ["Total (right axis)"],
        ncol=2, fontsize=8, loc="center left", bbox_to_anchor=(1.1, 0.5),
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)


if __name__ == "__main__":
    plot_grades(Path(sys.argv[1]), Path(sys.argv[2]), q3_from_fy23="--q3" in sys.argv)
