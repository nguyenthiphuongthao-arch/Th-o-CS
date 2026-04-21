import pandas as pd
import requests
import os
from io import StringIO
from flask import Flask
from threading import Thread
from telegram.ext import Application, MessageHandler, filters, CommandHandler

# --- SERVER WEB GIỮ BOT LUÔN THỨC ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive and Smart!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- CẤU HÌNH DỮ LIỆU ---
TOKEN = "8613912349:AAGi-Ow0sxYXme6m1iymgShWKZUbc7-Kh7k"
SHEET_ID = "1BHMhzxALXROCJg0yJzBWWxCBweWad4rPSGuGnGJat_4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def load_faq():
    try:
        # Tải dữ liệu từ Sheets
        res = requests.get(SHEET_URL)
        res.encoding = 'utf-8'
        # Đọc CSV, ép kiểu thành String để tránh lỗi số, bỏ các dòng trống
        df = pd.read_csv(StringIO(res.text), header=None).fillna("").astype(str)
        
        # Chuyển thành danh sách: [(từ_khóa, câu_trả_lời), ...]
        # Làm sạch dữ liệu: viết thường và bỏ khoảng cách thừa
        data = []
        for _, row in df.iterrows():
            key = row[0].lower().strip()
            val = row[1].strip()
            if key: # Chỉ thêm nếu ô từ khóa không trống
                data.append((key, val))
        
        print(f"✅ Đã nạp thành công {len(data)} từ khóa.")
        return data
    except Exception as e:
        print(f"❌ Lỗi nạp Sheets: {e}")
        return []

FAQ_DATA = load_faq()

# --- BỘ LỌC TỪ KHÓA SIÊU CẤP ---
async def handle_message(update, context):
    if not update.message or not update.message.text: return
    
    # Lấy tin nhắn khách và chuyển về chữ thường
    user_text = update.message.text.lower().strip()
    
    # Duyệt qua từng dòng dữ liệu từ Sheets
    for key, answer in FAQ_DATA:
        # KIỂM TRA: Nếu Từ khóa (Key) xuất hiện trong câu nhắn (user_text)
        # Ví dụ: Key là "thư", khách nhắn "gửi thư cho tôi" -> KHỚP!
        if key in user_text:
            await update.message.reply_text(answer)
            return # Thoát hàm ngay khi tìm thấy câu trả lời đầu tiên

async def update_cmd(update, context):
    global FAQ_DATA
    FAQ_DATA = load_faq()
    await update.message.reply_text("✅ Đã cập nhật dữ liệu mới nhất từ Google Sheets!")

if __name__ == '__main__':
    # Chạy "báo thức" cho Bot
    Thread(target=run_web).start()
    
    # Chạy Telegram Bot
    print("--- BOT ĐANG BẮT ĐẦU CHẠY ---")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("update", update_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(drop_pending_updates=True)
