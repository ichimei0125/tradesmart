
from datetime import datetime, timedelta
import os
from typing import List, Optional
from tradeengine.core.strategies import TradeStatus, simple_strategy
from tradeengine.models.trade import ConvertTradeToCandleStick, Trade
from tradeengine.tools.convertor import datetime_to_str


class Simulator:
    def __init__(self, trades: List[Trade], init_money:float=50000, loss_cut:float=40000, invest_money:float=10000, is_margin:bool=False):
        self.trades = trades
        self.account_money = init_money
        self.account_coin:float = 0.0
        self.loss_cut = loss_cut
        self.invest_money = invest_money

        # TODO: margin
        # TODO: realtime

    def run(self, candlesticks_num:int, candlestick_interval:int, fetch_interval:int) -> None:
        # TODO: not minute
        self.push_trade(self.trades, candlesticks_num, candlestick_interval, fetch_interval)

    def run_realtime(self) -> None:
        pass

    def push_trade(self, trades:List[Trade], candlesticks_num:int, candlestick_interval:int, fetch_interval:int):
        period = (candlesticks_num + 2) * candlestick_interval
        end_time = trades[-1].execution_time + timedelta(minutes=period)
        cached_candlestick = None
        tmp_trades = []
        for trade in reversed(trades):
            tmp_trades.insert(0, trade) # O(n), remove unused trades
            if trade.execution_time > end_time:
                cached_candlestick, _ = ConvertTradeToCandleStick(tmp_trades, cached_candlestick).by_minutes(candlestick_interval)
                trade_status = simple_strategy(cached_candlestick)
                if trade_status == TradeStatus.BUY:
                    self.sim_buy(trade.execution_time, cached_candlestick[0].close, self.invest_money)
                elif trade_status == TradeStatus.SELL:
                    self.sim_sell(trade.execution_time, cached_candlestick[0].close)
                end_time += timedelta(minutes=fetch_interval)
                # update tmp_trades
                start_time = end_time - timedelta(minutes=period)
                for i in range(len(tmp_trades.copy())-1, -1, -1):
                    if tmp_trades[i].execution_time < start_time:
                        tmp_trades.pop()
                    else:
                        break

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
        if self.account_money < self.loss_cut:
            print(f'LOSS CUT: {self.account_money}')
            os._exit(0)



