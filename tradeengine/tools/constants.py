from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class ConstantPaths:
    OUTPUT = Path('output')
    BEST_TRADE_OUTPUT = Path('output', 'best_trade')
    RL_MODELS = Path('output', 'rl_models')
    LSTM_MODELS = Path('output', 'lstm_models')

