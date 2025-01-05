from datetime import datetime, timezone
import os

def get_unique_name(exchange_name:str, symbol:str) -> str:
    return f'{exchange_name}_{symbol}'

def get_now() -> datetime:
    return datetime.now()

def local_2_utc(local: datetime) -> datetime:
    return local.astimezone(timezone.utc)

def create_folder_if_not_exists(folder_path) -> None:
    os.makedirs(folder_path, exist_ok=True)