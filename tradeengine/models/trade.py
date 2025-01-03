from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import heapq
from typing import List, Optional
from numpy import np

class Side(Enum):
    BUY = 'buy'
    SELL = 'sell'
    NONE = ''

@dataclass
class Trade:
    # exchange: str
    # symbol: str
    id: str
    side: Side
    size: float
    execution_time: datetime
    price: float

@dataclass
class CandleStick:
    # exchange: str
    # symbol: str
    open: float
    close: float
    high: float
    low: float
    volume: int
    opentime: datetime # 最初取引の時刻。

def sort_trades_desc(trades: List[Trade]) -> List[Trade]:
    if all(
        trades[i].execution_time >= trades[i + 1].execution_time
        for i in range(len(trades) - 1)
    ):
        # check sorted, O(n)
        return trades
    elif len(trades) < 10000:
        # O(nlogn)
        return _sort_trades_desc(trades)
    else: 
        # O(logn) push/pop, O(n) create
        return _sort_trades_desc_heapq(trades)

def _sort_trades_desc(trades: List[Trade]) -> List[Trade]:
    """sort trades by execution_time DESC, use this when len(trades) < 10000"""
    return sorted(trades, key=lambda trade: trade.execution_time, reverse=True)

def _sort_trades_desc_heapq(trades: List[Trade]) -> List[Trade]:
    """sort trades by execution_time DESC, use this when len(trades) > 10000"""
    heap = []
    for trade in trades:
        heapq.heappush(heap, (-trade.execution_time.timestamp(), trade))
    
    sorted_trades = []
    while heap:
        _, trade = heapq.heappop(heap)
        sorted_trades.append(trade)
    
    return sorted_trades

def trade_2_candlestick_minutes(trades:List[Trade], minute:int, cached:Optional[List[CandleStick]]=None) -> List[CandleStick]:
    trades = sort_trades_desc(trades)
    lastest_open_time_minute = (trades[0].execution_time.minute // minute) * minute
    open_time = trades[0].execution_time.replace(minute=lastest_open_time_minute, second=0, microsecond=0)

    candlesticks = []
    tmp_trades = []
    for i in range(len(trades)):
        if trades[i].execution_time < open_time:
            new_candlestick = CandleStick(
                open=tmp_trades[0],
                close=tmp_trades[-1],
                high=np.max(tmp_trades),
                low=np.min(tmp_trades),
                volume=tmp_trades.size,
                opentime=open_time,
            )
            candlesticks.append(new_candlestick)
            open_time -= timedelta(minutes=minute)
            tmp_trades = []

        if cached and open_time == cached[0].opentime: # if open_time != cached[0].opentime means different time scale, won't use cached data
            candlesticks += cached[1:]
            break

        tmp_trades = np.append(tmp_trades, trades[i])
    return candlesticks

def trade_2_candlestick_days(trades:List[Trade], day:int, cached:Optional[List[CandleStick]]) -> List[CandleStick]:
    trades = sort_trades_desc(trades)
    open_time = trades[0].execution_time.replace(hour=0 ,minute=0, second=0, microsecond=0)

    candlesticks = []
    tmp_trades = []
    for i in range(len(trades)):
        if trades[i].execution_time < open_time:
            new_candlestick = CandleStick(
                open=tmp_trades[0],
                close=tmp_trades[-1],
                high=np.max(tmp_trades),
                low=np.min(tmp_trades),
                volume=tmp_trades.size,
                opentime=open_time,
            )
            candlesticks.append(new_candlestick)
            open_time -= timedelta(days=day)
            tmp_trades = []

        if cached and open_time == cached[0].opentime: # if open_time != cached[0].opentime means different time scale, won't use cached data
            candlesticks += cached[1:]
            break

        tmp_trades = np.append(tmp_trades, trades[i])
    return candlesticks

