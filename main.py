import os
import threading
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---------------- CONFIG ---------------- #

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ---------------- FLASK APP ---------------- #

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Interest Calculator Bot is Running"

# ✅ HEALTH CHECK ENDPOINT (USE THIS IN UPTIMEROBOT)
@web_app.route("/health")
def health():
    return "OK"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# ---------------- TELEGRAM BOT ---------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Interest Calculator Bot\n\n"
        "Use:\n"
        "/calc principal rate start-date end-date\n\n"
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

        # ---------------- 30-DAY FINANCIAL SYSTEM ---------------- #
        months = (end.year - start.year) * 12 + (end.month - start.month)

        if end.day >= start.day:
            extra_days = end.day - start.day
        else:
            months -= 1
            extra_days = 30 - (start.day - end.day)

        total_days = months * 30 + extra_days

        # ---------------- INTEREST CALCULATION ---------------- #
        interest = principal * rate * (total_days / 30)

        await update.message.reply_text(
            f"📊 Interest Result\n\n"
            f"Principal: ₹{principal:,.0f}\n"
            f"Rate: {rate_percent}% per month\n"
            f"Days: {total_days}\n"
            f"Interest: ₹{round(interest):,}"
        )

    except Exception:
        await update.message.reply_text(
            "❌ Wrong Format!\n\n"
            "Use:\n"
            "/calc 1000000 0.9 16-08-2026 07-09-2026"
        )

# ---------------- START BOT ---------------- #

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("calc", calc))

    print("Bot is running...")
    app.run_polling()

# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    # Run Flask server in background (for Render + UptimeRobot)
    t1 = threading.Thread(target=run_web)
    t1.start()

    # Run Telegram bot in main thread
    run_bot()
