from typing import List
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

from api.db.common import _get_engine, _create_sessison, Base
from tools.common import get_unique_name
from tradeengine.models.trade import Trade

def _get_dbtrade_table_name(exchange_name:str, symbol:str) -> str:
    return f'{get_unique_name(exchange_name, symbol)}_trade'.lower()

def init_dbtrade_schema(exchange_name:str,symbol:str) -> None:
    table_name = _get_dbtrade_table_name(exchange_name, symbol)
    if table_name not in Base.metadata.tables:
        sqlalchemy.Table(
            table_name,
            Base.metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
            sqlalchemy.Column('size', sqlalchemy.Float),
            sqlalchemy.Column('side', sqlalchemy.String(length=4)),
            sqlalchemy.Column('execution_time', sqlalchemy.dialects.mysql.DATETIME(fsp=6), unique=True),
            extend_existing=False,
        )

def bulk_insert_trade(exchange_name: str, symbol: str, trades: List[Trade]) -> None:
    """
    trades: List of dictionaries containing trade data
    """
    _engine = _get_engine()
    _session = _create_sessison(_engine)

    table_name = _get_dbtrade_table_name(exchange_name, symbol)
    init_dbtrade_schema(exchange_name, symbol)
    Base.metadata.create_all(_engine)

    trade_data = [{"size": trade.size, "side": trade.side, "execution_time": trade.execution_time} for trade in trades]

    sql = sqlalchemy.text(f"""
          INSERT IGNORE INTO {table_name} (size, side, execution_time)
          VALUES (:size, :side, :execution_time)
          """)
    _session.execute(sql, trade_data)
    _session.commit()
