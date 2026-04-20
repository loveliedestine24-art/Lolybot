import telebot
import os
import yfinance as yf
import time
from flask import Flask
from threading import Thread

server = Flask(__name__)
@server.route("/")
def webhook(): return "Bot Live!", 200
def run(): server.run(host="0.0.0.0", port=10000)

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

def get_pro_signal(ticker):
    try:
        # Nou itilize Ticker olye de download pou l pi lejè
        asset = yf.Ticker(ticker)
        # Nou pran done pou 2 jou pou nou gen ase pou RSI a san fay
        data = asset.history(period='2d', interval='5m')
        
        if data.empty or len(data) < 20:
            return "⏳ Done yo poko disponib. Re-esye nan 1 minit."

        last_price = float(data['Close'].iloc[-1])
        # EMA 20
        ema20 = data['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
        
        # Kalkil RSI pi solid
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        # Evite divizyon pa zewo
        last_loss = loss.iloc[-1]
        if last_loss == 0:
            rsi = 100
        else:
            rs = gain.iloc[-1] / last_loss
            rsi = 100 - (100 / (1 + rs))

        trend = "UP 📈" if last_price > ema20 else "DOWN 📉"
        
        # Lojik siyal la
        if last_price > ema20 and rsi < 35:
            res = "✅ **BUY SIGNAL**"
        elif last_price < ema20 and rsi > 65:
            res = "🔥 **SELL SIGNAL**"
        else:
            res = "⚖️ **PA GEN SIYAL (STAB)**"

        return f"{res}\n\n💎 {ticker}\n💵 Pri: {last_price:.2f}\n📈 Trend: {trend}\n🔮 RSI: {rsi:.2f}"
    
    except Exception as e:
        print(f"Erè sou {ticker}: {e}")
        return "❌ Sèvè mache a okipe. Re-peze bouton an."

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('EURUSD=X', 'GC=F', 'BTC-USD', 'SOL-USD', 'ETH-USD', 'GBPUSD=X')
    bot.reply_to(message, "💰 **LolyBot Pro**\nChwazi yon pè:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    signal = get_pro_signal(message.text)
    bot.send_message(message.chat.id, signal, parse_mode="Markdown")

if __name__ == "__main__":
    bot.remove_webhook()
    Thread(target=run).start()
    bot.infinity_polling()
