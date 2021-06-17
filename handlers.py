import logging

from telegram import Update
from telegram.ext import CallbackContext, Handler, CommandHandler, RegexHandler, MessageHandler, Filters
from insult_detection import SentimentFilter

from deeppavlov import build_model, configs


class SuperHandler:
    """
    Abstract handler
    """
    def __init__(self):
        self.__logger = logging.getLogger(__file__)

    @property
    def handler_name(self) -> str:
        raise NotImplementedError()

    def _run_handler(self, update: Update, callback_context: CallbackContext):
        raise NotImplementedError()

    def _run_wrapper(self, update: Update, callback_context: CallbackContext):
        if update.effective_chat is None:
            self.__logger.error(f"Can't find source chat for {self.handler_name}")
            return

        self.__logger.info(
            f"Get {self.handler_name} from {update.effective_chat.id} ({update.effective_chat.username})"
        )

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


class SentimentHandler(SuperHandler):
    """
    Handler for toxic messages
    """
    def __init__(self):
        super().__init__()

        self.__message = 'Давай повежливее...'
        model = build_model(configs.classifiers.rusentiment_bert, download=False)
        self.__filter = SentimentFilter(model)

    @property
    def handler_name(self) -> str:
        return 'sentiment'

    def _run_handler(self, update: Update, callback_context: CallbackContext):
        callback_context.bot.send_message(chat_id=update.effective_chat.id, text=self.__message)

    def create(self) -> Handler:
        return MessageHandler(self.filter, self._run_wrapper)
