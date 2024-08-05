# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 00:11:17 2024

@author: Yunus
"""

# Required libraries
# pip install git+https://github.com/rongardF/tvdatafeed
# pip install tradingview-screener
# pip install backtesting


# libraries 
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from backtesting import Backtest, Strategy

# Tradingview 
tv = TvDatafeed()

# SMA
def sma(series, length):
    calc = series.rolling(window=length).mean()
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

# Stock names
Hisse = ['AKBNK','ALARK','ASELS','ASTOR','BIMAS',
	'BRSAN','DOAS','EKGYO','ENKAI','EREGL',
	'FROTO','GARAN','GUBRF','HEKTS','ISCTR',
	'KCHOL','KONTR','KOZAL','KRDMD','OYAKC',
	'PETKM','PGSUS','SAHOL','SASA','SISE',
	'TCELL','THYAO','TOASO','TUPRS','YKBNK']

# For recording the BIST30 results, two dataframe
df_bist30_RE = pd.DataFrame(columns=['Hisse Adı','SMA Kısa', 'SMA Uzun','Getiri Yüzdesi'])
df_bist30_WR = pd.DataFrame(columns=['Hisse Adı','SMA Kısa', 'SMA Uzun','Kazanma Oranı'])

for z in range(len(Hisse)):
    # Getting stock data from Tradingview library
    print(Hisse[z])
    data = tv.get_hist(symbol=Hisse[z], exchange='BIST', interval=Interval.in_daily, n_bars=1000)
    # Renaming data columns
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

    # Results
    df_RE = df_RE.sort_values(by='Getiri Yüzdesi', ascending=False)
    df_WR = df_WR.sort_values(by='Kazanma Oranı', ascending=False)
    RE_list = df_RE.iloc[0].tolist()
    WR_list = df_WR.iloc[0].tolist()
    df_bist30_RE.loc[len(df_bist30_RE)] = [Hisse[z]]+RE_list
    df_bist30_WR.loc[len(df_bist30_WR)] = [Hisse[z]]+WR_list

print(df_bist30_RE)
print(df_bist30_WR)