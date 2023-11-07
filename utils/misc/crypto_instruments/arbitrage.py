import ccxt
from loader import bot
from telebot.types import Message
from typing import NoReturn
from datetime import datetime
from config_data.config import DATE_FORMAT_FULL


class BestOffer:
    def __init__(self, symbol: str) -> NoReturn:
        self._exchanges = ['binance', 'bybit', 'okx', 'kucoin',
                           'kraken', 'bitstamp', 'bitfinex',
                           'upbit', 'gateio', 'gemini',
                           'coinbase', 'cryptocom']
        self._symbol = symbol
        self._exchanges_object = [getattr(ccxt, exchange)() for exchange in self._exchanges]
        self._best_bid = {'id': '', 'value': 0.0, 'mount': 0.0}
        self._best_ask = {'id': '', 'value': 0.0, 'mount': 0.0}
        self._bad_symbols = dict()

    def _calc_best(self, key: str, value: float, mount: float, exchange_id: str) -> None:
        if key == 'bids':
            if self._best_bid['value'] == 0 or value > self._best_bid['value']:
                self._best_bid['value'] = value
                self._best_bid['id'] = exchange_id
                self._best_bid['mount'] = mount
        if key == 'asks':
            if self._best_ask['value'] == 0 or value < self._best_ask['value']:
                self._best_ask['value'] = value
                self._best_ask['id'] = exchange_id
                self._best_ask['mount'] = mount

    def get_best_offer(self, message: Message) -> dict:
        for i, exchange in enumerate(self._exchanges_object, start=1):
            bot.send_message(message.chat.id, f'Выполняю анализ биржи <code>{exchange}</code>.. '
                                              f'({i}/{len(self._exchanges)})',
                             parse_mode='html')
            try:
                exchange.load_markets()
                if exchange.has['fetchOrderBook'] and self._symbol in exchange.symbols:
                    orderbook = exchange.fetch_order_book(self._symbol)
                    self._calc_best('bids', orderbook['bids'][0][0], orderbook['bids'][0][1], exchange)
                    self._calc_best('asks', orderbook['asks'][0][0], orderbook['asks'][0][1], exchange)
                else:
                    raise ValueError
            except Exception as ex:
                self._bad_symbols[exchange.id] = ex
        return {'best_bid': self._best_bid,
                'best_ask': self._best_ask,
                'spread': self._best_bid['value'] - self._best_ask['value'],
                'errors': self._bad_symbols,
                'time': datetime.strftime(datetime.now(), DATE_FORMAT_FULL),
                'volume': min(self._best_bid["mount"], self._best_ask['mount']),
                'profit': min(self._best_bid["mount"], self._best_ask['mount'] *
                              (self._best_bid['value'] - self._best_ask['value']))}

    @property
    def exchanges(self):
        return self._exchanges

    @exchanges.setter
    def exchanges(self, *new_exchanges):
        for exchange in new_exchanges:
            if exchange in ccxt.exchanges:
                self._exchanges.append(exchange)
            else:
                exit(f'С биржей {exchange} мы работать не умеем или ее не существует')
