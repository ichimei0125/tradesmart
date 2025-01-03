from api.crypto.exchange import Exchange
from api.crypto.bitflyer.bitflyer import Bitflyer
from config.config import Config
from tradeengine.models.trade import trade_2_candlestick_minutes

def main() -> None:
    # init
    c = Config()
    e = Bitflyer(c.bitflyer.symbols, c.bitflyer.dry_run_symbols)
    symbol_trades_dict = e.fetch_trades()

    candle_sticks = None
    for symbol, trades in symbol_trades_dict.items():
        candle_sticks = trade_2_candlestick_minutes(trades, 3, candle_sticks)
        pass

    

if __name__ == '__main__':
    main()