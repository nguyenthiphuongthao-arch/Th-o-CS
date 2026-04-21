import pandas as pd
import requests
import os
from io import StringIO
from flask import Flask
from threading import Thread
from telegram.ext import Application, MessageHandler, filters, CommandHandler

# --- SERVER ĐỂ RENDER KHÔNG NGỦ ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- CẤU HÌNH BOT ---
TOKEN = "8613912349:AAGi-Ow0sxYXme6m1iymgShWKZUbc7-Kh7k"
SHEET_ID = "1BHMhzxALXROCJg0yJzBWWxCBweWad4rPSGuGnGJat_4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def load_faq():
    try:
        res = requests.get(SHEET_URL)
        res.encoding = 'utf-8'
        # Đọc dữ liệu, bỏ hàng trống, ép kiểu về chuỗi
        df = pd.read_csv(StringIO(res.text), header=None).dropna()
        # Lưu vào dict với key đã được làm sạch (viết thường, bỏ khoảng trống thừa)
        return {str(k).lower().strip(): str(v).strip() for k, v in zip(df[0], df[1])}
    except: return {}

FAQ_DATA = load_faq()

# --- BỘ LỌC TỪ KHÓA THÔNG MINH ---
async def handle_message(update, context):
    if not update.message or not update.message.text: return
    
    # 1. Lấy tin nhắn khách và chuyển về chữ thường
    user_text = update.message.text.lower().strip()
    
    # 2. Ưu tiên: Tìm từ khóa nguyên cụm (Ví dụ: "thử việc")
    for key, answer in FAQ_DATA.items():
        if key in user_text:
            await update.message.reply_text(answer)
            return

    # 3. Phụ trợ: Nếu không khớp cụm, tách từng từ để tìm
    user_words = user_text.split()
    for word in user_words:
        if word in FAQ_DATA:
            await update.message.reply_text(FAQ_DATA[word])
            return

async def update_cmd(update, context):
    global FAQ_DATA
    FAQ_DATA = load_faq()
    await update.message.reply_text("✅ Đã cập nhật dữ liệu mới từ Sheets!")

if __name__ == '__main__':
    Thread(target=run_web).start()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("update", update_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(drop_pending_updates=True)
