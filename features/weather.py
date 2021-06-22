from navec import Navec
from slovnet import NER
import pymorphy2
import requests
from typing import List
from datetime import datetime, timedelta

OPEN_WEATHER_TOKEN = "OPEN_WEATHER_TOKEN"


class Weather:
    def __init__(self, token=OPEN_WEATHER_TOKEN):
        self.__token = token
        self.__navec = Navec.load('weights/navec_news_v1_1B_250K_300d_100q.tar')
        self.__ner = NER.load('weights/slovnet_ner_news_v1.tar')
        self.__ner.navec(self.__navec)
        self._morph = pymorphy2.MorphAnalyzer()
        self.__default_city = 'Москва'
        self.__unknown_message = 'Извини, но я не нашел такого города.'

        self.__translate = {
            'Clear': 'Ясно☀️',
            'Clouds': 'Облачно ☁',
            'Rain': 'Дождь☂️',
            'Snow': 'Снег❄️',
            'Mist': 'Туман🌫️',
            'Thunderstorm': 'Гроза🌩️',
            'Drizzle': 'Изморось🌧️',
        }

    def __lemmatize(self, text):
        words = text.split()
        res = list()
        for word in words:
            p = self._morph.parse(word)[0]
            res.append(p.normal_form)

        return res

    def __upper_message(self, message_list: List[str]) -> List[str]:
        return [x.capitalize() for x in message_list]

    def __get_city(self, message):
        lemmatized_upper_message = self.__upper_message(self.__lemmatize(message))
        markup = self.__ner(' '.join(lemmatized_upper_message))

        spans = [x for x in markup.spans if x.type == 'LOC']

        if len(spans) > 0:
            city = message[:spans[0].stop].strip().split(' ')[-1]
            city = ' '.join(self.__upper_message(self.__lemmatize(city)))

            return city

        return None

    def __get_day(self, message: str) -> int:
        lemmatized_message = self.__lemmatize(message)

        if 'сегодня' in lemmatized_message:
            return 0
        if 'завтра' in lemmatized_message:
            return 1
        if 'неделя' in lemmatized_message:
            return 7

        return 0

    def __get_translation(self, weather):
        if weather in self.__translate.keys():
            return self.__translate[weather]
        else:
            return weather

    def __get_desctiption(self, i, forecast, datetime_now):
        response = ''
        day_temp = int(forecast['temp']['day'])
        night_temp = int(forecast['temp']['night'])
        weather = forecast['weather'][0]['main']
        new_day = datetime_now + timedelta(days=i)

        response += f'{datetime.strftime(new_day, "%d.%m.%Y")}📅 '
        response += f'Температура днем: {day_temp}, ночью: {night_temp}, {self.__get_translation(weather)}\n'

        return response


    def get_weather(self, message):
        city_name = self.__get_city(message)

        if city_name is not None:
            response = ''

            current_weather_request = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}' \
                                      f'&units=metric&appid={OPEN_WEATHER_TOKEN}'
            current_weather = requests.get(current_weather_request).json()

            if 'coord' in current_weather.keys():
                lon, lat = current_weather['coord']['lon'], current_weather['coord']['lat']

                weather_forecast_request = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}' \
                                           f'&exclude=minutely,hourly&units=metric&appid={OPEN_WEATHER_TOKEN}'
                weather_forecast = requests.get(weather_forecast_request).json()

                case_city_name = self._morph.parse(city_name)[0].inflect({'loct'}).word.capitalize()

                response += 'Прогноз погоды в ' + case_city_name + ':\n'
                datetime_now = datetime.now()

                day = self.__get_day(message)

                if day == 0:
                    response += self.__get_desctiption(0, weather_forecast['daily'][0], datetime_now)
                elif day == 1:
                    response += self.__get_desctiption(1, weather_forecast['daily'][1], datetime_now)
                elif day == 7:
                    for i, forecast in enumerate(weather_forecast['daily']):
                        response += self.__get_desctiption(i, forecast, datetime_now)

                return response

        return self.__unknown_message
