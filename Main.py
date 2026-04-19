import telebot
import os
from flask import Flask
from threading import Thread

# Configuração para o Render não dar erro de "Port"
server = Flask(__name__)

@server.route("/")
def webhook():
    return "Lolybot ativo!", 200

def run():
    # O Render usa a porta 10000 por padrão no plano gratuito
    server.run(host="0.0.0.0", port=10000)

# O teu Token do Telegram
TOKEN = "8227900082:"AAGqkCKieoIvtdpKFH4czXpDnwwPRxz8vIc"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bot la ap mache sou GitHub/Render kounye a! 🚀")

if __name__ == "__main__":
    # Inicia o servidor Flask numa thread separada
    Thread(target=run).start()
    
    print("Bot a iniciar...")
    bot.infinity_polling()
