from src.api.binance_client import get_binance_client
from src.utils.logger import get_logger

logger = get_logger(__name__)

def test_testnet():
    logger.info("Testing Binance Testnet connection...")
    
    try:
        client = get_binance_client()
        # Test 1: Get account balance
        logger.info("Test 1: Fetching account balances...")
        balances = client.get_account_balance()
        print("YOUR TESTNET BALANCES:")
        for asset, amount in balances.items():
            print(f"{asset}: {amount}")
        
        # Test 2: Get current BTC price
        logger.info("Test 2: Fetching current BTC price...")
        price = client.client.get_symbol_ticker(symbol="BTCUSDT")
        print(f"Current BTC/USDT price: ${float(price['price']):,.2f}\n")
        
        # Test 3: Get server time (tests connection)
        logger.info("Test 3: Testing server connection...")
        server_time = client.client.get_server_time()
        print(f"Binance server time: {server_time['serverTime']}\n")
        
        logger.info("All tests passed.")
        
    except Exception as e:
        logger.error(f"Error testing testnet: {e}")

if __name__ == "__main__":
    test_testnet()