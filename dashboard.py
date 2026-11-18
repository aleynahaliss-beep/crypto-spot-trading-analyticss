from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
DATA = BASE / 'data' / 'daily_trades.csv'
OUT = BASE / 'dashboard'
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA, parse_dates=['trade_date'])
required = {'trade_date', 'trade_id', 'user_id', 'token', 'volume_usd'}
if not required.issubset(df.columns):
    raise ValueError(f'Missing columns: {required - set(df.columns)}')

daily = (df.groupby(['trade_date', 'token'], as_index=False)
           .agg(volume_usd=('volume_usd', 'sum'),
                active_traders=('user_id', 'nunique'),
                trades=('trade_id', 'count')))
daily['daily_volume_change_pct'] = daily.groupby('token')['volume_usd'].pct_change() * 100
summary = (df.groupby('token', as_index=False)
             .agg(total_volume_usd=('volume_usd', 'sum'),
                  total_trades=('trade_id', 'count'),
                  unique_traders=('user_id', 'nunique')))
daily.to_csv(OUT / 'daily_kpis.csv', index=False)
summary.to_csv(OUT / 'token_summary.csv', index=False)

pivot = daily.pivot(index='trade_date', columns='token', values='volume_usd').fillna(0)
ax = pivot.plot(marker='o', figsize=(10, 5))
ax.set_title('Daily Spot Trading Volume (Synthetic Data)')
ax.set_xlabel('Date')
ax.set_ylabel('Volume (USD)')
ax.grid(alpha=0.25)
plt.tight_layout()
plt.savefig(OUT / 'daily_volume.png', dpi=160)
plt.close()

ax = summary.set_index('token')['total_volume_usd'].plot(kind='bar', figsize=(8, 5))
ax.set_title('Total Spot Trading Volume by Token (Synthetic Data)')
ax.set_ylabel('Volume (USD)')
ax.set_xlabel('Token')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(OUT / 'token_volume.png', dpi=160)
plt.close()

ax = daily.pivot(index='trade_date', columns='token', values='active_traders').plot(marker='o', figsize=(10, 5))
ax.set_title('Daily Active Traders by Token (Synthetic Data)')
ax.set_xlabel('Date')
ax.set_ylabel('Unique Traders')
ax.grid(alpha=0.25)
plt.tight_layout()
plt.savefig(OUT / 'active_traders.png', dpi=160)
plt.close()

print('\nTOKEN SUMMARY\n', summary.to_string(index=False))
print('\nSaved reports and charts in:', OUT)
