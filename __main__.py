from api.crypto.exchange import Exchange
from api.crypto.bitflyer.bitflyer import Bitflyer
from config.config import Config

def main() -> None:
    # init
    c = Config()
    e = Bitflyer(c.bitflyer.symbols, c.bitflyer.dry_run_symbols)
    symbol_trades_dict = e.fetch_trades()

def simulator() -> None:
    from bot.simulator import Simulator
    c = Config()
    e = Bitflyer(c.bitflyer.symbols, c.bitflyer.dry_run_symbols)
    Simulator(e).run(last_days=10)
    # Simulator(e).test_ml()
    

if __name__ == '__main__':
    # main()
    simulator()