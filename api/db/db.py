from typing import Dict, List
import sqlalchemy
from sqlalchemy import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from config.config import Config
from api.db.common import _get_engine, Base
from api.db import *


# def init_table(exchange_symbols: Dict[str, List]) -> None:
#     """
#     params:
#       [exchange_name: [symbol1, symbol2, ....]]
#     """
#     engine = _get_engine()
#     Base.metadata.create_all(engine)
