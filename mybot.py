import pandas as pd
import requests
import os
from io import StringIO
from flask import Flask
from threading import Thread
from telegram.ext import Application, MessageHandler, filters, CommandHandler

# --- SERVER WEB ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive and Strong!"

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
        # Đọc dữ liệu, bỏ hàng trống, ép kiểu String
        df = pd.read_csv(StringIO(res.text), header=None).fillna("").astype(str)
        
        # Chuyển thành list tuple để xử lý vòng lặp mạnh hơn
        data = []
        for _, row in df.iterrows():
            k = row[0].lower().strip()
            v = row[1].strip()
            if k: data.append((k, v))
        print(f"✅ Đã nạp {len(data)} Key.")
        return data
    except: return []

FAQ_DATA = load_faq()

# --- BỘ LỌC TỪ KHÓA ĐA ĐIỂM ---
async def handle_message(update, context):
    if not update.message or not update.message.text: return
    
    # 1. Làm sạch tin nhắn khách gửi
    msg = update.message.text.lower().strip()
    
    # 2. Duyệt qua từng dòng trong Sheets
    for key, answer in FAQ_DATA:
        # KIỂM TRA MẠNH: 
        # Nếu Key nằm trong tin nhắn HOẶC Tin nhắn nằm trong Key
        if key in msg or msg in key:
            await update.message.reply_text(answer)
            return

async def update_cmd(update, context):
    global FAQ_DATA
    FAQ_DATA = load_faq()
    await update.message.reply_text("✅ Đã cập nhật dữ liệu mới nhất từ Google Sheets!")

if __name__ == '__main__':
    Thread(target=run_web).start()
    print("--- BOT IS READY ---")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("update", update_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(drop_pending_updates=True)
