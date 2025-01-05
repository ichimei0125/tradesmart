from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MarketInfo:
    CANDLESTICK_NUMS:int = 1000

@dataclass(frozen=True)
class ConstantPath:
    LOG_FOLDER:Path = Path('log')