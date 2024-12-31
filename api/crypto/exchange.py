from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

class Exchange(ABC):
    def __init__(self, exchange_name:str, symbols:List[str]):
        # TODO: check available
        self.exchange_name = exchange_name
        self.symbols = symbols

    @abstractmethod
    def fetch_history_data(self, since:Optional[datetime]) -> None:
        """
        param:
         - since: max history data, if is None
        """
        pass