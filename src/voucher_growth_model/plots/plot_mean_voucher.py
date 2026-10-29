import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("data/processed/clean/voucher_metrics_clean.csv", na_values=["N/A"])
df = df[["quarter", "mean_voucher"]]

fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(df["quarter"], df["mean_voucher"], marker="o", color="#1f5f8b")
ax.axvline("FY22Q4", color="grey", linestyle="--", linewidth=1)
ax.text(
    "FY23Q1", df["mean_voucher"].max(), " Universal expansion\n (FY23Q1 drop)",
    va="top", fontsize=9, color="grey",
)
ax.set_title("Arizona ESA mean voucher value by quarter")
ax.set_ylabel("Mean voucher value (USD)")
ax.yaxis.set_major_formatter(lambda x, _: f"${x:,.0f}")
ax.set_ylim(bottom=0)
ax.tick_params(axis="x", rotation=60)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig("outputs/mean_voucher/mean_voucher.png", dpi=150)
