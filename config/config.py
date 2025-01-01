from typing import List
import yaml

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
                # exchange base
                symbols = info['symbols']
                dry_run = info['dry_run']
                # exchange only
                match exchange_name:
                    case 'bitflyer':
                        self._bitflyer = Bitflyer(info['api_key'], info['api_secret'], symbols, dry_run)
                    case _:
                        raise NotImplementedError(f'{exchange_name} in {self._config_path} not implemented')

    @property
    def connection_string(self) -> str:
        return self._connection_string

    @property
    def bitflyer(self) -> 'Bitflyer':
        return self._bitflyer

class ExchangeBase():
    def __init__(self, symbols:List[str], dry_run_symbols:List[str]):
        self.symbols = symbols
        self.dry_run_symbols = dry_run_symbols

class Bitflyer(ExchangeBase):
    def __init__(self, api_key:str, api_secret:str, symbols:List[str], dry_run:List[str]):
        self.api_key = api_key
        self.api_secret = api_secret
        super().__init__(symbols, dry_run)
