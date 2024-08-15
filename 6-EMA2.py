# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 00:42:00 2024

@author: Yunus
"""

# Requirements
# pip install git+https://github.com/rongardF/tvdatafeed
# pip install tradingview-screener
# pip install backtesting
# pip install seaborn


# Libraries 
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from backtesting import Backtest, Strategy
import seaborn as sns
import matplotlib.pyplot as plt

# Tradingview
tv = TvDatafeed()

# Stock Name
Hisse = "EREGL"

# Stock Data from Tradingview
data = tv.get_hist(symbol=Hisse, exchange='BIST', interval=Interval.in_1_hour, n_bars=1000)
print(data)

# EMA
def ema(series, length):
    calc = series.ewm(span=length, adjust=False).mean()
    return calc

# Strategy
class Strategy(Strategy):
    def init(self):
        pass
    def next(self):
        if self.data['Entry'] == True and not self.position:
            self.buy()
        elif self.data['Exit'] == True:
            self.position.close()


# Renaming Data Columns
data.rename(columns={'open': 'Open', 'high': 'High',
                      'low': 'Low',
                      'close': 'Close',
                      'volume': 'Volume'},
                      inplace=True)

# Two dataframes for results
df_RE = pd.DataFrame(columns=['EMA Kısa', 'EMA Uzun','Getiri Yüzdesi'])
df_WR = pd.DataFrame(columns=['EMA Kısa', 'EMA Uzun','Kazanma Oranı'])

for i in range(5, 51):
    data['EMA_L1'] = ema(data['Close'], i)
    for j in range(i+1, 51):
        data['EMA_L2'] = ema(data['Close'], j)
        data['Entry'] = data['EMA_L1'] > data['EMA_L2']
        data['Exit'] = data['EMA_L1'] < data['EMA_L2']

        # Backtest 
        bt = Backtest(data, Strategy, cash=100000, commission=0.002)
        Stats = bt.run()
        RE = round(Stats.loc['Return [%]'], 2)
        WR = round(Stats.loc['Win Rate [%]'], 2)
        df_RE.loc[len(df_RE)] = [i,j,RE]
        df_WR.loc[len(df_WR)] = [i,j,WR]

# Plotting Results
df_RE = df_RE.sort_values(by='Getiri Yüzdesi', ascending=False)
df_WR = df_WR.sort_values(by='Kazanma Oranı', ascending=False)
print(df_RE)
print(df_WR)


# Data in pivot format 
heatmap_data_1 = df_RE.pivot(index='EMA Kısa', columns='EMA Uzun', values='Getiri Yüzdesi')
heatmap_data_2 = df_WR.pivot(index='EMA Kısa', columns='EMA Uzun', values='Kazanma Oranı')

# Plot the Getiri heatmap
plt.figure(figsize=(15, 12))
sns.heatmap(heatmap_data_1, annot=True, fmt=".0f", cmap="RdYlGn", linewidths=.5, annot_kws={"size": 6})
plt.title('EREGL Getiri Isı Haritası')
plt.show()

# Plot the Kazanma Oranı heatmap
plt.figure(figsize=(15, 12))
sns.heatmap(heatmap_data_2, annot=True, fmt=".0f", cmap="RdYlGn", linewidths=.5, annot_kws={"size": 6})
plt.title('EREGL Kazanma Oranı Isı Haritası')
plt.show()