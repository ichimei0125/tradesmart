from dataclasses import dataclass
from datetime import datetime
from typing import List

import numpy as np
import talib
from talib import MA_Type

@dataclass
class CandleStick:
    Open: float
    Close: float
    High: float
    Low: float
    Volume: float
    Opentime: datetime # 最初取引の時刻。

    def __post_init__(self):
        self.Volume = round(self.Volume, 3)

@dataclass
class Indicator:
    BBBands_Plus_2: float
    BBBands_Plus_3: float
    BBBands_Minus_2: float
    BBBands_Minus_3: float
    Stoch_K: float
    Stoch_D: float
    SMA_20: float
    SMA_200: float
    RSI: float
    MACD: float
    MACD_SIGNAL: float
    MACD_HIST: float
    Opentime: datetime # 最初取引の時刻。

def get_indicator(candlesticks:List[CandleStick]) -> List[Indicator]:
    opens = []
    closes = []
    highs = []
    lows = []
    opentimes = []
    for i in range(len(candlesticks)-1, -1, -1):
        opens = np.append(opens, candlesticks[i].Open)
        closes = np.append(closes, candlesticks[i].Close)
        highs = np.append(highs, candlesticks[i].High)
        lows = np.append(lows, candlesticks[i].Low)
        opentimes = np.append(opentimes, candlesticks[i].Opentime)

    # Stoch
    stoch_k, stoch_d = talib.STOCH(
        high=highs, low=lows, close=closes,
        fastk_period=14, slowk_period=3, slowk_matype= MA_Type.SMA,
        slowd_period=3, slowd_matype= MA_Type.SMA)

    # BBand
    bband_plus_2, _, bband_minus_2 =talib.BBANDS(real=closes, timeperiod=20, nbdevup=2, nbdevdn=2, matype=MA_Type.SMA)
    bband_plus_3, _, bband_minus_3 =talib.BBANDS(real=closes, timeperiod=20, nbdevup=3, nbdevdn=3, matype=MA_Type.SMA)

    # SMA
    sma_20 = talib.SMA(real=closes, timeperiod=20)
    sma_200 = talib.SMA(real=closes, timeperiod=200)

    # RSI
    rsi = talib.RSI(real=closes, timeperiod=14)

    # MACD
    macd, macdsignal, macdhist = talib.MACD(real=closes, fastperiod=12, slowperiod=26, signalperiod=9)

    # result
    res = []
    for i in range(len(candlesticks)-1, -1, -1):
        res.append(Indicator(
            BBBands_Plus_2 = bband_plus_2[i],
            BBBands_Plus_3 = bband_plus_3[i],
            BBBands_Minus_2 = bband_minus_2[i],
            BBBands_Minus_3 = bband_minus_3[i],
            Stoch_K = stoch_k[i],
            Stoch_D = stoch_d[i],
            SMA_20=sma_20[i],
            SMA_200=sma_200[i],
            RSI=rsi[i],
            MACD=macd[i],
            MACD_SIGNAL=macdsignal[i],
            MACD_HIST=macdhist[i],
            Opentime = opentimes[i],
        ))

    return res

def get_candlestick_prices(candlesticks:List[CandleStick], mode:str='close') -> List[float]:
    """mode must be \"open\", \"close\", \"high\", \"low\", \"opentime\""""
    match mode:
        case 'close':
            return [ candlestick.Close for candlestick in candlesticks]
        case 'open':
            return [ candlestick.Open for candlestick in candlesticks]
        case 'high':
            return [ candlestick.High for candlestick in candlesticks]
        case 'low':
            return [ candlestick.Low for candlestick in candlesticks]
        case 'opentime':
            return [ candlestick.Opentime for candlestick in candlesticks]
        case _:
            raise ValueError(f'invaid mode: {mode}, mode must be \"open\", \"close\", \"high\", \"low\", \"opentime\"')
