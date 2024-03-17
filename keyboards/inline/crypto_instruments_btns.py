from telebot import types # noqa
from utils.misc.logger import Logger
from typing import Union


def get_exchanges_links(bid_id: str, bid_link: str, ask_id: str, ask_link: str, message: types.Message) \
        -> Union[types.InlineKeyboardMarkup, types.ReplyKeyboardRemove]:
    """
    Generates the function comment for the given function.

    Args:
        bid_id (str): The ID of the bid.
        bid_link (str): The link for buying on the bid exchange.
        ask_id (str): The ID of the ask.
        ask_link (str): The link for selling on the ask exchange.
        message (types.Message): The message object.

    Returns:
        Union[types.InlineKeyboardMarkup, types.ReplyKeyboardRemove]: The generated inline keyboard markup or
         a reply keyboard remove object.
    """
    markup = types.InlineKeyboardMarkup()
    try:
        markup.add(types.InlineKeyboardButton(text=f'\U00002795 Купить на {bid_id}', url=bid_link))
        markup.add(types.InlineKeyboardButton(text=f'\U00002796 Продать на {ask_id}', url=ask_link))
    except Exception as ex:
        Logger(message).log_exception(error=ex, func_name='get_exchanges_links', handler_name='/arbitrage')
        return types.ReplyKeyboardRemove()
    else:
        return markup
