from typing import List
import yaml
import pathlib

class Config:
    def __init__(self):
        self._config_path = 'config.yaml'
        self._load_config()

        self._connection_string: str
        self._bitflyer: Bitflyer

    def _load_config(self):
        with open(self._config_path, 'r', encoding='utf8') as file:
            config_data = yaml.safe_load(file)

            self._connection_string = config_data['connection_string']

            for exchange_name, info in config_data['exchange'].items():
                match exchange_name:
                    case 'bitflyer':
                        self._bitflyer = Bitflyer(info['api_key'], info['api_secret'], info['symbols'])
                    case _:
                        raise NotImplementedError(f'{exchange_name} in {self._config_path} not implemented')

    @property
    def connection_string(self) -> str:
        return self._connection_string

    @property
    def bitflyer(self) -> 'Bitflyer':
        return self._bitflyer

class Bitflyer:
    def __init__(self, api_key:str, api_secret:str, symbols:List[str]):
        self.api_key = api_key
        self.api_secret = api_secret
        self.symbols = symbols
