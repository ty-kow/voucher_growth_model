import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

all_df = pd.read_csv("data/processed/clean/voucher_metrics_clean.csv", na_values=["N/A"])
all_df = all_df[["quarter", "total_enroll"]].dropna().reset_index(drop=True)
df = all_df[all_df["quarter"] >= "FY24Q1"].reset_index(drop=True)  # fit window
df["q"] = df["quarter"].str[-2:]

x = np.arange(len(df))
y = df["total_enroll"].to_numpy(dtype=float)
n = len(x)

# Same model as plot_enrollment_seasonal_model.py: dummies give seasonal factors,
# then linear OLS of adjusted enrollment on t gives the trend.
quarters = ["Q1", "Q2", "Q3", "Q4"]
X = np.column_stack([np.ones(n), x] + [(df["q"] == q).to_numpy(float) for q in quarters[1:]])
beta, *_ = np.linalg.lstsq(X, np.log(y), rcond=None)
s = np.array([0.0, *beta[2:]])
s -= s.mean()
factors = dict(zip(quarters, np.exp(s)))
adj = y / df["q"].map(factors).to_numpy()
fit = stats.linregress(x, adj)

future = [f"FY{fy}Q{q}" for fy in (27, 28, 29, 30) for q in (1, 2, 3, 4)]
trend_labels = list(df["quarter"]) + future
trend = fit.intercept + fit.slope * np.arange(len(trend_labels))

labels = list(all_df["quarter"]) + future
pos = {q: i for i, q in enumerate(labels)}

fig, ax = plt.subplots(figsize=(13, 6))
ax.plot([pos[q] for q in all_df["quarter"]], all_df["total_enroll"], marker="o", color="#1f5f8b", label="Actual enrollment")
ax.plot([pos[q] for q in trend_labels[:n]], trend[:n], color="#c0392b", label="OLS trend (fit FY24Q1-FY26Q4)")
ax.plot([pos[q] for q in trend_labels[n - 1:]], trend[n - 1:], color="#c0392b", linestyle="--", label="Trend extrapolation to FY30Q4")
ax.axvline(pos["FY24Q1"] - 0.5, color="black", linewidth=0.8, alpha=0.4)
ax.text(
    0.02, 0.97, f"Slope: {fit.slope:,.0f} students/quarter\nFY30Q4 trend: {trend[-1]:,.0f}",
    transform=ax.transAxes, va="top", fontsize=9, family="monospace",
    bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.9},
)
ax.set_xticks(range(len(labels)), labels)
ax.set_title("Total ESA enrollment with seasonally adjusted OLS trend (fit FY24Q1 onwards)")
ax.set_ylabel("Total enrollment (students)")
ax.yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
ax.tick_params(axis="x", rotation=70)
ax.grid(axis="y", alpha=0.3)
ax.legend(loc="lower right")
fig.tight_layout()
fig.savefig("outputs/naive_forecast/enrollment_trend_forecast.png", dpi=150)

print(pd.DataFrame({"quarter": future, "trend": trend[n:].round(0)}).to_string(index=False))
