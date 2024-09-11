# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 02:24:07 2024

@author: Yunus
"""

# Requirements
# pip install git+https://github.com/rongardF/tvdatafeed
# pip install backtesting

# Libraries
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from backtesting import Backtest, Strategy
import numpy as np

tv = TvDatafeed()

Hisse = "OYAKC"

data = tv.get_hist(symbol=Hisse, exchange='BIST', interval=Interval.in_1_hour, n_bars=1000)
print(data)

def sma(series, length):
    """
    Simple Moving Average.
    """
    return series.rolling(window=length).mean()

def ema(series, length):
    """
    Exponential Moving Average.
    """
    return series.ewm(span=length, adjust=False).mean()

def rma(series, length=None):
    """
    Relative Moving Average.
    """
    length = int(length) if length and length > 0 else 10
    alpha = (1.0 / length) if length > 0 else 0.5
    rma = series.ewm(alpha=alpha, min_periods=length).mean()
    return rma

def wma(series, length):
    """
    Weighted Moving Average.
    """
    weights = np.arange(1, length + 1)
    return series.rolling(length).apply(lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)

def hull_ma(series, length=9):
    """
    Hull Moving Average.
    """
    half_length = int(length / 2)
    wma_half = wma(series, half_length)
    wma_full = wma(series, length)
    raw_hma = 2 * wma_half - wma_full
    hma = wma(raw_hma, int(np.sqrt(length)))
    return hma

data['SMA10'] = sma(data['close'], 10)
data['SMA20'] = sma(data['close'], 20)
data['EMA10'] = ema(data['close'], 10)
data['EMA20'] = ema(data['close'], 20)
data['WMA10'] = wma(data['close'], 10)
data['WMA20'] = wma(data['close'], 20)
data['RMA10'] = rma(data['close'], 10)
data['RMA20'] = rma(data['close'], 20)
data['HMA10'] = hull_ma(data['close'], 10)
data['HMA20'] = hull_ma(data['close'], 20)

# Signal Calculations
# SMA
data['SMA_Entry'] = (data['SMA10'] > data['SMA20']) & (data['SMA10'].shift(1) <= data['SMA20'].shift(1))
data['SMA_Exit'] = (data['SMA10'] < data['SMA20']) & (data['SMA10'].shift(1) >= data['SMA20'].shift(1))

# EMA 
data['EMA_Entry'] = (data['EMA10'] > data['EMA20']) & (data['EMA10'].shift(1) <= data['EMA20'].shift(1))
data['EMA_Exit'] = (data['EMA10'] < data['EMA20']) & (data['EMA10'].shift(1) >= data['EMA20'].shift(1))

# WMA
data['WMA_Entry'] = (data['WMA10'] > data['WMA20']) & (data['WMA10'].shift(1) <= data['WMA20'].shift(1))
data['WMA_Exit'] = (data['WMA10'] < data['WMA20']) & (data['WMA10'].shift(1) >= data['WMA20'].shift(1))

# RMA
data['RMA_Entry'] = (data['RMA10'] > data['RMA20']) & (data['RMA10'].shift(1) <= data['RMA20'].shift(1))
data['RMA_Exit'] = (data['RMA10'] < data['RMA20']) & (data['RMA10'].shift(1) >= data['RMA20'].shift(1))

# HMA
data['HMA_Entry'] = (data['HMA10'] > data['HMA20']) & (data['HMA10'].shift(1) <= data['HMA20'].shift(1))
data['HMA_Exit'] = (data['HMA10'] < data['HMA20']) & (data['HMA10'].shift(1) >= data['HMA20'].shift(1))