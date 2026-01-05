import argparse
from src.api.binance_client import get_binance_client
from src.trading.strategy import (
    MovingAverageCrossoverStrategy,
    RSIStrategy,
    BollingerBandsStrategy,
    VATSStrategy
)
from src.trading.vwap_strategy import VWAPStrategy
from src.trading.backtest import Backtester
from config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


STRATEGIES = {
    "ma": {
        "name": "Moving Average Crossover",
        "class": MovingAverageCrossoverStrategy,
        "params": {
            "short_window": settings.SHORT_WINDOW,
            "long_window": settings.LONG_WINDOW,
        },
    },
    "rsi": {
        "name": "RSI Strategy",
        "class": RSIStrategy,
        "params": {"rsi_period": 14, "rsi_overbought": 70, "rsi_oversold": 30},
    },
    "bb": {
        "name": "Bollinger Bands Strategy",
        "class": BollingerBandsStrategy,
        "params": {
            "window": 20,
            "num_std": 2,
        },
    },
            "num_std": 2
    "vats": {
        "name": "VATS (Volatility-Adjusted Trend Score)",
        "class": VATSStrategy,
        "params": {
            "lookback_period": 20,
            "threshold": 0.5,
            "max_volatility": None,
        },
    },
    "vwap": {
        "name": "Rolling VWAP",
        "class": VWAPStrategy,
        "params": {
            "window": 20,
        },
    }
}

def get_strategy(strategy_name):
    if strategy_name not in STRATEGIES:
        available = ", ".join(STRATEGIES.keys())
        raise ValueError(f"Unknown strategy '{strategy_name}'. Available: {available}")

    strategy_config = STRATEGIES[strategy_name]
    logger.info(f"Loading strategy: {strategy_config['name']}")

    # Instantiate the strategy class with its parameters
    strategy_class = strategy_config["class"]
    strategy_params = strategy_config["params"]
    strategy_instance = strategy_class(**strategy_params)

    return strategy_instance


def main():
    parser = argparse.ArgumentParser(description="Binance Trading Bot")
    parser.add_argument(
        "--strategy",
        type=str,
        default="ma",
        choices=list(STRATEGIES.keys()),
        help="Trading strategy to use (default: ma). Options: ma, rsi, bb, vats",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="backtest",
        choices=["backtest", "live"],
        help="Trading mode: backtest or live",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default="1 day ago UTC",
        help="Start date for backtesting",
    )
    parser.add_argument(
        "--time-format",
        type=str,
        default="unix",
        choices=["unix", "human"],
        help="Timestamp format for trade logs: unix or human (default: unix)",
    )
    args = parser.parse_args()

    binance_client = get_binance_client()

    try:
        strategy = get_strategy(args.strategy)
        logger.info(
            f"Strategy loaded successfully: {STRATEGIES[args.strategy]['name']}"
        )
    except Exception as e:
        logger.error(f"Failed to load strategy: {e}")
        return

    if args.mode == "backtest":
        logger.info("Running in backtest mode")
        backtester = Backtester(
            binance_client,
            strategy,
            settings.SYMBOL,
            settings.INTERVAL,
            args.start_date,
            time_format=args.time_format,
        )
        backtester.run()
    elif args.mode == "live":
        logger.info("Running in live trading mode")
        # Live trading logic will be implemented here in the future
        logger.warning("Live trading mode is not yet implemented.")


if __name__ == "__main__":
    main()