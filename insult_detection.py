from deeppavlov import build_model, configs
from telegram.ext.filters import MessageFilter


class SentimentFilter(MessageFilter):
    def __init__(self, model):
        self.__model = model
        self.name = 'Sentiment Filter'

    def filter(self, message):
        if message.text is not None:
            return self.__model([message.text])[0] == 'negative'

        return False
