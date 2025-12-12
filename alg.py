from binance.client import Client
import pandas as pd

# ----------------------------------
# 1. Get 15-minute BTCUSDT candles
# ----------------------------------
client = Client()

klines = client.get_klines(
    symbol="BTCUSDT",
    interval=Client.KLINE_INTERVAL_1SECOND,
    limit=200
)

columns = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_asset_volume",
    "number_of_trades",
    "taker_buy_base", "taker_buy_quote", "ignore"
]

df = pd.DataFrame(klines, columns=columns)

df["close"] = df["close"].astype(float)
df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")

# ----------------------------------
# 2. Compute SMAs
# ----------------------------------
df["fast_sma"] = df["close"].rolling(window=9).mean()
df["slow_sma"] = df["close"].rolling(window=21).mean()

df = df.dropna()

# ----------------------------------
# 3. BUY or SELL ONLY
# ----------------------------------
fast_now = df["fast_sma"].iloc[-1]
slow_now = df["slow_sma"].iloc[-1]

if fast_now > slow_now:
    print("BUY")
else:
    print("SELL")
