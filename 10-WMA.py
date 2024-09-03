# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 02:06:47 2024

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

# Stock
Hisse = "ASELS"

# Stock data from Tradingview.
data = tv.get_hist(symbol=Hisse, exchange='BIST', interval=Interval.in_1_hour, n_bars=1000)
print(data)

# WMA
def wma(series, length):
    weights = np.arange(1, length + 1)
    return series.rolling(length).apply(lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)

# WMA 10
data['WMA10'] = wma(data['close'],10)
print(data)

# WMA 50
data['WMA50'] = wma(data['close'],50)
print(data)

# Entry - WMA10 > WMA50 
data['Entry'] = data['WMA10'] > data['WMA50']

# Exit - WMA10 < WMA50
data['Exit'] = data['WMA10'] < data['WMA50']
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

# Renaming data  columns
data.rename(columns={'open': 'Open', 'high': 'High',
                     'low': 'Low',
                     'close': 'Close',
                     'volume': 'Volume'},
                     inplace=True)

# Backtest
bt = Backtest(data, Strategy, cash=100000, commission=0.002)
Stats = bt.run()
print(Stats)