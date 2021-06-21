import requests
from googletrans import Translator

from httpcore._exceptions import ConnectError


class CatFactGenerator:
    __url__ = 'https://catfact.ninja/fact'
    __translator__ = Translator()

    def sample(self):
        try:
            req = requests.get(self.__url__)

            fact = req.json()['fact']
            fact = self.__translator__.translate(fact, dest='ru').text
        except (ConnectError, requests.ConnectionError):
            fact = 'Факты про кошек кончились :('
        return fact
