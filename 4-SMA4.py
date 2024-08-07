# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 00:12:52 2024

@author: Yunus
"""

from typing_extensions import DefaultDict
# pip install git+https://github.com/rongardF/tvdatafeed

import pandas as pd
from tvDatafeed import TvDatafeed, Interval

# Initialize TradingView data feed
tv = TvDatafeed()

# Define the best SMA periods for each stock
df_bist30 = [
    {"Hisse Adı": "AKBNK", "SMA Kısa": 18.0, "SMA Uzun": 22.0},
    {"Hisse Adı": "ALARK", "SMA Kısa": 5.0 , "SMA Uzun": 38.0},
    {"Hisse Adı": "ASELS", "SMA Kısa": 44.0, "SMA Uzun": 48.0},
    {"Hisse Adı": "ASTOR", "SMA Kısa": 15.0, "SMA Uzun": 17.0},
    {"Hisse Adı": "BIMAS", "SMA Kısa": 17.0, "SMA Uzun": 25.0},
    {"Hisse Adı": "BRSAN", "SMA Kısa": 22.0, "SMA Uzun": 36.0},
    {"Hisse Adı": "DOAS" , "SMA Kısa": 10.0, "SMA Uzun": 47.0},
    {"Hisse Adı": "EKGYO", "SMA Kısa": 5.0 , "SMA Uzun": 9.0},
    {"Hisse Adı": "ENKAI", "SMA Kısa": 47.0, "SMA Uzun": 49.00},
    {"Hisse Adı": "EREGL", "SMA Kısa": 21.0, "SMA Uzun": 28.0},
    {"Hisse Adı": "FROTO", "SMA Kısa": 32.0, "SMA Uzun": 34.0},
    {"Hisse Adı": "GARAN", "SMA Kısa": 22.0, "SMA Uzun": 33.0},
    {"Hisse Adı": "GUBRF", "SMA Kısa": 5.0 , "SMA Uzun": 11.0},
    {"Hisse Adı": "HEKTS", "SMA Kısa": 28.0, "SMA Uzun": 33.0},
    {"Hisse Adı": "ISCTR", "SMA Kısa": 7.0 , "SMA Uzun": 48.0},
    {"Hisse Adı": "KCHOL", "SMA Kısa": 45.0, "SMA Uzun": 49.0},
    {"Hisse Adı": "KONTR", "SMA Kısa": 5.0 , "SMA Uzun": 10.0},
    {"Hisse Adı": "KOZAL", "SMA Kısa": 16.0, "SMA Uzun": 23.0},
    {"Hisse Adı": "KRDMD", "SMA Kısa": 25.0, "SMA Uzun": 27.0},
    {"Hisse Adı": "OYAKC", "SMA Kısa": 19.0, "SMA Uzun": 31.0},
    {"Hisse Adı": "PETKM", "SMA Kısa": 19.0, "SMA Uzun": 37.0},
    {"Hisse Adı": "PGSUS", "SMA Kısa": 25.0, "SMA Uzun": 26.0},
    {"Hisse Adı": "SAHOL", "SMA Kısa": 19.0, "SMA Uzun": 25.0},
    {"Hisse Adı": "SASA" , "SMA Kısa": 6.0 , "SMA Uzun": 28.0},
    {"Hisse Adı": "SISE" , "SMA Kısa": 16.0, "SMA Uzun": 25.0},
    {"Hisse Adı": "TCELL", "SMA Kısa": 13.0, "SMA Uzun": 34.0},
    {"Hisse Adı": "THYAO", "SMA Kısa": 7.0 , "SMA Uzun": 44.0},
    {"Hisse Adı": "TOASO", "SMA Kısa": 31.0, "SMA Uzun": 32.0},
    {"Hisse Adı": "TUPRS", "SMA Kısa": 24.0, "SMA Uzun": 25.0},
    {"Hisse Adı": "YKBNK", "SMA Kısa": 5.0 , "SMA Uzun": 7.0}
]

# Creating DataFrame
df_bist30 = pd.DataFrame(df_bist30)

# Displaying the DataFrame
print(df_bist30)

# For recording the results, dataframe
df_bist30_Sonuclar = pd.DataFrame(columns=['datetime','Hisse Adı','open','high','low','close','volume','SMA Kısa', 'SMA Uzun','Entry','Exit'])


def sma(series, length):
    return series.rolling(window=length).mean()

# Loop through each stock in the DataFrame
for i in range(len(df_bist30)):
    hisse_adi = df_bist30.loc[i, 'Hisse Adı']
    sma_kisa = df_bist30.loc[i, 'SMA Kısa'].astype(int)
    sma_uzun = df_bist30.loc[i, 'SMA Uzun'].astype(int)

    # Retrieve historical data
    data = tv.get_hist(symbol=hisse_adi, exchange='BIST', interval=Interval.in_daily, n_bars=1000)
    data.reset_index(inplace=True)

    # Calculate short and long SMAs
    data['SMA Kısa'] = sma(data['close'], sma_kisa)
    data['SMA Uzun'] = sma(data['close'], sma_uzun)

    # Determine entry and exit points
    data['Entry'] = (data['SMA Kısa'] > data['SMA Uzun']) & (data['SMA Kısa'].shift(1) < data['SMA Uzun'].shift(1))
    data['Exit'] = (data['SMA Kısa'] < data['SMA Uzun']) & (data['SMA Kısa'].shift(1) > data['SMA Uzun'].shift(1))

    data_list = data.iloc[-1].tolist()
    df_bist30_Sonuclar.loc[len(df_bist30_Sonuclar)] =  data_list
    # Display the resulting DataFrame for each stock

df_bist30_Sonuclar.drop(columns=['open','high','low','volume'],inplace=True)
df_bist30_Sonuclar['datetime'] = pd.to_datetime(df_bist30_Sonuclar['datetime']).dt.date
print(df_bist30_Sonuclar)
