from datetime import datetime
from typing import List, Optional
import ccxt

from api.crypto.exchange import Exchange


class Bitflyer(Exchange):
    def __init__(self, symbols: List[str]):
        super().__init__('bitflyer', symbols)

    def fetch_history_data(self, since:Optional[datetime]):
        # if not since:

        exchange = ccxt.bitflyer()
        t = exchange.fetch_trades('BTC_JPY', limit=500) # max limit for bitflyer is 500
        pass