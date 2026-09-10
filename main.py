import os
import threading
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================= CONFIG ================= #

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ================= FLASK APP ================= #

app = Flask(__name__)

@app.route("/")
def home():
    return "Interest Calculator Bot Running"

# ✅ HEALTH CHECK (FOR UPTIMEROBOT)
@app.route("/health")
def health():
    return "OK"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ================= INTEREST LOGIC ================= #

def calculate_interest(principal, rate_percent, start_str, end_str):
    rate = rate_percent / 100

    start = datetime.strptime(start_str, "%d-%m-%Y")
    end = datetime.strptime(end_str, "%d-%m-%Y")

    # 30-day financial system
    months = (end.year - start.year) * 12 + (end.month - start.month)

    if end.day >= start.day:
        extra_days = end.day - start.day
    else:
        months -= 1
        extra_days = 30 - (start.day - end.day)

    total_days = months * 30 + extra_days

    interest = principal * rate * (total_days / 30)

    return total_days, round(interest)


# ================= TELEGRAM HANDLERS ================= #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Interest Calculator Bot\n\n"
        "Send multiple calculations like:\n\n"
        "/calc 1000000 0.9 11-07-2026 07-09-2026\n"
        "/calc 500000 1.0 01-08-2026 07-09-2026"
    )


async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        lines = text.split("\n")

        results = []
        total_interest = 0
        count = 1

        for line in lines:
            if "/calc" not in line:
                continue

            parts = line.strip().split()

            if len(parts) < 5:
                continue

            principal = float(parts[1])
            rate_percent = float(parts[2])
            start_date = parts[3]
            end_date = parts[4]

            days, interest = calculate_interest(
                principal,
                rate_percent,
                start_date,
                end_date
            )

            total_interest += interest

            results.append(
                f"{count}. Principal: ₹{principal:,.0f}\n"
                f"   Rate: {rate_percent}%\n"
                f"   Days: {days}\n"
                f"   Interest: ₹{interest:,}\n"
            )

            count += 1

        if not results:
            await update.message.reply_text("❌ No valid /calc data found.")
            return

        results.append(f"\n📌 TOTAL INTEREST: ₹{total_interest:,}")

        await update.message.reply_text(
            "📊 Interest Results:\n\n" + "\n".join(results)
        )

    except Exception:
        await update.message.reply_text(
            "❌ Error!\n\nFormat:\n/calc 1000000 0.9 11-07-2026 07-09-2026"
        )


# ================= BOT RUNNER ================= #

def run_bot():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()

    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("calc", calc))

    print("Bot is running...")
    app_bot.run_polling()


# ================= MAIN ================= #

if __name__ == "__main__":
    # Flask in background (Render + UptimeRobot)
    threading.Thread(target=run_flask).start()

    # Telegram bot in main thread
    run_bot()
