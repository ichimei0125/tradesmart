from datetime import datetime, timedelta
from typing import Optional
import os

from config.config import Config
from api.crypto.exchange import Exchange
from tools.common import get_now, local_2_utc
from tools.constants import MarketInfo
from tradeengine.simulator.simulator import Simulator as EngineSimulator
from tradeengine.tools.convertor import datetime_to_str

class Simulator:
    def __init__(self, exchagne:Exchange):
        self.exchange = exchagne
        self.config = Config()


    def run(self, since:Optional[datetime]=None) -> None:
        """since: default last 90 days"""
        if not since:
            since = get_now() - timedelta(days=90)
        since = local_2_utc(since)

        data = self.exchange.fetch_trades(since)
        for symbol, trades in data.items():
            print(symbol)
            # TODO: multi candlestick
            engine_simulator = EngineSimulator(
                trades=trades,
                init_money=50000,
                invest_money=self.config.bitflyer.invest_money,
                loss_cut=self.config.bitflyer.loss_cut,
            )

            engine_simulator.run(MarketInfo.CANDLESTICK_NUMS, 3, self.exchange.fetch_data_interval_minute)
