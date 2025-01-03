from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import heapq
from typing import List, Optional
import numpy as np

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
    volume: float
    opentime: datetime # 最初取引の時刻。

    def __post_init__(self):
        self.volume = round(self.volume, 3)

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

class ConverterTradeCandleStick:
    def __init__(self, trades:List[Trade], cached:Optional[List[CandleStick]]=None):
        self.trades = sort_trades_desc(trades)
        self.cached = cached

    def by_seconds(self, second:int) -> List[CandleStick]:
        if type(second) is not int or not (second > 0 and second <=60):
            raise ValueError(f'second must int and in 1~60, wrong second: {second}')
        lastest_open_time_second = (self.trades[0].execution_time.second // second) * second
        open_time = self.trades[0].execution_time.replace(second=lastest_open_time_second, microsecond=0)
        interval = timedelta(seconds=second)
        return self._convert(open_time, interval)

    def by_minutes(self, minute:int) -> List[CandleStick]:
        if type(minute) is not int or not (minute > 0 and minute <= 60):
            raise ValueError(f'minute must int and in 1~60, wrong minute: {minute}')
        lastest_open_time_minute = (self.trades[0].execution_time.minute // minute) * minute
        open_time = self.trades[0].execution_time.replace(minute=lastest_open_time_minute, second=0, microsecond=0)
        interval = timedelta(minutes=minute)
        return self._convert(open_time, interval)
    
    def by_hours(self, hour:int) -> List[CandleStick]:
        if type(hour) is not int or not (hour > 0 and hour <= 24):
            raise ValueError(f'hour must int and in 1~24, wrong hour: {hour}')
        lastest_open_time_hour = (self.trades[0].execution_time.hour // hour) * hour
        open_time = self.trades[0].execution_time.replace(hour=lastest_open_time_hour, minute=0, second=0, microsecond=0)
        interval = timedelta(hours=hour)
        return self._convert(open_time, interval)

    def by_days(self, day:int) -> List[CandleStick]:
        if type(day) is not int or not (day > 0 and day <= 28):
            raise ValueError(f'day must int and in 1~28, wrong day: {day}')
        lastest_open_time_day = (self.trades[0].execution_time.day // day) * day
        open_time = self.trades[0].execution_time.replace(day=lastest_open_time_day, hour=0 ,minute=0, second=0, microsecond=0)
        interval = timedelta(days=day)
        return self._convert(open_time, interval)

    def _convert(self, open_time:datetime, interval:timedelta) -> List[CandleStick]:
        candlesticks = []
        tmp_trades_price = []
        tmp_volume:float = 0
        for i in range(len(self.trades)):
            if self.trades[i].execution_time < open_time:
                new_candlestick = CandleStick(
                    open=tmp_trades_price[-1],
                    close=tmp_trades_price[0],
                    high=np.max(tmp_trades_price),
                    low=np.min(tmp_trades_price),
                    volume=tmp_volume,
                    opentime=open_time,
                )
                candlesticks.append(new_candlestick)
                # init first element
                open_time -= interval
                tmp_trades_price = [self.trades[i].price]
                tmp_volume = self.trades[i].size

            if self.cached and open_time == self.cached[0].opentime: # if open_time != cached[0].opentime means different time scale, won't use cached data
                candlesticks += self.cached[1:]
                break

            tmp_trades_price = np.append(tmp_trades_price, self.trades[i].price)
            tmp_volume += self.trades[i].size
        return candlesticks
