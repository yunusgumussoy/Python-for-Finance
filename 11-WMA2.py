# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 02:08:30 2024

@author: Yunus
"""

# Requirements
# pip install git+https://github.com/rongardF/tvdatafeed
# pip install tradingview-screener
# pip install backtesting


# Libraries
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from backtesting import Backtest, Strategy
import numpy as np

# Tradingview
tv = TvDatafeed()

# Stock Name
Hisse = "ASELS"

# Stock data from Tradingview
data = tv.get_hist(symbol=Hisse, exchange='BIST', interval=Interval.in_1_hour, n_bars=1000)
print(data)

# WMA 
def wma(series, length):
    weights = np.arange(1, length + 1)
    return series.rolling(length).apply(lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)

# Strategy
class Strategy(Strategy):
    def init(self):
        pass
    def next(self):
        if self.data['Entry'] == True and not self.position:
            self.buy()
        elif self.data['Exit'] == True:
            self.position.close()


# Renaming data columns
data.rename(columns={'open': 'Open', 'high': 'High',
                      'low': 'Low',
                      'close': 'Close',
                      'volume': 'Volume'},
                      inplace=True)

# Two empty dataframe for new calculations
df_RE = pd.DataFrame(columns=['WMA Kısa', 'WMA Uzun','Getiri Yüzdesi'])
df_WR = pd.DataFrame(columns=['WMA Kısa', 'WMA Uzun','Kazanma Oranı'])

for i in range(5, 51):
    data['WMA_L1'] = wma(data['Close'], i)
    for j in range(i+1, 51):
        data['WMA_L2'] = wma(data['Close'], j)
        data['Entry'] = data['WMA_L1'] > data['WMA_L2']
        data['Exit'] = data['WMA_L1'] < data['WMA_L2']

        # Backtest 
        bt = Backtest(data, Strategy, cash=100000, commission=0.002)
        Stats = bt.run()
        RE = round(Stats.loc['Return [%]'], 2)
        WR = round(Stats.loc['Win Rate [%]'], 2)
        df_RE.loc[len(df_RE)] = [i,j,RE]
        df_WR.loc[len(df_WR)] = [i,j,WR]

# Plot the results
df_RE = df_RE.sort_values(by='Getiri Yüzdesi', ascending=False)
df_WR = df_WR.sort_values(by='Kazanma Oranı', ascending=False)
print(df_RE)
print(df_WR)

# Seaborn for heatmap
# pip install seaborn

# Visualization libraries
import seaborn as sns
import matplotlib.pyplot as plt

# Pivot formatting
heatmap_data_1 = df_RE.pivot(index='WMA Kısa', columns='WMA Uzun', values='Getiri Yüzdesi')
heatmap_data_2 = df_WR.pivot(index='WMA Kısa', columns='WMA Uzun', values='Kazanma Oranı')

# Plot the Return heatmap
plt.figure(figsize=(15, 12))
sns.heatmap(heatmap_data_1, annot=True, fmt=".0f", cmap="RdYlGn", linewidths=.5, annot_kws={"size": 6})
plt.title('ASELS Getiri Isı Haritası')
plt.show()

# Plot the Win Rate heatmap
plt.figure(figsize=(15, 12))
sns.heatmap(heatmap_data_2, annot=True, fmt=".0f", cmap="RdYlGn", linewidths=.5, annot_kws={"size": 6})
plt.title('ASELS Kazanma Oranı Isı Haritası')
plt.show()