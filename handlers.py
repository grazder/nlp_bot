import logging

from telegram import Update
from telegram.ext import CallbackContext, Handler, CommandHandler, RegexHandler, MessageHandler, Filters
from insult_detection import SentimentAnalysis


class SuperHandler:
    """
    Abstract handler
    """
    def __init__(self):
        self.__logger = logging.getLogger(__file__)
        self.__analyser = SentimentAnalysis()
        self.__bad_message = 'Давай повежливей...'

    @property
    def handler_name(self) -> str:
        raise NotImplementedError()

    def _run_handler(self, update: Update, callback_context: CallbackContext):
        raise NotImplementedError()

    def _run_wrapper(self, update: Update, callback_context: CallbackContext):
        if update.effective_chat is None:
            self.__logger.error(f"Can't find source chat for {self.handler_name}")
            return

        sentiment = self.__analyser.get_sentiment(update.message.text)
        self.__logger.info(
            f"Get {self.handler_name} from {update.effective_chat.id} ({update.effective_chat.username}. Sentiment: {sentiment})"
        )

        # Check if there is no insults

        if sentiment == 'negative':
            callback_context.bot.send_message(chat_id=update.effective_chat.id, text=self.__bad_message)
        else:
            self._run_handler(update, callback_context)

    def create(self) -> Handler:
        raise NotImplementedError()


class StartHandler(SuperHandler):
    """
    Handler for start messages
    """
    def __init__(self):
        super().__init__()

        self.__message = 'Привет!'

    @property
    def handler_name(self) -> str:
        return 'start'

    def _run_handler(self, update: Update, callback_context: CallbackContext):
        callback_context.bot.send_message(chat_id=update.effective_chat.id, text=self.__message)

    def create(self) -> Handler:
        return CommandHandler(self.handler_name, self._run_wrapper)


class EndHandler(SuperHandler):
    """
    Handler for end messages
    """
    def __init__(self):
        super().__init__()

        self.__message = 'Пока!'

    @property
    def handler_name(self) -> str:
        return 'end'

    def _run_handler(self, update: Update, callback_context: CallbackContext):
        callback_context.bot.send_message(chat_id=update.effective_chat.id, text=self.__message)
        callback_context.user_data.clear()

    def create(self) -> Handler:
        return CommandHandler(self.handler_name, self._run_wrapper)


class UnknownHandler(SuperHandler):
    """
    Handler for unknown phrases
    """
    def __init__(self):
        super().__init__()

        self.__message = 'Я что-то тебя не понимаю...'

    @property
    def handler_name(self) -> str:
        return 'unknown'

    def _run_handler(self, update: Update, callback_context: CallbackContext):
        callback_context.bot.send_message(chat_id=update.effective_chat.id, text=self.__message)

    def create(self) -> Handler:
        return MessageHandler(Filters.regex(r'.*'), self._run_wrapper)
