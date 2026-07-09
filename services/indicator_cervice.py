import ccxt
import pandas as pd
import ta


def get_market_data(symbol="BTC/USDT", timeframe="1h", limit=100):
    exchange = ccxt.binance()

    ohlcv = exchange.fetch_ohlcv(
        symbol=symbol,
        timeframe=timeframe,
        limit=limit
    )

    df = pd.DataFrame(
        ohlcv,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        unit="ms"
    )

    return df


def calculate_indicators(df):
    df["EMA20"] = ta.trend.ema_indicator(
        df["close"],
        window=20
    )

    df["EMA50"] = ta.trend.ema_indicator(
        df["close"],
        window=50
    )

    df["RSI"] = ta.momentum.rsi(
        df["close"],
        window=14
    )

    return df


def analyze_market(symbol="BTC/USDT", timeframe="1h"):
    df = get_market_data(symbol, timeframe)
    df = calculate_indicators(df)

    last = df.iloc[-1]

    trend = "LONG ✅" if last["EMA20"] > last["EMA50"] else "SHORT ❌"

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "price": round(last["close"], 2),
        "ema20": round(last["EMA20"], 2),
        "ema50": round(last["EMA50"], 2),
        "rsi": round(last["RSI"], 2),
        "signal": trend
    }
