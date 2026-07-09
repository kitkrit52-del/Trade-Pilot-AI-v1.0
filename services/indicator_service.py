import ccxt
import pandas as pd
import ta


def get_signal(symbol="BTCUSDT", timeframe="1h"):
    exchange = ccxt.binance()

    pair = symbol.replace("USDT", "/USDT")

    candles = exchange.fetch_ohlcv(
        pair,
        timeframe=timeframe,
        limit=100
    )

    df = pd.DataFrame(
        candles,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    )

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

    last = df.iloc[-1]

    price = float(last["close"])
    ema20 = float(last["EMA20"])
    ema50 = float(last["EMA50"])
    rsi = float(last["RSI"])

    if ema20 > ema50 and rsi > 55:
        signal = "🟢 LONG"
    elif ema20 < ema50 and rsi < 45:
        signal = "🔴 SHORT"
    else:
        signal = "⚪ SKIP"

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "price": round(price, 2),
        "ema20": round(ema20, 2),
        "ema50": round(ema50, 2),
        "rsi": round(rsi, 2),
        "signal": signal,
        "sl": round(price * 0.99, 2),
        "tp1": round(price * 1.02, 2),
        "tp2": round(price * 1.04, 2),
    }
