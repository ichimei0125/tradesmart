from datetime import datetime
from typing import List
from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import DummyVecEnv
from pathlib import Path

from tradeengine.core.ml.reinforcement_learning import MarketEnv
from tradeengine.core.strategies import TradeStatus
from tradeengine.models.trade import CandleStick, Indicator
from tradeengine.tools.common import create_folder_if_not_exists


def _get_model_path(name:str) -> Path:
    folder = 'ml_models'
    create_folder_if_not_exists(folder)

    file_name = f'{name}_dqn_model.zip'
    return Path(folder, file_name)

def rl_training(name:str, candlesticks:List[CandleStick], indicators:List[Indicator], save_model=True) -> DQN:
    env = DummyVecEnv([lambda: MarketEnv(indicators, candlesticks)])
    check_env(env.envs[0], warn=True)

    model = DQN("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=10000)

    if save_model:
        model.save(_get_model_path(name))
    return model


def rl_run(name:str, candlesticks:List[CandleStick], indicators:List[Indicator], load_model=True, model=None) -> TradeStatus:
    if load_model:
        model= DQN.load(_get_model_path(name))
    else:
        model = model

    env = DummyVecEnv([lambda: MarketEnv(indicators, candlesticks)])
    check_env(env.envs[0], warn=True)

    action:int
    obs = env.reset()
    for _ in range(len(candlesticks)):
        action, _states = model.predict(obs)
        obs, reward, done, info = env.step(action)
        # print(f"Action: {action}, Reward: {reward}")
        if done:
            break

    return TradeStatus(action)
