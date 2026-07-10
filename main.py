from flask import Flask
from threading import Thread
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler
)
from services.indicator_service import get_signal, get_mtf_signal
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

web = Flask(__name__)

@web.route("/")
def health():
    return "Trade Pilot AI is running", 200


def run_web():
    port = int(os.environ.get("PORT", 8080))
    web.run(host="0.0.0.0", port=port)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Trade Pilot AI v1.1\n\n"
        "Доступні команди:\n"
        "/start\n"
        "/status\n"
        "/signal BTCUSDT 1h\n"
        "/signal ETHUSDT 15m"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🟢 Trade Pilot AI працює\n"
        "Версія: 1.1\n"
        "Хостинг: Zeabur\n"
        "Статус: ONLINE"
    )
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📊 Оберіть актив:",
        reply_markup=reply_markup
    )
    await update.message.reply_text(
        "📊 Оберіть актив:",
        reply_markup=reply_markup
    )
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # Крок 1 — вибір активу
    if data in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]:

        keyboard = [
            [
                InlineKeyboardButton("15m", callback_data=f"{data}|15m"),
                InlineKeyboardButton("1h", callback_data=f"{data}|1h")
            ],
            [
                InlineKeyboardButton("4h", callback_data=f"{data}|4h"),
                InlineKeyboardButton("1D", callback_data=f"{data}|1d")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"⏰ Оберіть таймфрейм для {data}:",
            reply_markup=reply_markup
        )
        return

    # Крок 2 — аналіз після вибору таймфрейму
    symbol, timeframe = data.split("|")

    signal_data = get_signal(symbol, timeframe)

    message = (
        f"📊 Trade Pilot AI\n\n"
        f"Актив: {signal_data['symbol']}\n"
        f"Таймфрейм: {signal_data['timeframe']}\n\n"
        f"💰 Ціна: {signal_data['price']} USDT\n"
        f"📈 EMA20: {signal_data['ema20']}\n"
        f"📉 EMA50: {signal_data['ema50']}\n"
        f"⚡ RSI14: {signal_data['rsi']}\n"
        f"📊 ATR14: {signal_data['atr']}\n"
        f"🔥 Volume: {signal_data['volume']}\n"
        f"⭐ Сила сигналу: {signal_data['score']}/4\n\n"
        f"📌 Support: {signal_data['support']}\n"
        f"📌 Resistance: {signal_data['resistance']}\n\n"
        f"📍 Сигнал: {signal_data['signal']}\n\n"
        f"🛑 Stop Loss: {signal_data['sl']}\n"
        f"🎯 TP1: {signal_data['tp1']}\n"
        f"🎯 TP2: {signal_data['tp2']}"
    )

    await query.edit_message_text(message)

    message = (
        f"📊 Trade Pilot AI\n\n"
        f"Актив: {data['symbol']}\n"
        f"Таймфрейм: {data['timeframe']}\n\n"
        f"💰 Ціна: {data['price']} USDT\n"
        f"📈 EMA20: {data['ema20']}\n"
        f"📉 EMA50: {data['ema50']}\n"
        f"⚡ RSI14: {data['rsi']}\n"
        f"📊 ATR14: {data['atr']}\n"
        f"🔥 Volume: {data['volume']}\n"
        f"⭐ Сила сигналу: {data['score']}/4\n\n"
        f"📌 Support: {data['support']}\n"
        f"📌 Resistance: {data['resistance']}\n\n"
        f"📍 Сигнал: {data['signal']}\n\n"
        f"🛑 Stop Loss: {data['sl']}\n"
        f"🎯 TP1: {data['tp1']}\n"
        f"🎯 TP2: {data['tp2']}"
    )

    await query.edit_message_text(message)
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = "BTCUSDT"
        timeframe = "1h"

        if len(context.args) >= 1:
            symbol = context.args[0].upper()

        if len(context.args) >= 2:
            timeframe = context.args[1]

        # Отримуємо дані аналізу
        data = get_signal(symbol, timeframe)

        message = (
            f"📊 Trade Pilot AI\n\n"
            f"Актив: {data['symbol']}\n"
            f"Таймфрейм: {data['timeframe']}\n\n"
            f"💰 Ціна: {data['price']} USDT\n"
            f"📈 EMA20: {data['ema20']}\n"
            f"📉 EMA50: {data['ema50']}\n"
            f"⚡ RSI14: {data['rsi']}\n"
            f"📊 ATR14: {data.get('atr', 'N/A')}\n"
            f"🔥 Volume: {data.get('volume', 'N/A')}\n"
            f"⭐ Сила сигналу: {data.get('score', 'N/A')}/4\n\n"
            f"📌 Support: {data.get('support', 'N/A')}\n"
            f"📌 Resistance: {data.get('resistance', 'N/A')}\n\n"
            f"📍 Сигнал: {data['signal']}\n\n"
            f"🛑 Stop Loss: {data['sl']}\n"
            f"🎯 TP1: {data['tp1']}\n"
            f"🎯 TP2: {data['tp2']}"
        )

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(
            f"❌ Помилка аналізу:\n{str(e)}"
        )

async def mtf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = "BTCUSDT"

    if len(context.args) >= 1:
        symbol = context.args[0].upper()

    result = get_mtf_signal(symbol)

    agreement = 0

    for tf in result:
        if result[tf]["signal"] == "🟢 LONG":
            agreement += 1

    agreement = 0

for tf in result:
    if result[tf]["signal"] == "🟢 LONG":
        agreement += 1

if agreement == 3:
    confidence = "🔥 HIGH"
    recommendation = "✅ LONG дозволений"

elif agreement == 2:
    confidence = "⚡ MEDIUM"
    recommendation = "⚠️ Вхід можливий з підтвердженням"

elif agreement == 1:
    confidence = "⚠️ LOW"
    recommendation = "⏳ Краще зачекати"

else:
    confidence = "❌ NONE"
    recommendation = "🚫 Торгівля не рекомендується"

message = (
    f"📊 Trade Pilot AI MTF\n\n"
    f"{symbol}\n\n"
    f"15m → {result['15m']['signal']} ⭐{result['15m']['score']}/4\n"
    f"1h → {result['1h']['signal']} ⭐{result['1h']['score']}/4\n"
    f"4h → {result['4h']['signal']} ⭐{result['4h']['score']}/4\n\n"
    f"━━━━━━━━━━━━━━━\n"
    f"📈 Узгодження: {agreement}/3\n"
    f"🎯 Confidence: {confidence}\n\n"
    f"{recommendation}"
)

await update.message.reply_text(message)
def main():
    Thread(target=run_web, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("mtf", mtf))
    app.add_handler(CallbackQueryHandler(button))

    print("🚀 Trade Pilot AI v1.1 запущено")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
