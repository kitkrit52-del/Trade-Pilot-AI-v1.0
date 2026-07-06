from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Trade Pilot AI\n\n"
        "Версія: 1.1\n\n"
        "Команди:\n"
        "/price BTC\n"
        "/price ETH"
    )
