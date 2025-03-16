import telebot
import config
from handlers import setup_handlers
import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from database import Database

# Инициализация базы данных
db = Database()

bot = telebot.TeleBot(config.TOKEN)
setup_handlers(bot, db)  # Передаем экземпляр базы данных в обработчики

async def main():
    application = Application.builder().token(config.TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    bot.polling(none_stop=True)
    asyncio.run(main())