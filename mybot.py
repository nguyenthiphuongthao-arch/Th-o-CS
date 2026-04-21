import pandas as pd
import requests
import os
from io import StringIO
from flask import Flask
from threading import Thread
from telegram.ext import Application, MessageHandler, filters, CommandHandler

# --- SERVER GIỮ NHIỆT (DÀNH CHO RENDER) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Smart and Alive!"

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
        # Đọc file CSV và loại bỏ các dòng trống
        df = pd.read_csv(StringIO(res.text), header=None).dropna()
        # Chuyển về Dictionary: { "từ khóa": "câu trả lời" }
        return dict(zip(df[0].astype(str).str.lower().str.strip(), df[1].astype(str).str.strip()))
    except Exception as e:
        print(f"Lỗi nạp Sheets: {e}")
        return {}

FAQ_DATA = load_faq()

# --- XỬ LÝ TIN NHẮN THÔNG MINH ---
async def handle_message(update, context):
    if not update.message or not update.message.text: return
    
    # Chuyển tin nhắn người dùng về chữ thường để so sánh
    user_text = update.message.text.lower().strip()
    
    # Duyệt qua danh sách từ khóa trong Sheets
    for key, answer in FAQ_DATA.items():
        # NÂNG CẤP: Nếu từ khóa xuất hiện bất kỳ đâu trong câu nhắn
        if key in user_text:
            await update.message.reply_text(answer)
            return # Dừng lại sau khi tìm thấy câu trả lời đầu tiên khớp

async def update_cmd(update, context):
    global FAQ_DATA
    FAQ_DATA = load_faq()
    await update.message.reply_text("✅ Hệ thống đã cập nhật kiến thức mới từ Sheets!")

if __name__ == '__main__':
    Thread(target=run_web).start()
    print("--- BOT THÔNG MINH ĐANG CHẠY ---")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("update", update_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(drop_pending_updates=True)
