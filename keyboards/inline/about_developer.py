from telebot import types


def about_me():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton('vk', url='https://vk.com/id275042632'),
               types.InlineKeyboardButton('instagram', url='https://www.instagram.com/jack_danie1s'))
    markup.row(types.InlineKeyboardButton('github', url='https://github.com/Dexiles'))
    return markup
