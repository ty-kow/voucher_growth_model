import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_csv("data/processed/clean/voucher_metrics_clean.csv", na_values=["N/A"])
df = df[["quarter", "mean_voucher"]]
df = df[df["quarter"] >= "FY23Q1"]

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["quarter"], df["mean_voucher"], marker="o", color="#1f5f8b")
trend = df[df["quarter"] >= "FY24Q1"]
x = [df["quarter"].tolist().index(q) for q in trend["quarter"]]
slope, intercept = np.polyfit(x, trend["mean_voucher"], 1)
ax.plot(
    trend["quarter"], [slope * i + intercept for i in x],
    linestyle="--", color="#c0392b", label=f"Linear trend, FY24Q1 onwards (${slope:,.0f}/quarter)",
)
ax.legend(loc="upper right")
ax.set_title("Arizona ESA mean voucher value by quarter, FY23Q1 onwards")
ax.set_ylabel("Mean voucher value (USD)")
ax.yaxis.set_major_formatter(lambda x, _: f"${x:,.0f}")
ax.set_ylim(9000, 11500)
ax.tick_params(axis="x", rotation=60)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig("outputs/mean_voucher/mean_voucher_fy23.png", dpi=150)
