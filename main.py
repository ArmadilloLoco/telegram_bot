import logging
import configparser
import telebot as tb
import random
# custom
import packages.handlers as hand
import packages.database as db
import packages.import_words as imp

COMMON_WORDS = 'common_words.csv'
TOKEN = hand.read_ini('telegram', 'token')
bot = tb.TeleBot(TOKEN)

class Command:
    TRAIN = "Потренироваться 📚"
    ADD = "Добавить слово ➕"
    DELETE = "Удалить слово 🔙"

# Обработка команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    imp.import_if_empty(COMMON_WORDS)
    db.add_user(user_id, username, first_name, last_name)

    welcome_text = (
        "Привет 👋 Давай попрактикуемся в английском языке. "
        "Тренировки можешь проходить в удобном для себя темпе.\n\n"
        "У тебя есть возможность использовать тренажёр, как конструктор, "
        "и собирать свою собственную базу для обучения. Для этого воспользуйся инструментами:\n\n"
        " * обавить слово ➕,\n"
        " * Удалить слово 🔙.\n\n"
        "Ну что, начнём ⬇️"
    )
    msg = bot.send_message(message.chat.id, welcome_text)
    bot.register_next_step_handler(msg, show_main_menu)

def show_main_menu(message):
    if hasattr(message, 'chat'):
        chat_id = message.chat.id
    else:
        chat_id = message
    markup = tb.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        tb.types.KeyboardButton(Command.TRAIN),
        tb.types.KeyboardButton(Command.ADD),
        tb.types.KeyboardButton(Command.DELETE)
    )
    bot.send_message(chat_id, "Выбери действие:", reply_markup=markup)

# Тренировка
@bot.message_handler(func=lambda message: message.text == Command.TRAIN)
def show_random_word(message):
    user_id = message.from_user.id
    words = db.get_all_words(user_id)

    word = random.choice(words)
    correct = word['word_eng']
    russian = word['word_rus']

    choices = list()
    for i in range(3):
        wrong_choice = random.choice(words)
        if wrong_choice['word_eng'] != correct:
            choices.append(wrong_choice['word_eng'])
        else:
            i -= 1
    choices.append(correct)
    random.shuffle(choices)

    markup = tb.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for choice in choices:
        markup.add(tb.types.KeyboardButton(choice))

    bot.send_message(message.chat.id, f"Как переводится слово: *{russian}*?", reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(message, check_answer, correct, russian)

def check_answer(message, correct, russian):
    user_answer = message.text.strip()
    if user_answer == correct:
        bot.send_message(message.chat.id, f"✅ Верно! *{russian}* — *{correct}*.", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, f"❌ Неверно. *{russian}* — *{correct}*.", parse_mode="Markdown")

    show_main_menu(message)

# Добавление слова
@bot.message_handler(func=lambda message: message.text == Command.ADD)
def add_russian_word(message):
    msg = bot.send_message(message.chat.id, "Введите слово на русском:")
    bot.register_next_step_handler(msg, add_english_word)

def add_english_word(message):
    russian = message.text.strip()
    msg = bot.send_message(message.chat.id, "Введите перевод на английском:")
    bot.register_next_step_handler(msg, save_user_word, russian)

def save_user_word(message, russian):
    english = message.text.strip()
    user_id = message.from_user.id

    db.add_user_word(user_id, russian, english)
    bot.send_message(message.chat.id, f"✅ Слово *{russian} - {english}* добавлено!", parse_mode="Markdown")

    show_main_menu(message.chat.id)

# Удаление слова
@bot.message_handler(func=lambda message: message.text == Command.DELETE)
def delete_word(message):
    user_id = message.from_user.id
    words = db.get_word(user_id)

    if not words:
        bot.send_message(message.chat.id, "У вас нет добавленных слов.")
        show_main_menu(message.chat.id)
        return

    markup = tb.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for word in words:
        markup.add(f"{word['word_rus']} → {word['word_eng']}")

    msg = bot.send_message(message.chat.id, "Выберите слово для удаления:", reply_markup=markup)
    bot.register_next_step_handler(msg, confirm_delete)


def confirm_delete(message):
    text = message.text.strip()
    try:
        russian, english = text.split(" → ")
    except:
        bot.send_message(message.chat.id, "Ошибка при выборе слова.")
        show_main_menu(message.chat.id)
        return

    user_id = message.from_user.id
    success = db.delete_user_word(user_id, russian, english)

    if success:
        bot.send_message(message.chat.id, f"🗑 Слово *{russian} - {english}* удалено.", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось удалить слово.")

    show_main_menu(message.chat.id)

if __name__ == '__main__':
    bot.polling()
