from pathlib import Path
from gymnasium import spaces
import gymnasium as gym
import numpy as np
from dataclasses import dataclass
from datetime import datetime
from typing import List
from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import DummyVecEnv
import matplotlib.pyplot as plt

from tradeengine.models.trade import CandleStick, Indicator
from tradeengine.core.strategies import TradeStatus
from tradeengine.tools.common import create_folder_if_not_exists


class MarketEnv(gym.Env):
    def __init__(self, indicators: List[Indicator], candlesticks: List[CandleStick]):
        super(MarketEnv, self).__init__()
        
        self.indicators = indicators
        self.candlesticks = candlesticks
        
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(17,), dtype=np.float64
        )
        self.action_space = spaces.Discrete(3)

        self.buy_prices:List[float] = []
        self.position = 0
        
        self.current_step = 0
        self.done = False


    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.current_step = 0
        self.done = False

        return self._get_observation(), {}

    def step(self, action):
        reward = 0
    
        current_price = self.candlesticks[self.current_step].close
        # future 3 candlesticks
        future_prices = []
        for index in range(self.current_step, min(self.current_step + 4, len(self.candlesticks))):
            future_prices.append(self.candlesticks[index].close)
    
        if action == TradeStatus.BUY.value: # buy
            if self.position == 0:
                self.position = 1
                self.buy_prices.append(current_price)
                reward = max(future_prices) - current_price
            else:
                reward = -0.5
        elif action == TradeStatus.SELL.value:  # sell
            if self.position == 1:
                self.position = 0
                buy_price = self.buy_prices.pop(0)
                # trade reward
                reward = current_price - buy_price
                # future prices reward
                reward += 0.5 * (current_price - max(future_prices))
            else:
                reward = -1
        elif action == TradeStatus.HOLD.value:  # hold
            reward = -0.1 # trade quickly
    
        # update status
        self.current_step += 1
        terminated = self.current_step >= len(self.candlesticks) - 1
        truncated = False
    
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
            indicator.SMA_20,
            indicator.SMA_200,
            indicator.RSI,
            indicator.MACD,
            indicator.MACD_SIGNAL,
            indicator.MACD_HIST,
            candlestick.open,
            candlestick.close,
            candlestick.high,
            candlestick.low,
            self.position,
        ], dtype=np.float64)

def _get_model_path(name:str) -> Path:
    folder = 'ml_models'
    create_folder_if_not_exists(folder)

    file_name = f'{name}_dqn_model.zip'
    return Path(folder, file_name)

def rl_training(name:str, candlesticks:List[CandleStick], indicators:List[Indicator], save_model=True) -> DQN:
    env = DummyVecEnv([lambda: MarketEnv(indicators, candlesticks)])
    check_env(env.envs[0], warn=True)

    model = DQN("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=len(candlesticks))

    if save_model:
        model.save(_get_model_path(name))
    return model


def rl_run(name:str, candlesticks:List[CandleStick], indicators:List[Indicator], load_model=True, model=None, show_pic:bool=False) -> TradeStatus:
    if load_model:
        model= DQN.load(_get_model_path(name))
    else:
        model = model

    env = DummyVecEnv([lambda: MarketEnv(indicators, candlesticks)])
    check_env(env.envs[0], warn=True)

    action:int
    actions:List[int] = []
    obs = env.reset()
    for _ in range(len(candlesticks)):
        action, _states = model.predict(obs)
        obs, reward, done, info = env.step(action)
        actions.append(action)
        if done:
            break

    if show_pic:
        prices = [c.close for c in candlesticks]
        times = [c.opentime for c in candlesticks]  # 提取 opentime
        buy_points = [i for i, a in enumerate(actions) if a == TradeStatus.BUY.value]
        sell_points = [i for i, a in enumerate(actions) if a == TradeStatus.SELL.value]

        plt.figure(figsize=(12, 6))
        plt.plot(times, prices, label=name)
        plt.scatter(
            [times[i] for i in buy_points],
            [prices[i] for i in buy_points],
            color="green",
            label="Buy",
            marker="^",
        )
        plt.scatter(
            [times[i] for i in sell_points],
            [prices[i] for i in sell_points],
            color="red",
            label="Sell",
            marker="v",
        )
        plt.xlabel("Time")
        plt.ylabel(f"{name} Price")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    return TradeStatus(action)