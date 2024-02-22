from telebot.handler_backends import StatesGroup, State


class Base_Arbitrage(StatesGroup):
    Start = State()
    Choose_pair = State()
    Get_result = State()
