# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 16:11:06 2024

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

# Backtest 
bt = Backtest(data, Strategy, cash=100000, commission=0.002)
Stats = bt.run()
print(Stats)