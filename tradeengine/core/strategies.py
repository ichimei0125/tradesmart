from copy import copy
from typing import List
from enum import Enum
from tradeengine.models.trade import CandleStick, get_indicator
import numpy as np

class TradeStatus(Enum):
    BUY = 1,
    SELL = 2,
    HOLD = 0,

def simple_strategy(candlesticks:List[CandleStick]) -> TradeStatus:
    """bascily for test, do not use this for real trading"""
    indicators = get_indicator(candlesticks)

    if indicators[1].Stoch_D < 25 or indicators[1].Stoch_K < 25:
        if candlesticks[1].close <= indicators[1].BBBands_Minus_2 and candlesticks[0].close >= indicators[0].BBBands_Minus_2:
            return TradeStatus.BUY

    if indicators[1].Stoch_D > 75 or indicators[1].Stoch_K > 75:
        if candlesticks[1].close >= indicators[1].BBBands_Plus_2 and candlesticks[0].close <= indicators[0].BBBands_Plus_2:
            return TradeStatus.SELL

    return TradeStatus.HOLD