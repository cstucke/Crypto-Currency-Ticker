import pandas as pd
from src.utils.logger import get_logger
from src.api.binance_client import BinanceClient
from src.trading.strategy import TradingStrategy
from config import settings
from datetime import datetime, timezone

logger = get_logger(__name__)

class Backtester:
    def __init__(self, client: BinanceClient, strategy: TradingStrategy, symbol: str, interval: str, start_date: str, time_format: str):
        self.client = client
        self.strategy = strategy
        self.symbol = symbol
        self.interval = interval
        self.start_date = start_date
        self.time_format = time_format
        self.initial_capital = settings.INITIAL_CAPITAL
        self.capital = settings.INITIAL_CAPITAL
        self.position = 0

    def format_timestamp(self, timestamp):
        if self.time_format == "human":
            return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
        return timestamp

    def run(self):
        logger.info("Starting backtest...")
        klines = self.client.get_historical_klines(self.symbol, self.interval, self.start_date)
        if not klines:
            logger.error("Could not fetch klines for backtesting.")
            return

        signals = self.strategy.generate_signals(klines)
        self.simulate_trades(signals)
        self.print_results(signals)

    def simulate_trades(self, signals):
        logger.info("Simulating trades...")
        for i, row in signals.iterrows():
            if row['positions'] == 1.0: # Buy signal
                if self.position == 0:
                    self.position = self.capital / row['close']
                    self.capital = 0
                    formatted_time = self.format_timestamp(row['timestamp'])
                    logger.info(f"Buying at {row['close']} on {formatted_time }")

            elif row['positions'] == -1.0: # Sell signal
                if self.position > 0:
                    self.capital = self.position * row['close']
                    self.position = 0
                    formatted_time = self.format_timestamp(row['timestamp'])
                    logger.info(f"Selling at {row['close']} on {formatted_time}")

    def print_results(self, signals):
        logger.info("Backtest finished. Results:")
        final_capital = self.capital
        if self.position > 0:
            last_close = signals['close'].iloc[-1]
            final_capital = self.position * float(last_close)

        profit = final_capital - self.initial_capital
        profit_percentage = (profit / self.initial_capital) * 100

        logger.info(f"Initial Capital: {self.initial_capital}")
        logger.info(f"Final Capital: {final_capital:.2f}")
        logger.info(f"Profit: {profit:.2f}")
        logger.info(f"Profit Percentage: {profit_percentage:.2f}%")
