import pandas as pd
from src.trading.strategy import TradingStrategy
from src.utils.logger import get_logger

logger = get_logger(__name__)

class VWAPStrategy(TradingStrategy):
    def __init__(self, window = 20):
        """
        Initialize a rolling VWAP (Volume-weighted average price) strategy

        VWAP is the ratio of cumulative traded value to cumulative traded volume over the specified window.
        The window is defined by the number of data points (default 20). Each data point represents a specific
        "snapshot" of the market depending upon how frequently we're getting new data (e.g. 1 minute, 24 hours).

        Args:
            window: The number of periods (i.e. data points) to calculate VWAP over. Must be a positive integer
        """
        self.window = window

    def generate_signal(self, klines):
        logger.info("Generating trading signals for VWAP Strategy")

        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])

        # Dataframe column to numeric conversion
        for col in ['high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])

        # Typical Price = (High + Low + Close) / 3
        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3

        df['vp'] = df['typical_price'] * df['volume']

        # Rolling VWAP Calculation: sum ( Volume * Price ) / sum ( Volume )
        df['rolling_vp_sum'] = df['vp'].rolling(window=self.window).sum()
        df['rolling_vol_sum'] = df['volume'].rolling(window=self.window).sum()

        # Actual VWAP Calculation based on rolling components
        df['vwap'] = df['rolling_vp_sum'] / df['rolling_vol_sum']

        """
        Generating final signals
        
        BUY when close crosses above VWAP (Bullish condition)
        Sell when close crosses below VWAP (Bearish condition)
        where:
            1 = Buy Order, -1 = Sell Order
        """

        df['signal'] = 0

        df.loc[df['close'] > df['vwap'], 'signal'] = 1

        df.loc[df['close'] < df['vwap'], 'signal'] = -1

        df['positions'] = df['signal'].diff()

        return df