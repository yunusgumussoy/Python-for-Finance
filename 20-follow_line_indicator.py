# -*- coding: utf-8 -*-
"""
Follow-line indicator
"""

# Requirements
# !pip install git+https://github.com/rongardF/tvdatafeed
# !pip install tradingview-screener
# !pip install backtesting

# Libraries
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from backtesting import Backtest, Strategy
from tradingview_screener import get_all_symbols
import numpy as np

# Tradingview
tv = TvDatafeed()

# SMA 
def sma(series, length):
    return series.rolling(window=length).mean()

# Standard Deviation
def stdev(series, length):
    avg = series.rolling(window=length).mean()
    sumOfSquareDeviations = series.rolling(window=length).apply(
        lambda x: ((x - avg.loc[x.index[-1]]) ** 2).sum(),
        raw=False)
    deviation = np.sqrt(sumOfSquareDeviations / length)
    return deviation

# Bollinger Band 
def bollinger_bands(series, length=20, std_multiplier=2):
    middle_band = sma(series, length)
    std = stdev(series, length)
    upper_band = middle_band + std * std_multiplier
    lower_band = middle_band - std * std_multiplier
    return lower_band, upper_band

# RMA
def rma(series, length=None):
    # Validate Arguments
    length = int(length) if length and length > 0 else 10
    alpha = (1.0 / length) if length > 0 else 0.5

    # Calculate Result
    rma = series.ewm(alpha=alpha, min_periods=length).mean()
    return rma

# True Range
def tr(high, low, close):
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr

# Average True Range
def atr(high, low, close, period=14):
    # Calculate true range (TR)
    true_range = tr(high, low, close)
    atr = rma(true_range,period)
    return atr

def FLI(data, atr_period=5):
    df = data.copy()
    df.reset_index(inplace=True)  # Ensure integer indexing
    df['trendline'] = 0.0
    df['itrend'] = 0.0
    df['Entry'] = False
    df['Exit'] = False
    df['in_Trade'] = False

    # ATR Calculation
    df['atr'] = atr(df['high'], df['low'], df['close'], atr_period)

    in_trade = False  # Flag to check if in a trade

    for i in range(1, len(df)):
        # Trend Line Calculation
        if df.loc[i, 'close'] > df.loc[i, 'BB_Upper']:
            df.loc[i, 'trendline'] = round(max(df.loc[i, 'low'] - df.loc[i, 'atr'], df.loc[i-1, 'trendline']),2)
        elif df.loc[i, 'close'] < df.loc[i, 'BB_Lower']:
            df.loc[i, 'trendline'] = round(min(df.loc[i, 'high'] + df.loc[i, 'atr'], df.loc[i-1, 'trendline']),2)
        else:
            df.loc[i, 'trendline'] = df.loc[i-1, 'trendline']

        # Trend Direction Calculation
        if df.loc[i, 'trendline'] > df.loc[i-1, 'trendline']:
            df.loc[i, 'itrend'] = 1
        elif df.loc[i, 'trendline'] < df.loc[i-1, 'trendline']:
            df.loc[i, 'itrend'] = -1
        else:
            df.loc[i, 'itrend'] = df.loc[i-1, 'itrend']

        # Entry and Exit Signals
        if not in_trade and df.loc[i-1, 'itrend'] == -1 and df.loc[i, 'itrend'] == 1:
            df.loc[i, 'Entry'] = True
            in_trade = True
        elif in_trade and df.loc[i-1, 'itrend'] == 1 and df.loc[i, 'itrend'] == -1:
            df.loc[i, 'Exit'] = True
            in_trade = False

        df.loc[i, 'in_Trade'] = in_trade  # Record whether in a trade

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


Hisseler = get_all_symbols(market='turkey')
Hisseler = [symbol.replace('BIST:', '') for symbol in Hisseler]
Hisseler = sorted(Hisseler)

# Columns for Reporting
Titles = ['Hisse Adı', 'Son Fiyat','Kazanma Oranı','Giriş Sinyali', 'Çıkış Sinyali']

# Dataframe for Signals
df_signals = pd.DataFrame(columns=Titles)

for Hisse in Hisseler:
    #try:
        # Variables
        BBperiod = 21
        BBdeviations = 1
        ATRperiod = 5
        data = tv.get_hist(symbol=Hisse, exchange='BIST', interval=Interval.in_1_hour, n_bars=1000)

        # Bollinger Band
        data['BB_Lower'], data['BB_Upper'] = bollinger_bands(data['close'], BBperiod, BBdeviations)

        # Flow Line Indicator 
        data = FLI(data, ATRperiod)

        # Renaming columns
        data.rename(columns={'open': 'Open', 'high': 'High',
                            'low': 'Low',
                            'close': 'Close',
                            'volume': 'Volume'},
                            inplace=True)

        # Index to datetime
        data['datetime'] = pd.to_datetime(data['datetime'])
        data.set_index('datetime', inplace=True)
        # Backtest
        bt = Backtest(data, Strategy, cash=100000, commission=0.002)
        Stats = bt.run()

        # Starting signals are false
        Buy = False
        Sell = False

        # Last 2 data 
        Signals = data.tail(2)

        # For easy operation, reset index
        Signals = Signals.reset_index()

        # Buy condition - previous buy condition is false & current buy condition is true 
        Buy = Signals.loc[0, 'Entry'] == False and Signals.loc[1, 'Entry'] ==True

        # Sell condition - previous sell condition is false & current sell condition is true 
        Sell = Signals.loc[0, 'Exit'] == False and Signals.loc[1, 'Exit'] == True

        # last price
        Last_Price = Signals.loc[1, 'Close']

        # a list named L1 -  stock name, last price
        # Win rate, signals
        L1 = [Hisse,Last_Price, round(Stats.loc['Win Rate [%]'], 2), str(Buy), str(Sell)]

        # print
        print(L1)

        # List to dataframe's last row
        df_signals.loc[len(df_signals)] = L1
    #except:
        #pass


# those have buy signals are true 
df_true = df_signals[(df_signals['Giriş Sinyali'] == 'True')]

# Ordering win rate 
df_true = df_true.sort_values(by='Kazanma Oranı', ascending=False)
print(df_true)