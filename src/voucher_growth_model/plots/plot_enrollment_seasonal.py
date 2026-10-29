import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_csv("data/processed/clean/voucher_metrics_clean.csv", na_values=["N/A"])
df = df[df["quarter"] >= "FY24Q1"][["quarter", "total_enroll"]].reset_index(drop=True)
df["q"] = df["quarter"].str[-2:]

x = np.arange(len(df))
y = df["total_enroll"].to_numpy(dtype=float)

# Trend from Q1-Q3 (assumed non-seasonal), then Q4 factor = mean actual/trend.
base = df["q"].isin(["Q1", "Q2", "Q3"]).to_numpy()
slope, intercept = np.polyfit(x[base], y[base], 1)
trend = slope * x + intercept
ratio = y / trend
factors = {q: ratio[(df["q"] == q).to_numpy()].mean() for q in ("Q4",)}

adj = y.copy()
for q, f in factors.items():
    m = (df["q"] == q).to_numpy()
    adj[m] = y[m] / f

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(df["quarter"], y, marker="o", color="#7f8c8d", linestyle="--", label="Raw")
ax.plot(df["quarter"], adj, marker="o", color="#1f5f8b", label="Seasonally adjusted (Q4)")
m = (df["q"] == "Q4").to_numpy()
ax.scatter(df["quarter"][m], adj[m], s=70, facecolors="none", edgecolors="#c0392b",
           zorder=3, label="Adjusted quarters")
ax.text(
    0.02, 0.97,
    f"Q4 factor: {factors['Q4']:.3f}\n"
    f"Trend: Q1-Q3 OLS, {slope:,.0f}/quarter",
    transform=ax.transAxes, va="top", fontsize=9, family="monospace",
    bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.9},
)
ax.set_title("Total ESA enrollment, FY24Q1 onwards (Q4 seasonally adjusted)")
ax.set_ylabel("Total enrollment (students)")
ax.yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
ax.tick_params(axis="x", rotation=60)
ax.grid(axis="y", alpha=0.3)
ax.legend(loc="lower right")

fig.tight_layout()
fig.savefig("outputs/enrollment/enrollment_seasonal.png", dpi=150)
print(factors)
print(pd.DataFrame({"quarter": df["quarter"], "raw": y, "adjusted": adj.round(0)}).to_string())
