import telebot
from telebot import types

from config import currency, TOKEN, MAIL_TOKEN, TO, FROM
from extensions import ConversionException, CurrencyConverter, GetWeather, send_email


def create_markup(base=None):
    """Currency keyboard."""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    buttons = []
    for val in currency.keys():
        if val != base:
            buttons.append(types.KeyboardButton(val.capitalize()))
    markup.add(*buttons)
    return markup


def create_weather_markup():
    """Weather keyboard."""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    buttons = [types.KeyboardButton('Set Location'), types.KeyboardButton('Get Weather')]
    markup.add(*buttons)
    return markup


bot = telebot.TeleBot(TOKEN)

get_weather = GetWeather(None)


@bot.message_handler(commands=['start', 'help'])
def start(message: telebot.types.Message):
    text = 'Доступные команды:\n/convert - конвертер валют\
\n/values - список доступных валют\
\n/weather - прогноз погоды\
\ndo <your todo> - отправить туду в things 3'
    bot.reply_to(message, text)


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for key in currency.keys():
        text = '\n'.join((text, key))
    bot.reply_to(message, text)


@bot.message_handler(commands=['weather'])
def weather(message: telebot.types.Message):
    markup = create_weather_markup()
    bot.send_message(message.chat.id, 'Choose an option:', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Set Location')
def set_location(message: telebot.types.Message):
    bot.send_message(message.chat.id, 'Please enter the location:')
    bot.register_next_step_handler(message, save_location)


def save_location(message: telebot.types.Message):
    get_weather.location = message.text.strip().lower()
    get_weather.get_coordinates()
    bot.send_message(message.chat.id, f'Location set to {get_weather.local_name}.')
    result = get_weather.get_weather()
    bot.send_message(message.chat.id, result)


@bot.message_handler(func=lambda message: message.text == 'Get Weather')
def get_forecast(message: telebot.types.Message):
    if get_weather.location is None:
        set_location(message)
    else:
        result = get_weather.get_weather()
        bot.send_message(message.chat.id, result)


@bot.message_handler(commands=['convert'])
def convert(message: telebot.types.Message):
    text = 'Выберите валюту для конвертирования:'
    print('message', message)
    bot.send_message(message.chat.id, text, reply_markup=create_markup())
    bot.register_next_step_handler(message, base_handler)


def base_handler(message: telebot.types.Message):
    base = message.text.strip().lower()
    print('base', base)
    text = 'Выберите валюту, в которую конвертировать:'
    bot.send_message(message.chat.id, text, reply_markup=create_markup(base))
    bot.register_next_step_handler(message, quote_handler, base)


def quote_handler(message: telebot.types.Message, base):
    quote = message.text.strip().lower()
    print('quote', quote)
    text = 'Выберите количество конвертируемой валюты:'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, amount_handler, base, quote)


def amount_handler(message: telebot.types.Message, base, quote):
    amount = message.text.strip()
    try:
        new_price = CurrencyConverter.get_price(base, quote, amount)
    except ConversionException as e:
        bot.send_message(message.chat.id, f"Ошибка в конвертации: \n{e}")
    else:
        text = f'Цена {amount} {quote} в {base}: {new_price}'
        bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: message.text.lower().startswith('do'))
def do_message_handler(message: telebot.types.Message):
    if '\n' in message.text:
        subject, body = message.text[3:].split('\n', 1)
    else:
        subject = message.text[3:]
        body = ""
    to = TO
    sent_from = FROM
    mail_app_password = MAIL_TOKEN
    send_email(subject, body, to, sent_from, mail_app_password)


@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice', 'video', 'document',
    'text', 'location', 'contact', 'sticker'])
def echo_message(message):
    print(f'\n{message.__dict__=}')
    # bot.reply_to(message, message)


bot.polling()
