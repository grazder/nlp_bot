from typing import List
import pymorphy2
from weather import Weather

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
        return ['привет', 'здарова', 'йоу']

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
        return 'bye'

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
