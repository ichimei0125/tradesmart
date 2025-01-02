from api.crypto.exchange import Exchange
from api.crypto.bitflyer.bitflyer import Bitflyer
from config.config import Config

def main() -> None:
    # init
    c = Config()
    e = Bitflyer(c.bitflyer.symbols, c.bitflyer.dry_run_symbols)
    e.fetch_history_data()
    

if __name__ == '__main__':
    main()