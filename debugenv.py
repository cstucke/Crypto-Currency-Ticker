import os

print("=== Environment Variables Debug ===")
print(f"BINANCE_API_KEY exists: {os.environ.get('BINANCE_API_KEY') is not None}")
print(f"BINANCE_API_KEY value: {os.environ.get('BINANCE_API_KEY', 'NOT SET')[:10]}...")
print(f"BINANCE_API_SECRET exists: {os.environ.get('BINANCE_API_SECRET') is not None}")
print(f"BINANCE_API_SECRET value: {os.environ.get('BINANCE_API_SECRET', 'NOT SET')[:10]}...")
print(f"BINANCE_TESTNET: {os.environ.get('BINANCE_TESTNET', 'NOT SET')}")
print("===================================")