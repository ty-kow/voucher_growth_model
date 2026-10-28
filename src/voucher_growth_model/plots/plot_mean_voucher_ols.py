import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv("data/processed/voucher_metrics_clean.csv", na_values=["N/A"])
df = df[df["quarter"] >= "FY24Q1"][["quarter", "mean_voucher"]].reset_index(drop=True)

x = np.arange(len(df))
y = df["mean_voucher"].to_numpy()
n = len(x)
fit = stats.linregress(x, y)
slope, intercept, se_slope = fit.slope, fit.intercept, fit.stderr
fitted = slope * x + intercept
resid = y - fitted

r2 = fit.rvalue**2
sigma = np.sqrt((resid**2).sum() / (n - 2))
t_stat = slope / se_slope
t_crit = stats.t.ppf(0.975, n - 2)
ci = (slope - t_crit * se_slope, slope + t_crit * se_slope)
se_fit = sigma * np.sqrt(1 / n + (x - x.mean()) ** 2 / ((x - x.mean()) ** 2).sum())
band = t_crit * se_fit

summary = (
    f"n = {n} quarters (FY24Q1-FY26Q4)\n"
    f"Slope: \\${slope:,.2f}/quarter\n"
    f"95% CI: \\${ci[0]:,.2f} to \\${ci[1]:,.2f}\n"
    f"Std. error: \\${se_slope:,.2f}\n"
    f"t-statistic: {t_stat:.2f} (df = {n - 2})\n"
    f"p-value: {fit.pvalue:.1e}\n"
    f"Intercept (FY24Q1): \\${intercept:,.2f}\n"
    f"R$^2$: {r2:.3f}\n"
    f"Residual std. error: \\${sigma:,.2f}"
)

fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(10, 8), sharex=True, gridspec_kw={"height_ratios": [3, 1.5]}
)
ax1.plot(df["quarter"], y, marker="o", color="#1f5f8b", label="Mean voucher value")
ax1.fill_between(
    df["quarter"], fitted - band, fitted + band, color="#c0392b", alpha=0.15,
    label="95% CI of fit",
)
ax1.plot(df["quarter"], fitted, linestyle="--", color="#c0392b", label="OLS fit")
ax1.text(
    0.02, 0.97, summary, transform=ax1.transAxes, va="top", fontsize=9,
    family="monospace", bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.9},
)
ax1.set_title("Least-squares trend in mean voucher value, FY24Q1 onwards")
ax1.set_ylabel("Mean voucher value (USD)")
ax1.yaxis.set_major_formatter(lambda v, _: f"${v:,.0f}")
ax1.legend(loc="lower right")
ax1.grid(axis="y", alpha=0.3)

ax2.bar(df["quarter"], resid, color="#7f8c8d")
ax2.axhline(0, color="black", linewidth=0.8)
ax2.set_ylabel("Residual (USD)")
ax2.set_title("Residuals", fontsize=10)
ax2.tick_params(axis="x", rotation=60)
ax2.grid(axis="y", alpha=0.3)

fig.tight_layout()
fig.savefig("outputs/mean_voucher/mean_voucher_ols.png", dpi=150)
