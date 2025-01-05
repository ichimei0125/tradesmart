from dataclasses import dataclass
from typing import Optional

@dataclass
class Invest:
    balance: float
    loss_cut: Optional[float]

@dataclass
class FixedInvest(Invest):
    invest: float

    def __post_init__(self):
        if self.invest > self.balance:
            raise Exception(f'For fixed invest, invest money must less or equal than balance, invest: {self.invest}, balance: {self.balance}')
