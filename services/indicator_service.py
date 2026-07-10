import ccxt
import pandas as pd
import ta


def get_signal(symbol="BTCUSDT", timeframe="1h"):
    exchange = ccxt.binance({
        "enableRateLimit": True
    })
def get_mtf_signal(symbol="BTCUSDT"):
    timeframes = ["15m", "1h", "4h"]

    results = {}

    for tf in timeframes:
        data = get_signal(symbol, tf)

        results[tf] = {
            "signal": data["signal"],
            "score": data["score"]
        }

    return results
    pair = symbol.replace("USDT", "/USDT")

    candles = exchange.fetch_ohlcv(
        pair,
        timeframe=timeframe,
        limit=150
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

    # EMA
    df["EMA20"] = ta.trend.ema_indicator(
        df["close"],
        window=20
    )

    df["EMA50"] = ta.trend.ema_indicator(
        df["close"],
        window=50
    )

    # RSI
    df["RSI"] = ta.momentum.rsi(
        df["close"],
        window=14
    )

    # ATR
    atr_indicator = ta.volatility.AverageTrueRange(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=14
    )

    df["ATR"] = atr_indicator.average_true_range()

    last = df.iloc[-1]

    price = round(float(last["close"]), 2)
    ema20 = round(float(last["EMA20"]), 2)
    ema50 = round(float(last["EMA50"]), 2)
    rsi = round(float(last["RSI"]), 2)
    atr = round(float(last["ATR"]), 2)

    # Volume analysis
    avg_volume = df["volume"].tail(20).mean()
    current_volume = float(last["volume"])

    if current_volume > avg_volume * 1.5:
        volume = "HIGH 🔥"
    else:
        volume = "NORMAL"

    # Support / Resistance
    support = round(float(df["low"].tail(20).min()), 2)
    resistance = round(float(df["high"].tail(20).max()), 2)

    # Signal strength
    score = 0

    if ema20 > ema50:
        score += 1

    if rsi > 55:
        score += 1

    if current_volume > avg_volume * 1.5:
        score += 1

    if price > support:
        score += 1

    # Trading signal
    if ema20 > ema50 and rsi > 55:
        signal = "🟢 LONG"
        sl = round(price - atr * 1.5, 2)
        tp1 = round(price + atr * 2, 2)
        tp2 = round(price + atr * 4, 2)

    elif ema20 < ema50 and rsi < 45:
        signal = "🔴 SHORT"
        sl = round(price + atr * 1.5, 2)
        tp1 = round(price - atr * 2, 2)
        tp2 = round(price - atr * 4, 2)

    else:
        signal = "🟡 WAIT"
        sl = "-"
        tp1 = "-"
        tp2 = "-"

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "price": price,
        "ema20": ema20,
        "ema50": ema50,
        "rsi": rsi,
        "atr": atr,
        "volume": volume,
        "score": score,
        "support": support,
        "resistance": resistance,
        "signal": signal,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2
    }
