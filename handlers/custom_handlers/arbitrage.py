from telebot.types import Message  # noqa
from telebot import types  # noqa
from loader import bot
from keyboards.reply import bidaskreplies as stack
from utils.misc.crypto_instruments import arbitrage
from config_data.config import ROUND_VALUE
from states.userstates.arbitrage_states import Base_Arbitrage


@bot.message_handler(commands=["arbitrage"])
def start_arbitrage(message: Message):
    """
    Handles the "arbitrage" command from the bot. This function sends a welcome message to the user and provides
    information about the cryptocurrency arbitrage tool. It compares currency exchange rates on selected
    crypto exchanges and returns the best offers for buying and selling.

    Parameters:
    - message(Message): A Message object representing the incoming message from the user.

    Returns:
    None
    """
    bot.send_message(message.chat.id, f'Добро пожаловать в раздел арбитража криптовалют. '
                                      f'Данный инструмент сравнивает курсы по выбранным валютным связкам на ваших '
                                      f'криптобиржах и возвращает выгодные предложения по покупке и продаже',
                     reply_markup=stack.start_reply())
    bot.set_state(message.from_user.id, Base_Arbitrage.Start, message.chat.id)  # переходим к состоянию


@bot.callback_query_handler(func=lambda call: True, state=Base_Arbitrage.Start)  # пытаемся его отловить
def order_book(message: Message):
    """
    Handles messages when the user's current state is GET_ORDER in the Arbitrage.CryptoArbitrage state machine.

    Parameters:
        message (Message): The message object containing information about the user's input.

    Returns:
        None

    Raises:
        None
    """
    if message.text == 'Начать' or message.text == 'Еще раз':
        bot.send_message(message.chat.id, 'Выберете валютную связку', reply_markup=stack.symbol_vars())
    bot.set_state(message.from_user.id, Base_Arbitrage.Choose_pair, message.chat.id)


@bot.callback_query_handler(func=lambda call: True, state=Base_Arbitrage.Choose_pair)
def get_counts(message: Message):
    """
    A callback query handler that processes the message and performs various actions based on the message text.
    Args:
        message: The message object containing information about the user's input.

    Returns: None

    """
    if message.text == 'Ввести свой вариант':
        order_book(message, False)
    elif message.text == 'Назад':
        pass
    elif not message.text.startswith('/'):
        symbol = message.text.lstrip()
        arbitrage_instrument = arbitrage.BestOffer(symbol, message)
        invoke = bot.send_message(message.chat.id, f'Анализ лучшего предложения в связке {symbol}\n'
                                                   f'Выбранные биржи: {", ".join(arbitrage_instrument.exchanges)}',
                                  reply_markup=types.ReplyKeyboardRemove())
        best = arbitrage_instrument.get_best_offer(message)
        errors = ', '.join(best["errors"].keys())
        if len(best['errors'].keys()) == 0:
            errors_text = 'Анализ произведен на всех выбранных биржах!'
        else:
            errors_text = f'Из бирж: {errors} не удалось извлечь данные в связке {symbol}'
        bot.delete_message(message.chat.id, invoke.message_id)
        bot.send_message(message.chat.id, f'Время анализа: {best["time"]}\n\n'
                                          f'Валютная связка: {symbol}\n'
                                          f'=> Выгодно купить: \nБиржа <code>{best["best_ask"]["id"]}</code>\n'
                                          f'Цена: {round(best["best_ask"]["value"], ROUND_VALUE)} USDT\n'
                                          f'Количество: {round(best["best_ask"]["mount"], ROUND_VALUE)}\n'
                                          f'=> Выгодно продать: \nБиржа <code>{best["best_bid"]["id"]}</code>\n'
                                          f'Цена: {round(best["best_bid"]["value"], ROUND_VALUE)} USDT\n'
                                          f'Количество: {round(best["best_bid"]["mount"], ROUND_VALUE)}\n'
                                          f'Спред при таком исходе составит: {round(best["spread"], ROUND_VALUE)} '
                                          f'USDT\n\n'
                                          f'Доступный объем для транзакции: {round(best["volume"], ROUND_VALUE)}\n'
                                          f'Максимальный выигрыш от сделки: {round(best["profit"], ROUND_VALUE)} USDT'
                                          f'\n\n{errors_text}',
                         parse_mode='html', reply_markup=types.ReplyKeyboardRemove())
        bot.delete_state(message.from_user.id, message.chat.id)
