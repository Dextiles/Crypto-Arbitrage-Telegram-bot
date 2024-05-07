import ccxt
from database import userdata_controller as controller
import json
from datetime import datetime
from telebot.types import Message, ReplyKeyboardRemove # noqa
from utils.misc.crypto_instruments.tradable_currency import get_tradable_currencies


def get_actual_symbols(message: Message) -> None:
    """
    Generate a set of actual symbols based on the exchanges provided.

    Parameters:
    exchanges (list[str]): A list of exchange names.

    Returns:
    set[str]: A set of actual symbols.
    """
    if controller.is_time_out(hours=24) or controller.get_common().allowed_symbols is None:
        actual_symbols = get_tradable_currencies()
        controller.update_common(allowed_symbols=json.dumps(actual_symbols))
        controller.update_common(work_symbols_date_analysis=datetime.now())
