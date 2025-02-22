import telebot
import config
from handlers import setup_handlers
import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters

bot = telebot.TeleBot(config.TOKEN)
setup_handlers(bot)

async def main():
    application = Application.builder().token(config.TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    bot.polling(none_stop=True)
    asyncio.run(main())
