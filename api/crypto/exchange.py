from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
import yfinance as yf

from tradeengine.models.trade import Trade
from tradeengine.models.candlestick import CandleStick

class Exchange(ABC):
    def __init__(self, exchange_name:str, symbols:List[str], dry_run:List[str]):
        # TODO: check available
        self.exchange_name = exchange_name
        self.symbols = symbols
        self.dry_run = set(dry_run)

        # trading frequency 
        self.is_realtime:bool = False
        self.fetch_data_interval_minute:int = 1
        # tech analysis
        self.candlestick_interval:int = 5

    def is_dry_run(self, symbol:str) -> bool:
        return symbol in self.dry_run

    @abstractmethod
    def fetch_trades(self, since:Optional[datetime]) -> Dict[str, List[Trade]]:
        """
        param:
         - since: max history data, if is None
        """
        pass

    @abstractmethod
    def fetch_candlesticks(self, since:Optional[datetime], use_yahoo_finance:bool=True) -> Dict[str, Dict[str, List[CandleStick]]]:
        """
        since: if none, CANDLESTICK_NUMS(defined at tools/constants.py) * self.fetch_data_interval_minute
        use_yahoo_finance: fetch data from yahoo_finance if cannot get enough data from exchange
        """ 
        pass

    def _fetch_candlesticks_by_yfinance(self, symbol:str, since:datetime, interval:str) -> List[CandleStick]:
        y = yf.Ticker(symbol)
        data = y.history(start=since, interval=interval)

        if data is None or data.shape[0] <= 0:
            raise Exception('Cannot get data from yfinance')

        res:List[CandleStick] = []
        for date, candlestick in data.iterrows():
            res.append(
                CandleStick(
                    open=candlestick['Open'],
                    close=candlestick['Close'],
                    high=candlestick['High'],
                    low=candlestick['Low'],
                    volume=candlestick['Volume'], # TODO: not same with exchange volume
                    opentime=date.to_pydatetime(),
                )
            )
        res.reverse()
        return res
