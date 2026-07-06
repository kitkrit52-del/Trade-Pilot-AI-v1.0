from telegram import Update
from telegram.ext import ContextTypes

from services.binance import get_price


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "BTCUSDT"

    if context.args:
        coin = context.args[0].upper()

        if coin == "ETH":
            symbol = "ETHUSDT"

    result = get_price(symbol)

    await update.message.reply_text(result)
