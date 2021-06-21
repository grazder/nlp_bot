from telegram.ext.filters import MessageFilter
from telegram import Message


class SentimentFilter(MessageFilter):
    """
    Sentiment Analysis Filter
    """
    def __init__(self, model):
        self.__model = model
        self.name = 'Sentiment Filter'

    def filter(self, message: Message) -> bool:
        if message.text is not None:
            return self.__model([message.text])[0] == 'negative'

        return False
