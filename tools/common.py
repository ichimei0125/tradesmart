from datetime import datetime, timezone

def get_unique_name(exchange_name:str, symbol:str) -> str:
    return f'{exchange_name}_{symbol}'

def get_now() -> datetime:
    return datetime.now()

def local_2_utc(local: datetime) -> datetime:
    return local.astimezone(timezone.utc)

def datetime_to_str(date:datetime) -> str:
    return date.strftime('%Y%m%d %H:%M:%S')