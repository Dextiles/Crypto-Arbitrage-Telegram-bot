from telebot.handler_backends import StatesGroup, State # noqa


class Arbitrage(StatesGroup):
    Start = State()
