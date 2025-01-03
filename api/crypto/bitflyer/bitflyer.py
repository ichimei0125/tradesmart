from datetime import datetime, timedelta, timezone
from typing import List, Optional
from threading import Lock, Condition
import ccxt
import asyncio

from api.crypto.exchange import Exchange
from api.db.trade import bulk_insert_trade, get_trades, get_lastest_trade_time
from tradeengine.models.trade import Trade, Side
from tools.common import get_now, local_2_utc

_public_cnt:int = 0
_public_datetime:Optional[datetime] = None
_api_lock = Lock() 
_api_condition = Condition(_api_lock)

class Bitflyer(Exchange):
    def __init__(self, symbols: List[str], dry_run: List[str]):
        super().__init__('bitflyer', symbols, dry_run)
        self.exchange = ccxt.bitflyer()
        self.exchange.enableRateLimit = False

    def _api_limit(self) -> None:
        """call this method before call api"""
        global _public_cnt, _public_datetime
        
        now = get_now()

        with _api_lock:
            if _public_datetime is None or (now - _public_datetime > timedelta(minutes=5)):
                _public_datetime = now
                _public_cnt = 0

            # over limit
            if _public_cnt >= (500 - 5):
                wait_time = 300 - (now - _public_datetime).total_seconds()
                print(f"API limit reached. Waiting for {wait_time:.2f} seconds.")
                if wait_time > 0:
                    _api_condition.wait(timeout=wait_time)

                _public_datetime = get_now()
                _public_cnt = 0

            _public_cnt += 1
            _api_condition.notify_all()

    def fetch_history_data(self, since:Optional[datetime]=None):
        if not since:
            since = get_now() - timedelta(days=30) # max histroy of bitflyer is past 31 days
        since = local_2_utc(since)

        # histroy data are too many, no multi process is better
        for symbol in self.symbols:
            # get db lastest data ~ now
            loop = asyncio.get_event_loop()
            _lastest_time = loop.run_until_complete(get_lastest_trade_time(self.exchange_name, symbol))
            if _lastest_time is not None:
                since = _lastest_time

            trades:List[Trade] = []
            before_id = None
            while True:
                self._api_limit()
                _trades:List
                if not before_id:
                    _trades = self.exchange.fetch_trades(symbol, limit=500) # max limit for bitflyer is 500
                else:
                    _trades = self.exchange.fetch_trades(symbol, limit=500, params={'before': before_id}) # max limit for bitflyer is 500

                __trades = [self._api_2_db_trade(_t) for _t in _trades]
                trades.extend(__trades)

                before_id = _trades[0]['id']
                lastest_datetime = __trades[0].execution_time

                if len(trades) >= 10000:
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(bulk_insert_trade(self.exchange_name, symbol, trades))
                    trades = []
                if lastest_datetime <= since:
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(bulk_insert_trade(self.exchange_name, symbol, trades))
                    break

    def _api_2_db_trade(self, data) -> Trade:
        _side:Side
        match data['side']:
            case Side.SELL.value:
                _side = Side.SELL
            case Side.BUY.value:
                _side = Side.BUY
            case _:
                _side = Side.NONE

        return Trade(
            id = data['id'],
            size = data['amount'],
            side = _side,
            execution_time = self._str_2_datetime(data['datetime']),
            price = data['price'],
        )

    def _str_2_datetime(self, s:str) -> datetime:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
