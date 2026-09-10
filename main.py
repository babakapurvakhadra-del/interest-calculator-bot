import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")

# -------- TELEGRAM BOT -------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Interest Calculator Bot\n\n"
        "Use:\n"
        "/calc principal rate start_date end_date\n\n"
        "Example:\n"
        "/calc 1400000 0.9 11-07-2026 07-09-2026"
    )

async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        principal = float(context.args[0])
        rate_percent = float(context.args[1])
        rate = rate_percent / 100

        start = datetime.strptime(context.args[2], "%d-%m-%Y")
        end = datetime.strptime(context.args[3], "%d-%m-%Y")

        # -------- YOUR 30-DAY MONTH LOGIC -------- #
        months = (end.year - start.year) * 12 + (end.month - start.month)

        if end.day >= start.day:
            extra_days = end.day - start.day
        else:
            months -= 1
            extra_days = 30 - (start.day - end.day)

        total_days = months * 30 + extra_days

        # -------- INTEREST -------- #
        interest = principal * rate * (total_days / 30)

        await update.message.reply_text(
            f"📊 Result:\n\n"
            f"Principal: ₹{principal:,.0f}\n"
            f"Rate: {rate_percent}% per month\n"
            f"Days: {total_days}\n"
            f"Interest: ₹{round(interest):,}"
        )

    except:
        await update.message.reply_text(
            "❌ Error!\n\n"
            "Correct format:\n"
            "/calc 1000000 0.9 16-08-2026 07-09-2026"
        )

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("calc", calc))
    print("Bot running...")
    app.run_polling()

# -------- FLASK SERVER (FOR RENDER FREE) -------- #

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# -------- MAIN -------- #

if __name__ == "__main__":
    # Run Flask in background
    t = threading.Thread(target=run_web)
    t.start()

    # Run bot in main thread
    run_bot()
