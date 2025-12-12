from binance.client import Client
import pandas as pd

# 1. Connect to Binance (public data only)
client = Client()

# 2. Request last 100 candles of 15-minute data
klines = client.get_klines(
    symbol="BTCUSDT",
    interval=Client.KLINE_INTERVAL_15MINUTE,
    limit=20
)

# 3. Define column names
columns = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_asset_volume",
    "number_of_trades",
    "taker_buy_base", "taker_buy_quote", "ignore"
]

# 4. Convert to DataFrame
df = pd.DataFrame(klines, columns=columns)

# 5. Convert numerical columns to float
for col in ["open", "high", "low", "close", "volume"]:
    df[col] = df[col].astype(float)

# 6. Convert timestamps
df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")

# 7. Display result
print(df[["open_time", "open", "high", "low", "close", "volume"]])
