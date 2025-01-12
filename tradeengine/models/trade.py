from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import heapq
from typing import List


class Side(Enum):
    BUY = 'buy'
    SELL = 'sell'
    NONE = ''

@dataclass
class Trade:
    id: str
    side: Side
    size: float
    execution_time: datetime
    price: float


def sort_trades_desc(trades: List[Trade]) -> List[Trade]:
    if all(
        trades[i].execution_time >= trades[i + 1].execution_time
        for i in range(len(trades) - 1)
    ):
        # check sorted, O(n)
        return trades
    elif len(trades) < 10000:
        # O(nlogn)
        return _sort_trades_desc(trades)
    else: 
        # O(logn) push/pop, O(n) create
        return _sort_trades_desc_heapq(trades)

def _sort_trades_desc(trades: List[Trade]) -> List[Trade]:
    """sort trades by execution_time DESC, use this when small data"""
    return sorted(trades, key=lambda trade: trade.execution_time, reverse=True)

def _sort_trades_desc_heapq(trades: List[Trade]) -> List[Trade]:
    """sort trades by execution_time DESC, use this when big data"""
    heap = []
    for trade in trades:
        heapq.heappush(heap, (-trade.execution_time.timestamp(), id(trade), trade))
    
    sorted_trades = []
    while heap:
        _, _, trade = heapq.heappop(heap)
        sorted_trades.append(trade)
    
    return sorted_trades
