
import sqlalchemy
from sqlalchemy import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from config.config import Config

Base = declarative_base()

_engine: Engine = None
_Session: sessionmaker = None

def _get_engine() -> Engine:
    global _engine
    if _engine is None:
        connection_string = Config().connection_string
        _engine = sqlalchemy.create_engine(
            connection_string,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            echo=True
        )
    return _engine


def _create_sessison(engine: Engine) -> Session:
    global _Session
    if _Session is None:
        _Session = sessionmaker(bind=engine)
    return _Session()