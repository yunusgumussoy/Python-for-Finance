# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 02:43:18 2024

@author: Yunus
"""

# !pip install git+https://github.com/rongardF/tvdatafeed

import pandas as pd
from tvDatafeed import TvDatafeed, Interval

tv = TvDatafeed()

# Stocks
bist100 = [
    "AEFES", "AGHOL", "AGROT", "AKBNK", "AKFGY", "AKFYE", "AKSA", "AKSEN", "ALARK", "ALFAS",
    "ARCLK", "ARDYZ", "ASELS", "ASTOR", "BERA", "BFREN", "BIMAS", "BINHO", "BRSAN", "BRYAT",
    "BTCIM", "CANTE", "CCOLA", "CIMSA", "CWENE", "DOAS", "DOHOL", "ECILC", "ECZYT", "EGEEN",
    "EKGYO", "ENERY", "ENJSA", "ENKAI", "EREGL", "EUPWR", "EUREN", "FROTO", "GARAN", "GESAN",
    "GOLTS", "GUBRF", "HALKB", "HEKTS", "ISCTR", "ISGYO", "ISMEN", "IZENR", "KAYSE", "KCAER",
    "KCHOL", "KLSER", "KONTR", "KONYA", "KOZAA", "KOZAL", "KRDMD", "KTLEV", "LMKDC", "MAVI",
    "MGROS", "MIATK", "OBAMS", "ODAS", "OTKAR", "OYAKC", "PEKGY", "PETKM", "PGSUS", "QUAGR",
    "REEDR", "SAHOL", "SASA", "SDTTR", "SISE", "SKBNK", "SMRTG", "SOKM", "TABGD", "TAVHL",
    "TCELL", "THYAO", "TKFEN", "TKNSA", "TMSN", "TOASO", "TSKB", "TTKOM", "TTRAK", "TUKAS",
    "TUPRS", "TURSG", "ULKER", "VAKBN", "VESBE", "VESTL", "YEOTK", "YKBNK", "YYLGD", "ZOREN"
]

# Dataframe for data
sonuclar = pd.DataFrame(columns=['Hisse', 'En_Iyi_Alim_Gunu', 'En_Iyi_Satim_Gunu'])

for hisse in bist100:
    try:
        # Daily data
        veri = tv.get_hist(symbol=hisse, exchange='BIST', interval=Interval.in_daily, n_bars=5000)

        if veri.empty:
            print(f"{hisse} için veri yok")
            continue

        # Month and Day
        veri['Ay'] = veri.index.month
        veri['Ayin_Gunu'] = veri.index.day

        # 0-1 Scaling
        veri['Olcekli_Dusuk'] = veri.groupby('Ay')['low'].transform(lambda x: (x - x.min()) / (x.max() - x.min()))
        veri['Olcekli_Yuksek'] = veri.groupby('Ay')['high'].transform(lambda x: (x - x.min()) / (x.max() - x.min()))

        # Average for every month day
        gunluk_analiz = veri.groupby('Ayin_Gunu').agg({
            'Olcekli_Dusuk': 'mean',
            'Olcekli_Yuksek': 'mean'
        }).rename(columns={
            'Olcekli_Dusuk': 'Ort_Olcekli_Dusuk',
            'Olcekli_Yuksek': 'Ort_Olcekli_Yuksek'
        })

        # Best day for buying and selling
        en_iyi_alim_gunu = gunluk_analiz['Ort_Olcekli_Dusuk'].idxmin()
        en_iyi_satim_gunu = gunluk_analiz['Ort_Olcekli_Yuksek'].idxmax()

        # Results to DataFrame
        sonuclar = pd.concat([sonuclar, pd.DataFrame({
            'Hisse': [hisse],
            'En_Iyi_Alim_Gunu': [en_iyi_alim_gunu],
            'En_Iyi_Satim_Gunu': [en_iyi_satim_gunu]
        })], ignore_index=True)

    except Exception as e:
        print(f"{hisse} için hata: {e}")

# Results
print(sonuclar.to_string(index=False))