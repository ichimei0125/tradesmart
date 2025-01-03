from datetime import datetime, timedelta
from typing import Optional
import os

from config.config import Config
from tradeengine.core.strategies import simple_strategy
from tradeengine.models.trade import ConvertTradeToCandleStick
from tradeengine.core.strategies import TradeStatus
from api.crypto.exchange import Exchange
from tools.common import get_now, local_2_utc, datetime_to_str
from tools.constants import MarketInfo

class Simulator:
    def __init__(self, exchagne:Exchange, init_money:float=50000):
        self.exchange = exchagne
        self.account_money = init_money
        self.account_coin:float = 0.0
        self.config = Config()

    def run(self, since:Optional[datetime]=None) -> None:
        """since: default last 90 days"""
        if not since:
            since = get_now() - timedelta(days=90)
        since = local_2_utc(since)

        data = self.exchange.fetch_trades(since)
        for symbol, trades in data.items():
            # TODO: multi candlestick
            self.push_trade(trades)

    def push_trade(self, trades):
        if self.exchange.is_realtime:
            # TODO: impl
            return

        period = (MarketInfo.CANDLESTICK_NUMS + 2) * self.exchange.fetch_data_interval_minute
        end_time = trades[-1].execution_time + timedelta(minutes=period)
        cached_candlestick = None
        tmp_trades = []
        for trade in reversed(trades):
            tmp_trades.insert(0, trade)
            if trade.execution_time > end_time:
                cached_candlestick, _ = ConvertTradeToCandleStick(tmp_trades, cached_candlestick).by_minutes(3)
                trade_status = simple_strategy(cached_candlestick)
                if trade_status == TradeStatus.BUY:
                    self.sim_buy(trade.execution_time, cached_candlestick[0].close, self.config.bitflyer.invest_money)
                elif trade_status == TradeStatus.SELL:
                    self.sim_sell(trade.execution_time, cached_candlestick[0].close)
                end_time += timedelta(minutes=self.exchange.fetch_data_interval_minute)

    def sim_buy(self, time, price:float, money:float) -> None:
        if self.account_money <= money:
            return
        _size = (money / price)
        self.account_coin += _size
        self.account_money -= money
        
        s_time = datetime_to_str(time)
        print(f'{s_time}, BUY, {price}, {_size}, {self.account_coin}, {self.account_money}')

    def sim_sell(self, time, price:float, size:Optional[float]=None) -> None:
        if size is None:
            size = self.account_coin

        if self.account_coin < 0.001:
            return

        self.account_coin -= size
        self.account_money += (price * size)

        s_time = datetime_to_str(time)
        print(f'{s_time}, SELL, {price}, {size}, {self.account_coin}, {self.account_money}')

        # loss_cut
        if self.account_money < self.config.bitflyer.loss_cut:
            print(f'LOSS CUT: {self.account_money}')
            os._exit(0)



