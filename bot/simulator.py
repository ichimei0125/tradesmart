from datetime import datetime, timedelta
from typing import Optional

from tradeengine.core.strategies import simple_strategy
from api.crypto.exchange import Exchange
from tools.common import get_now, local_2_utc

class Simulator:
    def __init__(self, exchagne:Exchange):
        self.exchange = exchagne

    def run(self, since:Optional[datetime]=None) -> None:
        """since: default last 90 days"""
        if not since:
            since = get_now() - timedelta(days=90)
        since = local_2_utc(since)

        data = self.exchange.fetch_candlesticks(since)
        for symbol, multi_candlesticks in data.items():
            for interval, candlesticks in multi_candlesticks.items():
                simple_strategy(candlesticks)