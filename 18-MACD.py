# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 14:16:52 2024

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

# Tradingview
tv = TvDatafeed()

# EMA
def ema(seri, uzunluk):
    """
    Verilen bir seri için Üssel Hareketli Ortalama (EMA) hesaplayın.
    """
    return seri.ewm(span=uzunluk, adjust=False).mean()

# MACD
def macd(seri, hizli=12, yavas=26, sinyal=9):
    """
    Verilen bir seri için Hareketli Ortalama Yakınsama Iraksama (MACD) hesaplayın ve bir DataFrame döndürün.

    Parametreler:
    - seri: Fiyat verilerini içeren pandas Serisi.
    - hizli (int): Hızlı EMA için periyot. Varsayılan 12'dir.
    - yavas (int): Yavaş EMA için periyot. Varsayılan 26'dır.
    - sinyal (int): Sinyal çizgisi EMA'sı için periyot. Varsayılan 9'dur.

    """
    ema_hizli = ema(seri, hizli)
    ema_yavas = ema(seri, yavas)
    macd_cizgisi = ema_hizli - ema_yavas
    sinyal_cizgisi = ema(macd_cizgisi, sinyal)
    macd_histogram = macd_cizgisi - sinyal_cizgisi

    return macd_cizgisi,sinyal_cizgisi, macd_histogram

# Strategy
class Strategy(Strategy):
    def init(self):
        pass
    def next(self):
        if self.data['Entry'] == True and not self.position:
            self.buy()
        elif self.data['Exit'] == True:
            self.position.close()

Hisse = "THYAO"
data = tv.get_hist(symbol=Hisse, exchange='BIST', interval=Interval.in_daily, n_bars=5000)
data['MACD'],data['Signal'],data['Histogram'] = macd(data['close'],12,26,9)
print(data)

data['Entry'] = data['MACD'] > data['Signal']
data['Exit'] = data['MACD'] < data['Signal']


data.rename(columns={'open': 'Open', 'high': 'High',
                     'low': 'Low',
                     'close': 'Close',
                     'volume': 'Volume'},
                     inplace=True)


# Backtest
bt = Backtest(data, Strategy, cash=100000, commission=0.002)
Stats = bt.run()
print(Stats)
