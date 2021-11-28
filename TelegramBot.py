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
from handlers import *
import os

PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

MAIN, BEER, CAT = 0, 1, 2


class TelegramBot:
    def __init__(self, token):
        self.__token = token
        self.__updater = Updater(self.__token)
        self.__dispatcher = self.__updater.dispatcher
        self.__logger = logging.getLogger(__file__)

        handler = self.__init_handlers()

        self.__dispatcher.add_handler(handler)
        self.__dispatcher.add_handler(HelpHandler().create())

    def __init_handlers(self) -> List[Handler]:
        main_message_handler = MainMessageHandler(MAIN, BEER)
        # sent_handler_main = SentimentHandler(MAIN)
        # sent_handler_beer = SentimentHandler(BEER)

        return ConversationHandler(
                entry_points=[StartHandler(MAIN).create(),
                              main_message_handler.create_start()],
                states={
                    MAIN: [
                        # sent_handler_main.create(),
                        HelpHandler().create(),
                        main_message_handler.create(),
                    ],
                    BEER: [
                        # sent_handler_beer.create(),
                        HelpHandler().create(),
                        BeerHandler(MAIN).create(),
                    ]
                },
                fallbacks=[EndHandler().create()]
            )

    def start(self):
        self.__logger.info("Start the Bot...")
        self.__updater.start_polling(none_stop=True)
        # self.__updater.start_webhook(listen="0.0.0.0",
        #                              port=int(PORT),
        #                              url_path=self.__token)
        # self.__updater.bot.setWebhook('https://nlp-pivo-bot.herokuapp.com/' + self.__token)
        self.__updater.idle()
