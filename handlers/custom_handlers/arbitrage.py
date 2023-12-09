from telebot.types import Message
from telebot import types
from loader import bot
from keyboards.reply import bidaskreplies as stack
from keyboards.inline import crypto_instruments_key as inline
from utils.misc.crypto_instruments import arbitrage
from config_data.config import ROUND_VALUE


@bot.message_handler(commands=["arbitrage"])
def start_arbitrage(message: Message):
    bot.send_message(message.chat.id, f'Добро пожаловать в раздел арбитража криптовалют. '
                                      f'Данный инструмент сравнивает курсы по выбранным валютным связкам на ваших '
                                      f'криптобиржах и возвращает выгодные предложения по покупке и продаже',
                     reply_markup=stack.start_reply())
    bot.register_next_step_handler(message, order_book)


def order_book(message: Message, default=True):
    if message.text == 'Начать' or message.text == 'Еще раз':
        if default:
            bot.send_message(message.chat.id, 'Выберете валютную связку',
                             reply_markup=stack.symbol_vars())
        else:
            bot.send_message(message.chat.id, 'Введите свою валютную связку в формате X/X (например BTC/USDT)',
                             reply_markup=stack.back())
        bot.register_next_step_handler(message, get_counts)
    elif message.text == 'Выход':
        go_exit(message)


def get_counts(message: Message):
    if message.text == 'Ввести свой вариант':
        order_book(message, False)
    elif message.text == 'Назад':
        order_book(message)
    elif message.text == 'Выход':
        go_exit(message)
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
        markup = inline.get_exchanges_links(best['best_ask'], best['best_bid'])
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
                         parse_mode='html', reply_markup=markup)
        bot.send_message(message.chat.id, 'Еще раз?', reply_markup=stack.again())
        bot.register_next_step_handler(message, order_book)


def go_exit(message: Message):
    bot.send_message(message.chat.id,
                     f'Спасибо за использование сервиса, введите /help для просмотра доступных команд!',
                     reply_markup=types.ReplyKeyboardRemove())
