# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 02:10:25 2024

@author: Yunus
"""

from typing_extensions import DefaultDict
# pip install git+https://github.com/rongardF/tvdatafeed

import pandas as pd
from tvDatafeed import TvDatafeed, Interval
import numpy as np

# Initialize TradingView data feed
tv = TvDatafeed()

# Define the best WMA periods for each stock
df_bist30 = [
    {"Hisse Adı": "AKBNK", "WMA Kısa":   5.0, "WMA Uzun": 7.0},
    {"Hisse Adı": "ALARK", "WMA Kısa":  12.0, "WMA Uzun":49.0},
    {"Hisse Adı": "ASELS", "WMA Kısa":  46.0, "WMA Uzun":49.0},
    {"Hisse Adı": "ASTOR", "WMA Kısa":  19.0, "WMA Uzun":20.0},
    {"Hisse Adı": "BIMAS", "WMA Kısa":  27.0, "WMA Uzun":32.0},
    {"Hisse Adı": "BRSAN", "WMA Kısa":  31.0, "WMA Uzun":42.0},
    {"Hisse Adı": "DOAS" , "WMA Kısa":  41.0, "WMA Uzun":50.0},
    {"Hisse Adı": "EKGYO", "WMA Kısa":   7.0, "WMA Uzun": 8.0},
    {"Hisse Adı": "ENKAI", "WMA Kısa":  10.0, "WMA Uzun":32.0},
    {"Hisse Adı": "EREGL", "WMA Kısa":  26.0, "WMA Uzun":27.00},
    {"Hisse Adı": "FROTO", "WMA Kısa":  34.0, "WMA Uzun":35.0},
    {"Hisse Adı": "GARAN", "WMA Kısa":  47.0, "WMA Uzun":48.0},
    {"Hisse Adı": "GUBRF", "WMA Kısa":   8.0, "WMA Uzun":13.0},
    {"Hisse Adı": "HEKTS", "WMA Kısa":  35.0, "WMA Uzun":45.0},
    {"Hisse Adı": "ISCTR", "WMA Kısa":   5.0, "WMA Uzun": 6.0},
    {"Hisse Adı": "KCHOL", "WMA Kısa":  36.0, "WMA Uzun":44.0},
    {"Hisse Adı": "KONTR", "WMA Kısa":   8.0, "WMA Uzun":10.0},
    {"Hisse Adı": "KOZAL", "WMA Kısa":  19.0, "WMA Uzun":29.0},
    {"Hisse Adı": "KRDMD", "WMA Kısa":   6.0, "WMA Uzun": 7.0},
    {"Hisse Adı": "OYAKC", "WMA Kısa":   7.0, "WMA Uzun": 8.0},
    {"Hisse Adı": "PETKM", "WMA Kısa":   7.0, "WMA Uzun":11.0},
    {"Hisse Adı": "PGSUS", "WMA Kısa":   5.0, "WMA Uzun":31.0},
    {"Hisse Adı": "SAHOL", "WMA Kısa":  19.0, "WMA Uzun":50.0},
    {"Hisse Adı": "SASA" , "WMA Kısa":   9.0, "WMA Uzun":26.0},
    {"Hisse Adı": "SISE" , "WMA Kısa":  23.0, "WMA Uzun":25.0},
    {"Hisse Adı": "TCELL", "WMA Kısa":  21.0, "WMA Uzun":43.0},
    {"Hisse Adı": "THYAO", "WMA Kısa":  20.0, "WMA Uzun":48.0},
    {"Hisse Adı": "TOASO", "WMA Kısa":  26.0, "WMA Uzun":32.0},
    {"Hisse Adı": "TUPRS", "WMA Kısa":  10.0, "WMA Uzun":28.0},
    {"Hisse Adı": "YKBNK", "WMA Kısa":   6.0, "WMA Uzun": 8.0}
]

# Creating DataFrame
df_bist30 = pd.DataFrame(df_bist30)

# Displaying the DataFrame
print(df_bist30)

# New Dataframe for data
df_bist30_Sonuclar = pd.DataFrame(columns=['datetime','Hisse Adı','open','high','low','close','volume','WMA Kısa', 'WMA Uzun','Entry','Exit'])



# WMA 
def wma(series, length):
    weights = np.arange(1, length + 1)
    return series.rolling(length).apply(lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)

# Loop through each stock in the DataFrame
for i in range(len(df_bist30)):
    hisse_adi = df_bist30.loc[i, 'Hisse Adı']
    WMA_kisa = df_bist30.loc[i, 'WMA Kısa'].astype(int)
    WMA_uzun = df_bist30.loc[i, 'WMA Uzun'].astype(int)

    # Retrieve historical data
    data = tv.get_hist(symbol=hisse_adi, exchange='BIST', interval=Interval.in_daily, n_bars=1000)
    data.reset_index(inplace=True)

    # Calculate short and long WMAs
    data['WMA Kısa'] = wma(data['close'], WMA_kisa)
    data['WMA Uzun'] = wma(data['close'], WMA_uzun)

    # Determine entry and exit points
    data['Entry'] = (data['WMA Kısa'] > data['WMA Uzun']) & (data['WMA Kısa'].shift(1) < data['WMA Uzun'].shift(1))
    data['Exit'] = (data['WMA Kısa'] < data['WMA Uzun']) & (data['WMA Kısa'].shift(1) > data['WMA Uzun'].shift(1))

    data_list = data.iloc[-1].tolist()
    df_bist30_Sonuclar.loc[len(df_bist30_Sonuclar)] =  data_list
    # Display the resulting DataFrame for each stock

df_bist30_Sonuclar.drop(columns=['open','high','low','volume'],inplace=True)
df_bist30_Sonuclar['datetime'] = pd.to_datetime(df_bist30_Sonuclar['datetime']).dt.date
print(df_bist30_Sonuclar)
