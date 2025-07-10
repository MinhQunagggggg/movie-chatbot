from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from chatbot import generate_answer

BOT_TOKEN = "7920415552:AAF3IDcVqYWOGXrrbrOFl_Go2TNEeyNIpzs"

# 🟢 /start → Gửi chào + gợi ý
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Xin chào bạn! Chúc bạn có một ngày tốt lành.")
    await update.message.reply_text("🤖 Bạn cần mình hỗ trợ gì ha?")

    # Gợi ý 3 câu hỏi mẫu
    suggestions = [
        "🔹 Trailer phim M3GAN 2.0",
        "🔹 Phim của đạo diễn Victor Vũ",
        "🔹 Lịch phim hôm nay"
    ]
    msg = "💡 Ví dụ bạn có thể hỏi:\n" + "\n".join(suggestions)
    await update.message.reply_text(msg)

# 🟢 Xử lý tin nhắn người dùng
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    response = generate_answer(user_input)
    await update.message.reply_text(response)

# 🟢 Khởi động bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Lệnh /start
    app.add_handler(CommandHandler("start", start))

    # Mọi tin nhắn khác
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot Telegram đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()