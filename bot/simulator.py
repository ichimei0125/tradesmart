from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple
import pandas as pd

from matplotlib import pyplot as plt

from config.config import Config
from api.crypto.exchange import Exchange
from tools.common import get_now, local_2_utc, get_unique_name
from tools.constants import MarketInfo
from tradeengine.models.trade import Trade
from tradeengine.models.candlestick import CandleStick, get_candlestick_prices, get_indicator
from tradeengine.tools.common import create_folder_if_not_exists
from tradeengine.tools.convertor import convert_dataclass_to_dataframe
from tradeengine.models.invest import FixedInvest, Invest
from tradeengine.simulator.simulator import Simulator as EngineSimulator
from tradeengine.core.ml.reinforcement_learning import rl_training, rl_run
from tradeengine.core.ml.lstm import lstm_training, lstm_run

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
            done, not_done = concurrent.futures.wait(futures)
            
            for future in done:
                if future.exception():
                    raise Exception(future.exception())

    def _engin_simulator_run(self, trades:List[Trade], symbol:str, invest_stragety:Invest) -> None:

        engine_simulator = EngineSimulator(
            trades=trades,
            invest=invest_stragety,
            name = get_unique_name(self.exchange.exchange_name, symbol),
        )

        engine_simulator.run(MarketInfo.CANDLESTICK_NUMS, self.exchange.candlestick_interval, self.exchange.fetch_data_interval_minute, self.exchange.exchange_name, symbol)

    def test_rl(self,  last_days:int=59, training_test_ratio:float=0.5) -> None:
        since = get_now() - timedelta(days=last_days)
        since = local_2_utc(since)
        data = self.exchange.fetch_candlesticks(since, use_yahoo_finance=False)

        for symbol, candlesticks_info in data.items():
            print(symbol)
            name = get_unique_name(self.exchange.exchange_name, symbol)

            # TODO: multi candlesticks
            for _, candlesticks in candlesticks_info.items():
                indicators = get_indicator(candlesticks)

                index = int(len(candlesticks) * (1- training_test_ratio))

                training_candlesticks = candlesticks[index:]
                training_indicators = indicators[index:]
                test_candlesticks = candlesticks[:index]
                test_indicators = indicators[:index]

                best_buy_times, best_sell_times = _find_best_trade(candlesticks)
                rl_training(name, training_candlesticks, training_indicators, best_buy_times, best_sell_times)
                rl_run(name, test_candlesticks, test_indicators, show_pic=True)

    def find_best_trade(self, since:datetime) -> None:
        data = self.exchange.fetch_candlesticks(since, use_yahoo_finance=False)
        for symbol, candlestick_info in data.items():
            for _, candlesticks in candlestick_info.items():
                find_best_trade(candlesticks, name=get_unique_name(self.exchange.exchange_name, symbol), show_pic=False)

    def train_lstm(self, last_days:int=90, training_test_ratio:float=0.8) -> None:
        since = get_now() - timedelta(days=last_days)
        since = local_2_utc(since)
        data = self.exchange.fetch_candlesticks(since, use_yahoo_finance=False)
        for symbol, candlestick_info in data.items():
            name = get_unique_name(self.exchange.exchange_name, symbol)
            for _, candlesticks in candlestick_info.items():
                index = int(len(candlesticks) * (1- training_test_ratio))

                training_candlesticks = candlesticks[index:]
                test_candlesticks = candlesticks[:index]

                lstm_training(name, training_candlesticks)
                # lstm_run(name, training_candlesticks)


def _find_best_trade(candlesticks:List[CandleStick]) -> Tuple[List[datetime], List[datetime]]:
    """return: best_buy_times, best_sell_times"""
    prices = get_candlestick_prices(candlesticks)

    best_buy_times:List[datetime] = []
    best_sell_times:List[datetime] = []

    is_up = prices[-2] > prices[-1]
    is_down = prices[-2] < prices[-1]
    index = len(prices) - 2
    while index > 0:
        current_price = prices[index-1]
        last_price = prices[index]

        # top, best sell
        if is_up and current_price < last_price:
            best_sell_times.append(candlesticks[index].Opentime)
        # down, best buy
        if is_down and current_price > last_price:
            best_buy_times.append(candlesticks[index].Opentime)

        # update vars
        is_up = current_price > last_price
        is_down = current_price < last_price
        index -= 1

    return best_buy_times, best_sell_times

def find_best_trade(candlesticks:List[CandleStick], is_save:bool=True, show_pic:bool = True, name:Optional[str]=None) -> pd.DataFrame:
    best_buy_times, best_sell_times = _find_best_trade(candlesticks)
    indicators = get_indicator(candlesticks)

    candlestick_df = convert_dataclass_to_dataframe(candlesticks, index_field="Opentime")
    indicator_df = convert_dataclass_to_dataframe(indicators, index_field="Opentime")

    merged_df = candlestick_df.join(indicator_df, how='left')

    merged_df.insert(0, 'buy', merged_df.index.map(lambda opentime: 1 if opentime.to_pydatetime() in best_buy_times else None ))
    merged_df.insert(1, 'sell', merged_df.index.map(lambda opentime: 1 if opentime.to_pydatetime() in best_sell_times else None ))

    merged_df.sort_index(inplace=True)

    if is_save:
        folder = Path('output', 'best_trade')
        create_folder_if_not_exists(folder)
        file_name = f'best_trade_{name}_{merged_df.index.min()}_{merged_df.index.max()}.csv'
        merged_df.to_csv(folder.joinpath(file_name))

    if show_pic:
        prices = get_candlestick_prices(candlesticks)
        times = get_candlestick_prices(candlesticks, mode='opentime')

        candlesticks_dict = {}
        for candlestick in candlesticks:
            candlesticks_dict[candlestick.Opentime] = candlestick.Close

        plt.figure(figsize=(12, 6))
        plt.plot(times, prices, label=name)
        plt.scatter(
            best_buy_times,
            [candlesticks_dict[time] for time in best_buy_times],
            color="green",
            label="Buy",
            marker="^",
        )
        plt.scatter(
            best_sell_times,
            [candlesticks_dict[time] for time in best_sell_times],
            color="red",
            label="Sell",
            marker="v",
        )
        plt.xlabel("Time")
        plt.ylabel(f"{name} Price")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    return merged_df