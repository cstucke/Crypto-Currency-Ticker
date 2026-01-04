import pandas as pd
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
        df['close'] = pd.to_numeric(df['close'])
        df['short_mavg'] = df['close'].rolling(window=self.short_window, min_periods=1).mean()
        df['long_mavg'] = df['close'].rolling(window=self.long_window, min_periods=1).mean()

        df['signal'] = 0
        df.loc[self.short_window:, 'signal'] = (df['short_mavg'] > df['long_mavg']).astype(
            int)
        df['positions'] = df['signal'].diff()

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
                                   'number_of_trades', 'taker_buy_base_asset_volume',
                                   'taker_buy_quote_asset_volume',
                                   'ignore'])
        df['close'] = pd.to_numeric(df['close'])

        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        df['signal'] = 0
        df.loc[df['rsi'] > self.rsi_overbought, 'signal'] = -1  # Sell signal
        df.loc[df['rsi'] < self.rsi_oversold, 'signal'] = 1  # Buy signal
        df['positions'] = df['signal'].diff()

        return df


class YOLOStrategy(TradingStrategy):
    def __init__(self, dip_threshold=3.0, rip_threshold=3.0):
        self.dip_threshold = dip_threshold
        self.rip_threshold = rip_threshold

    def generate_signals(self, klines):
        logger.info("Generating trading signals for YOLO Strategy")
        df = pd.DataFrame(klines,
                          columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                   'quote_asset_volume',
                                   'number_of_trades', 'taker_buy_base_asset_volume',
                                   'taker_buy_quote_asset_volume',
                                   'ignore'])
        df['close'] = pd.to_numeric(df['close'])
        df['open'] = pd.to_numeric(df['open'])

        # Calculate percentage change for each candle
        df['pct_change'] = ((df['close'] - df['open']) / df['open']) * 100

        df['signal'] = 0
        df.loc[df['pct_change'] <= -self.dip_threshold, 'signal'] = 1  # Buy signal
        df.loc[df['pct_change'] >= self.rip_threshold, 'signal'] = -1  # Sell signal
        df['positions'] = df['signal'].diff()
        num_buys = (df['pct_change'] <= -self.dip_threshold).sum()
        num_sells = (df['pct_change'] >= self.rip_threshold).sum()
        logger.info(f"Buy signals: {num_buys}, Sell signals: {num_sells}")

        return df