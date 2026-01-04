import unittest
import pandas as pd
from src.trading.strategy import MovingAverageCrossoverStrategy, RSIStrategy, VATSStrategy


class TestStrategies(unittest.TestCase):

    def setUp(self):
        # Create a sample DataFrame for testing
        self.klines = [
            [1622505600000, '40000', '40100', '39900', '40050', '100', 1622505659999, '4000000', 1000, '50', '2000000',
             '0'],
            [1622505660000, '40050', '40200', '40000', '40150', '120', 1622505719999, '4818000', 1200, '60', '2409000',
             '0'],
            [1622505720000, '40150', '40300', '40100', '40250', '110', 1622505779999, '4427500', 1100, '55', '2213750',
             '0'],
            [1622505780000, '40250', '40400', '40200', '40350', '130', 1622505839999, '5245500', 1300, '65', '2622750',
             '0'],
            [1622505840000, '40350', '40500', '40300', '40450', '140', 1622505899999, '5663000', 1400, '70', '2831500',
             '0'],
            [1622505900000, '40450', '40600', '40400', '40000', '150', 1622505959999, '6090000', 1500, '75', '3045000',
             '0'],
            [1622505960000, '40000', '40100', '39800', '39850', '160', 1622506019999, '6376000', 1600, '80', '3188000',
             '0'],
            [1622506020000, '39850', '39900', '39700', '39750', '170', 1622506079999, '6757500', 1700, '85', '3378750',
             '0'],
            [1622506080000, '39750', '39800', '39600', '39650', '180', 1622506139999, '7137000', 1800, '90', '3568500',
             '0'],
            [1622506140000, '39650', '39700', '39500', '39550', '190', 1622506199999, '7514500', 1900, '95', '3757250',
             '0']
        ]
        self.df = pd.DataFrame(self.klines,
                               columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                        'taker_buy_quote_asset_volume', 'ignore'])
        self.df['close'] = pd.to_numeric(self.df['close'])

    def test_moving_average_crossover_strategy(self):
        strategy = MovingAverageCrossoverStrategy(short_window=3, long_window=6)
        result_df = strategy.generate_signals(self.klines)
        self.assertIn('signal', result_df.columns)
        self.assertIn('positions', result_df.columns)
        self.assertEqual(result_df['signal'].iloc[-1], 0)

    def test_rsi_strategy(self):
        strategy = RSIStrategy(rsi_period=4, rsi_overbought=70, rsi_oversold=30)
        result_df = strategy.generate_signals(self.klines)
        self.assertIn('rsi', result_df.columns)
        self.assertIn('signal', result_df.columns)
        self.assertIn('positions', result_df.columns)
        self.assertEqual(result_df['signal'].iloc[-1], 1)

    def test_vats_strategy_basic(self):
        """Test VATS strategy generates valid signals."""
        strategy = VATSStrategy(lookback_period=10, threshold=0.3, max_volatility=None)
        result_df = strategy.generate_signals(self.klines)
        self.assertIn("signal", result_df.columns)
        self.assertIn("positions", result_df.columns)
        self.assertIn("returns", result_df.columns)
        self.assertIn("rolling_mean", result_df.columns)
        self.assertIn("rolling_std", result_df.columns)
        self.assertIn("vats_score", result_df.columns)
        # Check signals are valid values (0, 1, or -1)
        valid_signals = result_df["signal"].isin([0, 1, -1]).all()
        self.assertTrue(valid_signals, "All signals should be 0, 1, or -1")


    def test_vats_strategy_volatility_filter(self):
        """Test VATS volatility filter works."""
        # Strategy with very low volatility threshold
        strategy = VATSStrategy(
            lookback_period=10,
            threshold=0.3,
            max_volatility=0.0001,  # Very low threshold - will filter most signals
        )
        result_df = strategy.generate_signals(self.klines)

        # Most signals should be filtered out (HOLD=0)
        hold_signals = (result_df["signal"] == 0).sum()
        total_signals = len(result_df)

        # At least 50% should be HOLD due to volatility filter
        self.assertGreater(
            hold_signals / total_signals,
            0.5,
            "Volatility filter should cause more HOLD signals",
        )

    def test_vats_strategy_threshold_sensitivity(self):
        """Test that higher threshold generates fewer signals."""
        # Low threshold strategy (more sensitive)
        strategy_low = VATSStrategy(lookback_period=10, threshold=0.2)
        df_low = strategy_low.generate_signals(self.klines)
        signals_low = (df_low["positions"] != 0).sum()

        # High threshold strategy (less sensitive)
        strategy_high = VATSStrategy(lookback_period=10, threshold=0.8)
        df_high = strategy_high.generate_signals(self.klines)
        signals_high = (df_high["positions"] != 0).sum()

        # Lower threshold should generate more signals
        self.assertGreaterEqual(
            signals_low,
            signals_high,
            "Lower threshold should generate equal or more signals",
        )

if __name__ == '__main__':
    unittest.main()
