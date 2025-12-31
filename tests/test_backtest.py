import unittest
from unittest.mock import MagicMock
from src.trading.backtest import Backtester
from src.trading.strategy import TradingStrategy
from src.api.binance_client import BinanceClient
from config import settings
import pandas as pd

class TestBacktester(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock(spec=BinanceClient)
        self.strategy = TradingStrategy(settings.SHORT_WINDOW, settings.LONG_WINDOW)
        self.backtester = Backtester(self.mock_client, self.strategy, 'BTCUSDT', '15m', '1 day ago UTC')

    def test_run_backtest(self):
        # Sample klines data for mocking the API response
        klines_data = [
            [1625097600000, '50000', '50500', '49500', '50200', '1000', 1625098499999, '50200000', 100, '500', '25100000', '0'],
            [1625098500000, '50200', '50700', '50100', '50600', '1200', 1625099399999, '60720000', 120, '600', '30360000', '0'],
            # Add more data points as needed to test the strategy
        ]
        self.mock_client.get_historical_klines.return_value = klines_data

        # Mock the strategy to return a pre-defined signals dataframe
        signals_df = pd.DataFrame({
            'timestamp': [1625097600000, 1625098500000],
            'close': [50200.0, 50600.0],
            'positions': [1.0, -1.0] # Buy signal then a Sell signal
        })
        self.strategy.generate_signals = MagicMock(return_value=signals_df)

        self.backtester.run()

        # Assertions to check if the backtest ran as expected
        self.assertEqual(self.mock_client.get_historical_klines.call_count, 1)
        self.strategy.generate_signals.assert_called_once()
        # More specific assertions can be added here to check the final capital, profit, etc.

if __name__ == '__main__':
    unittest.main()
