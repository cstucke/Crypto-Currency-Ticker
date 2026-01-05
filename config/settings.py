import os

# Binance API credentials (optional for backtesting)
API_KEY = os.environ.get('BINANCE_API_KEY')
API_SECRET = os.environ.get('BINANCE_API_SECRET')

# Testnet flag
USE_TESTNET = os.environ.get('BINANCE_TESTNET', 'false').lower() == 'true'

# Trading parameters
SYMBOL = 'BTCUSDT'
INTERVAL = '15m'
SHORT_WINDOW = 10
LONG_WINDOW = 50

# Backtesting parameters
INITIAL_CAPITAL = 10000