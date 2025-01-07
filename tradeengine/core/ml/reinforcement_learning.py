from gymnasium import spaces
import gymnasium
import numpy as np
from dataclasses import dataclass
from datetime import datetime
from typing import List

from tradeengine.models.trade import CandleStick, Indicator
from tradeengine.core.strategies import TradeStatus


class MarketEnv(gymnasium.Env):
    def __init__(self, indicators: List[Indicator], candlesticks: List[CandleStick]):
        super(MarketEnv, self).__init__()
        
        self.indicators = indicators
        self.candlesticks = candlesticks
        
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(12,), dtype=np.float32
        )
        
        self.action_space = spaces.Discrete(3)
        
        self.current_step = 0
        self.done = False


    def reset(self, seed=None, options=None):
        # 设置随机种子（如果需要）
        if seed is not None:
            self.np_random, seed = gymnasium.utils.seeding.np_random(seed)

        # 初始化环境状态
        self.current_step = 0
        self.done = False

        # 返回初始状态和一个空的信息字典
        return self._get_observation(), {}

    def step(self, action):
        reward = 0
    
        # 获取当前和下一步的收盘价
        current_price = self.candlesticks[self.current_step].close
        next_price = (
            self.candlesticks[self.current_step + 1].close
            if self.current_step + 1 < len(self.candlesticks)
            else current_price
        )
    
        # 奖励逻辑：根据动作判断
        if action == TradeStatus.BUY.value:  # 买入
            reward = next_price - current_price
        elif action == TradeStatus.SELL.value:  # 卖出
            reward = current_price - next_price
        elif action == TradeStatus.HOLD.value:  # 保持
            reward = 0
    
        # 状态更新
        self.current_step += 1
        terminated = self.current_step >= len(self.candlesticks) - 1  # 判断是否结束
        truncated = False  # Gym中表示是否由于时间限制提前结束
    
        # 返回值必须是五元组
        return self._get_observation(), reward, terminated, truncated, {}


    def _get_observation(self):
        indicator = self.indicators[self.current_step]
        candlestick = self.candlesticks[self.current_step]
        
        return np.array([
            indicator.BBBands_Plus_2,
            indicator.BBBands_Plus_3,
            indicator.BBBands_Minus_2,
            indicator.BBBands_Minus_3,
            indicator.Stoch_K,
            indicator.Stoch_D,
            candlestick.open,
            candlestick.close,
            candlestick.high,
            candlestick.low,
            candlestick.volume,
            candlestick.opentime.timestamp(),
        ], dtype=np.float32)