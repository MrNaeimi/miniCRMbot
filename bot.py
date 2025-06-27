from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import sqlite3
import csv
import os

# مراحل گفتگو
ASK_PHONE, ASK_NAME = range(2)

# ذخیره در دیتابیس و CSV
def save_user(telegram_id, phone, full_name):
    # ذخیره در دیتابیس SQLite
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO users (telegram_id, phone, full_name) VALUES (?, ?, ?)",
                (telegram_id, phone, full_name))
    conn.commit()
    conn.close()

    # ذخیره در فایل CSV
    file_exists = os.path.isfile("users.csv")
    with open("users.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["telegram_id", "phone", "full_name"])
        writer.writerow([telegram_id, phone, full_name])

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("📋 ثبت نام")]]
    await update.message.reply_text(
        "سلام به فروشگاه زنجیره‌ای امیران خوش اومدی! 🎉\n"
        "برای اطلاع از تخفیفات ویژه و جشنواره‌ها، لطفاً ثبت نام کنید:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# مرحله ثبت‌نام
async def handle_signup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 لطفاً شماره تماس خود را ارسال کنید:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("ارسال شماره تماس", request_contact=True)]],
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    return ASK_PHONE

# دریافت شماره
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    phone = contact.phone_number if contact else update.message.text
    context.user_data["phone"] = phone
    await update.message.reply_text("🙏 حالا لطفاً نام و نام خانوادگی خود را وارد کنید:")
    return ASK_NAME

# دریافت نام
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    full_name = update.message.text
    telegram_id = update.message.from_user.id
    phone = context.user_data["phone"]

    save_user(telegram_id, phone, full_name)

    await update.message.reply_text(
        f"✅ ثبت‌نام با موفقیت انجام شد!\n\n👤 نام: {full_name}\n📞 شماره: {phone}"
    )
    return ConversationHandler.END

# لغو عملیات
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⛔ ثبت‌نام لغو شد.")
    return ConversationHandler.END

# اجرای ربات
if __name__ == '__main__':
    print("✅ ربات در حال اجراست...")
    app = ApplicationBuilder().token("api-key").build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(📋 ثبت نام)$"), handle_signup)],
        states={
            ASK_PHONE: [MessageHandler(filters.CONTACT | filters.TEXT, get_phone)],
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("✅ منتظریم که کاربر دکمه `/start` رو بزنه...")
    app.run_polling()
