from telebot import types
import ccxt


def get_exchanges_links(bid_id, bid_link, ask_id, ask_link):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=f'Купить на {bid_id}', url=bid_link))
    markup.add(types.InlineKeyboardButton(text=f'Продать на {ask_id}', url=ask_link))
    return markup
