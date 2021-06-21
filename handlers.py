import logging
import os

from telegram import Update, InputMediaPhoto
from telegram.ext import CallbackContext, Handler, CommandHandler, RegexHandler, MessageHandler, Filters, ConversationHandler
from filters import SentimentFilter, HelloFilter
from text_handlers import HelloTextHandler, EndTextHandler, WeatherTextHandler, BeerTextHandler, CatTextHandler
from beer.src.beer_embedding import BeerEmbedding

from deeppavlov import build_model, configs


class SuperHandler:
    """
    Abstract handler
    """
    def __init__(self, default_state: int = 0):
        self.__logger = logging.getLogger(__file__)
        self._default_state = default_state

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

        return self._run_handler(update, callback_context)

    def create(self) -> Handler:
        raise NotImplementedError()


class StartHandler(SuperHandler):
    """
    Handler for start messages
    """
    def __init__(self, default_state: int = 0):
        super().__init__(default_state)

        self.__message = 'Привет!'

    @property
    def handler_name(self) -> str:
        return 'start'

    def _run_handler(self, update: Update, callback_context: CallbackContext):
        callback_context.bot.send_message(chat_id=update.effective_chat.id, text=self.__message)

        return self._default_state

    def create(self) -> Handler:
        return CommandHandler(self.handler_name, self._run_wrapper)


class EndHandler(SuperHandler):
    """
    Handler for end messages
    """
    def __init__(self, default_state: int = 0):
        super().__init__(default_state)

        self.__message = 'Пока!'

    @property
    def handler_name(self) -> str:
        return 'end'

    def _run_handler(self, update: Update, callback_context: CallbackContext):
        callback_context.bot.send_message(chat_id=update.effective_chat.id, text=self.__message)
        callback_context.user_data.clear()

        return ConversationHandler.END

    def create(self) -> Handler:
        return CommandHandler(self.handler_name, self._run_wrapper)


class UnknownHandler(SuperHandler):
    """
    Handler for unknown phrases
    """
    def __init__(self, default_state: int = 0):
        super().__init__(default_state)

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
    def __init__(self, default_state: int = 0):
        super().__init__(default_state)

        self.__message = 'Давай повежливее...'
        model = build_model(configs.classifiers.rusentiment_bert, download=False)
        self.__filter = SentimentFilter(model)

    @property
    def handler_name(self) -> str:
        return 'sentiment'

    def _run_handler(self, update: Update, callback_context: CallbackContext):
        callback_context.bot.send_message(chat_id=update.effective_chat.id, text=self.__message)

        return self._default_state

    def create(self) -> Handler:
        return MessageHandler(self.__filter, self._run_wrapper)


class MainMessageHandler(SuperHandler):
    """
    Handler for intent detection
    """
    def __init__(self, main_state: int = 0, beer_state: int = 1):
        super().__init__()

        self.__main_state = main_state
        self.__beer_state = beer_state

        self.__unknown_message = 'Я тебя не понял.'
        self.__logger = logging.getLogger(__file__)
        self.__text_handlers = [
            HelloTextHandler(),
            WeatherTextHandler(),
            CatTextHandler(),
            BeerTextHandler(),
            EndTextHandler()
        ]

        self.__hello_filter = HelloFilter()
        self.__ask_message = 'Могу ли я тебе что-то подсказать?'

    @property
    def handler_name(self) -> str:
        return 'main message'

    def _run_handler(self, update: Update, callback_context: CallbackContext):
        return_message = ''
        logger_message = ''

        end_activated = False
        beer_activated = False
        messages = []

        for handler in self.__text_handlers:
            handler_trigger, handler_message = handler.get(update.message.text)

            if handler_trigger:
                messages += [handler_message]
                logger_message += handler.handler_name + ', '

                end_activated = end_activated or handler.handler_name == 'end'
                beer_activated = beer_activated or handler.handler_name == 'beer'

        if len(logger_message) > 0 and not(end_activated and beer_activated):
            self.__logger.info(
                f"Understood message from {update.effective_chat.id} ({update.effective_chat.username}). Found {logger_message[:-2]}."
            )

            for message in messages:
                callback_context.bot.send_message(chat_id=update.effective_chat.id, text=message)

            if end_activated:
                return ConversationHandler.END
            elif beer_activated:
                return self.__beer_state
        else:
            self.__logger.info(
                f"Didn't understand message from {update.effective_chat.id} ({update.effective_chat.username})."
            )
            callback_context.bot.send_message(chat_id=update.effective_chat.id, text=self.__unknown_message)

        callback_context.bot.send_message(chat_id=update.effective_chat.id, text=self.__ask_message)

        return self.__main_state

    def create(self) -> Handler:
        return MessageHandler(Filters.regex(r'.*'), self._run_wrapper)

    def create_start(self) -> Handler:
        return MessageHandler(self.__hello_filter, self._run_wrapper)


class BeerHandler(SuperHandler):
    """
    Handler for toxic messages
    """
    def __init__(self, default_state: int = 0):
        super().__init__(default_state)

        self.__ask_message = 'Может ты хочешь что-то кроме пива?'
        self.__model = BeerEmbedding()
        self.__path_to_images = 'beer/'

    @property
    def handler_name(self) -> str:
        return 'beer'

    def _run_handler(self, update: Update, callback_context: CallbackContext):
        beer_list = self.__model.match(update.message.text)

        media = [InputMediaPhoto(media=open(os.path.join(self.__path_to_images, x.img_path[3:]), 'rb'),
                                 caption=x.name) for x in beer_list]

        return_message = '\n'.join([f'{i}. {x.name}'for i, x in enumerate(beer_list)])

        callback_context.bot.send_message(chat_id=update.effective_chat.id, text=return_message)
        update.message.reply_media_group(media)
        callback_context.bot.send_message(chat_id=update.effective_chat.id, text=self.__ask_message)

        return self._default_state

    def create(self) -> Handler:
        return MessageHandler(Filters.regex(r'.*'), self._run_wrapper)
