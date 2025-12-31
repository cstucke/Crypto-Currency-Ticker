import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)

class TradingStrategy:
    def __init__(self, short_window, long_window):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, klines):
        logger.info("Generating trading signals")
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['close'] = pd.to_numeric(df['close'])
        df['short_mavg'] = df['close'].rolling(window=self.short_window, min_periods=1).mean()
        df['long_mavg'] = df['close'].rolling(window=self.long_window, min_periods=1).mean()

        df['signal'] = 0
        df.loc[self.short_window:, 'signal'] = (df['short_mavg'][self.short_window:] > df['long_mavg'][self.short_window:]).astype(int)
        df['positions'] = df['signal'].diff()

        return df
