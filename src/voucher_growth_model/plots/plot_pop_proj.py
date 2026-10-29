import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("data/processed/clean/az_pop_proj_clean.csv")

fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
for ax, col, title, color in [
    (axes[0], "pop_total", "Total population", "#1f5f8b"),
    (axes[1], "pop_5_19", "Population aged 5-19", "#b5532a"),
]:
    ax.plot(df["year"], df[col], marker="o", color=color)
    ax.set_title(title, loc="left")
    ax.set_ylabel("Persons")
    ax.yaxis.set_major_formatter(lambda x, _: f"{x / 1e6:.2f}M")
    ax.grid(axis="y", alpha=0.3)
axes[1].set_xlabel("Year")
axes[1].set_xticks(df["year"][::2])
fig.suptitle("Arizona population projections, 2026-2046 (OEO medium series)")
fig.tight_layout()
os.makedirs("outputs/population", exist_ok=True)
fig.savefig("outputs/population/pop_proj.png", dpi=150)
