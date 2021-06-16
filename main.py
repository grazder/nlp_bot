from TelegramBot import TelegramBot

BOT_TOKEN = "1864955125:AAHolvS42alOUd4V-4HT6r6-dhyelNLGjZU"


def main() -> None:
    bot = TelegramBot(BOT_TOKEN)
    bot.start()


if __name__ == '__main__':
    main()
