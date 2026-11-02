import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_csv("data/processed/clean/voucher_metrics_clean.csv", na_values=["N/A"])
df = df[df["quarter"] >= "FY24Q1"][["quarter", "mean_voucher"]].reset_index(drop=True)
df["q"] = df["quarter"].str[-2:]

x = np.arange(len(df))
y = df["mean_voucher"].to_numpy(dtype=float)
n = len(x)

# Multiplicative model: log(y) = a + b*t + seasonal(quarter), Q1 as reference level.
quarters = ["Q1", "Q2", "Q3", "Q4"]
X = np.column_stack([np.ones(n), x] + [(df["q"] == q).to_numpy(float) for q in quarters[1:]])
beta, *_ = np.linalg.lstsq(X, np.log(y), rcond=None)
resid = np.log(y) - X @ beta
df_resid = n - X.shape[1]
sigma2 = (resid**2).sum() / df_resid
se = np.sqrt(np.diag(sigma2 * np.linalg.inv(X.T @ X)))

# Seasonal factors normalised to geometric mean 1.
s = np.array([0.0, *beta[2:]])
s -= s.mean()
factors = dict(zip(quarters, np.exp(s)))
adj = y / df["q"].map(factors).to_numpy()
fitted = np.exp(X @ beta)

growth = np.exp(beta[1]) - 1
summary = (
    f"Quarterly growth: {growth:.2%} (SE {se[1]:.4f} log pts)\n"
    + "\n".join(f"{q} factor: {f:.4f}" for q, f in factors.items())
    + f"\nResidual SE: {np.sqrt(sigma2):.4f} log pts (df = {df_resid})"
)

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(df["quarter"], y, marker="o", color="#7f8c8d", linestyle="--", label="Raw")
ax.plot(df["quarter"], adj, marker="o", color="#1f5f8b", label="Seasonally adjusted")
ax.plot(df["quarter"], fitted, color="#c0392b", linestyle=":", label="Model fit (trend + seasonal)")
ax.text(
    0.02, 0.97, summary, transform=ax.transAxes, va="top", fontsize=9, family="monospace",
    bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.9},
)
ax.set_title("Mean voucher value, FY24Q1 onwards (seasonally adjusted)")
ax.set_ylabel("Mean voucher value (USD)")
ax.yaxis.set_major_formatter(lambda v, _: f"${v:,.0f}")
ax.tick_params(axis="x", rotation=60)
ax.grid(axis="y", alpha=0.3)
ax.legend(loc="lower right")

fig.tight_layout()
fig.savefig("outputs/mean_voucher/mean_voucher_seasonal_model.png", dpi=150)
print(summary)
print(pd.DataFrame({"quarter": df["quarter"], "raw": y, "adjusted": adj.round(2)}).to_string())
