from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

class Exchange(ABC):
    def __init__(self, exchange_name:str, symbols:List[str], dry_run:List[str]):
        # TODO: check available
        self.exchange_name = exchange_name
        self.symbols = symbols
        self.dry_run = set(dry_run)

    def is_dry_run(self, symbol:str) -> bool:
        return symbol in self.dry_run

    @abstractmethod
    def fetch_history_data(self, since:Optional[datetime]) -> None:
        """
        param:
         - since: max history data, if is None
        """
        pass