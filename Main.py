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
        # Nou itilize "period" 7 jou pou n asire nou gen ase done pou EMA200
        data = yf.download(ticker, period='7d', interval='5m', progress=False)
        
        if data.empty or len(data) < 50:
            return "⏳ Done yo poko disponib. Re-esye nan 1 minit."

        # Kalkil pri ak endikatè
        last_price = float(data['Close'].iloc[-1])
        ema200 = data['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
        
        # Kalkil RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))

        trend = "UP 📈" if last_price > ema200 else "DOWN 📉"
        
        # Kondisyon siyal
        status = "📊 Analiz: "
        if last_price > ema200 and rsi < 35:
            status = "✅ **BUY (Fò)**"
        elif last_price < ema200 and rsi > 65:
            status = "🔥 **SELL (Fò)**"
        else:
            status = "⚖️ **Mache a stab (Pa gen siyal)**"

        return (f"{status}\n\n💎 Pè: {ticker}\n💵 Pri: {last_price:.2f}\n📈 Trend: {trend}\n🔮 RSI: {rsi:.2f}")

    except Exception as e:
        print(f"Erè: {e}")
        return "❌ Sèvè mache a okipe. Tann 10 segonn epi re-peze bouton an."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('EURUSD=X', 'GC=F', 'BTC-USD', 'SOL-USD', 'ETH-USD', 'GBPUSD=X')
    bot.reply_to(message, "💰 **LolyBot Smart Pro**\nChwazi yon byen pou n analize:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_message(message.chat.id, f"🔍 M ap chèche done pou {message.text}...")
    signal = get_pro_signal(message.text)
    bot.send_message(message.chat.id, signal, parse_mode="Markdown")

if __name__ == "__main__":
    bot.remove_webhook()
    Thread(target=run).start()
    bot.infinity_polling()
