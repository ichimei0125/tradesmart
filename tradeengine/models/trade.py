from enum import Enum
from datetime import datetime

class Side(Enum):
    BUY = 'buy'
    SELL = 'sell'
    NONE = ''

class Trade:
    # exchange: str
    # symbol: str
    id: str
    side: Side
    size: float
    execution_time: datetime
    price: float

class CandleStick:
    # exchange: str
    # symbol: str
    open: float
    close: float
    high: float
    low: float
    volume: int
    tradetime: datetime # 最終取引の時刻。

