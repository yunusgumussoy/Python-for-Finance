# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 00:39:17 2024

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

# Tradingview
tv = TvDatafeed()

# Stock Name 
Hisse = "EREGL"

# Hisse Verilerini Tradingview Kütüphanesinden çekiyoruz.
data = tv.get_hist(symbol=Hisse, exchange='BIST', interval=Interval.in_1_hour, n_bars=1000)
print(data)

# EMA
def ema(series, length):
    calc = series.ewm(span=length, adjust=False).mean()
    return calc

# EMA 5 
data['EMA5'] = ema(data['close'],5)
print(data)

# EMA 20 
data['EMA20'] = ema(data['close'],20)
print(data)

# EMA5 > EMA20 - Entry
data['Entry'] = data['EMA5'] > data['EMA20']

# EMA5 < EMA20 - Exit
data['Exit'] = data['EMA5'] < data['EMA20']
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

# Renaming columns 
data.rename(columns={'open': 'Open', 'high': 'High',
                     'low': 'Low',
                     'close': 'Close',
                     'volume': 'Volume'},
                     inplace=True)

# Backtest
bt = Backtest(data, Strategy, cash=100000, commission=0.002)
Stats = bt.run()
print(Stats)