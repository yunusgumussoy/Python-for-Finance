# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 14:39:20 2024

@author: Yunus
"""

# Requirements
# !pip install git+https://github.com/rongardF/tvdatafeed
# !pip install tradingview-screener
# !pip install backtesting

# Libraries 
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from backtesting import Backtest, Strategy
import numpy as np

# Tradingview
tv = TvDatafeed()

# SMA
def sma(series, length):
    """
    Belirli bir serinin Basit Hareketli Ortalamasını (SMA) hesaplar.
    """
    return series.rolling(window=length).mean()

# Standard Deviation
def stdev(series, length):
    """
    Standard Deviation
    """
    # Average
    avg = series.rolling(window=length).mean()

    # Sum of Square Deviations
    sumOfSquareDeviations = series.rolling(window=length).apply(
        lambda x: ((x - avg.loc[x.index[-1]]) ** 2).sum(),
        raw=False)

    # Deviation
    deviation = np.sqrt(sumOfSquareDeviations / length)
    return deviation

# Bollinger Band
def bollinger_bands(series, length=20, std_multiplier=2):
    """
    Bollinger Band
    """
    middle_band = sma(series, length)
    std = stdev(series, length)
    print(std*std_multiplier)
    upper_band = middle_band + std * std_multiplier
    lower_band = middle_band - std * std_multiplier
    return lower_band, upper_band


# Strategy
class Strategy(Strategy):
    def init(self):
        pass
    def next(self):
        if self.data['Entry'] == True and not self.position:
            self.buy()
        elif self.data['Exit'] == True:
            self.position.close()

Hisse = "DOAS"
data = tv.get_hist(symbol=Hisse, exchange='BIST', interval=Interval.in_daily, n_bars=5000)
print(data)

data['BB_Lower'],data['BB_Upper'] = bollinger_bands(data['close'],20,2)
print(data)



data['Entry'] = (data['close'] > data['BB_Lower']) & (data['close'].shift(1) < data['BB_Lower'])
data['Exit'] = data['close'] > data['BB_Upper']


# Renaming column names
data.rename(columns={'open': 'Open', 'high': 'High',
                     'low': 'Low',
                     'close': 'Close',
                     'volume': 'Volume'},
                     inplace=True)


# Backtest
bt = Backtest(data, Strategy, cash=100000, commission=0.002)
Stats = bt.run()
print(Stats)