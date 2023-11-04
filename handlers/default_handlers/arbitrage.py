import ccxt
from telebot.types import Message
from telebot import types
from loader import bot
from keyboards.reply import bidaskreplies as stack
from keyboards.inline import crypto_instruments_key as crypto_key
from utils.misc.crypto_instruments import arbitrage


@bot.message_handler(commands=["arbitrage"])
def order_book(message: Message):
    bot.send_message(message.chat.id, 'Введите валютную связку (например BTC/USD)',
                     reply_markup=stack.symbol_vars())
    bot.register_next_step_handler(message, get_counts)


def get_counts(message: Message):
    symbol = message.text.lstrip()
    arbitrage_instrument = arbitrage.BestOffer(symbol)
    bot.send_message(message.chat.id, f'Анализ лучшего предложения в связке {symbol}\n'
                                      f'Биржи: {", ".join(arbitrage_instrument.exchanges)},',
                     reply_markup=types.ReplyKeyboardRemove())
    best = arbitrage_instrument.get_best_offer(message)
    string = ''
    for i, (exchange, error) in enumerate(best['exceptions'].items(), start=1):
        string += f'{i}) Из биржи {exchange} не удалось извлечь данные из за ошибки: ({error})\n'
    bot.send_message(message.chat.id, f'Лучшее предложение на бирже {best["offer"]["id"]}\n'
                                      f'Спред тут составит {round(best["offer"]["spread"], 8)}',
                     reply_markup=crypto_key.get_extended_markup())
    bot.send_message(message.chat.id, string)


