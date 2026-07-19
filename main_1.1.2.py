from flask import Flask
from threading import Thread
import os
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from services.indicator_service import (
    get_signal,
    get_mtf_signal
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ==========================
# Logging
# ==========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("TradePilotAI")

# ==========================
# Flask Health Check
# ==========================

web = Flask(__name__)

@web.route("/")
def health():
    return "Trade Pilot AI v1.2 ONLINE", 200


def run_web():
    port = int(os.environ.get("PORT", 8080))
    web.run(
        host="0.0.0.0",
        port=port
    )

# ==========================
# Helpers
# ==========================

def build_signal_message(data):

    if data["macd"] > data["macd_signal"]:
        macd_status = "🟢 Bullish Cross"
    else:
        macd_status = "🔴 Bearish Cross"

    if data["ema20"] > data["ema50"]:
        trend = "🟢 Bullish"
    else:
        trend = "🔴 Bearish"

    if data["score"] >= 5:
        confidence = "🔥 HIGH"

    elif data["score"] == 4:
        confidence = "⚡ GOOD"

    elif data["score"] == 3:
        confidence = "🟡 MEDIUM"

    else:
        confidence = "🔴 LOW"

    return (
        f"📊 Trade Pilot AI\n\n"
        f"🪙 Актив: {data['symbol']}\n"
        f"⏰ Таймфрейм: {data['timeframe']}\n\n"

        f"💰 Ціна: {data['price']} USDT\n"
        f"📈 EMA20: {data['ema20']}\n"
        f"📉 EMA50: {data['ema50']}\n\n"

        f"⚡ RSI14: {data['rsi']}\n"
        f"📉 MACD: {data['macd']}\n"
        f"📈 Signal: {data['macd_signal']}\n"
        f"🔔 {macd_status}\n\n"

        f"📊 ATR14: {data['atr']}\n"
        f"🔥 Volume: {data['volume']}\n"

        f"⭐ Score: {data['score']}/5\n"
        f"🎯 Confidence: {confidence}\n"
        f"📈 Trend: {trend}\n\n"

        f"📌 Support: {data['support']}\n"
        f"📌 Resistance: {data['resistance']}\n\n"

        f"📍 Signal: {data['signal']}\n\n"

        f"🛑 Stop Loss: {data['sl']}\n"
        f"🎯 TP1: {data['tp1']}\n"
        f"🎯 TP2: {data['tp2']}"
    )

# ==========================
# Commands
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logger.info("/start")

    await update.message.reply_text(
        "🚀 Trade Pilot AI v1.2 Stable\n\n"
        "Доступні команди:\n\n"
        "/status\n"
        "/menu\n"
        "/signal BTCUSDT 1h\n"
        "/mtf BTCUSDT"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logger.info("/status")

    await update.message.reply_text(
        "🟢 Trade Pilot AI ONLINE\n"
        "Version: 1.2 Stable\n"
        "Hosting: Zeabur"
    )


# ==========================
# MENU
# ==========================

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logger.info("/menu")

    keyboard = [
        [
            InlineKeyboardButton("₿ BTC", callback_data="BTCUSDT"),
            InlineKeyboardButton("Ξ ETH", callback_data="ETHUSDT")
        ],
        [
            InlineKeyboardButton("◎ SOL", callback_data="SOLUSDT"),
            InlineKeyboardButton("✕ XRP", callback_data="XRPUSDT")
        ]
    ]

    await update.message.reply_text(
        "📊 Оберіть актив:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==========================
# CALLBACK BUTTONS
# ==========================

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    callback = query.data

    logger.info(f"BUTTON -> {callback}")

    try:

        # -----------------------
        # STEP 1
        # -----------------------

        if "|" not in callback:

            symbol = callback

            keyboard = [
                [
                    InlineKeyboardButton(
                        "15m",
                        callback_data=f"{symbol}|15m"
                    ),
                    InlineKeyboardButton(
                        "1H",
                        callback_data=f"{symbol}|1h"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "4H",
                        callback_data=f"{symbol}|4h"
                    ),
                    InlineKeyboardButton(
                        "1D",
                        callback_data=f"{symbol}|1d"
                    )
                ]
            ]

            await query.edit_message_text(
                text=f"⏰ Оберіть таймфрейм для {symbol}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            return

        # -----------------------
        # STEP 2
        # -----------------------

        symbol, timeframe = callback.split("|")

        logger.info(
            f"ANALYSIS {symbol} {timeframe}"
        )

        signal_data = get_signal(
            symbol,
            timeframe
        )

        message = build_signal_message(
            signal_data
        )

        await query.edit_message_text(
            message
        )

    except Exception as e:

        logger.exception(e)

        await query.edit_message_text(
            f"❌ Помилка аналізу\n\n{e}"
        )


# ==========================
# SIGNAL
# ==========================

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logger.info("/signal")

    try:

        symbol = "BTCUSDT"
        timeframe = "1h"

        if len(context.args) >= 1:
            symbol = context.args[0].upper()

        if len(context.args) >= 2:
            timeframe = context.args[1]

        signal_data = get_signal(
            symbol,
            timeframe
        )

        await update.message.reply_text(
            build_signal_message(signal_data)
        )

    except Exception as e:

        logger.exception(e)

        await update.message.reply_text(
            f"❌ Помилка:\n{e}"
        )


# ==========================
# MULTI TIMEFRAME
# ==========================

async def mtf(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logger.info("/mtf")

    try:

        symbol = "BTCUSDT"

        if len(context.args) >= 1:
            symbol = context.args[0].upper()

        result = get_mtf_signal(symbol)

        agreement = sum(
            1
            for tf in result
            if result[tf]["signal"] == "🟢 LONG"
        )

        if agreement == 3:
            confidence = "🔥 HIGH"
            recommendation = "✅ LONG дозволений"

        elif agreement == 2:
            confidence = "⚡ MEDIUM"
            recommendation = "⚠️ Вхід можливий"

        elif agreement == 1:
            confidence = "🟡 LOW"
            recommendation = "⏳ Краще зачекати"

        else:
            confidence = "🔴 NONE"
            recommendation = "🚫 Торгівля не рекомендується"

        message = (
            f"📊 Trade Pilot AI MTF\n\n"

            f"🪙 {symbol}\n\n"

            f"15m → {result['15m']['signal']} ⭐{result['15m']['score']}/5\n"
            f"1h  → {result['1h']['signal']} ⭐{result['1h']['score']}/5\n"
            f"4h  → {result['4h']['signal']} ⭐{result['4h']['score']}/5\n\n"

            f"━━━━━━━━━━━━━━━\n"

            f"📈 Agreement : {agreement}/3\n"
            f"🎯 Confidence : {confidence}\n\n"

            f"{recommendation}"
        )

        await update.message.reply_text(
            message
        )

    except Exception as e:

        logger.exception(e)

        await update.message.reply_text(
            f"❌ Помилка:\n{e}"
        )


# ==========================
# MAIN
# ==========================

def main():

    logger.info(
        "Trade Pilot AI стартує..."
    )

    Thread(
        target=run_web,
        daemon=True
    ).start()

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "status",
            status
        )
    )

    app.add_handler(
        CommandHandler(
            "menu",
            menu
        )
    )

    app.add_handler(
        CommandHandler(
            "signal",
            signal
        )
    )

    app.add_handler(
        CommandHandler(
            "mtf",
            mtf
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            button
        )
    )

    logger.info(
        "✅ Trade Pilot AI v1.2 Stable ONLINE"
    )

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
