import telebot

TOKEN = '7699418300:AAEBbhuXEG4ik71Bqs97n_hoQb2mlZ5zjBw'
CHANNEL_IDS = {
    "лудка": -1002875538571,
    "альфа": -1002749803298
}

BANNED_USERS = set()
WARNINGS = {}  # user_id: warning_count

bot = telebot.TeleBot(TOKEN)

def is_username_present(text):
    return "@" in text

def has_required_hashtag(text):
    return "#лудка" in text.lower() or "#альфа" in text.lower()

def get_channel_ids(text):
    lower_text = text.lower()
    ids = []
    if "лудка" in lower_text:
        ids.append(CHANNEL_IDS["лудка"])
    if "альфа" in lower_text:
        ids.append(CHANNEL_IDS["альфа"])
    return ids

@bot.message_handler(commands=['start'])
def handle_start(message):
    welcome = (
        "👋 Добро пожаловать!\n\n"
        "Перед отправкой обязательно прикрепите к сообщению ваш @username и один из хэштегов:\n"
        "#Лудка или #Альфа\n\n"
        "⚠️ Неправильно оформленные сообщения получают предупреждение.\n"
        "📛 После 3-х предупреждений вы будете заблокированы."
    )
    bot.send_message(message.chat.id, welcome)

@bot.message_handler(content_types=['text', 'photo', 'document', 'video', 'voice', 'audio', 'sticker'])
def forward_message(message):
    user_id = message.from_user.id

    if user_id in BANNED_USERS:
        print(f"Заблокированный пользователь {user_id} попытался отправить сообщение.")
        return

    # Проверка текста в зависимости от типа сообщения
    msg_text = ""
    if message.text:
        msg_text = message.text
    elif message.caption:
        msg_text = message.caption
    else:
        msg_text = ""

    # Проверка на оформление
    warnings = WARNINGS.get(user_id, 0)
    formatted = True

    if not is_username_present(msg_text):
        formatted = False
        bot.send_message(message.chat.id, "⚠️ Получено предупреждение\nСоблюдайте правильность оформления (добавьте @username)")
        warnings += 1

    if not has_required_hashtag(msg_text):
        formatted = False
        bot.send_message(message.chat.id, "⚠️ Получено предупреждение\nСоблюдайте правильность оформления (добавьте #Лудка или #Альфа)")
        warnings += 1

    # Обновляем счётчик предупреждений
    if warnings >= 3:
        BANNED_USERS.add(user_id)
        bot.send_message(message.chat.id, "🚫 Вы заблокированы за многократное нарушение правил.")
        return
    else:
        WARNINGS[user_id] = warnings

    if not formatted:
        return  # Не пересылаем неправильно оформленные сообщения

    # Определяем, в какие каналы отправить сообщение
    channels = get_channel_ids(msg_text)

    if not channels:
        bot.send_message(message.chat.id, "⚠️ Сообщение не содержит ключевых слов для маршрутизации.")
        return

    success = 0
    for channel_id in channels:
        try:
            bot.forward_message(channel_id, message.chat.id, message.message_id)
            success += 1
        except Exception as e:
            print(f"Ошибка при пересылке в канал {channel_id}: {e}")

    if success > 0:
        bot.send_message(message.chat.id, "✅ Сообщение передано на обработку.")
    else:
        bot.send_message(message.chat.id, "❌ Произошла ошибка при отправке.")

bot.polling()
