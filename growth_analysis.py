from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
REPORTS = ROOT / 'reports'
REPORTS.mkdir(exist_ok=True)

trades = pd.read_csv(DATA / 'growth_trades.csv', parse_dates=['trade_date'])
campaigns = pd.read_csv(DATA / 'campaigns.csv')
liquidity = pd.read_csv(DATA / 'liquidity.csv')

# Retention: proportion of first-day traders who trade again on a later date.
first = trades.groupby(['token', 'user_id'])['trade_date'].min().rename('first_trade_date').reset_index()
activity = trades.merge(first, on=['token', 'user_id'])
returned = (activity['trade_date'] > activity['first_trade_date']).groupby([activity['token'], activity['user_id']]).any().reset_index(name='returned_later')
retention = returned.groupby('token').agg(first_time_traders=('user_id', 'nunique'), returning_traders=('returned_later', 'sum')).reset_index()
retention['repeat_trader_rate_pct'] = (100 * retention['returning_traders'] / retention['first_time_traders']).round(2)

# Attribution is illustrative: campaign IDs are assigned in the synthetic data.
trades['fee_revenue_usd'] = trades['volume_usd'] * trades['fee_rate']
revenue = trades.dropna(subset=['campaign_id']).groupby('campaign_id', as_index=False)['fee_revenue_usd'].sum()
performance = campaigns.merge(revenue, on='campaign_id', how='left').fillna({'fee_revenue_usd': 0})
performance['roi_pct'] = ((performance['fee_revenue_usd'] - performance['campaign_cost_usd']) / performance['campaign_cost_usd'] * 100).round(2)
performance['roas'] = (performance['fee_revenue_usd'] / performance['campaign_cost_usd']).round(2)

# Illustrative asset score, not an exchange production risk model.
volume = trades.groupby('token', as_index=False)['volume_usd'].sum()
score = volume.merge(retention[['token','repeat_trader_rate_pct']], on='token').merge(liquidity, on='token')
score['volume_score'] = (score['volume_usd'] / score['volume_usd'].max() * 100).round(1)
score['liquidity_score'] = (100 - score['spread_bps'].clip(0,100))
score['asset_score'] = (0.4 * score['volume_score'] + 0.35 * score['repeat_trader_rate_pct'] + 0.25 * score['liquidity_score']).round(1)
score['priority'] = pd.cut(score['asset_score'], bins=[-1,40,70,101], labels=['Monitor','Test growth','Prioritize'])

for name, frame in [('retention',retention), ('campaign_roi',performance), ('asset_scores',score)]:
    frame.to_csv(REPORTS / f'{name}.csv', index=False)
    print(f'\n{name.upper()}\n{frame.to_string(index=False)}')
print('\nReports saved to:', REPORTS)
