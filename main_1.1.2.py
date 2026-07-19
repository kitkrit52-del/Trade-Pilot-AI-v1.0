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
