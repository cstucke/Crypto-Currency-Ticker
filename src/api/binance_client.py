from binance.client import Client
from config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class BinanceClient:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)

    def get_historical_klines(self, symbol, interval, start_str, end_str=None):
        logger.info(f"Fetching historical klines for {symbol} with interval {interval}")
        try:
            klines = self.client.get_historical_klines(symbol, interval, start_str, end_str)
            return klines
        except Exception as e:
            logger.error(f"Error fetching historical klines: {e}")
            return []

    def place_order(self, symbol, side, type, quantity):
        logger.info(f"Placing a {side} order for {quantity} of {symbol}")
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=type,
                quantity=quantity
            )
            logger.info(f"Order placed: {order}")
            return order
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None

def get_binance_client():
    return BinanceClient(settings.API_KEY, settings.API_SECRET)
