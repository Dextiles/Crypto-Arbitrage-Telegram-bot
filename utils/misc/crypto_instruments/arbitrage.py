import time

import ccxt
from loader import bot
from telebot.types import Message, ReplyKeyboardRemove
from typing import NoReturn
from datetime import datetime
from config_data.config import DATE_FORMAT_FULL
from telebot import types as btn
from threading import Thread


class Exchanges:
    def __init__(self, message: Message):
        self.__exchanges = ['binance', 'bybit', 'okx', 'kucoin',
                            'kraken', 'bitstamp', 'bitfinex',
                            'upbit', 'gateio', 'gemini',
                            'coinbase', 'cryptocom', 'bitget', 'mexc']
        self.__errors = dict()
        self.__exchanges_obj = [getattr(ccxt, exchange)() for exchange in self.__exchanges]
        self.__load_markets_all(message)

    def __load_markets_all(self, message):
        invoke = bot.send_message(message.chat.id, f'Во время загрузки ничего не нажимайте.. ',
                                                   reply_markup=ReplyKeyboardRemove())
        msg = bot.send_message(message.chat.id, 'Ждите, загружаем биржи..')
        for i, exchange in enumerate(self.__exchanges_obj):
            try:
                exchange.load_markets()
            except Exception as ex:
                self.__errors[exchange.id] = ex
            finally:
                bot.edit_message_text(message_id=msg.message_id,
                                      chat_id=message.chat.id,
                                      text=f'Ждите, загружаем биржи.. '
                                           f'\nВыполнено {round(i/len(self.__exchanges_obj) * 100)}%')
        bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        bot.delete_message(chat_id=message.chat.id, message_id=invoke.message_id)

    @property
    def exchanges_objects(self):
        return self.__exchanges_obj

    @property
    def exchanges(self):
        return self.__exchanges

    @exchanges.setter
    def exchanges(self, *new_exchanges):
        for exchange in new_exchanges:
            if exchange in ccxt.exchanges:
                self.__exchanges.append(exchange)
            else:
                exit(f'С биржей {exchange} мы работать не умеем или ее не существует')


class BestOffer(Exchanges):
    def __init__(self, symbol: str, message: Message) -> NoReturn:
        super().__init__(message)
        self._exchanges = super().exchanges
        self._symbol = symbol
        self._exchanges_object = super().exchanges_objects
        self._best_bid = {'id': '', 'value': 0.0, 'mount': 0.0, 'link': ''}
        self._best_ask = {'id': '', 'value': 0.0, 'mount': 0.0, 'link': ''}
        self._bad_symbols = dict()

    def _calc_best(self, key: str, value: float, mount: float, exchange_id: str, link: str) -> None:
        if key == 'bids':
            if self._best_bid['value'] == 0 or value > self._best_bid['value']:
                self._best_bid['value'] = value
                self._best_bid['id'] = exchange_id
                self._best_bid['mount'] = mount
                self._best_bid['url'] = link
        if key == 'asks':
            if self._best_ask['value'] == 0 or value < self._best_ask['value']:
                self._best_ask['value'] = value
                self._best_ask['id'] = exchange_id
                self._best_ask['mount'] = mount
                self._best_ask['url'] = link

    def get_best_offer(self, message: Message) -> dict:
        bot.send_message(message.chat.id, 'Ждите...', reply_markup=btn.ReplyKeyboardRemove())
        for i, exchange in enumerate(self._exchanges_object, start=1):
            try:
                if exchange.has['fetchOrderBook'] and self._symbol in exchange.symbols:
                    orderbook = exchange.fetch_order_book(self._symbol)
                    self._calc_best('bids', orderbook['bids'][0][0], orderbook['bids'][0][1], exchange,
                                    exchange.urls['www'])
                    self._calc_best('asks', orderbook['asks'][0][0], orderbook['asks'][0][1], exchange,
                                    exchange.urls['www'])
                else:
                    raise ValueError
            except Exception as ex:
                self._bad_symbols[exchange.id] = ex
        volume = min(self._best_bid["mount"], self._best_ask['mount'])
        spread = self._best_bid['value'] - self._best_ask['value']
        profit = volume * spread
        return {'best_bid': self._best_bid,
                'best_ask': self._best_ask,
                'spread': spread,
                'errors': self._bad_symbols,
                'time': datetime.strftime(datetime.now(), DATE_FORMAT_FULL),
                'volume': volume,
                'profit': profit}


