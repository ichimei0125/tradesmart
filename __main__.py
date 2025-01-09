import argparse
import asyncio
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

async def update_model() -> None:
    # TODO: sepreate
    from bot.simulator import Simulator
    c = Config()
    e = Bitflyer(c.bitflyer.symbols, c.bitflyer.dry_run_symbols)
    Simulator(e).test_ml()
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="tradebot")
    subparsers = parser.add_subparsers(dest="mode", required=True, help="select a mode to run")

    subparsers.add_parser("trade", help="trade mode, default mode")
    subparsers.add_parser("simulate", help="simulate past data")
    subparsers.add_parser("update_model", help="update bot's model")

    args = parser.parse_args()

    # default
    if args.mode is None:
        args.mode = "trade"

    if args.mode == "trade":
        main()
    elif args.mode == "simulate":
        simulator(args.last_days)
    elif args.mode == "update_model":
        asyncio.run(update_model())