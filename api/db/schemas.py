import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Trade(Base):
    __abstract__ = True

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    size = sqlalchemy.Column(sqlalchemy.Float)
    side = sqlalchemy.Column(sqlalchemy.String)
    execution_time = sqlalchemy.Column(sqlalchemy.DateTime)

    @classmethod
    def set_table_name(cls, exchange_name:str, symbol:str):
        cls.__tablename__ = f'{exchange_name}_{symbol}_trade'
