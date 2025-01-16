from copy import copy
from typing import List
from enum import Enum
from tradeengine.models.candlestick import CandleStick, Indicator, get_indicator
import numpy as np

class TradeStatus(Enum):
    BUY = 1,
    SELL = 2,
    HOLD = 0,

def simple_strategy(candlesticks:List[CandleStick]) -> TradeStatus:
    """bascily for test, do not use this for real trading"""
    indicators = get_indicator(candlesticks)

    if indicators[1].Stoch_D < 25 or indicators[1].Stoch_K < 25:
        if candlesticks[1].Close <= indicators[1].BBBands_Minus_2 and candlesticks[0].Close >= indicators[0].BBBands_Minus_2:
            return TradeStatus.BUY

    if indicators[1].Stoch_D > 75 or indicators[1].Stoch_K > 75:
        if candlesticks[1].Close >= indicators[1].BBBands_Plus_2 and candlesticks[0].Close <= indicators[0].BBBands_Plus_2:
            return TradeStatus.SELL

    return TradeStatus.HOLD

def tech_strategy(candlesticks:List[CandleStick], indicators:List[Indicator]) -> TradeStatus:

    is_positive_env = indicators[0].SMA_20 > indicators[2].SMA_20
    is_negative_env = indicators[0].SMA_20 < indicators[2].SMA_20

    # rsi
    is_buy_rsi_cross = indicators[0].RSI > indicators[0].RSI_MA
    is_sell_rsi_cross = indicators[0].RSI < indicators[0].RSI_MA
    is_buy_rsi_val = indicators[0].RSI < 30 + 2
    is_sell_rsi_val = indicators[0].RSI > 70 - 2

    # stock
    is_buy_stoch_cross = indicators[0].Stoch_K > indicators[0].Stoch_D
    is_sell_stoch_cross = indicators[0].Stoch_K < indicators[0].Stoch_D
    is_buy_stoch_val = indicators[0].Stoch_K < (20 + 2) or indicators[0].Stoch_D < (20 + 2)
    is_sell_stoch_val = indicators[0].Stoch_K > (80 -2) or indicators[0].Stoch_D > (80 - 2)

    # BBands
    is_buy_bbands = candlesticks[0].Close < indicators[0].BBBands_Minus_2
    is_sell_bbands = candlesticks[0].Close > indicators[0].BBBands_Plus_2

    # buy more, sell less
    if is_positive_env:
        if any([is_buy_rsi_cross, is_buy_rsi_val, is_buy_stoch_val, is_buy_bbands]):
            return TradeStatus.BUY
        
        if is_sell_rsi_val or is_sell_stoch_val:
            return TradeStatus.SELL

    # buy less, sell more
    if is_negative_env:
        if is_buy_rsi_val or is_buy_stoch_val:
            return TradeStatus.BUY
        
        if any([is_sell_rsi_cross, is_sell_rsi_val, is_sell_stoch_val, is_sell_bbands]):
            return TradeStatus.SELL

    return TradeStatus.HOLD