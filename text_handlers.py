from typing import List

class SuperTextHandler:
    """
    Abstract handler
    """
    def __init__(self):
        pass

    @property
    def handler_name(self) -> str:
        raise NotImplementedError()

    @property
    def _handler_triggers(self) -> List[str]:
        raise NotImplementedError()

    def _get_message(self, message: str) -> str:
        raise NotImplementedError()

    def get(self, message: str) -> (bool, str):
        trigger = any(word in message.lower() for word in self._handler_triggers)

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
                'добрый вечер', 'добрый день', 'доброе утро']

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
        return ['пока', 'до встречи', 'досвидание',
                'досвидания', 'прощай']

    def _get_message(self, message: str) -> str:
        return self.__message


class WeatherTextHandler(SuperTextHandler):
    """
    Handler for greetings in message
    """
    def __init__(self):
        super().__init__()

    @property
    def handler_name(self) -> str:
        return 'weather'

    @property
    def _handler_triggers(self) -> List[str]:
        return ['погода', 'погоды', 'погоде',
                'прогноз', ]

    def _get_message(self, message: str) -> str:
        return self.__message