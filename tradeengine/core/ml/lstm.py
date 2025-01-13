from pathlib import Path
from typing import List, Optional
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import LSTM, Dense # type: ignore
from tensorflow.keras.models import load_model # type: ignore

from tradeengine.core.strategies import TradeStatus
from tradeengine.models.candlestick import CandleStick, get_candlestick_prices
from tradeengine.tools.common import create_folder_if_not_exists
from tradeengine.tools.constants import ConstantPaths

class MarketLSTM:
    def __init__(self, candlesticks:List[CandleStick]):
        self.prices = list(reversed(get_candlestick_prices(candlesticks)))
        self.times = list(reversed(get_candlestick_prices(candlesticks, 'opentime')))

    def preprocess_data(self, look_back:int=3):
        """look_back: past days"""

        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(np.array(self.prices).reshape(-1, 1))

        X, y = [], []
        for i in range(look_back, len(scaled_data)):
            X.append(scaled_data[i - look_back:i, 0])
            y.append(scaled_data[i, 0])

        return np.array(X), np.array(y), scaler

    def create_lstm_model(self, input_shape) -> Sequential:
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            LSTM(50, return_sequences=False),
            Dense(25),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def train_model(self, train_test_ratio:float=0.8, save_path:Optional[str]=None, show_pic:bool=True) -> Sequential:
        X, y, scaler = self.preprocess_data()

        split_idx = int(len(X) * train_test_ratio)
        X_train, y_train = X[:split_idx], y[:split_idx]
        X_test, y_test = X[split_idx:], y[split_idx:]
        train_times = self.times[:split_idx]
        test_times = self.times[split_idx+3:]

        X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
        X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

        # train
        model = self.create_lstm_model((X_train.shape[1], 1))
        model.fit(X_train, y_train, batch_size=1, epochs=10)

        if save_path:
            model.save(save_path)

        # predict
        predictions = model.predict(X_test)
        predictions = scaler.inverse_transform(predictions.reshape(-1, 1))

        real_values = scaler.inverse_transform(y_test.reshape(-1, 1))

        if show_pic:
            plt.figure(figsize=(10, 6))
            plt.plot(self.times, self.prices, label='Real Prices', marker='o')
            plt.plot(test_times, predictions, label='Predicted Prices', marker='x')
            plt.legend()
            plt.xlabel('Time')
            plt.ylabel('Price')
            plt.title('LSTM Price Prediction')
            plt.show()

        return model

    def predict(self, model:Optional[Sequential]=None, save_path:str="", show_pic:bool=True) -> List[float]:
        if not model:
            model = load_model(save_path)

        X, y, scaler = self.preprocess_data()

        # predict
        predictions = model.predict(X)
        predictions = scaler.inverse_transform(predictions.reshape(-1, 1))

        real_values = scaler.inverse_transform(y.reshape(-1, 1))

        if show_pic:
            plt.figure(figsize=(10, 6))
            plt.plot(real_values, label='Real Prices', marker='o')
            plt.plot(predictions, label='Predicted Prices', marker='x')
            plt.legend()
            plt.xlabel('Time')
            plt.ylabel('Price')
            plt.title('LSTM Price Prediction')
            plt.show()

        return predictions

def _get_model_path(name:str) -> Path:
    folder = ConstantPaths.LSTM_MODELS
    create_folder_if_not_exists(folder)

    file_name = f'{name}_lstm_model.keras'
    return folder.joinpath(file_name)

def lstm_training(name, candlesticks: List[CandleStick]) -> None:
    engine = MarketLSTM(candlesticks)
    engine.train_model(save_path=_get_model_path(name), show_pic=False)

def lstm_run(name, candlesticks: List[CandleStick]) -> List[float]:
    engine = MarketLSTM(candlesticks)
    res = engine.predict(save_path=_get_model_path(name))

    return res 