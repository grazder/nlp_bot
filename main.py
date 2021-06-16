from TelegramBot import TelegramBot

BOT_TOKEN = "TELEGRAM_TOKEN"

def main() -> None:
    bot = TelegramBot(BOT_TOKEN)
    bot.start()


if __name__ == '__main__':
    main()
