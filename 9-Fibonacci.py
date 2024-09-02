# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 01:43:09 2024

@author: Yunus
"""

# Requirements
# pip install git+https://github.com/rongardF/tvdatafeed

# Libraries
import numpy as np
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from scipy.signal import argrelextrema

# TvDatafeed
tv = TvDatafeed()

# Stock Names
bist100 = [
        "AEFES","AGHOL","AGROT","AKBNK","AKFGY","AKFYE","AKSA","AKSEN","ALARK","ALFAS",
        "ARCLK","ARDYZ","ASELS","ASTOR","BERA","BFREN","BIMAS","BINHO","BRSAN","BRYAT",
        "BTCIM","CANTE","CCOLA","CIMSA","CWENE","DOAS","DOHOL","ECILC","ECZYT","EGEEN",
        "EKGYO","ENERY","ENJSA","ENKAI","EREGL","EUPWR","EUREN","FROTO","GARAN","GESAN",
        "GOLTS","GUBRF","HALKB","HEKTS","ISCTR","ISGYO","ISMEN","IZENR","KAYSE","KCAER",
        "KCHOL","KLSER","KONTR","KONYA","KOZAA","KOZAL","KRDMD","KTLEV","LMKDC","MAVI",
        "MGROS","MIATK","OBAMS","ODAS","OTKAR","OYAKC","PEKGY","PETKM","PGSUS","QUAGR",
        "REEDR","SAHOL","SASA","SDTTR","SISE","SKBNK","SMRTG","SOKM","TABGD","TAVHL",
        "TCELL","THYAO","TKFEN","TKNSA","TMSN","TOASO","TSKB","TTKOM","TTRAK","TUKAS",
        "TUPRS","TURSG","ULKER","VAKBN","VESBE","VESTL","YEOTK","YKBNK","YYLGD","ZOREN"
    ]

# New Dataframe for data of stocks
df_bist=pd.DataFrame(columns=["datetime","Hisse","val","type","Fibo0","Fibo236","Fibo382","Fibo618","Fibo100",
                              "Range","Pct_Fibo0","Pct_Fibo236","Pct_Fibo382","Pct_Fibo618","Pct_Fibo100"])

# Fibonacci Levels
def calc_fibo(X, Y):
    A = min(X, Y)
    B = max(X, Y)
    Fibo3 = B - (B - A) * 0.382
    Fibo2 = B - (B - A) * 0.618
    Fibo1 = B - (B - A) * 0.764
    Fibo_List = [A, Fibo1, Fibo2, Fibo3, B]
    return Fibo_List

# Calculation of distance
def calculate_percentage_distance(current, levels):
    percentages = [(current - level) / current * 100 for level in levels]
    percentages = [round(abs(percentage), 2) for percentage in percentages]
    return percentages

# Data Preparing
for Hisse in bist100:
    try:
        # Data
        data = tv.get_hist(symbol=Hisse, exchange='BIST', interval=Interval.in_daily, n_bars=1000)

        # Calculation of turning from High
        hh_indices = argrelextrema(data['high'].values, comparator=np.greater, order=5)[0]

        # List for Zigzag points
        zigzag_points = []

        # Finding low points between highs
        for i in range(len(hh_indices)):
            # Add the high point
            high_idx = data.index[hh_indices[i]]
            zigzag_points.append((high_idx, data['high'].loc[high_idx], 'high'))

            if i < len(hh_indices) - 1:
                next_high_idx = data.index[hh_indices[i + 1]]
                low_range = data.loc[high_idx:next_high_idx]
                low_range = low_range[low_range.index != high_idx]
                low_range = low_range[low_range.index < next_high_idx]
                if not low_range.empty:
                    low_idx = low_range['low'].idxmin()
                    if low_idx != high_idx:
                        zigzag_points.append((low_idx, data['low'].loc[low_idx], 'low'))

        # Last data
        last_time = data.index[-1]
        last_val = data['close'].iloc[-1]
        last_type = 'current'

        # Merging Zigzag points and last data
        zigzag_points.append((last_time, last_val, last_type))

        # New dataframe for Zigzag points
        df_zigzag = pd.DataFrame(zigzag_points, columns=['datetime', 'val', 'type'])

        # Dataframe ordering historically
        df_zigzag.sort_values(by='datetime', inplace=True)
        df_zigzag.reset_index(drop=True, inplace=True)

        # Taking the last 3 data
        df_zigzag = df_zigzag.tail(3).reset_index(drop=True)

        # new columns for Fibonacci levels
        df_zigzag[['Fibo0', 'Fibo236', 'Fibo382', 'Fibo618', 'Fibo100']] = np.nan

        # Checking columns consist of 3 columns, calculating Fibonacci levels
        if len(df_zigzag) >= 3:
            df_zigzag.insert(1, 'Hisse', Hisse)
            X = df_zigzag.loc[0, 'val']
            Y = df_zigzag.loc[1, 'val']
            C = df_zigzag.loc[2,'val']

            # X < C < Y
            if min(X, Y) <= C <= max(X, Y):
                Fibo_List = calc_fibo(Y, X) # Check
                df_zigzag.loc[2, 'Fibo0'] = round(Fibo_List[0],2)
                df_zigzag.loc[2, 'Fibo236'] = round(Fibo_List[1],2)
                df_zigzag.loc[2, 'Fibo382'] = round(Fibo_List[2],2)
                df_zigzag.loc[2, 'Fibo618'] = round(Fibo_List[3],2)
                df_zigzag.loc[2, 'Fibo100'] = round(Fibo_List[4],2)
                df_zigzag.loc[2, 'Range'] = round(100 * (X - Y) / X, 2)

                # Calculating distance of last data to Fibonacci levels
                current_val = df_zigzag.loc[2, 'val']
                fibo_levels = df_zigzag.loc[2, ['Fibo0', 'Fibo236', 'Fibo382', 'Fibo618', 'Fibo100']].values
                percentages = calculate_percentage_distance(current_val, fibo_levels)
                df_zigzag.loc[2, ['Pct_Fibo0', 'Pct_Fibo236', 'Pct_Fibo382', 'Pct_Fibo618', 'Pct_Fibo100']] = percentages
                last_row = df_zigzag.iloc[-1].tolist()
                print(last_row[1:])
                df_bist.loc[len(df_bist)] = last_row
    except:
        pass

df_fibo236 = df_bist[['datetime', 'Hisse','val', 'Fibo236','Pct_Fibo236']].copy()
df_fibo382 = df_bist[['datetime', 'Hisse','val', 'Fibo382','Pct_Fibo382']].copy()
df_fibo618 = df_bist[['datetime', 'Hisse','val', 'Fibo618','Pct_Fibo618']].copy()
print(df_fibo382)

# Percentage distances ascending order
df_fibo236_sorted = df_fibo236.sort_values(by='Pct_Fibo236').reset_index(drop=True)
df_fibo382_sorted = df_fibo382.sort_values(by='Pct_Fibo382').reset_index(drop=True)
df_fibo618_sorted = df_fibo618.sort_values(by='Pct_Fibo618').reset_index(drop=True)

# Results
print("Fibo236 Yüzdelik Uzaklıkları (Artan Sıra):")
print(df_fibo236_sorted.head(10))

print("\nFibo382 Yüzdelik Uzaklıkları (Artan Sıra):")
print(df_fibo382_sorted.head(10))

print("\nFibo618 Yüzdelik Uzaklıkları (Artan Sıra):")
print(df_fibo618_sorted.head(10))