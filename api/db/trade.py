from datetime import datetime, timedelta, timezone
from typing import List, Optional
import sqlalchemy
from sqlalchemy import Tuple, select
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from api.db.common import _get_engine, _create_sessison, Base
from tools.common import get_now, get_unique_name
from tradeengine.models.trade import Trade

def _get_dbtrade_table_name(exchange_name:str, symbol:str) -> str:
    return f'{get_unique_name(exchange_name, symbol)}_trade'.lower()

def _init_dbtrade_schema(exchange_name:str,symbol:str) -> None:
    table_name = _get_dbtrade_table_name(exchange_name, symbol)
    if table_name not in Base.metadata.tables:
        sqlalchemy.Table(
            table_name,
            Base.metadata,
            sqlalchemy.Column('id', sqlalchemy.String(length=15), primary_key=True),
            sqlalchemy.Column('price', sqlalchemy.Float),
            sqlalchemy.Column('size', sqlalchemy.Float),
            sqlalchemy.Column('side', sqlalchemy.String(length=4)),
            sqlalchemy.Column('execution_time', sqlalchemy.dialects.mysql.DATETIME(fsp=6)),
            extend_existing=False,
        )

def _init_trade_session(exchange_name:str, symbol:str) -> Session:
    _engine = _get_engine()
    _session = _create_sessison(_engine)

    _init_dbtrade_schema(exchange_name, symbol)
    Base.metadata.create_all(_engine)
    return _session

async def bulk_insert_trade(exchange_name: str, symbol: str, trades: List[Trade]) -> None:
    if not trades or len(trades) <= 0:
        return

    _session = _init_trade_session(exchange_name, symbol)
    table_name = _get_dbtrade_table_name(exchange_name, symbol)

    trade_data = [{
        "id": trade.id,
        "price": trade.price,
        "size": trade.size,
        "side": trade.side.value,
        "execution_time": trade.execution_time}
        for trade in trades]

    sql = sqlalchemy.text(f"""
          INSERT IGNORE INTO {table_name} (id, price, size, side, execution_time)
          VALUES (:id, :price, :size, :side, :execution_time)
          """)
    _session.execute(sql, trade_data)
    _session.commit()

async def get_trades(exchange_name:str, symbol:str, last_days:Optional[int] = 90) -> List[Trade]:
    _session = _init_trade_session(exchange_name, symbol)
    table_name = _get_dbtrade_table_name(exchange_name, symbol)

    now = get_now()
    since = now - timedelta(days=last_days)

    results = _session.execute(
        select(Base.metadata.tables[table_name])
        .where(Base.metadata.tables[table_name].c.execution_time > since)
        .order_by(Base.metadata.tables[table_name].c.execution_time.desc())
    ).fetchall()

    trades = []
    for row in results:
        row_dict = dict(row._mapping)
        row_dict["execution_time"] = row_dict["execution_time"].replace(tzinfo=timezone.utc)
        trades.append(Trade(**row_dict))
    return trades

async def get_lastest_trade_time(exchange_name:str, symbol:str) -> Optional[datetime]:
    _session = _init_trade_session(exchange_name, symbol)
    table_name = _get_dbtrade_table_name(exchange_name, symbol)

    result = _session.execute(
        select(Base.metadata.tables[table_name])
        .order_by(Base.metadata.tables[table_name].c.execution_time.desc())
    ).first()

    if result is None:
        return result

    trade = Trade(**result._mapping)
    return trade.execution_time.replace(tzinfo=timezone.utc)