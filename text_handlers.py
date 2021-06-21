from typing import List
import pymorphy2
from features.weather import Weather
from features.cat_facts import CatFactGenerator

class SuperTextHandler:
    """
    Abstract handler
    """
    def __init__(self):
        self._morph = pymorphy2.MorphAnalyzer()

    def _lemmatize(self, text):
        words = text.split()
        res = list()
        for word in words:
            p = self._morph.parse(word)[0]
            res.append(p.normal_form)

        return res

    @property
    def handler_name(self) -> str:
        raise NotImplementedError()

    @property
    def _handler_triggers(self) -> List[str]:
        raise NotImplementedError()

    def _get_message(self, message: str) -> str:
        raise NotImplementedError()

    def get(self, message: str) -> (bool, str):
        print(self._lemmatize(message))
        tokens = ' '.join(self._lemmatize(message))
        trigger = any(word in tokens for word in self._handler_triggers)

        if trigger:
            return trigger, self._get_message(message)

        return trigger, None


class HelloTextHandler(SuperTextHandler):
    """
    Handler for greetings in message
    """
    def __init__(self):
        super().__init__()
        self.__message = 'Привет!'

    @property
    def handler_name(self) -> str:
        return 'hello'

    @property
    def _handler_triggers(self) -> List[str]:
        return ['привет', 'здарова', 'йоу',
                'здравствовать', 'здравствуйте', 'прив',
                'здаров']

    def _get_message(self, message: str) -> str:
        return self.__message


class EndTextHandler(SuperTextHandler):
    """
    Handler for greetings in message
    """
    def __init__(self):
        super().__init__()
        self.__message = 'Пока!'

    @property
    def handler_name(self) -> str:
        return 'end'

    @property
    def _handler_triggers(self) -> List[str]:
        return ['пока', 'досвидание', 'поки',
                'досвидания', 'прощай']

    def _get_message(self, message: str) -> str:
        return self.__message


class WeatherTextHandler(SuperTextHandler):
    """
    Handler for greetings in message
    """
    def __init__(self):
        super().__init__()
        self.__weather = Weather()

    @property
    def handler_name(self) -> str:
        return 'weather'

    @property
    def _handler_triggers(self) -> List[str]:
        return ['погода', 'температура']

    def _get_message(self, message: str) -> str:
        return self.__weather.get_weather(message)


class BeerTextHandler(SuperTextHandler):
    """
    Handler for beer searcher
    """
    def __init__(self):
        super().__init__()

    @property
    def handler_name(self) -> str:
        return 'beer'

    @property
    def _handler_triggers(self) -> List[str]:
        return ['пиво', 'пивикс', 'пивчанский', 'пив', 'пиву']

    def _get_message(self, message: str) -> str:
        return 'Какое пиво ты бы хотел?'


class CatTextHandler(SuperTextHandler):
    """
    Handler for beer searcher
    """
    def __init__(self):
        super().__init__()
        self.__generator = CatFactGenerator()

    @property
    def handler_name(self) -> str:
        return 'cat'

    @property
    def _handler_triggers(self) -> List[str]:
        return ['кошка', 'кот', 'котенок', 'киска', 'котик']

    def _get_message(self, message: str) -> str:
        return 'Интересный факт про котика: ' + self.__generator.sample()
