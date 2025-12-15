from binance.client import Client

client = Client()

price = client.get_symbol_ticker(symbol="BTCUSDT")
print(price)
