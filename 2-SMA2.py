# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 16:18:26 2024

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

# Tradingview .
tv = TvDatafeed()

# Stock Name
Hisse = "EREGL"

# Stock data from Tradingview
data = tv.get_hist(symbol=Hisse, exchange='BIST', interval=Interval.in_1_hour, n_bars=1000)
print(data)

# SMA 
def sma(series, length):
    calc = series.rolling(window=length).mean()
    return calc

# SMA 5 
data['SMA5'] = sma(data['close'],5)
print(data)

# SMA 20 
data['SMA20'] = sma(data['close'],20)
print(data)

# Entry condition: SMA 5 > SMA 20 
data['Entry'] = data['SMA5'] > data['SMA20']

# Exit condition: SMA 5 < SMA 20
data['Exit'] = data['SMA5'] < data['SMA20']
print(data)

# Strategy
class Strategy(Strategy):
    def init(self):
        pass
    def next(self):
        if self.data['Entry'] == True and not self.position:
            self.buy()
        elif self.data['Exit'] == True:
            self.position.close()

# Data Columns Rename - Backtest library requires capitals in columns
data.rename(columns={'open': 'Open', 'high': 'High',
                     'low': 'Low',
                     'close': 'Close',
                     'volume': 'Volume'},
                     inplace=True)

# For recording the results, two dataframe
df_RE = pd.DataFrame(columns=['SMA Kısa', 'SMA Uzun','Getiri Yüzdesi'])
df_WR = pd.DataFrame(columns=['SMA Kısa', 'SMA Uzun','Kazanma Oranı'])

for i in range(5, 51):
    data['SMA_L1'] = sma(data['Close'], i)
    for j in range(i+1, 51):
        data['SMA_L2'] = sma(data['Close'], j)
        data['Entry'] = data['SMA_L1'] > data['SMA_L2']
        data['Exit'] = data['SMA_L1'] < data['SMA_L2']

        # Backtest
        bt = Backtest(data, Strategy, cash=100000, commission=0.002)
        Stats = bt.run()
        RE = round(Stats.loc['Return [%]'], 2)
        WR = round(Stats.loc['Win Rate [%]'], 2)
        df_RE.loc[len(df_RE)] = [i,j,RE]
        df_WR.loc[len(df_WR)] = [i,j,WR]

# Result plotting
df_RE = df_RE.sort_values(by='Getiri Yüzdesi', ascending=False)
df_WR = df_WR.sort_values(by='Kazanma Oranı', ascending=False)
print(df_RE)
print(df_WR)


# Making results in pivot format
heatmap_data_1 = df_RE.pivot(index='SMA Kısa', columns='SMA Uzun', values='Getiri Yüzdesi')
heatmap_data_2 = df_WR.pivot(index='SMA Kısa', columns='SMA Uzun', values='Kazanma Oranı')

# Plot the return heatmap
plt.figure(figsize=(15, 12))
sns.heatmap(heatmap_data_1, annot=True, fmt=".0f", cmap="RdYlGn", linewidths=.5, annot_kws={"size": 6})
plt.title('EREGL Getiri Isı Haritası')
plt.show()

# Plot the winning rate heatmap
plt.figure(figsize=(15, 12))
sns.heatmap(heatmap_data_2, annot=True, fmt=".0f", cmap="RdYlGn", linewidths=.5, annot_kws={"size": 6})
plt.title('EREGL Kazanma Oranı Isı Haritası')
plt.show()