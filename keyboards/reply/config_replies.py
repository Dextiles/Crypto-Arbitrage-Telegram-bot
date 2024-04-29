from telebot import types # noqa
from database.default_values_config.default_getter import GetDefaultValues


def get_start_config_reply() -> types.ReplyKeyboardMarkup:
    """
    A function to initialize a reply keyboard markup with two buttons for starting and exiting.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(types.KeyboardButton('Изменить настройки'), types.KeyboardButton('Выход'))
    return markup


def get_options_to_config_button() -> types.ReplyKeyboardMarkup:
    """
    A function to initialize a reply keyboard markup with two buttons for starting and exiting.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(types.KeyboardButton('Сбросить все настройки'))
    markup.row(types.KeyboardButton('Криптобиржи'), types.KeyboardButton('Криптовалюты'))
    markup.row(types.KeyboardButton('Профит'), types.KeyboardButton('Выход'))
    return markup


def go_exit_button() -> types.ReplyKeyboardMarkup:
    """
    A function to initialize a reply keyboard markup with two buttons for starting and exiting.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(types.KeyboardButton('Выход'))
    return markup


def get_go_exit_or_clear_buttons() -> types.ReplyKeyboardMarkup:
    """
    A function to initialize a reply keyboard markup with two buttons for starting and exiting.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(types.KeyboardButton('Очистить черный список'), types.KeyboardButton('Выход'))
    return markup


def get_exchanges_buttons() -> types.ReplyKeyboardMarkup:
    """
    A function to initialize a reply keyboard markup with two buttons for starting and exiting.
    """
    exchanges_names = GetDefaultValues().exchanges
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(types.KeyboardButton('binance'), types.KeyboardButton("bybit"), types.KeyboardButton("okx"))
    markup.row(types.KeyboardButton("kucoin"), types.KeyboardButton("upbit"), types.KeyboardButton("gateio"))
    markup.row(types.KeyboardButton("gemini"), types.KeyboardButton("zonda"), types.KeyboardButton("cryptocom"))
    markup.row(types.KeyboardButton('Выход'))
    return markup
