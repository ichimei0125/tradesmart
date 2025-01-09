
from datetime import datetime, timedelta
import os
from typing import List, Optional
from tradeengine.core.ml.reinforcement_learning_traning import rl_run
from tradeengine.core.strategies import TradeStatus, simple_strategy
from tradeengine.models.trade import ConvertTradeToCandleStick, Trade, get_indicator, sort_trades_desc
from tradeengine.models.invest import *
from tradeengine.tools.convertor import datetime_to_str
from tradeengine.tools.common import get_unique_name
from tradeengine.tools.log import log

class Simulator:
    def __init__(self, trades: List[Trade], invest: Invest, name:str, is_margin:bool=False):
        self.trades = sort_trades_desc(trades)
        self.account_money = invest.balance
        self.account_coin:float = 0.0
        self.loss_cut = invest.loss_cut
        self.name = name

        self.invest_strategy = invest

        # TODO: margin
        # TODO: realtime

    def run(self, candlesticks_num:int, candlestick_interval:int, fetch_interval:int, exchange_name:str, symbol:str) -> None:
        # TODO: not minute
        log_filename = get_unique_name(exchange_name, symbol) + '.log'
        _log = log(log_filename, 'simulator') 
        self.push_trade(self.trades, candlesticks_num, candlestick_interval, fetch_interval, _log)

    def run_realtime(self) -> None:
        pass

    def push_trade(self, trades:List[Trade], candlesticks_num:int, candlestick_interval:int, fetch_interval:int, _log:log):
        period = (candlesticks_num + 2) * candlestick_interval
        end_time = trades[-1].execution_time + timedelta(minutes=period)
        cached_candlesticks = None
        tmp_trades = []
        for trade in reversed(trades):
            tmp_trades.insert(0, trade) # O(n), remove unused trades
            if trade.execution_time > end_time:
                _, cached_candlesticks = ConvertTradeToCandleStick(tmp_trades, cached_candlesticks, check_trades_order=False).by_minutes(candlestick_interval)
                indicators = get_indicator(cached_candlesticks)
                # trade_status = simple_strategy(cached_candlesticks)
                trade_status = rl_run(self.name, cached_candlesticks, indicators)

                if trade_status == TradeStatus.BUY:
                    self.sim_buy(trade.execution_time, cached_candlesticks[0].close, self._get_buy_money(), _log)
                elif trade_status == TradeStatus.SELL:
                    self.sim_sell(trade.execution_time, cached_candlesticks[0].close, self._get_sell_size(), _log)
                end_time += timedelta(minutes=fetch_interval)
                # update tmp_trades
                start_time = end_time - timedelta(minutes=period)
                for i in range(len(tmp_trades.copy())-1, -1, -1):
                    if tmp_trades[i].execution_time < start_time:
                        tmp_trades.pop()
                    else:
                        break

    def _get_buy_money(self) -> float:
        _type = type(self.invest_strategy)
        if _type is FixedInvest:
            return self.invest_strategy.invest
        else:
            raise TypeError(f'need type Invest, type: {_type}')

    def _get_sell_size(self) -> float:
        _type = type(self.invest_strategy)
        if _type is FixedInvest:
            return self.account_coin
        else:
            raise TypeError(f'need type Invest, type: {_type}')


    def sim_buy(self, time, price:float, money:float, _log:log) -> str:
        if self.account_money <= money:
            return
        _size = (money / price)
        self.account_coin += _size
        self.account_money -= money

        # loss_cut, for margin
        if self.loss_cut and self.account_coin < 0.001 and self.account_money < self.loss_cut:
            _log.warning(f'LOSS CUT: {self.account_money}')
        
        s_time = datetime_to_str(time)
        _log.info(f'{s_time}, BUY, {price:.2f}, {_size}, {self.account_coin}, {self.account_money:.2f}')

    def sim_sell(self, time, price:float, size:float, _log:log) -> str:
        if self.account_coin < 0.001:
            return

        self.account_coin -= size
        self.account_money += (price * size)

        # loss_cut
        if self.loss_cut and self.account_coin < 0.001 and self.account_money < self.loss_cut:
            _log.warning(f'LOSS CUT: {self.account_money}')

        s_time = datetime_to_str(time)
        _log.info(f'{s_time}, SELL, {price:.2f}, {size}, {self.account_coin}, {self.account_money:.2f}')




