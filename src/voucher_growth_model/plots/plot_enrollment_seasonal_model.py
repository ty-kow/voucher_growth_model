import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv("data/processed/clean/voucher_metrics_clean.csv", na_values=["N/A"])
df = df[df["quarter"] >= "FY24Q1"][["quarter", "total_enroll"]].reset_index(drop=True)
df["q"] = df["quarter"].str[-2:]

x = np.arange(len(df))
y = df["total_enroll"].to_numpy(dtype=float)
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

# Trend: linear OLS of seasonally adjusted enrollment on t.
fit = stats.linregress(x, adj)
fitted = fit.intercept + fit.slope * x
sigma_adj = np.sqrt(((adj - fitted) ** 2).sum() / (n - 2))
t_crit = stats.t.ppf(0.975, n - 2)
se_fit = sigma_adj * np.sqrt(1 / n + (x - x.mean()) ** 2 / ((x - x.mean()) ** 2).sum())
band = t_crit * se_fit
ci = (fit.slope - t_crit * fit.stderr, fit.slope + t_crit * fit.stderr)
summary = (
    f"Slope: {fit.slope:,.0f} students/quarter (SE {fit.stderr:,.0f})\n"
    f"Slope 95% CI: {ci[0]:,.0f} to {ci[1]:,.0f}\n"
    + "\n".join(f"{q} factor: {f:.3f}" for q, f in factors.items())
    + f"\nResidual SE: {sigma_adj:,.0f} students (df = {n - 2})"
)

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(df["quarter"], y, marker="o", color="#7f8c8d", linestyle="--", label="Raw")
ax.plot(df["quarter"], adj, marker="o", color="#1f5f8b", label="Seasonally adjusted (all quarters)")
ax.fill_between(df["quarter"], fitted - band, fitted + band, color="#c0392b", alpha=0.15, label="95% CI of trend")
ax.plot(df["quarter"], fitted,color="#c0392b", linestyle=":", label="OLS trend (fit to adjusted)")
ax.text(
    0.02, 0.97, summary, transform=ax.transAxes, va="top", fontsize=9, family="monospace",
    bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.9},
)
ax.set_title("Total ESA enrollment, FY24Q1 onwards (all quarters seasonally adjusted)")
ax.set_ylabel("Total enrollment (students)")
ax.yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
ax.tick_params(axis="x", rotation=60)
ax.grid(axis="y", alpha=0.3)
ax.legend(loc="lower right")

fig.tight_layout()
fig.savefig("outputs/enrollment/enrollment_seasonal_model.png", dpi=150)
print(summary)
print(pd.DataFrame({"quarter": df["quarter"], "raw": y, "adjusted": adj.round(0)}).to_string())
