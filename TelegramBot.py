from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    Handler
)
import logging
from typing import Dict, List
from handlers import StartHandler, EndHandler, UnknownHandler, SentimentHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


class TelegramBot:
    def __init__(self, token):
        self.__updater = Updater(token)
        self.__dispatcher = self.__updater.dispatcher
        self.__logger = logging.getLogger(__file__)

        handlers = self.__init_handlers()

        for handler in handlers:
            self.__dispatcher.add_handler(handler)

    def __init_handlers(self) -> List[Handler]:
        return [
            StartHandler().create(),
            EndHandler().create(),
            UnknownHandler().create(),
        ]

    def start(self):
        self.__logger.info("Start the Bot...")
        self.__updater.start_polling()
        self.__updater.idle()
