from datetime import datetime, timedelta
from typing import List, Optional
import os

from config.config import Config
from api.crypto.exchange import Exchange
from tools.common import get_now, local_2_utc
from tools.constants import MarketInfo
from tradeengine.models.trade import Trade
from tradeengine.simulator.simulator import Simulator as EngineSimulator
from tradeengine.tools.convertor import datetime_to_str

import concurrent.futures
from multiprocessing import cpu_count

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

        with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count()) as executor:
            futures = [executor.submit(self._engin_simulatro_run, trades, symbol) for symbol, trades in data.items()]
            concurrent.futures.wait(futures)

    def _engin_simulatro_run(self, trades:List[Trade], symbol:str, init_money:int=50000) -> None:
        engine_simulator = EngineSimulator(
            trades=trades,
            init_money=init_money,
            invest_money=self.config.bitflyer.invest_money,
            loss_cut=self.config.bitflyer.loss_cut,
        )

        engine_simulator.run(MarketInfo.CANDLESTICK_NUMS, 3, self.exchange.fetch_data_interval_minute, self.exchange.exchange_name, symbol)