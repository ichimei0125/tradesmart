from enum import Enum
from datetime import datetime

class Side(Enum):
    BUY = 'buy'
    SELL = 'sell'

class Trade:
    exchange: str
    symbol: str
    side: Side
    execution_time: datetime

class CandleStick:
    # exchange: str
    # symbol: str
    open: float
    close: float
    high: float
    low: float
    volume: int
    tradetime: datetime # 最終取引の時刻。

