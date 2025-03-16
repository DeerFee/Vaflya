import logging
import aiohttp
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import json

# Вставьте сюда ваш токен от BotFather
TELEGRAM_TOKEN = '6794667704:AAF0KLoAnBuYgTu_5cPrI10A-K_ET1orT3Q'

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для отправки запроса к Shikimori API
async def search_anime(query):
    headers = {
        'User-Agent': 'AnimeSearchBot/1.0',
        'Accept': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # Используем правильный эндпоинт и параметры поиска
            url = 'https://shikimori.one/api/animes'
            params = {
                'search': query,
                'limit': 1,  # Ограничиваем результат одним аниме
                'order': 'popularity'  # Сортируем по популярности
            }
            
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error during API request: {e}")
            return None

# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        'Привет! Я бот для поиска аниме в базе Shikimori.\n'
        'Просто отправь мне название аниме, и я найду информацию о нем.'
    )

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: CallbackContext) -> None:
    query = update.message.text
    await update.message.reply_text(f'🔍 Ищу информацию об аниме "{query}"...')
    
    results = await search_anime(query)
    if results and len(results) > 0:
        try:
            anime = results[0]
            # Формируем базовую информацию об аниме
            title_russian = anime.get('russian', 'Нет русского названия')
            title_japanese = anime.get('name', 'Нет японского названия')
            score = anime.get('score', 'Нет оценки')
            status = anime.get('status', 'Неизвестно')
            episodes = anime.get('episodes', 'Неизвестно')
            url = f"https://shikimori.one/animes/{anime['id']}"
            
            # Статусы на русском
            status_map = {
                'released': 'Вышло',
                'ongoing': 'Онгоинг',
                'anons': 'Анонс'
            }
            
            message = (
                f"🎬 *{title_russian}*\n"
                f"🈲 {title_japanese}\n"
                f"⭐️ Оценка: {score}\n"
                f"📺 Эпизоды: {episodes}\n"
                f"📊 Статус: {status_map.get(status, status)}\n"
                f"🔗 [Подробнее на Shikimori]({url})"
            )
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
        except Exception as e:
            logger.error(f"Error processing anime data: {e}")
            await update.message.reply_text('Произошла ошибка при обработке данных об аниме.')
    else:
        await update.message.reply_text('К сожалению, не удалось найти информацию об этом аниме. Попробуйте уточнить запрос.')

def main() -> None:
    # Создаем Application и передаем ему токен вашего бота
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()