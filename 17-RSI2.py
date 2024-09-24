# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 14:09:35 2024

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

# Stocks
Hisseler = ['AKBNK','ALARK','ASELS','ASTOR','BIMAS',
	'BRSAN','DOAS','EKGYO','ENKAI','EREGL',
	'FROTO','GARAN','GUBRF','HEKTS','ISCTR',
	'KCHOL','KONTR','KOZAL','KRDMD','OYAKC',
	'PETKM','PGSUS','SAHOL','SASA','SISE',
	'TCELL','THYAO','TOASO','TUPRS','YKBNK']


# RMA
def rma(series, length=None):
    """
    Belirli bir kapanış fiyatı serisinin Göreceli Hareketli Ortalama'sını (RMA) hesaplar.
    """
    length = int(length) if length and length > 0 else 10
    alpha = (1.0 / length) if length > 0 else 0.5
    rma = series.ewm(alpha=alpha, min_periods=length).mean()
    return rma


# RSI
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
    # Price variance
    scalar = 100
    drift = 1
    negative = series.diff(drift)
    positive = negative.copy()

    # negatives are 0 for positive series
    positive[positive < 0] = 0
    # pozitives are 0 for negative series
    negative[negative > 0] = 0

    # Average gain and loss
    positive_avg = rma(positive, length=length)
    negative_avg = rma(negative, length=length)

    # RSI
    rsi = scalar * positive_avg / (positive_avg + negative_avg.abs())
    return rsi

def Sell_Strategy(data,tp=10,ec=0.90):
    df=data.copy()
    df['Stop Loss'] = np.nan
    df['Entry Price'] = np.nan
    df['Exit'] = False
    df['Trade'] = "BEKLE"
    in_trade=False
    for i in range(1,len(df)):
            if in_trade==False:
                entry_condition = (df.loc[i,'Entry'] == True) & (df.loc[i-1,'Entry']==False)
                if entry_condition:
                    in_trade = True
                    entry_price = df.loc[i, 'close']
                    stop_loss = entry_price*0.90

                    df.loc[i,'Entry'] = True
                    df.loc[i,'Trade'] = 'AL'
                    df.loc[i,'Entry Price']  = entry_price
                    df.loc[i,'Stop Loss'] = stop_loss
            else:
                exit_condition_1 = df.loc[i,'close'] < stop_loss
                exit_condition_2 = (df.loc[i-1, 'close'] > entry_price * (1 + tp / 100))
                if exit_condition_1:
                    in_trade = False
                    df.loc[i,'Exit'] = True
                    df.loc[i,'Trade'] = 'ZARAR KES'

                if exit_condition_2:
                    in_trade = False
                    df.loc[i,'Exit'] = True
                    df.loc[i,'Trade'] = 'SAT'
    return df

# Strategy
class Strategy(Strategy):
    def init(self):
        pass
    def next(self):
        if self.data['Entry'] == True and not self.position:
            self.buy()
        elif self.data['Exit'] == True:
            self.position.close()

# BIST30 
df_bist30_RE = pd.DataFrame(columns=['Hisse Adı','Getiri Yüzdesi','Son Sinyal'])
df_bist30_WR = pd.DataFrame(columns=['Hisse Adı','Kazanma Oranı','Son Sinyal'])

for hisse in Hisseler:
  try:

    # Stock data from Tradingview
    data = tv.get_hist(symbol=hisse, exchange='BIST', interval=Interval.in_daily, n_bars=5000)
    data.reset_index(inplace=True)

    # RSI
    data['RSI14'] = rsi(data['close'],14)
    data['Entry'] = (data['RSI14'] > 30)

    # Sell Strategy
    data=Sell_Strategy(data,10,0.90)

    # Column rename
    data.rename(columns={'open': 'Open', 'high': 'High',
                        'low': 'Low',
                        'close': 'Close',
                        'volume': 'Volume'},
                        inplace=True)

    # Backtest
    bt = Backtest(data, Strategy, cash=100000, commission=0.002)
    Stats = bt.run()
    RE = round(Stats.loc['Return [%]'], 2)
    WR = round(Stats.loc['Win Rate [%]'], 2)

    # Signal
    Signals = data.tail(2).reset_index()
    Buy = Signals.loc[0, 'Entry'] == False and Signals.loc[1, 'Entry'] ==True

    df_bist30_RE.loc[len(df_bist30_RE)] = [hisse,RE,Buy]
    df_bist30_WR.loc[len(df_bist30_WR)] = [hisse,WR,Buy]
  except:
    pass

print(df_bist30_RE)
print(df_bist30_WR)