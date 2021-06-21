from telegram.ext.filters import MessageFilter
from telegram import Message
from text_handlers import HelloTextHandler


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


class HelloFilter(MessageFilter):
    """
    Hello Filter
    """
    def __init__(self):
        self.name = 'end'
        self.__text_handler = HelloTextHandler()

    def filter(self, message: Message) -> bool:
        if message.text is not None:
            handler_trigger, handler_message = self.__text_handler.get(message.text)
            return handler_trigger

        return False
