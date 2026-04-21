import pandas as pd
import requests
import os
from io import StringIO
from flask import Flask
from threading import Thread
from telegram.ext import Application, MessageHandler, filters, CommandHandler

# --- PHẦN LỪA RENDER ĐỂ CHẠY FREE ---
app_web = Flask('')
@app_web.route('/')
def home(): return "Bot is Alive!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host='0.0.0.0', port=port)

# --- PHẦN BOT TELEGRAM ---
TOKEN = "8613912349:AAGi-Ow0sxYXme6m1iymgShWKZUbc7-Kh7k"
SHEET_ID = "1BHMhzxALXROCJg0yJzBWWxCBweWad4rPSGuGnGJat_4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def load_faq():
    try:
        res = requests.get(SHEET_URL)
        res.encoding = 'utf-8'
        df = pd.read_csv(StringIO(res.text), header=None)
        return dict(zip(df[0].astype(str).str.lower().str.strip(), df[1].astype(str).str.strip()))
    except: return {}

FAQ_DATA = load_faq()

async def handle_message(update, context):
    txt = update.message.text.lower().strip()
    for k, v in FAQ_DATA.items():
        if k in txt:
            await update.message.reply_text(v)
            return

async def update_cmd(update, context):
    global FAQ_DATA
    FAQ_DATA = load_faq()
    await update.message.reply_text("✅ Đã cập nhật dữ liệu từ Sheets!")

if __name__ == '__main__':
    # Chạy server web song song với bot
    Thread(target=run_web).start()
    
    print("--- BOT ĐANG CHẠY 24/7 ---")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("update", update_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
