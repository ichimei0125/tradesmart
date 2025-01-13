from datetime import datetime
import math
from pathlib import Path
from gymnasium import spaces
import gymnasium as gym
import numpy as np
from typing import List
from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import DummyVecEnv
import matplotlib.pyplot as plt

from tradeengine.models.candlestick import CandleStick, Indicator
from tradeengine.core.strategies import TradeStatus
from tradeengine.tools.common import create_folder_if_not_exists
from tradeengine.tools.constants import ConstantPaths


class MarketEnv(gym.Env):
    def __init__(self, 
                 indicators: List[Indicator], 
                 candlesticks: List[CandleStick], 
                 best_buy_times: List[datetime] = [],
                 best_sell_times: List[datetime] = []):
        super(MarketEnv, self).__init__()
        
        self.indicators = indicators
        self.candlesticks = candlesticks
        
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(13,), dtype=np.float64
        )
        self.action_space = spaces.Discrete(3)

        self.buy_prices:List[float] = []
        
        self.current_step = 0
        self.done = False

        self.best_buy_times = set(best_buy_times)
        self.best_sell_time = set(best_sell_times)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.current_step = 0
        self.done = False

        return self._get_observation(), {}

    def step(self, action):
        reward = 0
    
        current_price = self.candlesticks[self.current_step].Close
        # future 3 candlesticks
        future_prices = []
        for index in range(self.current_step, min(self.current_step + 4, len(self.candlesticks))):
            future_prices.append(self.candlesticks[index].Close)

        open_time = self.candlesticks[self.current_step].Opentime
        is_best_buy_time = open_time in self.best_buy_times
        is_best_sell_time = open_time in self.best_sell_time
    
        if action == TradeStatus.BUY.value: # buy
            self.buy_prices.append(current_price)
            reward = 1.5 * self._get_ratio(current_price, max(future_prices)) # 1.5: payment for selling reward
            if len(self.best_buy_times) > 0 and is_best_buy_time:
                reward += 0.1
        elif action == TradeStatus.SELL.value:  # sell
            reward = 0.0
            if len(self.buy_prices) > 0:
                buy_price = self.buy_prices.pop(0)
                # trade reward
                reward += self._get_ratio(buy_price, current_price)
            # future prices reward
            reward += 0.5 * -1 * (self._get_ratio(current_price, max(future_prices)))
            if len(self.best_sell_time) > 0 and is_best_sell_time:
                reward += 0.1
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
            # candlestick.Open,
            candlestick.Close,
            # candlestick.High,
            # candlestick.Low,
        ], dtype=np.float64)

    def _get_ratio(self, old_num:float, new_num:float) -> float:
        return round((old_num - new_num) / old_num, 3)

def _get_model_path(name:str) -> Path:
    folder = ConstantPaths.RL_MODELS
    create_folder_if_not_exists(folder)

    file_name = f'{name}_dqn_model.zip'
    return folder.joinpath(file_name)

def rl_training(name:str, candlesticks:List[CandleStick], indicators:List[Indicator], best_buy_times:List[datetime]=[], best_sell_times:List[datetime]=[], save_model=True) -> DQN:
    env = DummyVecEnv([lambda: MarketEnv(indicators, candlesticks, best_buy_times, best_sell_times)])
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
        prices = [c.Close for c in candlesticks]
        times = [c.Opentime for c in candlesticks]  # 提取 opentime
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