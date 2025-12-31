import argparse
from src.api.binance_client import get_binance_client
from src.trading.strategy import TradingStrategy
from src.trading.backtest import Backtester
from config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Binance Trading Bot')
    parser.add_argument('--mode', type=str, default='backtest', choices=['backtest', 'live'], help='Trading mode: backtest or live')
    parser.add_argument('--start-date', type=str, default='1 day ago UTC', help='Start date for backtesting')
    args = parser.parse_args()

    binance_client = get_binance_client()
    strategy = TradingStrategy(settings.SHORT_WINDOW, settings.LONG_WINDOW)

    if args.mode == 'backtest':
        logger.info("Running in backtest mode")
        backtester = Backtester(binance_client, strategy, settings.SYMBOL, settings.INTERVAL, args.start_date)
        backtester.run()
    elif args.mode == 'live':
        logger.info("Running in live trading mode")
        # Live trading logic will be implemented here in the future
        logger.warning("Live trading mode is not yet implemented.")

if __name__ == '__main__':
    main()
