import telebot
import os
from flask import Flask
from threading import Thread

# Konfigirasyon pou Render
server = Flask(__name__)

@server.route("/")
def webhook():
    return "Lolybot ativo!", 200

def run():
    server.run(host="0.0.0.0", port=10000)

# Nouvo Token ou a
TOKEN = "8227900082:AAGqkCKieoIvtdpkFH4czXpDnwwPRxz8vIc"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bot la ap mache sou GitHub/Render kounye a! 🚀")

if __name__ == "__main__":
    Thread(target=run).start()
    print("Bot a iniciar...")
    bot.infinity_polling()

