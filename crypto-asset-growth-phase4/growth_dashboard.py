"""Phase 4: static growth dashboard from Phase 3 synthetic reports."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
OUTPUT = ROOT / "growth_dashboard"
OUTPUT.mkdir(exist_ok=True)

ret = pd.read_csv(REPORTS / "retention.csv")
roi = pd.read_csv(REPORTS / "campaign_roi.csv")
scores = pd.read_csv(REPORTS / "asset_scores.csv")
liq = pd.read_csv(ROOT / "data" / "liquidity.csv")


def save_bar(df, x, y, title, ylabel, filename, horizontal=False, baseline=None):
    fig, ax = plt.subplots(figsize=(9, 5))
    if horizontal:
        ax.barh(df[x], df[y])
        ax.set_xlabel(ylabel)
    else:
        ax.bar(df[x], df[y])
        ax.set_ylabel(ylabel)
        ax.tick_params(axis="x", rotation=15)
    if baseline is not None:
        (ax.axvline if horizontal else ax.axhline)(baseline, linestyle="--", linewidth=1)
    ax.set_title(title)
    ax.grid(axis="x" if horizontal else "y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUTPUT / filename, dpi=160)
    plt.close(fig)

save_bar(ret, "token", "repeat_trader_rate_pct", "Repeat Trader Rate by Token (Synthetic)", "Repeat trader rate (%)", "retention.png")
save_bar(roi, "campaign_id", "roi_pct", "Attributed Campaign ROI (Synthetic)", "ROI (%)", "campaign_roi.png", baseline=0)
save_bar(scores, "token", "asset_score", "Illustrative Asset Score (Synthetic)", "Weighted score (0–100)", "asset_scores.png")
save_bar(liq, "token", "spread_bps", "Illustrative Spread by Token (Synthetic)", "Spread (basis points)", "spread.png")

summary = scores[["token", "volume_usd", "repeat_trader_rate_pct", "spread_bps", "asset_score", "priority"]].copy()
summary.to_csv(OUTPUT / "growth_summary.csv", index=False)
print("Dashboard charts and summary saved in:", OUTPUT)
print(summary.to_string(index=False))
