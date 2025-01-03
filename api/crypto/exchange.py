from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from tradeengine.models.trade import Trade, CandleStick

class Exchange(ABC):
    def __init__(self, exchange_name:str, symbols:List[str], dry_run:List[str]):
        # TODO: check available
        self.exchange_name = exchange_name
        self.symbols = symbols
        self.dry_run = set(dry_run)

        # trading frequency 
        self.is_realtime:bool = False
        self.fetch_data_interval_minute:int = 1

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
    def fetch_candlesticks(self) -> Dict[str, Dict[timedelta, List[CandleStick]]]:
        """
        since: CANDLESTICK_NUMS(defined at tools/constants.py) * self.fetch_data_interval_minute
        """
        pass