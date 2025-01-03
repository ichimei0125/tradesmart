from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from threading import Lock, Condition
import ccxt
import asyncio

from api.crypto.exchange import Exchange
from api.db.trade import bulk_insert_trade, get_trades, get_lastest_trade_time
from tradeengine.models.trade import CandleStick, Trade, Side, ConvertTradeToCandleStick
from tools.common import get_now, local_2_utc
from tools.constants import MarketInfo

# public api limit: 500/5min
_public_cnt:int = 0
_public_datetime:Optional[datetime] = None
_public_api_lock = Lock() 
_public_api_condition = Condition(_public_api_lock)
# TODO: private api limit 500/5min (not trade so many times)?

class Bitflyer(Exchange):
    def __init__(self, symbols: List[str], dry_run: List[str]):
        super().__init__('bitflyer', symbols, dry_run)
        self.exchange = ccxt.bitflyer()
        self.exchange.enableRateLimit = False

        # trading frequency 
        self.is_realtime:bool = False
        self.fetch_data_interval_minute:int = 1

        # cache
        self.cache_trades:List[Trade]
        self.cache_candlesticks:List[Trade]

    def _public_api_limit(self) -> None:
        """call this method before call api"""
        global _public_cnt, _public_datetime
        
        now = get_now()

        with _public_api_lock:
            if _public_datetime is None or (now - _public_datetime > timedelta(minutes=5)):
                _public_datetime = now
                _public_cnt = 0

            # over limit
            if _public_cnt >= (500 - 5):
                wait_time = 300 - (now - _public_datetime).total_seconds()
                print(f"Public API limit reached. Waiting for {wait_time:.2f} seconds.")
                if wait_time > 0:
                    _public_api_condition.wait(timeout=wait_time)

                _public_datetime = get_now()
                _public_cnt = 0

            _public_cnt += 1
            _public_api_condition.notify_all()

    def fetch_trades(self, since:Optional[datetime]=None) -> Dict[str, List[Trade]]:
        # TODO cache
        now = get_now()
        if not since:
            since = now - timedelta(days=30) # max histroy of bitflyer is past 31 days
        since = local_2_utc(since)
        last_days = (local_2_utc(now) - since).days

        res = {}
        # TODO: multi process?
        # histroy data are too many, no multi process is better
        for symbol in self.symbols:
            # TODO: consider missing data in db
            # get db lastest data ~ now
            _lastest_time = asyncio.run(get_lastest_trade_time(self.exchange_name, symbol))
            if _lastest_time is not None:
                since = _lastest_time

            trades:List[Trade] = []
            before_id = None
            while True:
                self._public_api_limit()
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
                    asyncio.run(bulk_insert_trade(self.exchange_name, symbol, trades))
                    trades = []
                if lastest_datetime <= since:
                    asyncio.run(bulk_insert_trade(self.exchange_name, symbol, trades))
                    break
            data = asyncio.run(get_trades(self.exchange_name, symbol, last_days))
            res[symbol] = data
        return res

    def fetch_candlesticks(self, since) -> Dict[str, Dict[timedelta, List[CandleStick]]]:
        if since is None:
            last_minutes = (MarketInfo.CANDLESTICK_NUMS + 2) * self.fetch_data_interval_minute
            since = get_now() - timedelta(minutes=last_minutes)
        since = local_2_utc(since)
        trades_dict = self.fetch_trades(since=since)

        # TODO: multi candlestick
        res = {}
        for symbol, trades in trades_dict.items():
            candlesticks, interval = ConvertTradeToCandleStick(trades).by_minutes(3)
            res[symbol] = {interval:candlesticks}

        return res

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
