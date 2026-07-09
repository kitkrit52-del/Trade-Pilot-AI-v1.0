from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
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
        "✅ Це Python-бот Trade Pilot AI.\n"
        "Версія: 1.0\n"
        "Хостинг: Zeabur"
    )
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Це Python-бот Trade Pilot AI.\n"
        "Версія: 1.0\n"
        "Хостинг: Zeabur"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🟢 Trade Pilot AI працює\n"
        "Версія: 1.0\n"
        "Хостинг: Zeabur\n"
        "Статус: ONLINE"
    )
def main():
    Thread(target=run_web, daemon=True).start()
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("status", status))

print("🚀 Trade Pilot AI запущено")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("🚀 Trade Pilot AI запущено")

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
