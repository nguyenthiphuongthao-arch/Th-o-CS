import pandas as pd
import requests
import logging
from io import StringIO
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

TOKEN = "8613912349:AAGi-Ow0sxYXme6m1iymgShWKZUbc7-Kh7k"
SHEET_ID = "1BHMhzxALXROCJg0yJzBWWxCBweWad4rPSGuGnGJat_4"
# Link lấy đúng sheet đầu tiên dưới dạng CSV
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def load_faq():
    try:
        response = requests.get(SHEET_URL)
        response.encoding = 'utf-8'
        # Đọc dữ liệu, bỏ qua tiêu đề nếu có
        df = pd.read_csv(StringIO(response.text), header=None)
        
        # Chuyển đổi dữ liệu thành danh sách để xử lý chính xác hơn
        faq_list = []
        for _, row in df.iterrows():
            question = str(row[0]).lower().strip()
            answer = str(row[1]).strip()
            if question != "nan" and answer != "nan":
                faq_list.append({"q": question, "a": answer})
        
        print(f"✅ Đã nạp {len(faq_list)} cặp câu hỏi/trả lời.")
        return faq_list
    except Exception as e:
        print(f"❌ Lỗi tải dữ liệu: {e}")
        return []

FAQ_DATA = load_faq()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_text = update.message.text.lower().strip()
    print(f"📩 Khách nhắn: {user_text}") # Xem khách nhắn gì ở CMD
    
    best_match = None
    
    # Ưu tiên 1: Khớp hoàn toàn hoặc từ khóa nằm trong câu hỏi
    for item in FAQ_DATA:
        if item['q'] in user_text or user_text in item['q']:
            best_match = item['a']
            break # Tìm thấy cái đầu tiên khớp là dừng
            
    if best_match:
        print(f"✅ Bot trả lời: {best_match[:50]}...")
        await update.message.reply_text(best_match)
    else:
        print("❓ Không tìm thấy câu trả lời khớp.")
        await update.message.reply_text("Xin lỗi, mình chưa tìm thấy thông tin khớp. Bạn có thể hỏi rõ hơn không?")

async def update_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global FAQ_DATA
    FAQ_DATA = load_faq()
    await update.message.reply_text("🔄 Hệ thống đã cập nhật dữ liệu mới nhất từ Google Sheets!")

if __name__ == '__main__':
    print("--- BOT FAQ ĐANG CHẠY ---")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("update", update_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()