import ccxt
from telebot.types import Message
from telebot import types
from loader import bot
from datetime import datetime
from config_data import config
import prettytable as pt
from keyboards.reply import bidaskreplies as stack


class W:
    def __init__(self):
        self.f = ''


work = W()


@bot.message_handler(commands=["order"])
def order_book(message: Message):
    bot.send_message(message.chat.id, 'Введите валютную связку (например BTC/USD)',
                     reply_markup=stack.symbol_vars())
    bot.register_next_step_handler(message, get_counts)


def get_counts(message: Message):
    symbol = message.text.lstrip()
    exc = ['binance', 'bybit', 'okx', 'kucoin', 'kraken', 'bitstamp', 'bitfinex', 'upbit', 'gateio', 'gemini',
           'coinbase', 'cryptocom']
    bot.send_message(message.chat.id, f'Ждите, собираем информацию\n'
                                      f'Биржи: {", ".join(exc)}\n'
                                      f'Связка: {symbol}', reply_markup=types.ReplyKeyboardRemove())
    exchanges = [getattr(ccxt, exchange)() for exchange in exc]
    spreads = dict()
    exceptions = list()
    for i, exchange in enumerate(exchanges, start=1):
        try:
            orderbook = exchange.fetch_order_book(symbol)
        except Exception as ex:
            exceptions.append(exchange.id)
        else:
            bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
            ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
            spread = (ask - bid) if (bid and ask) else None
            spreads[exchange.id] = spread
        finally:
            bot.send_message(message.chat.id, f'Анализирую биржу {exchange.id}... ({i}/{len(exchanges)})')

    sorted_exc = sorted(spreads.items(), key=lambda item: item[1], reverse=True)
    bot.send_message(message.chat.id, f'Наилучшее предложение в связке {symbol} на бирже {sorted_exc[0][0]}'
                                      f', спред составит {sorted_exc[0][1]}')
    if len(exceptions) > 0:
        bot.send_message(message.chat.id, f'Не удалось сделать запрос на биржи {", ".join(exceptions)}'
                                          f', так так как эти биржы не имеют связки {symbol}')
