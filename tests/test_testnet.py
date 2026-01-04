from src.api.binance_client import get_binance_client
from src.utils.logger import get_logger

logger = get_logger(__name__)

def test_testnet():
    client = get_binance_client()
    
    # Test getting account balance
    balances = client.get_account_balance()
    print(f"Your testnet balances: {balances}")
    
    # Test getting current price
    price = client.client.get_symbol_ticker(symbol="BTCUSDT")
    print(f"Current BTC price: {price}")

if __name__ == "__main__":
    test_testnet()