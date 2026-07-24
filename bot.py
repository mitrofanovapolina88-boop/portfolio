import telebot
from telebot import types
import re
import random
from googletrans import Translator

# Замените на ваш токен
TOKEN = '8666801573:AAGs_xuLW76f2K1yK3o84okG0f7xqW_SwAY'
bot = telebot.TeleBot(TOKEN)

# Создаём переводчик один раз
translator = Translator()

# Состояния
START = 'start'
AWAIT_FIRST_NUMBER = 'await_first_number'
AWAIT_OPERATION = 'await_operation'
AWAIT_SECOND_NUMBER = 'await_second_number'
AWAIT_ESSAY_TOPIC = 'await_essay_topic'
AWAIT_TRANSLATE_LANG = 'await_translate_lang'
AWAIT_TRANSLATE_TEXT = 'await_translate_text'

user_data = {}

# ---------- Функция перевода через googletrans ----------
def translate_text(text, target_lang):
    try:
        result = translator.translate(text, dest=target_lang)
        return result.text, result.src
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return None, None

# ---------- Клавиатуры ----------
def main_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('Решить пример', callback_data='solve')
    btn2 = types.InlineKeyboardButton('Покушать', callback_data='eat')
    btn3 = types.InlineKeyboardButton('Сочинение', callback_data='essay')
    btn4 = types.InlineKeyboardButton('Перевод', callback_data='translate')
    keyboard.add(btn1, btn2, btn3, btn4)
    return keyboard

def numbers_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    buttons = []
    for i in range(1, 10):
        buttons.append(types.InlineKeyboardButton(str(i), callback_data=f'digit_{i}'))
    buttons.append(types.InlineKeyboardButton('все', callback_data='all'))
    keyboard.add(*buttons)
    return keyboard

def operations_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    ops = ['+', '-', '*', '%']
    buttons = [types.InlineKeyboardButton(op, callback_data=f'op_{op}') for op in ops]
    keyboard.add(*buttons)
    return keyboard

def eat_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    items = ['торт', 'пицца', 'суп', 'бутерброд', 'салат']
    buttons = [types.InlineKeyboardButton(item, callback_data=f'eat_{item}') for item in items]
    keyboard.add(*buttons)
    return keyboard

def language_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    langs = {
        'Английский': 'en',
        'Русский': 'ru',
        'Турецкий': 'tr',
        'Немецкий': 'de',
        'Китайский': 'zh-cn'
    }
    buttons = [types.InlineKeyboardButton(name, callback_data=f'lang_{code}') for name, code in langs.items()]
    keyboard.add(*buttons)
    return keyboard

# ---------- Генератор сочинения ----------
def generate_essay(topic):
    templates = [
        f"Сочинение на тему «{topic}».\n\n"
        f"Тема «{topic}» очень важна и актуальна в современном мире. "
        f"Многие люди задумываются о её значении. В своём сочинении я хотел(а) бы "
        f"рассмотреть основные аспекты этой темы.\n\n"
        f"Во-первых, стоит отметить, что «{topic}» затрагивает глубокие вопросы "
        f"человеческого бытия. Это понятие многогранно, и каждый человек понимает "
        f"его по-своему. Некоторые видят в нём источник вдохновения, другие – "
        f"вызов, который нужно принять.\n\n"
        f"Во-вторых, нельзя не упомянуть, что «{topic}» тесно связана с нашей "
        f"повседневной жизнью. Мы сталкиваемся с ней каждый день, даже не замечая этого. "
        f"Примеры можно найти в искусстве, литературе, истории и даже в обычных разговорах.\n\n"
        f"В заключение хочется сказать, что «{topic}» – это не просто слово, это целый мир, "
        f"который ждёт своего исследователя. Каждый из нас может внести свой вклад в понимание "
        f"этой темы и обогатить свой внутренний мир.",
        
        f"Эссе: размышления о «{topic}».\n\n"
        f"Когда я думаю о «{topic}», я вспоминаю множество ассоциаций. "
        f"Для меня это символ перемен, роста и новых возможностей. "
        f"В современном мире, где всё быстро меняется, важно сохранять связь с теми ценностями, "
        f"которые делает нас людьми.\n\n"
        f"Рассматривая «{topic}» с разных сторон, я прихожу к выводу, что она является "
        f"отражением нашего внутреннего мира. То, как мы воспринимаем эту тему, говорит о нас больше, "
        f"чем любые слова. Она побуждает нас к самоанализу и развитию.\n\n"
        f"Подводя итог, можно сказать, что «{topic}» – это бесконечный источник для размышлений. "
        f"И я рад(а), что могу поделиться своими мыслями на этот счёт."
    ]
    return random.choice(templates)

