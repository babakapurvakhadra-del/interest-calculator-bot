import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Interest Calculator Bot\n\n"
        "Use format:\n"
        "/calc principal rate start_date end_date\n\n"
        "Example:\n"
        "/calc 1400000 0.9 11-07-2026 07-09-2026"
    )

# Calculate interest
async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        principal = float(context.args[0])
        rate = float(context.args[1]) / 100  # convert % to decimal
        start_date = datetime.strptime(context.args[2], "%d-%m-%Y")
        end_date = datetime.strptime(context.args[3], "%d-%m-%Y")

        days = (end_date - start_date).days

        interest = principal * rate * (days / 30)

        await update.message.reply_text(
            f"📊 Result:\n\n"
            f"Principal: ₹{principal:,.0f}\n"
            f"Rate: {rate*100}% per month\n"
            f"Days: {days}\n"
            f"Interest: ₹{interest:,.0f}"
        )

    except Exception as e:
        await update.message.reply_text("❌ Error! Use correct format.\nExample:\n/calc 1000000 0.9 16-08-2026 07-09-2026")

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("calc", calc))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
