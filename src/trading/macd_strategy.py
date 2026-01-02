import pandas as pd
from src.utils.logger import get_logger
from src.trading.strategy import TradingStrategy

logger = get_logger(__name__)


class MACDStrategy(TradingStrategy):
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        """
        Initialize MACD Strategy
        
        Args:
            fast_period: Period for fast EMA (default: 12)
            slow_period: Period for slow EMA (default: 26)
            signal_period: Period for signal line EMA (default: 9)
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        logger.info(f"Initialized MACD Strategy with periods: {fast_period}/{slow_period}/{signal_period}")

    def calculate_ema(self, data, period):
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()

    def generate_signals(self, klines):
        """
        Generate trading signals based on MACD crossover
        
        Args:
            klines: Raw kline data from Binance API
            
        Returns:
            DataFrame with MACD indicators and trading signals
        """
        logger.info("Generating trading signals for MACD Strategy")
        
        # Parse kline data into DataFrame
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 
            'close_time', 'quote_asset_volume', 'number_of_trades', 
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        # Convert close price to numeric
        df['close'] = pd.to_numeric(df['close'])
        
        # Calculate MACD components
        df['ema_fast'] = self.calculate_ema(df['close'], self.fast_period)
        df['ema_slow'] = self.calculate_ema(df['close'], self.slow_period)
        
        # MACD Line = Fast EMA - Slow EMA
        df['macd_line'] = df['ema_fast'] - df['ema_slow']
        
        # Signal Line = 9-period EMA of MACD Line
        df['signal_line'] = self.calculate_ema(df['macd_line'], self.signal_period)
        
        # MACD Histogram (optional, for visualization)
        df['macd_histogram'] = df['macd_line'] - df['signal_line']
        
        # Generate trading signals
        # Signal = 1 when MACD line is above signal line (bullish)
        # Signal = -1 when MACD line is below signal line (bearish)
        # Signal = 0 for neutral
        df['signal'] = 0
        df.loc[df['macd_line'] > df['signal_line'], 'signal'] = 1   # Buy signal
        df.loc[df['macd_line'] < df['signal_line'], 'signal'] = -1  # Sell signal
        
        # Positions: 1 = Buy signal (crossover), -1 = Sell signal (crossunder), 0 = Hold
        df['positions'] = df['signal'].diff()
        
        logger.info(f"Generated {len(df[df['positions'] > 0])} buy signals and {len(df[df['positions'] < 0])} sell signals")
        
        return df