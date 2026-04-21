import pandas as pd
import requests
import os
from io import StringIO
from flask import Flask
from threading import Thread
from telegram.ext import Application, MessageHandler, filters, CommandHandler

# --- PHẦN 1: SERVER ĐỂ RENDER KHÔNG BỊ LỖI ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- PHẦN 2: CẤU HÌNH BOT ---
TOKEN = "8613912349:AAGi-Ow0sxYXme6m1iymgShWKZUbc7-Kh7k"
SHEET_ID = "1BHMhzxALXROCJg0yJzBWWxCBweWad4rPSGuGnGJat_4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def load_faq():
    try:
        res = requests.get(SHEET_URL)
        res.encoding = 'utf-8'
        # Đọc dữ liệu và xóa các hàng trống
        df = pd.read_csv(StringIO(res.text), header=None).dropna()
        # Tạo từ điển { "từ khóa": "câu trả lời" }
        return dict(zip(df[0].astype(str).str.lower().str.strip(), df[1].astype(str).str.strip()))
    except: return {}

FAQ_DATA = load_faq()

# --- PHẦN 3: XỬ LÝ TIN NHẮN THÔNG MINH ---
async def handle_message(update, context):
    if not update.message or not update.message.text: return
    user_text = update.message.text.lower().strip()
    
    # Duyệt qua từng Key trong Sheets, nếu Key có trong câu nhắn -> Trả lời
    for key, answer in FAQ_DATA.items():
        if key in user_text:
            await update.message.reply_text(answer)
            return

async def update_cmd(update, context):
    global FAQ_DATA
    FAQ_DATA = load_faq()
    await update.message.reply_text("✅ Đã cập nhật dữ liệu mới từ Sheets!")

if __name__ == '__main__':
    # Chạy server phụ
    Thread(target=run_web).start()
    # Chạy Bot chính
    print("--- BOT IS STARTING ---")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("update", update_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(drop_pending_updates=True)
