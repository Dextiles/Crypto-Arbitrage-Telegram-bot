from telebot.handler_backends import StatesGroup, State # noqa


class Arbitrage(StatesGroup):
    Start = State()


class UserSettings(StatesGroup):
    Start = State()
    Choose_what_to_change = State()
    CryptoCurrency = State()
    Exchange = State()
    Profit = State()
