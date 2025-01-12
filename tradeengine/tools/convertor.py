from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import numpy as np

from tradeengine.models.candlestick import CandleStick
from tradeengine.models.trade import Trade, sort_trades_desc

def datetime_to_str(date:datetime) -> str:
    return date.strftime('%Y-%m-%d %H:%M:%S')

class ConvertTradeToCandleStick:
    def __init__(self, trades:List[Trade], cached:Optional[List[CandleStick]]=None, check_trades_order:bool=True):
        if check_trades_order:
            trades = sort_trades_desc(trades)
        self.trades = trades
        self.cached = cached

    def by_seconds(self, second:int) -> Tuple[str, List[CandleStick]]:
        if type(second) is not int or not (second > 0 and second <=60):
            raise ValueError(f'second must int and in 1~60, wrong second: {second}')
        lastest_open_time_second = (self.trades[0].execution_time.second // second) * second
        open_time = self.trades[0].execution_time.replace(second=lastest_open_time_second, microsecond=0)
        interval = timedelta(seconds=second)
        return f'{second}s', self._convert(open_time, interval)

    def by_minutes(self, minute:int) -> Tuple[List[CandleStick], timedelta]:
        if type(minute) is not int or not (minute > 0 and minute <= 60):
            raise ValueError(f'minute must int and in 1~60, wrong minute: {minute}')
        lastest_open_time_minute = (self.trades[0].execution_time.minute // minute) * minute
        open_time = self.trades[0].execution_time.replace(minute=lastest_open_time_minute, second=0, microsecond=0)
        interval = timedelta(minutes=minute)
        return f'{minute}m', self._convert(open_time, interval)
    
    def by_hours(self, hour:int) -> Tuple[List[CandleStick], timedelta]:
        if type(hour) is not int or not (hour > 0 and hour <= 24):
            raise ValueError(f'hour must int and in 1~24, wrong hour: {hour}')
        lastest_open_time_hour = (self.trades[0].execution_time.hour // hour) * hour
        open_time = self.trades[0].execution_time.replace(hour=lastest_open_time_hour, minute=0, second=0, microsecond=0)
        interval = timedelta(hours=hour)
        return f'{hour}h', self._convert(open_time, interval)

    def by_days(self, day:int) -> Tuple[List[CandleStick], timedelta]:
        if type(day) is not int or not (day > 0 and day <= 28):
            raise ValueError(f'day must int and in 1~28, wrong day: {day}')
        lastest_open_time_day = (self.trades[0].execution_time.day // day) * day
        open_time = self.trades[0].execution_time.replace(day=lastest_open_time_day, hour=0 ,minute=0, second=0, microsecond=0)
        interval = timedelta(days=day)
        return f'{day}d', self._convert(open_time, interval)

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