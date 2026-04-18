import telebot

TOKEN = "8227900082:AAEMxoasdVlr4sNm6nMaBxhksyyJBPRupUM"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bot la ap mache sou GitHub/Render kounye a! 🚀")

print("Bot la ap demare...")
bot.infinity_polling()
