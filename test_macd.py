import argparse
from src.api.binance_client import get_binance_client
from src.trading.strategy import MovingAverageCrossoverStrategy, RSIStrategy
from src.trading.macd_strategy import MACDStrategy
from src.trading.backtest import Backtester
from config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

def run_strategy_comparison(start_date='7 days ago UTC'):
    """
    Run backtests for multiple strategies and compare results
    """
    logger.info("=" * 60)
    logger.info("STRATEGY COMPARISON BACKTEST")
    logger.info("=" * 60)
    
    binance_client = get_binance_client()
    
    # Define strategies to test
    strategies = {
        'Moving Average Crossover': MovingAverageCrossoverStrategy(
            settings.SHORT_WINDOW, 
            settings.LONG_WINDOW
        ),
        'MACD': MACDStrategy(
            fast_period=12, 
            slow_period=26, 
            signal_period=9
        ),
        'RSI': RSIStrategy(
            rsi_period=14,
            rsi_overbought=70,
            rsi_oversold=30
        )
    }
    
    results = {}
    
    # Run backtest for each strategy
    for strategy_name, strategy in strategies.items():
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Testing Strategy: {strategy_name}")
        logger.info(f"{'=' * 60}")
        
        backtester = Backtester(
            binance_client, 
            strategy, 
            settings.SYMBOL, 
            settings.INTERVAL, 
            start_date
        )
        backtester.run()
        
        # Store results
        final_capital = backtester.capital
        if backtester.position > 0:
            # If still holding position, calculate current value
            klines = binance_client.get_historical_klines(
                settings.SYMBOL, 
                settings.INTERVAL, 
                start_date
            )
            if klines:
                last_close = float(klines[-1][4])  # Close price
                final_capital = backtester.position * last_close
        
        profit = final_capital - settings.INITIAL_CAPITAL
        profit_percentage = (profit / settings.INITIAL_CAPITAL) * 100
        
        results[strategy_name] = {
            'final_capital': final_capital,
            'profit': profit,
            'profit_percentage': profit_percentage
        }
    
    print_comparison_summary(results)

def print_comparison_summary(results):
    """
    Print a formatted comparison of all strategy results
    """
    logger.info("\n" + "=" * 60)
    logger.info("COMPARISON SUMMARY")
    logger.info("=" * 60)
    
    sorted_results = sorted(
        results.items(), 
        key=lambda x: x[1]['profit_percentage'], 
        reverse=True
    )
    
    logger.info(f"\nInitial Capital: ${settings.INITIAL_CAPITAL:,.2f}")
    logger.info(f"Symbol: {settings.SYMBOL}")
    logger.info(f"Interval: {settings.INTERVAL}\n")
    
    for rank, (strategy_name, result) in enumerate(sorted_results, 1):
        logger.info(f"{rank}. {strategy_name}")
        logger.info(f"   Final Capital: ${result['final_capital']:,.2f}")
        logger.info(f"   Profit: ${result['profit']:,.2f}")
        logger.info(f"   Profit %: {result['profit_percentage']:.2f}%")
        logger.info("")
    
    best_strategy = sorted_results[0][0]
    logger.info(f"Best Performing Strategy: {best_strategy}")
    logger.info("=" * 60)

def main():
    parser = argparse.ArgumentParser(description='Test MACD Strategy and Compare with Others')
    parser.add_argument(
        '--start-date', 
        type=str, 
        default='7 days ago UTC', 
        help='Start date for backtesting (e.g., "7 days ago UTC", "1 Jan, 2024")'
    )
    parser.add_argument(
        '--strategy',
        type=str,
        choices=['macd', 'ma', 'rsi', 'all'],
        default='all',
        help='Which strategy to test (default: all)'
    )
    args = parser.parse_args()
    
    binance_client = get_binance_client()
    
    if args.strategy == 'all':
        run_strategy_comparison(args.start_date)
    else:
        # Run single strategy backtest
        if args.strategy == 'macd':
            strategy = MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
            strategy_name = "MACD"
        elif args.strategy == 'ma':
            strategy = MovingAverageCrossoverStrategy(settings.SHORT_WINDOW, settings.LONG_WINDOW)
            strategy_name = "Moving Average Crossover"
        elif args.strategy == 'rsi':
            strategy = RSIStrategy(rsi_period=14, rsi_overbought=70, rsi_oversold=30)
            strategy_name = "RSI"
        
        logger.info(f"Testing {strategy_name} Strategy")
        backtester = Backtester(
            binance_client, 
            strategy, 
            settings.SYMBOL, 
            settings.INTERVAL, 
            args.start_date
        )
        backtester.run()

if __name__ == '__main__':
    main()