from telebot import types


def deep_size():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(types.KeyboardButton('5'), types.KeyboardButton('10'))
    markup.row(types.KeyboardButton('15'), types.KeyboardButton('20'))
    return markup


def symbol_vars():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(types.KeyboardButton('BTC/USDT'), types.KeyboardButton('ETH/USDT'), types.KeyboardButton('AXS/USDT'))
    markup.row(types.KeyboardButton('BNB/USDT'), types.KeyboardButton('XRP/USDT'), types.KeyboardButton('ADA/USDT'))
    markup.row(types.KeyboardButton('Ввести свой вариант'), types.KeyboardButton('Выход'))
    return markup


def back():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row('Назад')
    return markup


def again():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(types.KeyboardButton('Еще раз'), types.KeyboardButton('Выход'))
    return markup


def start_reply():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(types.KeyboardButton('Начать'), types.KeyboardButton('Выход'))
    return markup
