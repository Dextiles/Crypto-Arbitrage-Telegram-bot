from telebot import types


def get_extended_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Показать полные сведения', callback_data='show_all'))
    return markup
