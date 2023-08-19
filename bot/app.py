import telebot
from telebot import types

from config import currency, TOKEN
from extensions import ConversionException, CurrencyConverter, GetWeather


def create_markup(base=None):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    buttons = []
    for val in currency.keys():
        if val != base:
            buttons.append(types.KeyboardButton(val.capitalize()))
    markup.add(*buttons)
    return markup


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def start(message: telebot.types.Message):
    text = 'Доступные команды:\n/convert - конвертер валют\
\n/values - список доступных валют\
\n/weather - прогноз погоды'
    bot.reply_to(message, text)


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for key in currency.keys():
        text = '\n'.join((text, key))
    bot.reply_to(message, text)


@bot.message_handler(commands=['weather'])
def weather(message: telebot.types.Message):
    text = 'Укажите город'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, get_forecast)


def get_forecast(message: telebot.types.Message):
    location = message.text.strip().lower()
    get_weather = GetWeather(location)
    result = get_weather.get_coordinates()
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


bot.polling()
