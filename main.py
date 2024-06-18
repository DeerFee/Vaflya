import telebot
import config
from handlers import setup_handlers

bot = telebot.TeleBot(config.TOKEN)
setup_handlers(bot)

if __name__ == "__main__":
    bot.polling(none_stop=True)
