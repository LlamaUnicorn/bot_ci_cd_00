import json

import requests
import yagmail

from config import currency, WEATHER_TOKEN


class ConversionException(Exception):
    pass


class CurrencyConverter:
    @staticmethod
    def get_price(quote: str, base: str, amount: str):
        if quote == base:
            raise ConversionException(f'Невозможно перевести одинаковые валюты {base}.')

        try:
            quote_ticker = currency[quote.lower()]
        except KeyError:
            raise ConversionException(f'Не удалось обработать валюту {quote}.')

        try:
            base_ticker = currency[base.lower()]
        except KeyError:
            raise ConversionException(f'Не удалось обработать валюту {base}.')

        try:
            amount = float(amount)
        except ValueError:
            raise ConversionException(f'Не удалось обработать количество {amount}.')

        r = requests.get(f'https://api.exchangerate.host/convert?from={quote_ticker}&to={base_ticker}&amount={amount}')
        total_base = json.loads(r.content)['result']
        total_base = round(total_base, 2)
        message = total_base
        return message


#  Сначала реализовал функционал получения прогноза погоды в виде класса. Позже переделаю (надеюсь).
#  Попробуйте вместо названия города ввести цифру.


class GetWeather:
    def __init__(self, city):
        self._location = city
        self.location_lat = None
        self.location_lon = None
        self.local_name = None

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if isinstance(value, str):
            self._location = value
        else:
            raise ValueError('Значение должно быть строкой')

    def get_coordinates(self):
        # Get city coordinates (lat, lon)
        web_source = f'https://api.openweathermap.org/geo/1.0/direct?q={self._location}&limit=5&appid={WEATHER_TOKEN}&lang=ru'
        r = requests.get(web_source)
        texts = json.loads(r.content)
        self.location_lat = texts[0]['lat']
        self.location_lon = texts[0]['lon']
        self.local_name = texts[0]['local_names']['ru']

    def get_weather(self):
        # Get weather for the location
        located_weather = f'https://api.openweathermap.org/data/2.5/weather?lat={self.location_lat}&lon={self.location_lon}&appid={WEATHER_TOKEN}&units=metric'
        weather_request = requests.get(located_weather)
        texts_weather = json.loads(weather_request.content)
        # weather_report = f"{texts[0]['local_names']['ru']}: ощущается, как {texts_weather['main']['feels_like']}°C."
        weather_report = f"{self.local_name}: ощущается, как {texts_weather['main']['feels_like']}°C."
        print(weather_report)
        return weather_report

    @staticmethod
    def run(self):
        self.get_coordinates()


def send_email(subject, body, to, mail_user, mail_app_password):
    yag = yagmail.SMTP(user=mail_user, password=mail_app_password)
    yag.send(to=to, subject=subject, contents=body)
