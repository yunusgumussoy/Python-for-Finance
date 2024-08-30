# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 00:44:08 2024

@author: Yunus
"""

from typing_extensions import DefaultDict
# pip install git+https://github.com/rongardF/tvdatafeed

import pandas as pd
from tvDatafeed import TvDatafeed, Interval

# Initialize TradingView data feed
tv = TvDatafeed()

# Define the best EMA periods for each stock
df_bist30 = [
    {"Hisse Adı": "AKBNK", "EMA Kısa": 42.0, "EMA Uzun": 50.0},
    {"Hisse Adı": "ALARK", "EMA Kısa": 11.0, "EMA Uzun": 27.0},
    {"Hisse Adı": "ASELS", "EMA Kısa": 30.0, "EMA Uzun": 49.0},
    {"Hisse Adı": "ASTOR", "EMA Kısa": 13.0, "EMA Uzun": 16.0},
    {"Hisse Adı": "BIMAS", "EMA Kısa": 49.0, "EMA Uzun": 50.0},
    {"Hisse Adı": "BRSAN", "EMA Kısa": 19.0, "EMA Uzun": 41.0},
    {"Hisse Adı": "DOAS" , "EMA Kısa": 14.0, "EMA Uzun": 36.0},
    {"Hisse Adı": "EKGYO", "EMA Kısa":  5.0, "EMA Uzun":  6.0},
    {"Hisse Adı": "ENKAI", "EMA Kısa": 10.0, "EMA Uzun": 16.0},
    {"Hisse Adı": "EREGL", "EMA Kısa":  7.0, "EMA Uzun":  19.0},
    {"Hisse Adı": "FROTO", "EMA Kısa": 49.0, "EMA Uzun": 50.0},
    {"Hisse Adı": "GARAN", "EMA Kısa": 46.0, "EMA Uzun": 48.0},
    {"Hisse Adı": "GUBRF", "EMA Kısa":  9.0, "EMA Uzun": 48.0},
    {"Hisse Adı": "HEKTS", "EMA Kısa": 38.0, "EMA Uzun": 39.0},
    {"Hisse Adı": "ISCTR", "EMA Kısa": 37.0, "EMA Uzun": 41.0},
    {"Hisse Adı": "KCHOL", "EMA Kısa": 34.0, "EMA Uzun": 46.0},
    {"Hisse Adı": "KONTR", "EMA Kısa": 12.0, "EMA Uzun": 18.0},
    {"Hisse Adı": "KOZAL", "EMA Kısa":  9.0, "EMA Uzun": 19.0},
    {"Hisse Adı": "KRDMD", "EMA Kısa":  5.0, "EMA Uzun": 21.0},
    {"Hisse Adı": "OYAKC", "EMA Kısa": 48.0, "EMA Uzun": 49.0},
    {"Hisse Adı": "PETKM", "EMA Kısa":  5.0, "EMA Uzun":  7.0},
    {"Hisse Adı": "PGSUS", "EMA Kısa": 10.0, "EMA Uzun": 41.0},
    {"Hisse Adı": "SAHOL", "EMA Kısa": 38.0, "EMA Uzun": 45.0},
    {"Hisse Adı": "SASA" , "EMA Kısa": 40.0, "EMA Uzun": 43.0},
    {"Hisse Adı": "SISE" , "EMA Kısa": 11.0, "EMA Uzun": 40.0},
    {"Hisse Adı": "TCELL", "EMA Kısa":  7.0, "EMA Uzun":  9.0},
    {"Hisse Adı": "THYAO", "EMA Kısa": 23.0, "EMA Uzun": 47.0},
    {"Hisse Adı": "TOASO", "EMA Kısa": 12.0, "EMA Uzun": 40.0},
    {"Hisse Adı": "TUPRS", "EMA Kısa": 37.0, "EMA Uzun": 49.0},
    {"Hisse Adı": "YKBNK", "EMA Kısa":  5.0, "EMA Uzun": 29.0}
]

# Creating DataFrame
df_bist30 = pd.DataFrame(df_bist30)

# Displaying the DataFrame
print(df_bist30)

# New Dataframe for results
df_bist30_Sonuclar = pd.DataFrame(columns=['datetime','Hisse Adı','open','high','low','close','volume','EMA Kısa', 'EMA Uzun','Entry','Exit'])


def ema(series, length):
    calc = series.ewm(span=length, adjust=False).mean()
    return calc

# Loop through each stock in the DataFrame
for i in range(len(df_bist30)):
    hisse_adi = df_bist30.loc[i, 'Hisse Adı']
    EMA_kisa = df_bist30.loc[i, 'EMA Kısa'].astype(int)
    EMA_uzun = df_bist30.loc[i, 'EMA Uzun'].astype(int)

    # Retrieve historical data
    data = tv.get_hist(symbol=hisse_adi, exchange='BIST', interval=Interval.in_daily, n_bars=1000)
    data.reset_index(inplace=True)

    # Calculate short and long EMAs
    data['EMA Kısa'] = ema(data['close'], EMA_kisa)
    data['EMA Uzun'] = ema(data['close'], EMA_uzun)

    # Determine entry and exit points
    data['Entry'] = (data['EMA Kısa'] > data['EMA Uzun']) & (data['EMA Kısa'].shift(1) < data['EMA Uzun'].shift(1))
    data['Exit'] = (data['EMA Kısa'] < data['EMA Uzun']) & (data['EMA Kısa'].shift(1) > data['EMA Uzun'].shift(1))

    data_list = data.iloc[-1].tolist()
    df_bist30_Sonuclar.loc[len(df_bist30_Sonuclar)] =  data_list
    # Display the resulting DataFrame for each stock

df_bist30_Sonuclar.drop(columns=['open','high','low','volume'],inplace=True)
df_bist30_Sonuclar['datetime'] = pd.to_datetime(df_bist30_Sonuclar['datetime']).dt.date
print(df_bist30_Sonuclar)
