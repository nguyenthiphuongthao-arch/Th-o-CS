import pandas as pd
import requests
import os
from io import StringIO
from flask import Flask
from threading import Thread
from telegram.ext import Application, MessageHandler, filters, CommandHandler

# --- SERVER ĐỂ RENDER VÀ CRON-JOB TRUY CẬP ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot is Alive and Running!"

@app_web.route('/health')
def health():
    return "OK", 200

def run_web():
    # Render yêu cầu chạy trên port mà họ cấp, mặc định thường là 10000
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

# --- CẤU HÌNH BOT ---
TOKEN = "8613912349:AAGi-Ow0sxYXme6m1iymgShWKZUbc7-Kh7k"
SHEET_ID = "1BHMhzxALXROCJg0yJzBWWxCBweWad4rPSGuGnGJat_4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def load_faq():
    try:
        res = requests.get(SHEET_URL)
        res.encoding = 'utf-8'
        df = pd.read_csv(StringIO(res.text), header=None)
        return dict(zip(df[0].astype(str).str.lower().str.strip(), df[1].astype(str).str.strip()))
    except:
        return {}

FAQ_DATA = load_faq()

async def handle_message(update, context):
    if not update.message or not update.message.text: return
    txt = update.message.text.lower().strip()
    # Tìm kiếm từ khóa trong câu hỏi
    for k, v in FAQ_DATA.items():
        if k in txt:
            await update.message.reply_text(v)
            return

async def update_cmd(update, context):
    global FAQ_DATA
    FAQ_DATA = load_faq()
    await update.message.reply_text("✅ Đã nạp lại dữ liệu mới từ Google Sheets!")

if __name__ == '__main__':
    # 1. Khởi chạy Server Web ở luồng phụ
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    # 2. Khởi chạy Bot Telegram ở luồng chính
    print("--- HỆ THỐNG ĐANG BẮT ĐẦU ---")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("update", update_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Sử dụng polling để nhận tin nhắn
    app.run_polling(drop_pending_updates=True)
