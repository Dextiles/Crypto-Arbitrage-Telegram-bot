from telebot import types


def get_extended_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Показать полные сведения', callback_data='show_all'))
    return markup


def get_exchanges_links(bid: dict, ask: dict):
    markup = types.InlineKeyboardMarkup()
    bid_exc_id = str(bid["id"])
    bid_exc_url = str(bid['link'])
    ask_exc_id = str(ask['id'])
    ask_exc_url = str(ask['link'])
    markup.row(types.InlineKeyboardButton(text=bid_exc_id, callback_data='linker'),
               types.InlineKeyboardButton(text=ask_exc_id, callback_data='linker'))
    return markup
