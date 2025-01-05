from datetime import datetime, timedelta
from typing import List, Optional
import os

from config.config import Config
from api.crypto.exchange import Exchange
from tools.common import get_now, local_2_utc
from tools.constants import MarketInfo
from tradeengine.models.trade import Trade
from tradeengine.models.invest import FixedInvest, Invest
from tradeengine.simulator.simulator import Simulator as EngineSimulator
from tradeengine.tools.convertor import datetime_to_str

import concurrent.futures
from multiprocessing import cpu_count

class Simulator:
    def __init__(self, exchagne:Exchange):
        self.exchange = exchagne
        self.config = Config()


    def run(self, account_money:int=50000, last_days:int=90) -> None:
        since = get_now() - timedelta(days=last_days)
        since = local_2_utc(since)

        data = self.exchange.fetch_trades(since)

        invest_stragety = FixedInvest(
            balance=account_money,
            loss_cut=self.config.bitflyer.loss_cut,
            invest=self.config.bitflyer.invest_money,
        )

        with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count()) as executor:
            futures = [executor.submit(self._engin_simulator_run, trades, symbol, invest_stragety) for symbol, trades in data.items()]
            concurrent.futures.wait(futures)

    def _engin_simulator_run(self, trades:List[Trade], symbol:str, invest_stragety:Invest) -> None:

        engine_simulator = EngineSimulator(
            trades=trades,
            invest=invest_stragety
        )

        engine_simulator.run(MarketInfo.CANDLESTICK_NUMS, 3, self.exchange.fetch_data_interval_minute, self.exchange.exchange_name, symbol)