# ---------- Обработчик /start ----------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    user_data[user_id] = {'state': START, 'first_number': '', 'operation': None, 'second_number': ''}
    bot.send_message(
        user_id,
        'Привет! Я бот-калькулятор, помощник в сочинениях и переводчик.\nЧто ты хочешь сделать?',
        reply_markup=main_menu_keyboard()
    )

# ---------- Обработчик callback-запросов ----------
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id
    data = call.data

    if user_id not in user_data:
        user_data[user_id] = {'state': START, 'first_number': '', 'operation': None, 'second_number': ''}

    state = user_data[user_id]['state']

    # --- Главное меню ---
    if data == 'solve':
        user_data[user_id]['state'] = AWAIT_FIRST_NUMBER
        user_data[user_id]['first_number'] = ''
        user_data[user_id]['operation'] = None
        user_data[user_id]['second_number'] = ''
        bot.edit_message_text(
            'Введите первое число (нажимайте цифры, затем "все"):',
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=numbers_keyboard()
        )
        return

    elif data == 'eat':
        bot.edit_message_text(
            'Выбери, что хочешь съесть:',
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=eat_keyboard()
        )
        return

    elif data == 'essay':
        user_data[user_id]['state'] = AWAIT_ESSAY_TOPIC
        bot.edit_message_text(
            'Напишите тему сочинения (любым текстом).\nНапример: "Смысл жизни", "Лето", "Дружба" и т.д.',
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        return

    elif data == 'translate':
        user_data[user_id]['state'] = AWAIT_TRANSLATE_LANG
        bot.edit_message_text(
            'Выберите язык, на который нужно перевести:',
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=language_keyboard()
        )
        return

    # --- Режим еды ---
    if data.startswith('eat_'):
        item = data.split('_')[1]
        bot.edit_message_text(
            f'Ням-ням! Спасибо за {item}!\nВам приятного аппетита!',
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        bot.send_message(user_id, 'Что хочешь сделать дальше?', reply_markup=main_menu_keyboard())
        user_data[user_id]['state'] = START
        return

    # --- Выбор языка для перевода ---
    if data.startswith('lang_'):
        lang_code = data.split('_')[1]
        user_data[user_id]['target_lang'] = lang_code
        user_data[user_id]['state'] = AWAIT_TRANSLATE_TEXT
        lang_names = {
            'en': 'Английский',
            'ru': 'Русский',
            'tr': 'Турецкий',
            'de': 'Немецкий',
            'zh-cn': 'Китайский'
        }
        lang_name = lang_names.get(lang_code, lang_code)
        bot.edit_message_text(
            f'Выбран язык: {lang_name}\nТеперь введите текст или слово для перевода:',
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        return

    # --- Режим решения примера (цифры, операция) ---
    if data.startswith('digit_'):
        digit = data.split('_')[1]
        if state == AWAIT_FIRST_NUMBER:
            user_data[user_id]['first_number'] += digit
            bot.answer_callback_query(call.id, f'Текущее число: {user_data[user_id]["first_number"]}')
        elif state == AWAIT_SECOND_NUMBER:
            user_data[user_id]['second_number'] += digit
            bot.answer_callback_query(call.id, f'Текущее число: {user_data[user_id]["second_number"]}')
        else:
            bot.answer_callback_query(call.id, 'Сначала начните ввод числа')
        return

    if data == 'all':
        if state == AWAIT_FIRST_NUMBER:
            first = user_data[user_id]['first_number']
            if first == '':
                bot.answer_callback_query(call.id, 'Вы не ввели ни одной цифры!')
                return
            user_data[user_id]['state'] = AWAIT_OPERATION
            bot.edit_message_text(
                f'Первое число: {first}\nВыберите операцию:',
                chat_id=user_id,
                message_id=call.message.message_id,
                reply_markup=operations_keyboard()
            )
        elif state == AWAIT_SECOND_NUMBER:
            second = user_data[user_id]['second_number']
            if second == '':
                bot.answer_callback_query(call.id, 'Вы не ввели ни одной цифры!')
                return
            first = int(user_data[user_id]['first_number'])
            op = user_data[user_id]['operation']
            second_num = int(second)
            result = None
            error = None
            try:
                if op == '+':
                    result = first + second_num
                elif op == '-':
                    result = first - second_num
                elif op == '*':
                    result = first * second_num
                elif op == '%':
                    if second_num == 0:
                        error = 'Ошибка: деление на ноль!'
                    else:
                        result = first / second_num
            except Exception as e:
                error = str(e)

            if error:
                bot.edit_message_text(
                    f'Пример: {first} {op} {second_num} = ?\n{error}',
                    chat_id=user_id,
                    message_id=call.message.message_id,
                    reply_markup=None
                )
            else:
                bot.edit_message_text(
                    f'Пример: {first} {op} {second_num} = {result}',
                    chat_id=user_id,
                    message_id=call.message.message_id,
                    reply_markup=None
                )
            bot.send_message(user_id, 'Что хочешь сделать дальше?', reply_markup=main_menu_keyboard())
            user_data[user_id]['state'] = START
        else:
            bot.answer_callback_query(call.id, 'Неверное состояние')
        return

    if data.startswith('op_'):
        op = data.split('_')[1]
        if state == AWAIT_OPERATION:
            user_data[user_id]['operation'] = op
            user_data[user_id]['state'] = AWAIT_SECOND_NUMBER
            user_data[user_id]['second_number'] = ''
            bot.edit_message_text(
                f'Вы выбрали операцию {op}\nВведите второе число (цифры, затем "все"):',
                chat_id=user_id,
                message_id=call.message.message_id,
                reply_markup=numbers_keyboard()
            )
        else:
            bot.answer_callback_query(call.id, 'Сначала введите первое число')
        return

    bot.answer_callback_query(call.id, 'Неизвестная команда')

# ---------- Обработчик текстовых сообщений ----------
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.chat.id
    if user_id not in user_data:
        user_data[user_id] = {'state': START, 'first_number': '', 'operation': None, 'second_number': ''}

    state = user_data[user_id]['state']

    # Сочинение
    if state == AWAIT_ESSAY_TOPIC:
        topic = message.text.strip()
        if not topic:
            bot.reply_to(message, 'Пожалуйста, введите тему текстом.')
            return
        essay = generate_essay(topic)
        bot.reply_to(message, f'📝 Ваше сочинение на тему "{topic}":\n\n{essay}')
        user_data[user_id]['state'] = START
        bot.send_message(user_id, 'Что хочешь сделать дальше?', reply_markup=main_menu_keyboard())
        return

    # Перевод
    if state == AWAIT_TRANSLATE_TEXT:
        text = message.text.strip()
        if not text:
            bot.reply_to(message, 'Пожалуйста, введите текст для перевода.')
            return
        target_lang = user_data[user_id].get('target_lang', 'en')
        translated, src_lang = translate_text(text, target_lang)
        if translated is None:
            bot.reply_to(message, '❌ Не удалось перевести текст. Возможно, нет интернета или лимиты API.')
        else:
            lang_names = {
                'en': 'Английский',
                'ru': 'Русский',
                'tr': 'Турецкий',
                'de': 'Немецкий',
                'zh-cn': 'Китайский'
            }
            target_name = lang_names.get(target_lang, target_lang)
            src_name = lang_names.get(src_lang, src_lang) if src_lang != 'auto' else 'неизвестного'
            bot.reply_to(
                message,
                f'🌍 Перевод с {src_name} на {target_name}:\n\n'
                f'📥 Исходный текст:\n{text}\n\n'
                f'📤 Перевод:\n{translated}'
            )
        user_data[user_id]['state'] = START
        bot.send_message(user_id, 'Что хочешь сделать дальше?', reply_markup=main_menu_keyboard())
        return

    # Если бот не ожидает текст, отправляем в меню
    bot.reply_to(message, 'Пожалуйста, используйте кнопки для навигации.', reply_markup=main_menu_keyboard())

# ---------- Запуск ----------
if __name__ == '__main__':
    bot.polling(non_stop=True)
