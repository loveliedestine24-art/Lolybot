import telebot
import os
import yfinance as yf
import time
from flask import Flask
from threading import Thread

server = Flask(__name__)

@server.route("/")
def webhook():
    return "Bot Smart Pro Live!", 200

def run():
    server.run(host="0.0.0.0", port=10000)

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

def get_pro_signal(ticker):
    try:
        # Nou pran done 5 jou pou EMA 200 an ka kalkile byen
        data = yf.download(ticker, period='5d', interval='1m', progress=False)
        if data.empty or len(data) < 200:
            return "⏳ Done yo ap chaje... Tann 15 segonn epi re-peze bouton an."
        
        last_price = data['Close'].iloc[-1]
        ema200 = data['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
        
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))

        trend_up = last_price > ema200
        
        if trend_up and rsi < 32:
            return f"✅ **BUY (CONFIRMED)**\n💎 {ticker}\n📈 Trend: UP\n📊 RSI: {rsi:.2f}"
        elif not trend_up and rsi > 68:
            return f"🔥 **SELL (CONFIRMED)**\n💎 {ticker}\n📉 Trend: DOWN\n📊 RSI: {rsi:.2f}"
        else:
            return f"📊 **Analiz...**\nTrend: {'UP' if trend_up else 'DOWN'}\nRSI: {rsi:.2f}\n⚠️ Pa gen siyal fò."
    except:
        return "❌ Mache a ap chaje. Re-esye."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('EUR/USD', 'GOLD (XAU)', 'BTC/USD', 'SOL/USD', 'ETH/USD', 'GBP/USD')
    bot.reply_to(message, "💰 **LolyBot Smart Pro**\nChwazi yon pè:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    pairs = {'EUR/USD': 'EURUSD=X', 'GOLD (XAU)': 'GC=F', 'BTC/USD': 'BTC-USD', 'SOL/USD': 'SOL-USD', 'ETH/USD': 'ETH-USD', 'GBP/USD': 'GBPUSD=X'}
    if message.text in pairs:
        bot.send_message(message.chat.id, f"🔍 Analiz {message.text}...")
        bot.send_message(message.chat.id, get_pro_signal(pairs[message.text]), parse_mode="Markdown")

if __name__ == "__main__":
    # N ap efase tout koneksyon ki te la anvan
    bot.remove_webhook()
    time.sleep(1)
    
    Thread(target=run).start()
    bot.infinity_polling(timeout=20)
