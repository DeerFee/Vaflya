import random
import os
import requests
from telebot import types
import wikipediaapi
import config
from utils import upload_image_to_imagebb, get_neko_image, get_waifu_image, get_nsfw_waifu_image

# Хранилища сообщений
anonymous_messages = {}
message_storage = {}

# Настройка Wikipedia API
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
            print(f"API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error during API request: {e}")
        return None

def setup_handlers(bot, db):
    @bot.message_handler(commands=['start'])
    def start(message):
        # Добавляем пользователя в базу данных
        db.add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        sti = open('static/pepeez.webp', 'rb')
        bot.send_sticker(message.chat.id, sti)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("🎲 Рандомное число")
        item2 = types.KeyboardButton("Список команд")
        item3 = types.KeyboardButton("Обратная связь")
        item4 = types.KeyboardButton("Мой профиль")
        markup.add(item1, item2, item3, item4)

        bot.send_message(message.chat.id, 
                        f"Здарова попущенец!\nЯ - <b>{bot.get_me().first_name}</b>.\nЯ создан для тестов ", 
                        parse_mode="html", 
                        reply_markup=markup)

    @bot.message_handler(commands=['vova'])
    def aboba(message):
        sti = open('static/vova.webp', 'rb')
        bot.send_sticker(message.chat.id, sti)
        bot.send_message(message.chat.id, "Я как лох, мне нужен ВОВА но он сука блять стал ебаным абобой.\nРазбил мне сердце, и я не могу это простить.")

    # Команды для работы с сообщениями
    @bot.message_handler(commands=['send_anon'])
    def send_anonymous_message(message):
        try:
            command_parts = message.text.split(maxsplit=2)
            if len(command_parts) < 3:
                bot.reply_to(message, "❌ Использование: /send_anon @username текст сообщения")
                return

            target_username = command_parts[1].replace("@", "")
            message_text = command_parts[2]

            if len(message_text) > 4000:
                bot.reply_to(message, "❌ Сообщение слишком длинное. Максимальная длина - 4000 символов.")
                return

            # Получаем информацию о пользователе из базы данных
            target_user = db.get_user_by_username(target_username)
            
            if not target_user:
                bot.reply_to(message, "❌ Пользователь не найден или никогда не использовал бота.")
                return

            try:
                sent_message = bot.send_message(
                    target_user['user_id'],  # Используем user_id вместо username
                    f"📨 *Анонимное сообщение*:\n\n{message_text}",
                    parse_mode="Markdown"
                )
                
                if sent_message:
                    bot.reply_to(message, "✅ Сообщение успешно отправлено!")
                    db.log_command(message.from_user.id, "send_anon")
                    
            except Exception as e:
                bot.reply_to(message, "❌ Не удалось отправить сообщение. Возможно, пользователь заблокировал бота.")
            
        except Exception as e:
            bot.reply_to(message, "❌ Произошла ошибка при отправке сообщения.")

    @bot.message_handler(commands=['write'])
    def write_message_dialog(message):
        msg = bot.reply_to(message, "Укажите @username получателя:")
        bot.register_next_step_handler(msg, process_username_step)

    @bot.message_handler(commands=['write'])
    def write_message_dialog(message):
        """
        Начало диалога для отправки сообщения
        """
        markup = types.ForceReply(selective=True)
        msg = bot.send_message(
            message.chat.id, 
            "Укажите @username получателя (например: @tapo4eckk):",
            reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_username_step)

    def process_username_step(message):
        """
        Обработка введенного username получателя
        """
        try:
            # Очищаем username от @ если он есть
            target_username = message.text.replace("@", "").strip()
            
            if not target_username:
                bot.reply_to(message, "❌ Username не может быть пустым. Попробуйте /write еще раз.")
                return

            # Проверяем существование пользователя в базе
            target_user = db.get_user_by_username(target_username)
            
            if not target_user:
                bot.reply_to(
                    message, 
                    "❌ Пользователь не найден или никогда не использовал бота.\n"
                    "Убедитесь, что пользователь уже запускал бота хотя бы раз."
                )
                return
            
            user_data = {"target_username": target_username, "target_user_id": target_user['user_id']}
            markup = types.ForceReply(selective=True)
            msg = bot.reply_to(
                message, 
                "📝 Введите текст сообщения:",
                reply_markup=markup
            )
            bot.register_next_step_handler(msg, process_message_step, user_data)
            
        except Exception as e:
            bot.reply_to(
                message, 
                "❌ Произошла ошибка. Попробуйте снова с помощью команды /write"
            )

    def process_message_step(message, user_data):
        """
        Обработка введенного текста сообщения
        """
        try:
            message_text = message.text.strip()
            target_username = user_data["target_username"]
            target_user_id = user_data["target_user_id"]

            if not message_text:
                bot.reply_to(message, "❌ Сообщение не может быть пустым. Попробуйте /write еще раз.")
                return

            if len(message_text) > 4000:
                bot.reply_to(message, "❌ Сообщение слишком длинное (максимум 4000 символов). Попробуйте /write еще раз.")
                return

            # Сохраняем сообщение во временное хранилище
            message_storage[message.from_user.id] = {
                'text': message_text,
                'target_user_id': target_user_id
            }

            # Создаем клавиатуру для выбора типа отправки
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("📩 Обычное", callback_data=f"send_normal_{target_username}"),
                types.InlineKeyboardButton("🕵️ Анонимное", callback_data=f"send_anon_{target_username}")
            )
            markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_send"))

            preview_text = (
                f"*Предпросмотр сообщения для @{target_username}*:\n\n"
                f"{message_text[:100]}{'...' if len(message_text) > 100 else ''}\n\n"
                f"Выберите тип отправки:"
            )
            
            bot.reply_to(
                message,
                preview_text,
                reply_markup=markup,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            bot.reply_to(message, "❌ Произошла ошибка. Попробуйте снова с помощью команды /write")

    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        """
        Обработчик callback-запросов от инлайн-кнопок
        """
        try:
            # Обработка отправки сообщений
            if call.data.startswith(('send_normal_', 'send_anon_')):
                action, target_username = call.data.split('_', 2)[1:]
                stored_data = message_storage.get(call.from_user.id)
                
                if not stored_data:
                    bot.answer_callback_query(call.id, "❌ Сообщение не найдено. Попробуйте снова.")
                    return

                message_text = stored_data['text']
                target_user_id = stored_data['target_user_id']

                if action == 'normal':
                    text = f"📩 Сообщение от @{call.from_user.username}:\n\n{message_text}"
                else:
                    text = f"📨 *Анонимное сообщение*:\n\n{message_text}"

                try:
                    sent_message = bot.send_message(
                        target_user_id,
                        text,
                        parse_mode="Markdown"
                    )
                    
                    if sent_message:
                        bot.answer_callback_query(call.id, "✅ Сообщение отправлено!")
                        bot.edit_message_text(
                            "✅ Сообщение успешно отправлено!",
                            call.message.chat.id,
                            call.message.message_id
                        )
                        # Очищаем сообщение из хранилища
                        del message_storage[call.from_user.id]
                        # Логируем отправку
                        db.log_command(call.from_user.id, f"send_{action}")
                except Exception as e:
                    bot.answer_callback_query(
                        call.id,
                        "❌ Не удалось отправить сообщение. Возможно, пользователь заблокировал бота."
                    )

            # Обработка отмены отправки
            elif call.data == "cancel_send":
                if call.from_user.id in message_storage:
                    del message_storage[call.from_user.id]
                bot.answer_callback_query(call.id, "🚫 Отправка отменена")
                bot.edit_message_text(
                    "🚫 Отправка сообщения отменена",
                    call.message.chat.id,
                    call.message.message_id
                )

            # Обработка настроек уведомлений
            elif call.data == "toggle_notifications":
                user_info = db.get_user(call.from_user.id)
                new_status = not user_info['notifications_enabled']
                db.update_user_settings(call.from_user.id, notifications_enabled=new_status)
                status_text = "включены" if new_status else "выключены"
                bot.answer_callback_query(call.id, f"Уведомления {status_text}")
                bot.edit_message_text(
                    f"⚙️ Настройки обновлены!\nУведомления {status_text}",
                    call.message.chat.id,
                    call.message.message_id
                )
                
        except Exception as e:
            bot.answer_callback_query(
                call.id,
                "❌ Произошла ошибка. Попробуйте еще раз."
            )

    # Существующие команды
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
                print(f"Error processing anime data: {e}")
                bot.send_message(message.chat.id, 'Произошла ошибка при обработке данных об аниме.')
        else:
            bot.send_message(message.chat.id, 'К сожалению, не удалось найти информацию об этом аниме. Попробуйте уточнить запрос.')

    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        if call.data.startswith(('send_normal_', 'send_anon_')):
            try:
                action, target_username = call.data.split('_', 2)[1:]
                message_text = message_storage.get(call.from_user.id)
                
                if not message_text:
                    bot.answer_callback_query(call.id, "❌ Сообщение не найдено. Попробуйте снова.")
                    return

                # Получаем информацию о пользователе из базы данных
                target_user = db.get_user_by_username(target_username)
                
                if not target_user:
                    bot.answer_callback_query(call.id, "❌ Пользователь не найден или никогда не использовал бота.")
                    return

                if action == 'normal':
                    text = f"📩 Сообщение от @{call.from_user.username}:\n\n{message_text}"
                else:
                    text = f"📨 *Анонимное сообщение*:\n\n{message_text}"

                try:
                    sent_message = bot.send_message(
                        target_user['user_id'],
                        text,
                        parse_mode="Markdown"
                    )
                    
                    if sent_message:
                        bot.answer_callback_query(call.id, "✅ Сообщение отправлено!")
                        bot.edit_message_text(
                            "✅ Сообщение успешно отправлено!",
                            call.message.chat.id,
                            call.message.message_id
                        )
                        del message_storage[call.from_user.id]
                        db.log_command(call.from_user.id, f"send_{action}")
                except:
                    bot.answer_callback_query(call.id, "❌ Не удалось отправить сообщение. Возможно, пользователь заблокировал бота.")
                
            except Exception as e:
                bot.answer_callback_query(call.id, "❌ Ошибка при отправке сообщения")

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

    @bot.message_handler(content_types=['text'])
    def handle_text(message):
        if message.chat.type == 'private':
            if message.text == '🎲 Рандомное число':
                bot.send_message(message.chat.id, str(random.randint(0, 100)))
            elif message.text == 'Список команд':
                commands_text = (
                    '<b>Основные</b>:\n'
                    '/start - старт бота если пропали кнопки\n'
                    '/vova - Вова.\n'
                    '/search [запрос] - для поиска информации в Википедии\n\n'
                                        '<b>Сообщения</b>:\n'
                    '/write - Отправить сообщение через диалог\n'
                    '/send_anon @username текст - Отправить анонимное сообщение\n\n'
                    '<b>Арты</b>\n'
                    '/neko - арты с сайта <a href="nekos.life">Nekos</a>\n'
                    '/waifu - арты с сайта <a href="waifu.pics">Waifu</a>\n'
                    '/waifu_nsfw - арты с сайта <a href="waifu.pics">Waifu</a> (Категория <b>NSFW</b>)\n\n'
                    '<b>Аниме</b>\n'
                    '/anime [Название Аниме] - Поиск аниме по базе <a href="shikimori.one">Шикимори</a>\n\n'
                    '<b>Утилиты</b>\n'
                    'Отправьте боту картинку для автоматической загрузки на <a href="https://imgbb.com">ImgBB</a>\n\n'
                    '<b>Профиль</b>:\n'
                    '/profile - Посмотреть свой профиль\n'
                    '/settings - Настройки бота'
                )
                bot.send_message(
                    message.chat.id,
                    commands_text,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
            elif message.text == 'Обратная связь':
                bot.send_message(
                    message.chat.id,
                    'По этим адресам, можно связатся со мной, для чего-либо\n'
                    'TG - @tapo4eckk\n'
                    'Почта - godstarkg@gmail.com'
                )
            elif message.text == 'Мой профиль':
                user_info = db.get_user(message.from_user.id)
                if user_info:
                    profile_text = (
                        f"👤 *Ваш профиль*\n\n"
                        f"🆔 ID: `{user_info['user_id']}`\n"
                        f"👤 Имя: {user_info['first_name']}\n"
                        f"📝 Username: @{user_info['username']}\n"
                        f"⭐️ Рейтинг: {user_info['rating']}\n"
                        f"📅 Дата регистрации: {user_info['registration_date']}\n"
                        f"🌍 Язык: {user_info['language']}\n"
                        f"🔔 Уведомления: {'Включены' if user_info['notifications_enabled'] else 'Выключены'}"
                    )
                    bot.send_message(message.chat.id, profile_text, parse_mode="Markdown")
                else:
                    bot.send_message(message.chat.id, "Профиль не найден. Используйте /start для регистрации.")
            else:
                bot.send_message(message.chat.id, 'Если пропали кнопки, пропиши /start еще раз.')

    # Обработчик для старой команды /send (сохранен для обратной совместимости)
    @bot.message_handler(commands=['send'])
    def send_legacy_message(message):
        bot.send_message(message.chat.id, 
                        "ℹ️ Эта команда устарела. Используйте:\n"
                        "/write - для отправки сообщения через диалог\n"
                        "/send_anon @username текст - для отправки анонимного сообщения")

