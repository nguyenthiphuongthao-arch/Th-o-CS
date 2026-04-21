import pandas as pd
import requests
import os
from io import StringIO
from flask import Flask
from threading import Thread
from telegram.ext import Application, MessageHandler, filters, CommandHandler

# --- WEB SERVER GIỮ BOT THỨC ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive and Smart!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- CẤU HÌNH ---
TOKEN = "8613912349:AAGi-Ow0sxYXme6m1iymgShWKZUbc7-Kh7k"
SHEET_ID = "1BHMhzxALXROCJg0yJzBWWxCBweWad4rPSGuGnGJat_4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def load_faq():
    try:
        res = requests.get(SHEET_URL)
        res.encoding = 'utf-8'
        # Đọc dữ liệu, bỏ hàng trống, ép kiểu chuỗi
        df = pd.read_csv(StringIO(res.text), header=None).dropna()
        # Lưu vào danh sách các cặp (từ khóa, trả lời)
        return [(str(k).lower().strip(), str(v).strip()) for k, v in zip(df[0], df[1])]
    except Exception as e:
        print(f"Lỗi nạp dữ liệu: {e}")
        return []

FAQ_DATA = load_faq()

# --- BỘ LỌC TỪ KHÓA CHÍNH XÁC ---
async def handle_message(update, context):
    if not update.message or not update.message.text: return
    
    # 1. Chuyển tin nhắn của khách về chữ thường
    user_text = update.message.text.lower().strip()
    
    # 2. KIỂM TRA TỪNG DÒNG TRONG SHEETS
    # Nếu từ khóa ở Cột A xuất hiện trong câu khách nhắn -> Trả lời ngay
    for key, answer in FAQ_DATA:
        if key in user_text:
            await update.message.reply_text(answer)
            return # Dừng lại sau khi tìm thấy từ khóa đầu tiên khớp

async def update_cmd(update, context):
    global FAQ_DATA
    FAQ_DATA = load_faq()
    await update.message.reply_text("✅ Đã nạp lại dữ liệu mới nhất từ Sheets!")

if __name__ == '__main__':
    # Chạy Web Server
    Thread(target=run_web).start()
    
    # Chạy Telegram Bot
    print("--- BOT ĐANG KHỞI CHẠY ---")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("update", update_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(drop_pending_updates=True)
