Để đảm bảo Bot của bạn hoạt động "mượt" nhất trên Render, tự động nhận diện từ khóa thông minh (dù nằm trong câu dài), và không bao giờ bị "ngủ quên", đây là bản code hoàn chỉnh nhất.

Bạn hãy copy toàn bộ đoạn này và dán đè vào file mybot.py trên GitHub của mình nhé.

Python
import pandas as pd
import requests
import os
import logging
from io import StringIO
from flask import Flask
from threading import Thread
from telegram.ext import Application, MessageHandler, filters, CommandHandler

# --- 1. TẠO SERVER WEB (GIỮ CHO BOT LUÔN THỨC) ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot is Smart and Running 24/7!"

@app_web.route('/health')
def health():
    return "OK", 200

def run_web():
    # Lấy cổng từ môi trường Render (mặc định 10000)
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

# --- 2. CẤU HÌNH THÔNG TIN BOT ---
TOKEN = "8613912349:AAGi-Ow0sxYXme6m1iymgShWKZUbc7-Kh7k"
SHEET_ID = "1BHMhzxALXROCJg0yJzBWWxCBweWad4rPSGuGnGJat_4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# Thiết lập nhật ký lỗi
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def load_faq():
    """Hàm tải và xử lý dữ liệu từ Google Sheets"""
    try:
        response = requests.get(SHEET_URL)
        response.encoding = 'utf-8'
        # Đọc CSV, loại bỏ dòng trống, chuyển về chữ thường để dễ so khớp
        df = pd.read_csv(StringIO(response.text), header=None).dropna()
        # Tạo từ điển { "từ khóa": "câu trả lời" }
        faq_dict = {}
        for _, row in df.iterrows():
            key = str(row[0]).lower().strip()
            val = str(row[1]).strip()
            faq_dict[key] = val
        print(f"✅ Đã nạp {len(faq_dict)} cặp câu hỏi/trả lời.")
        return faq_dict
    except Exception as e:
        print(f"❌ Lỗi nạp Sheets: {e}")
        return {}

# Khởi tạo dữ liệu lúc chạy bot
FAQ_DATA = load_faq()

# --- 3. XỬ LÝ TIN NHẮN THÔNG MINH ---
async def handle_message(update, context):
    if not update.message or not update.message.text: return
    
    # Chuyển tin nhắn khách gửi về chữ thường
    user_text = update.message.text.lower().strip()
    
    # Duyệt qua tất cả Key trong Sheets
    # Nếu Key (từ khóa) nằm trong câu nhắn của khách -> Trả lời
    found_reply = False
    for key, answer in FAQ_DATA.items():
        if key in user_text:
            await update.message.reply_text(answer)
            found_reply = True
            break # Dừng lại sau khi tìm thấy từ khóa đầu tiên khớp
    
    # (Tùy chọn) Nếu không tìm thấy từ khóa nào
    # if not found_reply:
    #     await update.message.reply_text("Xin lỗi, mình chưa hiểu ý bạn. Bạn có thể hỏi rõ hơn không?")

async def update_cmd(update, context):
    """Lệnh /update để nạp lại dữ liệu mới từ Sheets mà không cần khởi động lại bot"""
    global FAQ_DATA
    FAQ_DATA = load_faq()
    await update.message.reply_text("✅ Hệ thống đã cập nhật kiến thức mới nhất từ Google Sheets!")

# --- 4. CHƯƠNG TRÌNH CHÍNH ---
if __name__ == '__main__':
    # Chạy Web Server ở luồng phụ (Background Thread)
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    # Chạy Telegram Bot ở luồng chính
    print("--- ĐANG KHỞI ĐỘNG BOT ---")
    app_bot = Application.builder().token(TOKEN).build()
    
    # Thêm các bộ xử lý
    app_bot.add_handler(CommandHandler("update", update_cmd))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Bắt đầu nhận tin nhắn
    print("--- BOT ĐÃ SẴN SÀNG ---")
    app_bot.run_polling(drop_pending_updates=True)
