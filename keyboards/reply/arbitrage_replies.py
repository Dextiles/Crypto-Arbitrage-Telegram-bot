from telebot import types # noqa


def create_start_reply() -> types.ReplyKeyboardMarkup:
    """
    A function to initialize a reply keyboard markup with two buttons for starting and exiting.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(types.KeyboardButton('Начать \U00002705'), types.KeyboardButton('Выход \U0000274E'))
    return markup
