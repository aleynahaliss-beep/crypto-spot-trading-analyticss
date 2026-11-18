"""Analyze synthetic spot trading activity with pandas.

Run: python analysis.py
"""
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent


def analyze_token(trades: pd.DataFrame, token: str) -> pd.DataFrame:
    """Return total USD volume, trade count and unique active traders."""
    required = {"trade_id", "user_id", "token", "volume_usd"}
    missing = required - set(trades.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    selected = trades.loc[trades["token"] == token]
    return pd.DataFrame([{
        "token": token,
        "total_volume_usd": selected["volume_usd"].sum(),
        "total_trades": len(selected),
        "active_traders": selected["user_id"].nunique(),
    }])


def main() -> None:
    trades = pd.read_csv(BASE_DIR / "data" / "trades.csv")
    print("Sample trades:")
    print(trades.to_string(index=False))
    summary = analyze_token(trades, "ACTX")
    print("\nACTX performance:")
    print(summary.to_string(index=False))
    output = BASE_DIR / "actx_summary.csv"
    summary.to_csv(output, index=False)
    print(f"\nSaved: {output.name}")


if __name__ == "__main__":
    main()
