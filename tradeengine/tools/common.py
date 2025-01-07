import os

def get_unique_name(exchange_name:str, symbol:str) -> str:
    return f'{exchange_name}_{symbol}'

def create_folder_if_not_exists(folder_path) -> None:
    os.makedirs(folder_path, exist_ok=True)