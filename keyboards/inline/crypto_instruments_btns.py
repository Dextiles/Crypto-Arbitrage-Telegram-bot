from telebot import types # noqa


def get_exchanges_links(bid_id: str, bid_link: str, ask_id: str, ask_link: str) -> types.InlineKeyboardMarkup:
    """
    Generate a markup with inline keyboard buttons for buying and selling on different exchanges.

    Parameters:
    bid_id (str): The ID of the exchange for buying.
    bid_link (str): The URL link for buying on the specified exchange.
    ask_id (str): The ID of the exchange for selling.
    ask_link (str): The URL link for selling on the specified exchange.

    Returns:
    types.InlineKeyboardMarkup: A markup with inline keyboard buttons for buying and selling on different exchanges.
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=f'\U00002795 Купить на {bid_id}', url=bid_link))
    markup.add(types.InlineKeyboardButton(text=f'\U00002796 Продать на {ask_id}', url=ask_link))
    return markup