class BestOfferFull(Exchanges):
    def __init__(self, message: Message):
        self._chat_id = message.chat.id
        super().__init__(message)
        self._exchanges = super().exchanges
        self._exchanges_object = super().exchanges_objects
        self._best = {'bid': {'id': '', 'value': 0.0},
                      'ask': {'id': '', 'value': 0.0},
                      'symbol': '',
                      'spread': 0.0,
                      'total': 0,
                      'mount': 0,
                      'excnages': self._exchanges}
        self._working_directory = dict()

    def _counter(self, i_num, sym, exch):
        best = {sym: {'ask': 0, 'ask_exc': '',
                      'bid': 0, 'bid_exc': '',
                      'ask_lim': 0,
                      'bid_lim': 0,
                      'СПРЕД': 0}}
        for exchange in exch:
            try:
                orderbook = exchange.fetch_order_book(sym)
                bid, bid_mount = orderbook['bids'][0]
                ask, ask_mount = orderbook['asks'][0]
                best[sym]['mount'] = min(ask_mount, bid_mount)
                if best[sym]['ask'] == 0 or best[sym]['ask'] > ask:
                    best[sym]['ask'] = ask
                    best[sym]['ask_exc'] = exchange.id
                    best[sym]['ask_lim'] = ask_mount
                if best[sym]['bid'] == 0 or best[sym]['bid'] < bid:
                    best[sym]['bid'] = bid
                    best[sym]['bid_exc'] = exchange.id
                    best[sym]['bid_lim'] = bid_mount
            except Exception as exception:
                pass
        spread = round(best[sym]['bid'] - best[sym]['ask'], 5)
        best[sym]['СПРЕД'] = spread

        if spread > 0 and spread > self._best['spread']:
            self._best['symbol'] = sym
            self._best['ask']['id'] = best[sym]['ask_exc']
            self._best['ask']['value'] = best[sym]['ask']  #buy
            self._best['bid']['id'] = best[sym]['bid_exc']
            self._best['bid']['value'] = best[sym]['bid']  #sell
            self._best['spread'] = best[sym]['СПРЕД']
            self._best['mount'] = min(best[sym]['bid_lim'], best[sym]['ask_lim'])
            self._best['total'] = self._best['mount'] * self._best['spread']

    def get_best_offer(self):
        for exchange in self._exchanges_object:
            try:
                pairs = list(filter(lambda sym: sym.endswith('/USDT'), exchange.symbols))
                for pair in pairs:
                    if pair not in self._working_directory.keys():
                        self._working_directory[pair] = [exchange]
                    else:
                        self._working_directory[pair].append(exchange)
            except Exception as ex:
                pass

        for key, value in list(self._working_directory.items()):
            if len(value) < 2:
                del self._working_directory[key]

        start = bot.send_message(chat_id=self._chat_id, text=f'Обрабатываем пары..')
        for i, (symbol, exchanges) in enumerate(self._working_directory.items()):
            Thread(target=self._counter, args=(i, symbol, exchanges)).start()
            if i % 10 == 0:
                time.sleep(0.5)
                bot.edit_message_text(message_id=start.message_id,
                                      chat_id=self._chat_id,
                                      text=f'Обработано {i} криптопар')
                self._best['total'] = i
        time.sleep(3)
        bot.delete_message(message_id=start.message_id, chat_id=self._chat_id)
        return self._best
