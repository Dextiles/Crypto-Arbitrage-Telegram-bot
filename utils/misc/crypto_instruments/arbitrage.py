import ccxt
from loader import bot
from telebot.types import Message


class BestOffer:
    def __init__(self, symbol):
        self._exchanges = ['binance', 'bybit', 'okx', 'kucoin',
                           'kraken', 'bitstamp', 'bitfinex',
                           'upbit', 'gateio', 'gemini',
                           'coinbase', 'cryptocom']
        self._symbol = symbol
        self._exchanges_object = [getattr(ccxt, exchange)() for exchange in self._exchanges]
        self._best_offer = {'id': '', 'spread': 0}
        self._unsuccess_get = dict()

    def get_best_offer(self, message: Message) -> dict:
        for i, exchange in enumerate(self._exchanges_object, start=1):
            try:
                orderbook = exchange.fetch_order_book(self._symbol)
            except Exception as ex:
                self._unsuccess_get[exchange.id] = ex
            else:
                bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
                ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
                spread = (ask - bid) if (bid and ask) else None
                if self._best_offer['spread'] < spread:
                    self._best_offer['id'] = exchange.id
                    self._best_offer['spread'] = spread
            finally:
                bot.send_message(message.chat.id, f'Выполняю анализ биржи {exchange}.. ({i}/{len(self._exchanges)})')
        return {'offer': self._best_offer, 'exceptions': self._unsuccess_get}

    @property
    def exchanges(self):
        return self._exchanges

    @exchanges.setter
    def exchanges(self, *exchanges):
        for exchange in exchanges:
            if exchange in ccxt.exchanges:
                self._exchanges.append(exchange)
            else:
                exit(f'С биржей {exchange} мы работать не умеем или ее не существует')
