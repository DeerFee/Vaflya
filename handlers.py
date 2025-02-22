import random
import os
import requests
from telebot import types
import wikipediaapi
import config
from utils import upload_image_to_imagebb, get_neko_image, get_waifu_image, get_nsfw_waifu_image

anonymous_messages = {}

user_agent = "Vaflya/1.0 (https://t.me/VaflyaT_bot)"
wiki_wiki = wikipediaapi.Wikipedia(
    language='ru',
    extract_format=wikipediaapi.ExtractFormat.WIKI,
    user_agent=user_agent
)

def search_anime(query):
    headers = {
        'User-Agent': 'AnimeSearchBot/1.0',
        'Accept': 'application/json'
    }
    
    try:
        url = 'https://shikimori.one/api/animes'
        params = {
            'search': query,
            'limit': 1,
            'order': 'popularity'
        }
        
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API error: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error during API request: {e}")
        return None

def setup_handlers(bot):

    @bot.message_handler(commands=['start'])
    def start(message):
        sti = open('static/pepeez.webp', 'rb')
        bot.send_sticker(message.chat.id, sti)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("🎲 Рандомное число")
        item2 = types.KeyboardButton("Список команд")
        item3 = types.KeyboardButton("Обратная связь")
        markup.add(item1, item2, item3)

        bot.send_message(message.chat.id, f"Здарова попущенец!\nЯ - <b>{message.from_user.first_name}</b>.\nЯ создан для тестов ", parse_mode="html", reply_markup=markup)

    @bot.message_handler(commands=['vova'])
    def aboba(message):
        sti = open('static/vova.webp', 'rb')
        bot.send_sticker(message.chat.id, sti)
        bot.send_message(message.chat.id, "Я как лох, мне нужен ВОВА но он сука блять стал ебаным абобой.\nРазбил мне сердце, и я не могу это простить.")

    @bot.message_handler(commands=['send'])
    def send_message(message):
        bot.send_message(message.chat.id, "Введите ваше анонимное сообщение:")
        bot.register_next_step_handler(message, process_message)

    def process_message(message):
        chat_id = message.chat.id
        key = str(random.randint(1000, 9999))
        anonymous_messages[key] = message.text
        bot.send_message(chat_id, f"Ваше анонимное сообщение получено. Ваш уникальный ключ: {key}")

    @bot.message_handler(commands=['get'])
    def get_message(message):
        bot.send_message(message.chat.id, "Введите ключ для получения анонимного сообщения:")
        bot.register_next_step_handler(message, retrieve_message)

    def retrieve_message(message):
        chat_id = message.chat.id
        key = message.text
        if key in anonymous_messages:
            bot.send_message(chat_id, f"Анонимное сообщение: {anonymous_messages[key]}")
        else:
            bot.send_message(chat_id, "Сообщение не найдено.")

    @bot.message_handler(commands=['search'])
    def search(message):
        query = message.text.split(' ', 1)
        if len(query) < 2:
            bot.send_message(message.chat.id, "Пожалуйста, укажите запрос для поиска.")
            return

        query = query[1]
        page = wiki_wiki.page(query)

        if page.exists():
            summary = page.summary[:4000]
            article_url = f"https://ru.wikipedia.org/wiki/{query.replace(' ', '_')}"
            bot.send_message(message.chat.id, f"{summary}<a href='{article_url}'>\nДочитать на Википедии</a>", parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, "По вашему запросу ничего не найдено.")

    @bot.message_handler(commands=['neko'])
    def send_neko(message):
        neko_image_url = get_neko_image()
        if neko_image_url:
            bot.send_photo(message.chat.id, neko_image_url)
        else:
            bot.reply_to(message, "Не удалось получить изображение неко-тян.")

    @bot.message_handler(commands=['waifu'])
    def send_waifu(message):
        waifu_image_url = get_waifu_image('waifu')
        if waifu_image_url:
            bot.send_photo(message.chat.id, waifu_image_url)
        else:
            bot.reply_to(message, "Не удалось получить изображение waifu.")

    @bot.message_handler(commands=['waifu_nsfw'])
    def send_nsfw_waifu(message):
        waifu_image_url = get_nsfw_waifu_image('waifu')
        if waifu_image_url:
            bot.send_photo(message.chat.id, waifu_image_url)
        else:
            bot.reply_to(message, "Не удалось получить изображение waifu.")

    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path

        image_url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"
        image_response = requests.get(image_url)

        if image_response.status_code == 200:
            with open('temp_image.jpg', 'wb') as f:
                f.write(image_response.content)

            uploaded_url = upload_image_to_imagebb(config.IMAGE_BB_KEY, 'temp_image.jpg')

            if uploaded_url:
                bbcode = f"[img]{uploaded_url}[/img]"
                htmlcode = f'<img src="{uploaded_url}" alt="Image"/>'
                bot.reply_to(message, f"Изображение успешно загружено.\n\nBBCode:\n```\n{bbcode}\n```\n\nHTML:\n```\n{htmlcode}\n```", parse_mode="Markdown")
            else:
                bot.reply_to(message, "Ошибка при загрузке изображения.")
        else:
            bot.reply_to(message, "Ошибка при получении изображения.")

    @bot.message_handler(commands=['anime'])
    def handle_anime(message):
        query = message.text.split(' ', 1)
        if len(query) < 2:
            bot.send_message(message.chat.id, "Пожалуйста, укажите название аниме.")
            return
        
        query = query[1]
        bot.send_message(message.chat.id, f'🔍 Ищу информацию об аниме "{query}"...')
        
        results = search_anime(query)
        if results and len(results) > 0:
            try:
                anime = results[0]
                title_russian = anime.get('russian', 'Нет русского названия')
                title_japanese = anime.get('name', 'Нет японского названия')
                score = anime.get('score', 'Нет оценки')
                status = anime.get('status', 'Неизвестно')
                episodes = anime.get('episodes', 'Неизвестно')
                url = f"https://shikimori.one/animes/{anime['id']}"
                
                status_map = {
                    'released': 'Вышло',
                    'ongoing': 'Онгоинг',
                    'anons': 'Анонс'
                }
                
                message_text = (
                    f"🎬 *{title_russian}*\n"
                    f"🈲 {title_japanese}\n"
                    f"⭐️ Оценка: {score}\n"
                    f"📺 Эпизоды: {episodes}\n"
                    f"📊 Статус: {status_map.get(status, status)}\n"
                    f"🔗 [Подробнее на Shikimori]({url})"
                )
                
                bot.send_message(
                    message.chat.id,
                    message_text,
                    parse_mode='Markdown',
                    disable_web_page_preview=False
                )
            except Exception as e:
                logger.error(f"Error processing anime data: {e}")
                bot.send_message(message.chat.id, 'Произошла ошибка при обработке данных об аниме.')
        else:
            bot.send_message(message.chat.id, 'К сожалению, не удалось найти информацию об этом аниме. Попробуйте уточнить запрос.')  

    @bot.message_handler(content_types=['text'])
    def lalala(message):
        if message.chat.type == 'private':
            if message.text == '🎲 Рандомное число':
                bot.send_message(message.chat.id, str(random.randint(0, 100)))
            elif message.text == 'Список команд':
                commands_text = (
                    '<b>Основные</b>:\n'
                    '/start\n'
                    '/vova\n'
                    '/search [запрос] - для поиска информации в Википедии\n\n'
                    '<b>Арты</b>\n'
                    '/neko - арты с сайта <a href="nekos.life">Nekos</a>\n'
                    '/waifu - арты с сайта <a href="waifu.pics">Waifu</a>\n'
                    '/waifu_nsfw - арты с сайта <a href="waifu.pics">Waifu</a> (Категория <b>NSFW</b>)\n\n'
                    '<b>Плюшки</b>\n'
                    '/anime [Навзание Аниме] - Поиск аниме по базе <a href="shikimori.one">Шикимори</a>\n'
                    'Так же, если вы отправите боту картинку, он автоматом зальет её на <a href="https://imgbb.com">ImgBB</a>'
                )
                bot.send_message(
                    message.chat.id,
                    commands_text,
                    parse_mode="HTML"
                )
            elif message.text == 'Обратная связь':
                bot.send_message(
                    message.chat.id,
                    'По этим адресам, можно связатся со мной, для чего-либо\n'
                    'TG - @tapo4eckk\n'
                    'Почта - godstarkg@gmail.com'
                )
            else:
                bot.send_message(message.chat.id, 'Если пропали кнопки, пропиши /start еще раз.')

