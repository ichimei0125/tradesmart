from copy import copy
from typing import List
from enum import Enum
from tradeengine.models.trade import CandleStick, Indicator
import talib
from talib import MA_Type
import numpy as np

class TradeStatus(Enum):
    BUY = 0,
    SELL = 1,
    DO_NOTHING = 9,

def get_indicator(candlesticks:List[CandleStick]) -> List[Indicator]:
    opens = []
    closes = []
    highs = []
    lows = []
    opentimes = []
    for i in range(len(candlesticks)-1, -1, -1):
        opens = np.append(opens, candlesticks[i].open)
        closes = np.append(closes, candlesticks[i].close)
        highs = np.append(highs, candlesticks[i].high)
        lows = np.append(lows, candlesticks[i].low)
        opentimes = np.append(opentimes, candlesticks[i].opentime)

    # Stoch
    stoch_k, stoch_d = talib.STOCH(
        high=highs, low=lows, close=closes,
        fastk_period=14, slowk_period=3, slowk_matype= MA_Type.SMA,
        slowd_period=3, slowd_matype= MA_Type.SMA)

    # BBand
    bband_plus_2, _, bband_minus_2 =talib.BBANDS(real=closes, timeperiod=20, nbdevup=2, nbdevdn=2, matype=MA_Type.SMA)
    bband_plus_3, _, bband_minus_3 =talib.BBANDS(real=closes, timeperiod=20, nbdevup=3, nbdevdn=3, matype=MA_Type.SMA)

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
            opentime = opentimes[i],
        ))

    return res


def simple_strategy(candlesticks:List[CandleStick]) -> TradeStatus:
    indicators = get_indicator(candlesticks)

    if indicators[1].Stoch_D < 25 or indicators[1].Stoch_K < 25:
        if candlesticks[1].close <= indicators[1].BBBands_Minus_2 and candlesticks[0].close >= indicators[0].BBBands_Minus_2:
            return TradeStatus.BUY

    if indicators[1].Stoch_D > 75 or indicators[1].Stoch_K > 75:
        if candlesticks[1].close >= indicators[1].BBBands_Plus_2 and candlesticks[0].close <= indicators[0].BBBands_Plus_2:
            return TradeStatus.SELL

    return TradeStatus.DO_NOTHING