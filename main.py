from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import Conflict
import os
import sys

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Trade Pilot AI v1.0 запущено успішно!"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("Trade Pilot AI v1.0 працює...")
    
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Conflict as e:
        print(f"⚠️ Conflict error: {e}")
        print("Another bot instance is running. Please stop it first.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
