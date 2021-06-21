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
from handlers import StartHandler, EndHandler, \
    SentimentHandler, MainMessageHandler, \
    BeerHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

MAIN, BEER = 0, 1


class TelegramBot:
    def __init__(self, token):
        self.__updater = Updater(token)
        self.__dispatcher = self.__updater.dispatcher
        self.__logger = logging.getLogger(__file__)

        handler = self.__init_handlers()

        self.__dispatcher.add_handler(handler)

    def __init_handlers(self) -> List[Handler]:
        main_message_handler = MainMessageHandler()
        # sent_handler_main = SentimentHandler(MAIN)
        # sent_handler_beer = SentimentHandler(BEER)

        return ConversationHandler(
                entry_points=[StartHandler(MAIN).create(),
                              main_message_handler.create_start()],
                states={
                    MAIN: [
#                        sent_handler_main.create(),
                        main_message_handler.create()
                    ],
                    BEER: [
#                        sent_handler_beer.create(),
                        BeerHandler(MAIN).create()
                    ]
                },
                fallbacks=[EndHandler().create()]
            )


    def start(self):
        self.__logger.info("Start the Bot...")
        self.__updater.start_polling()
        self.__updater.idle()
