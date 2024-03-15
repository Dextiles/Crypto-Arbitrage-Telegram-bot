import ccxt
from database import userdata_controller as controller
import json
from datetime import datetime
from telebot.types import Message, ReplyKeyboardRemove # noqa
from loader import bot
from database.userdata_view import get_last_update
from database.default_values_config.default_getter import GetDefaultValues


def get_actual(exchanges: list[str]):
    actual_symbols = list()
    for current_exchange in [getattr(ccxt, exchange)() for exchange in exchanges]:
        try:
            current_exchange.load_markets()
            current_sym = [sym.split('/USDT')[0] for sym in list(filter(lambda sym: sym.endswith('/USDT'), current_exchange.symbols))]
        except Exception as ex:
            pass
        else:
            actual_symbols.extend(current_sym)
    return list(set(actual_symbols))


def get_actual_symbols(message: Message) -> None:
    """
    Generate a set of actual symbols based on the exchanges provided.

    Parameters:
    exchanges (list[str]): A list of exchange names.

    Returns:
    set[str]: A set of actual symbols.
    """
    if controller.is_time_out(hours=24) or controller.get_common().allowed_symbols is None:
        invoke = bot.send_message(message.chat.id, f'Подождите, выполняется обновление списка криптовалют...\n'
                                                   f'Данная процедура выполняется раз в сутки, '
                                                   f'{get_last_update()}',
                                  reply_markup=ReplyKeyboardRemove())
        actual_symbols = get_actual(GetDefaultValues().exchanges)
        bot.delete_message(invoke.chat.id, invoke.message_id)
        controller.update_common(allowed_symbols=json.dumps(actual_symbols))
        controller.update_common(work_symbols_date_analysis=datetime.now())
