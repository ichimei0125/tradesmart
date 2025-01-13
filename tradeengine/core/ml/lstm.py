from typing import List
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import LSTM, Dense # type: ignore

from tradeengine.models.candlestick import CandleStick, get_candlestick_prices

class MarketLSTM:
    def __init__(self, candlesticks:List[CandleStick]):
        self.prices = list(reversed(get_candlestick_prices(candlesticks)))

    def preprocess_data(self, look_back:int=3):
        """look_back: past days"""

        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(np.array(self.prices).reshape(-1, 1))

        X, y = [], []
        for i in range(look_back, len(scaled_data)):
            X.append(scaled_data[i - look_back:i, 0])
            y.append(scaled_data[i, 0])

        return np.array(X), np.array(y), scaler

    def create_lstm_model(self, input_shape):
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            LSTM(50, return_sequences=False),
            Dense(25),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def run(self, train_test_ratio:float=0.8, show_pic:bool=True) -> None:
        X, y, scaler = self.preprocess_data()

        split_idx = int(len(X) * train_test_ratio)
        X_train, y_train = X[:split_idx], y[:split_idx]
        X_test, y_test = X[split_idx:], y[split_idx:]

        X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
        X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

        # train
        model = self.create_lstm_model((X_train.shape[1], 1))
        model.fit(X_train, y_train, batch_size=1, epochs=10)

        # predict
        predictions = model.predict(X_test)
        predictions = scaler.inverse_transform(predictions.reshape(-1, 1))

        real_values = scaler.inverse_transform(y_test.reshape(-1, 1))

        if show_pic:
            plt.figure(figsize=(10, 6))
            plt.plot(real_values, label='Real Prices', marker='o')
            plt.plot(predictions, label='Predicted Prices', marker='x')
            plt.legend()
            plt.xlabel('Time')
            plt.ylabel('Price')
            plt.title('LSTM Price Prediction')
            plt.show()