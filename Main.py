import telebot
import os
import yfinance as yf
import pandas as pd
from flask import Flask
from threading import Thread

server = Flask(__name__)

@server.route("/")
def webhook():
    return "Lolybot Smart Pro Live!", 200

def run():
    server.run(host="0.0.0.0", port=10000)

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

def get_pro_signal(ticker):
    try:
        # Nou pran done 2 jou pou EMA 200 an ka kalkile byen
        data = yf.download(ticker, period='2d', interval='1m', progress=False)
        if data.empty or len(data) < 200:
            return "⚠️ Done yo ap chaje, re-esye nan 30 segonn..."
        
        last_price = data['Close'].iloc[-1]
        
        # 1. EMA 200 (Liy Tandans Jeneral)
        ema200 = data['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
        
        # 2. RSI (Relative Strength Index)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))

        # --- SMART LOGIC ---
        trend_up = last_price > ema200
        
        # Si tandans lan se UP epi RSI di mache a ba (Oversold) -> BUY
        if trend_up and rsi < 32:
            return (f"✅ **SIYAL BUY (CONFIRMED)**\n"
                    f"💎 Pè: {ticker}\n"
                    f"📈 Tandans: MOUNTE\n"
                    f"📊 RSI: {rsi:.2f}\n"
                    f"⏱️ Tan: 2-3 minit sou Pocket Option")
        
        # Si tandans lan se DOWN epi RSI di mache a wo (Overbought) -> SELL
        elif not trend_up and rsi > 68:
            return (f"🔥 **SIYAL SELL (CONFIRMED)**\n"
                    f"💎 Pè: {ticker}\n"
                    f"📉 Tandans: DESANN\n"
                    f"📊 RSI: {rsi:.2f}\n"
                    f"⏱️ Tan: 2-3 minit sou Pocket Option")
        
        else:
            state = "Mounte" if trend_up else "Desann"
            return (f"📊 **An Analiz...**\n"
                    f"Tandans: {state}\n"
                    f"RSI: {rsi:.2f}\n"
                    f"⚠️ Pa gen konfimasyon solid kounye a.")

    except Exception as e:
        return f"❌ Erè: Re-esye ankò."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('EUR/USD', 'GOLD (XAU)', 'BTC/USD', 'SOL/USD', 'ETH/USD', 'GBP/USD')
    bot.reply_to(message, "💰 **LolyBot Smart Pro V2**\nObjektif: $20-$50/jou.\nChwazi yon pè pou n kòmanse:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    pairs = {
        'EUR/USD': 'EURUSD=X', 'GOLD (XAU)': 'GC=F',
        'BTC/USD': 'BTC-USD', 'SOL/USD': 'SOL-USD',
        'ETH/USD': 'ETH-USD', 'GBP/USD': 'GBPUSD=X'
    }
    if message.text in pairs:
        bot.send_message(message.chat.id, f"🔍 M ap analize {message.text}...")
        signal = get_pro_signal(pairs[message.text])
        bot.send_message(message.chat.id, signal, parse_mode="Markdown")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
