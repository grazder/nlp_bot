import logging

from telegram import Update
from telegram.ext import CallbackContext, Handler, CommandHandler, RegexHandler, MessageHandler, Filters
from filters import SentimentFilter
from text_handlers import HelloTextHandler, EndTextHandler, WeatherTextHandler

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
        return MessageHandler(self.__filter, self._run_wrapper)


class MainMessageHandler(SuperHandler):
    """
    Handler for intent detection
    """
    def __init__(self):
        super().__init__()
        self.__unknown_message = 'Я тебя не понял.'
        self.__logger = logging.getLogger(__file__)
        self.__text_handlers = [
            HelloTextHandler(),
            WeatherTextHandler(),
            EndTextHandler()
        ]

    @property
    def handler_name(self) -> str:
        return 'main message'

    def _run_handler(self, update: Update, callback_context: CallbackContext):
        return_message = ''
        logger_message = ''

        for handler in self.__text_handlers:
            handler_trigger, handler_message = handler.get(update.message.text)

            if handler_trigger:
                return_message += handler_message + (' ' if handler_message[-1] != '\n' else '')
                logger_message += handler.handler_name + ', '

        if len(return_message) > 0:
            self.__logger.info(
                f"Understood message from {update.effective_chat.id} ({update.effective_chat.username}). Found {logger_message[:-2]}."
            )

            callback_context.bot.send_message(chat_id=update.effective_chat.id, text=return_message)
        else:
            self.__logger.info(
                f"Didn't understand message from {update.effective_chat.id} ({update.effective_chat.username})."
            )
            callback_context.bot.send_message(chat_id=update.effective_chat.id, text=self.__unknown_message)

    def create(self) -> Handler:
        return MessageHandler(Filters.regex(r'.*'), self._run_wrapper)
