# -*- coding: utf-8 -*-
"""
William - R
"""

# Requirements
# !pip install git+https://github.com/rongardF/tvdatafeed
# !pip install tradingview-screener
# !pip install backtesting

# Libraries
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from backtesting import Backtest, Strategy

# Tradingview
tv = TvDatafeed()

# Stock name
Hisse = "AKBNK"

# Stock data from Tradingview
data = tv.get_hist(symbol=Hisse, exchange='BIST', interval=Interval.in_daily, n_bars=1000)
print(data)

# William R 
def williams_r(high, low, close, window=14):
    """
    Williams %R (W.R) 
    """
    # highest high
    highest_high = high.rolling(window=window).max()

    # lowest low
    lowest_low = low.rolling(window=window).min()

    # Williams %R 
    williams_r = -100 * (highest_high - close) / (highest_high - lowest_low)

    return williams_r


# William R 
data['William_R'] = williams_r(data['high'],data['low'],data['close'],14)
print(data)

# Entry condition: William %R > -80 
data['Entry'] = (data['William_R'] > -80) & (data['William_R'].shift(1) <= -80)

# Exit condition: William %R > -20 
data['Exit'] = (data['William_R'] > -20) & (data['William_R'].shift(1) <= -20)

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

# Backtest
bt = Backtest(data, Strategy, cash=100000, commission=0.002)
Stats = bt.run()
print(Stats)