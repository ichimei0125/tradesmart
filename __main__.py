from api.exchange import Exchange
from api.bitflyer.bitflyer import Bitflyer

def main() -> None:
    a = Bitflyer(['test'])
    a.fetch_history_data()
    

if __name__ == '__main__':
    main()