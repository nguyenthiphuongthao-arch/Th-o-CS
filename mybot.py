import pandas as pd
import requests
import os
from io import StringIO
from flask import Flask
from threading import Thread
from telegram.ext import Application, MessageHandler, filters, CommandHandler

# --- SERVER ĐỂ RENDER KIỂM TRA ---
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
        df = pd.read_csv(StringIO(res.text), header=None)
        return dict(zip(df[0].astype(str).str.lower().str.strip(), df[1].astype(str).str.strip()))
    except: return {}

FAQ_DATA = load_faq()

async def handle_message(update, context):
    if not update.message or not update.message.text: return
    txt = update.message.text.lower().strip()
    for k, v in FAQ_DATA.items():
        if k in txt:
            await update.message.reply_text(v)
            return

async def update_cmd(update, context):
    global FAQ_DATA
    FAQ_DATA = load_faq()
    await update.message.reply_text("✅ Đã cập nhật dữ liệu!")

if __name__ == '__main__':
    Thread(target=run_web).start()
    print("--- BOT STARTED ---")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("update", update_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(drop_pending_updates=True)
