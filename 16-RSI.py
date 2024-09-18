# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 03:08:15 2024

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
Hisse = "PGSUS"

# Stock data from Tradingview
data = tv.get_hist(symbol=Hisse, exchange='BIST', interval=Interval.in_daily, n_bars=1000)
print(data)

# RMA - Relative Moving Average
def rma(series, length=None):
    """
    Belirli bir kapanış fiyatı serisinin Göreceli Hareketli Ortalama'sını (RMA) hesaplar.
    """
    length = int(length) if length and length > 0 else 10
    alpha = (1.0 / length) if length > 0 else 0.5
    rma = series.ewm(alpha=alpha, min_periods=length).mean()
    return rma


# RSI - Relative Strength Index
def rsi(series, length=14):
    """
    Belirli bir serinin Göreceli Güç Endeksi'ni (RSI) hesaplayın.

    Parametreler:
    - series: Fiyat verilerini içeren pandas Serisi.
    - length: RSI periyodunun uzunluğu (varsayılan 14'tür).
    - scalar: RSI değerlerini ayarlamak için kullanılan skaler faktör (varsayılan 100'dür).
    - drift: Fiyat değişiklikleri için dönem sayısı (varsayılan 1'dir).

    Döndürür:
    - Girdi parametrelerine göre hesaplanmış RSI değerlerini içeren pandas Serisi.
    """
    # Changes on prices
    scalar = 100
    drift = 1
    negative = series.diff(drift)
    positive = negative.copy()

    # For Pozitive series, negatives = 0
    positive[positive < 0] = 0
    # For Negative series, pozitives = 0 
    negative[negative > 0] = 0

    # Average gain and loss
    positive_avg = rma(positive, length=length)
    negative_avg = rma(negative, length=length)

    # RSI calculation
    rsi = scalar * positive_avg / (positive_avg + negative_avg.abs())
    return rsi


# RSI
data['RSI14'] = rsi(data['close'],14)
print(data)

# Entry term - RSI14 > 30
data['Entry'] = data['RSI14'] > 30

# Exit term - RSI70 > 70
data['Exit'] = data['RSI14'] > 70
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

# data columns renaming
data.rename(columns={'open': 'Open', 'high': 'High',
                     'low': 'Low',
                     'close': 'Close',
                     'volume': 'Volume'},
                     inplace=True)

# Backtest 
bt = Backtest(data, Strategy, cash=100000, commission=0.002)
Stats = bt.run()
print(Stats)
# print(data.to_string())