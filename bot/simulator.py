from datetime import datetime, timedelta
from typing import List, Optional
import os

from config.config import Config
from api.crypto.exchange import Exchange
from tools.common import get_now, local_2_utc, get_unique_name
from tools.constants import MarketInfo
from tradeengine.models.trade import Trade, ConvertTradeToCandleStick, get_indicator
from tradeengine.models.invest import FixedInvest, Invest
from tradeengine.simulator.simulator import Simulator as EngineSimulator
from tradeengine.core.ml.reinforcement_learning_traning import rl_training, rl_run

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
            invest=invest_stragety,
            name = get_unique_name(self.exchange.exchange_name, symbol),
        )

        engine_simulator.run(MarketInfo.CANDLESTICK_NUMS, 3, self.exchange.fetch_data_interval_minute, self.exchange.exchange_name, symbol)

    def test_ml(self,  last_days:int=59, training_test_ratio:float=0.5) -> None:
        since = get_now() - timedelta(days=last_days)
        since = local_2_utc(since)
        data = self.exchange.fetch_candlesticks(since)

        for symbol, candlesticks_info in data.items():
            print(symbol)
            name = get_unique_name(self.exchange.exchange_name, symbol)

            # TODO: multi candlesticks
            for _, candlesticks in candlesticks_info.items():
                indicators = get_indicator(candlesticks)

                index = int(len(candlesticks) * training_test_ratio)

                training_candlesticks = candlesticks[:index]
                training_indicators = indicators[:index]
                test_candlesticks = candlesticks[index:]
                test_indicators = indicators[index:]

                rl_training(name, training_candlesticks, training_indicators)
                rl_run(name, test_candlesticks, test_indicators)


