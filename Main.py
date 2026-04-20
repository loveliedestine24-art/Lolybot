import telebot
import os
import yfinance as yf
import pandas as pd
from flask import Flask
from threading import Thread
import time

server = Flask(__name__)

@server.route("/")
def webhook():
    return "Lolybot Pro Online!", 200

def run():
    server.run(host="0.0.0.0", port=10000)

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

def get_pro_signal(ticker):
    try:
        # Nou pran done 5 jou pou asire EMA 200 an gen ase pwen
        data = yf.download(ticker, period='5d', interval='1m', progress=False)
        if data.empty or len(data) < 200:
            return "⏳ Done yo ap chaje... Tann 10 segonn epi re-peze bouton an."
        
        last_price = data['Close'].iloc[-1]
        ema200 = data['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
        
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))

        trend_up = last_price > ema200
        
        if trend_up and rsi < 32:
            return f"✅ **SIYAL BUY (CONFIRMED)**\n💎 {ticker}\n📈 Trend: UP\n📊 RSI: {rsi:.2f}\n⏱️ 2-3 Minit"
        elif not trend_up and rsi > 68:
            return f"🔥 **SIYAL SELL (CONFIRMED)**\n💎 {ticker}\n📉 Trend: DOWN\n📊 RSI: {rsi:.2f}\n⏱️ 2-3 Minit"
        else:
            t_msg = "UP 📈" if trend_up else "DOWN 📉"
            return f"📊 **An Analiz**\nTrend: {t_msg}\nRSI: {rsi:.2f}\n⚠️ Pa gen konfimasyon."
    except Exception as e:
        print(f"Error: {e}")
        return "❌ Erè done. Re-esye nan yon ti moman."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('EUR/USD', 'GOLD (XAU)', 'BTC/USD', 'SOL/USD', 'ETH/USD', 'GBP/USD')
    bot.reply_to(message, "💰 **LolyBot Smart Pro V2**\nChwazi yon pè:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    pairs = {'EUR/USD': 'EURUSD=X', 'GOLD (XAU)': 'GC=F', 'BTC/USD': 'BTC-USD', 'SOL/USD': 'SOL-USD', 'ETH/USD': 'ETH-USD', 'GBP/USD': 'GBPUSD=X'}
    if message.text in pairs:
        bot.send_message(message.chat.id, f"🔍 Analiz {message.text}...")
        bot.send_message(message.chat.id, get_pro_signal(pairs[message.text]), parse_mode="Markdown")

if __name__ == "__main__":
    # ETAP KRITIK: Efase vye koneksyon pou evite erè 409
    bot.remove_webhook()
    time.sleep(1)
    
    Thread(target=run).start()
    print("Bot ap demanre...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
