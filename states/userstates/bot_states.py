from telebot.handler_backends import StatesGroup, State # noqa


class Arbitrage(StatesGroup):
    """
    state machine of the '/arbitrage' handler
    Start = state of the start of the arbitrage process
    """
    Start = State()


class UserSettings(StatesGroup):
    """
    state machine of the '/config' handler
    Start = state of the start of the configuration process
    Choose_what_to_change = state of the choosing what to change in the user settings
    CryptoCurrency = state of the choosing crypto currencies
    Exchange = state of the choosing exchange
    Profit = state of the choosing profit
    """
    Start = State()
    Choose_what_to_change = State()
    CryptoCurrency = State()
    Exchange = State()
    Profit = State()
