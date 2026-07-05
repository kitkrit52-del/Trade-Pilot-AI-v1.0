from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import Conflict
import os
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Trade Pilot AI v1.0 запущено успішно!"
    )

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("Trade Pilot AI v1.0 працює...")
    
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            await app.run_polling(allowed_updates=Update.ALL_TYPES)
        except Conflict as e:
            retry_count += 1
            print(f"⚠️ Conflict detected (attempt {retry_count}/{max_retries}): {e}")
            print("Another bot instance is running. Waiting before retry...")
            
            if retry_count >= max_retries:
                print("❌ Max retries reached. Shutting down.")
                await app.stop()
                return 1
            
            # Wait before retrying
            await asyncio.sleep(5)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            await app.stop()
            return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
