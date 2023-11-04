from telebot import types


def deep_size():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(types.KeyboardButton('5'), types.KeyboardButton('10'))
    markup.row(types.KeyboardButton('15'), types.KeyboardButton('20'))
    markup.row(types.KeyboardButton('Свой вариант'))
    return markup


def symbol_vars():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(types.KeyboardButton('BTC/USDT'), types.KeyboardButton('ETH/USDT'))
    markup.row(types.KeyboardButton('BNB/USDT'), types.KeyboardButton('XRP/USDT'))
    markup.row(types.KeyboardButton('Свой вариант'))
    return markup

