from telebot import types # noqa


def get_start_config_reply() -> types.ReplyKeyboardMarkup:
    """
    A function to initialize a reply keyboard markup with two buttons for starting and exiting.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(types.KeyboardButton('Изменить настройки'), types.KeyboardButton('Выход'))
    return markup


def get_options_to_config() -> types.ReplyKeyboardMarkup:
    """
    A function to initialize a reply keyboard markup with two buttons for starting and exiting.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(types.KeyboardButton('Криптобиржи'), types.KeyboardButton('Криптовалюты'))
    markup.row(types.KeyboardButton('Профит'), types.KeyboardButton('Выход'))
    return markup


def go_exit() -> types.ReplyKeyboardMarkup:
    """
    A function to initialize a reply keyboard markup with two buttons for starting and exiting.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(types.KeyboardButton('Выход'))
    return markup


def go_exit_or_clear() -> types.ReplyKeyboardMarkup:
    """
    A function to initialize a reply keyboard markup with two buttons for starting and exiting.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(types.KeyboardButton('Очистить черный список'), types.KeyboardButton('Выход'))
    return markup
