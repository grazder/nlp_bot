from TelegramBot import TelegramBot

from data import get_data


def main() -> None:
    bot = TelegramBot()
    bot.start()


if __name__ == '__main__':
    get_data()
    main()
