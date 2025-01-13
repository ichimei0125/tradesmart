import argparse
from api.crypto.exchange import Exchange
from api.crypto.bitflyer.bitflyer import Bitflyer
from config.config import Config
from bot.simulator import Simulator
from datetime import datetime, timedelta
from tools.common import get_unique_name

def main() -> None:
    # init
    c = Config()
    e = Bitflyer(c.bitflyer.symbols, c.bitflyer.dry_run_symbols)
    symbol_trades_dict = e.fetch_trades()

def simulator() -> None:
    c = Config()
    e = Bitflyer(c.bitflyer.symbols, c.bitflyer.dry_run_symbols)
    Simulator(e).run(last_days=10)

def update_model() -> None:
    # TODO: sepreate
    c = Config()
    e = Bitflyer(c.bitflyer.symbols, c.bitflyer.dry_run_symbols)
    Simulator(e).test_rl(training_test_ratio=0.8)

def find_best() -> None:
    c = Config()
    e = Bitflyer(c.bitflyer.symbols, c.bitflyer.dry_run_symbols)
    since = datetime.now() - timedelta(days=90)
    Simulator(e).find_best_trade(since)

def lstm() -> None:
    c = Config()
    e = Bitflyer(c.bitflyer.symbols, c.bitflyer.dry_run_symbols)
    Simulator(e).test_lstm()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="tradebot")
    subparsers = parser.add_subparsers(dest="mode", required=True, help="select a mode to run")

    subparsers.add_parser("trade", help="trade mode, default mode")
    sub_simulate = subparsers.add_parser("simulate", help="simulate past data")
    sub_simulate.add_argument("--find_best_trade", action="store_true", help="Find the best trades")
    sub_simulate.add_argument("--lstm", action="store_true", help="use LSTM to preidct")
    subparsers.add_parser("update_model", help="update bot's model")

    args = parser.parse_args()

    # default
    if args.mode is None:
        args.mode = "trade"

    if args.mode == "trade":
        main()
    elif args.mode == "simulate":
        if args.find_best_trade:
            find_best()
        elif args.lstm:
            lstm()
        else:
            simulator()
    elif args.mode == "update_model":
        update_model()