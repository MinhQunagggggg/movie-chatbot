# run_both.py
import os
import threading
from flask import Flask, request, jsonify
from chatbot import generate_answer
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Flask app
app = Flask(__name__)

@app.get("/")
def home():
    return "✅ Movie Chatbot API is running!"

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    reply = generate_answer(message)
    return jsonify({"reply": reply})

# Telegram handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Xin chào bạn! Chúc bạn có một ngày tốt lành.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    response = generate_answer(user_input)
    await update.message.reply_text(response)

def run_telegram():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_telegram, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
