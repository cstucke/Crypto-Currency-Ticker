import pandas as pd
import numpy as np
from src.utils.logger import get_logger
from abc import ABC, abstractmethod

logger = get_logger(__name__)


class TradingStrategy(ABC):
    @abstractmethod
    def generate_signals(self, klines):
        raise NotImplementedError


class MovingAverageCrossoverStrategy(TradingStrategy):
    def __init__(self, short_window, long_window):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, klines):
        logger.info("Generating trading signals for Moving Average Crossover Strategy")
        df = pd.DataFrame(klines,
                          columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                   'quote_asset_volume',
                                   'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
                                   'ignore'])
        df["close"] = pd.to_numeric(df["close"])
        df["short_mavg"] = (
            df["close"].rolling(window=self.short_window, min_periods=1).mean()
        )
        df["long_mavg"] = (
            df["close"].rolling(window=self.long_window, min_periods=1).mean()
        )

        df["signal"] = 0
        df.loc[self.short_window :, "signal"] = (
            df["short_mavg"] > df["long_mavg"]
        ).astype(int)
        df["positions"] = df["signal"].diff()

        return df


class RSIStrategy(TradingStrategy):
    def __init__(self, rsi_period=14, rsi_overbought=70, rsi_oversold=30):
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

    def generate_signals(self, klines):
        logger.info("Generating trading signals for RSI Strategy")
        df = pd.DataFrame(klines,
                          columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                   'quote_asset_volume',
                                   'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
                                   'ignore'])
        df["close"] = pd.to_numeric(df["close"])

        # Calculate RSI
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))

        df["signal"] = 0
        df.loc[df["rsi"] > self.rsi_overbought, "signal"] = -1  # Sell signal
        df.loc[df["rsi"] < self.rsi_oversold, "signal"] = 1  # Buy signal
        df["positions"] = df["signal"].diff()

        return df


class VATSStrategy(TradingStrategy):
    """
    Volatility-Adjusted Trend Score (VATS) Strategy.
    Computes simple returns from a sequence of prices.
    Generates a BUY, SELL, or HOLD signal based on a volatility-adjusted trend score.
    """

    def __init__(self, lookback_period=20, threshold=0.5, max_volatility=None):
        self.lookback_period = lookback_period
        self.threshold = threshold
        self.max_volatility = max_volatility

    def generate_signals(self, klines):
        logger.info("Generating trading signals for VATS Strategy")
        df = pd.DataFrame(klines,
                          columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                   'quote_asset_volume',
                                   'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
                                   'ignore'])
        df["close"] = pd.to_numeric(df["close"])

        # pct_change() is equivalent to: (price[i] - price[i-1]) / price[i-1]
        df["returns"] = df["close"].pct_change()
        df["rolling_mean"] = df["returns"].rolling(window=self.lookback_period).mean()
        df["rolling_std"] = df["returns"].rolling(window=self.lookback_period).std()
        # Calculate VATS score = μ / σ (risk-adjusted momentum)
        df["vats_score"] = np.where(  # avoids division with zero
            df["rolling_std"] > 0,
            df["rolling_mean"] / df["rolling_std"],
            0,
        )
        df["signal"] = 0  # HOLD
        df.loc[df["vats_score"] > self.threshold, "signal"] = 1  # BUY
        df.loc[df["vats_score"] < -self.threshold, "signal"] = -1  # SELL
        # Apply volatility filter
        if self.max_volatility is not None:
            high_volatility = df["rolling_std"] > self.max_volatility
            #  HOLD during high volatility periods
            df.loc[high_volatility, "signal"] = 0
        df["signal"] = df["signal"].replace(0, np.nan).ffill().fillna(0)
        df["positions"] = df["signal"].diff()
        logger.info(
            f"VATS debug — "
            f"mean score={df['vats_score'].mean():.4f}, "
            f"max score={df['vats_score'].max():.4f}, "
            f"min score={df['vats_score'].min():.4f}"
        )
        return df
    
class BollingerBandsStrategy(TradingStrategy):
    def __init__(self, window=20, num_std=2):
        self.window = window
        self.num_std = num_std

    def generate_signals(self, klines):
        logger.info("Generating trading signals for Bollinger Bands Strategy")

        df = pd.DataFrame(
            klines,
            columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
                'ignore'
            ]
        )

        df['close'] = pd.to_numeric(df['close'])

        # Bollinger Bands calculation
        df['middle_band'] = df['close'].rolling(window=self.window).mean()
        df['std'] = df['close'].rolling(window=self.window).std()
        df['upper_band'] = df['middle_band'] + self.num_std * df['std']
        df['lower_band'] = df['middle_band'] - self.num_std * df['std']

        # Signals
        df['signal'] = 0
        df.loc[df['close'] < df['lower_band'], 'signal'] = 1   # Buy
        df.loc[df['close'] > df['upper_band'], 'signal'] = -1  # Sell

        df['positions'] = df['signal'].diff()

        return df

