from telegram.ext import Updater
from typing import List
from handlers import *
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

MAIN, BEER, CAT = 0, 1, 2


class TelegramBot:
    def __init__(self):
        self.__updater = Updater(os.environ['TELEGRAM_TOKEN'])
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
        self.__updater.start_polling()
        self.__updater.idle()
