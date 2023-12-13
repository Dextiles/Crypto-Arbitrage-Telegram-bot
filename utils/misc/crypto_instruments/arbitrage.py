import time
import ccxt
from loader import bot
from telebot.types import Message, ReplyKeyboardRemove # noqa
from typing import NoReturn
from datetime import datetime
from config_data.config import DATE_FORMAT_FULL
from telebot import types as btn # noqa
from threading import Thread
from database.userdata import Users
import json


class Exchanges:
    def __init__(self, message: Message) -> NoReturn:
        self.__current_user = Users.get_or_none(Users.user_id == message.from_user.id)
        self.__exchanges = json.loads(self.__current_user.work_exchanges)
        self.__min_profit = self.__current_user.default_profit
        self.__errors = dict()
        self.__exchanges_obj = [getattr(ccxt, exchange)() for exchange in self.__exchanges]
        self.__load_markets_all(message)

    def __load_markets_all(self, message) -> NoReturn:
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
                                           f'\nВыполнено {round(i / len(self.__exchanges_obj) * 100)}%')
        bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        bot.delete_message(chat_id=message.chat.id, message_id=invoke.message_id)

    def universe_fee_calculation(self, exchange, symbol: str, option: str, price: float) \
            -> dict[str, float]:
        try:
            if option not in ('byu', 'sell') and symbol not in exchange.symbols:
                raise ValueError
            date = exchange.calculate_fee(symbol=symbol,
                                          type='limit',
                                          side=option,
                                          amount=1,
                                          price=price)
            return {
                'cost': float(date['cost']),
                'fee': float(date['rate']),
                'fee_cost': price - float(date['cost'])
            }
        except Exception as ex:
            print(ex)
            self.__errors['fee'] = ex

    @property
    def min_profit(self) -> int:
        return self.__min_profit

    @property
    def errors(self) -> dict[str, str]:
        return self.__errors

    @property
    def exchanges_objects(self):
        return self.__exchanges_obj

    @property
    def exchanges(self) -> list:
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
        self._best = {'bid': {'id': '', 'value': 0.0, 'link': '', 'fee': 0.0},
                      'ask': {'id': '', 'value': 0.0, 'link': '', 'fee': 0.0},
                      'symbol': '',
                      'spread': 0.0,
                      'mount': 0.0,
                      'excnages': self._exchanges,
                      'total': 0}
        self._working_directory = dict()

    def _counter(self, sym, exch):
        best = {sym: {'ask': 0, 'ask_exc': exch[0],
                      'bid': 0, 'bid_exc': exch[0],
                      'ask_lim': 0.0, 'ask_link': '',
                      'bid_lim': 0.0, 'bid_link': '',
                      'СПРЕД': 0.0}}
        for exchange in exch:
            try:
                orderbook = exchange.fetch_order_book(sym)
                bid, bid_mount = orderbook['bids'][0]
                ask, ask_mount = orderbook['asks'][0]
                best[sym]['mount'] = min(ask_mount, bid_mount)
                if best[sym]['ask'] == 0 or best[sym]['ask'] > ask:
                    best[sym]['ask'] = ask
                    best[sym]['ask_exc'] = exchange
                    best[sym]['ask_lim'] = ask_mount
                    best[sym]['ask_link'] = exchange.links['www']
                if best[sym]['bid'] == 0 or best[sym]['bid'] < bid:
                    best[sym]['bid'] = bid
                    best[sym]['bid_exc'] = exchange
                    best[sym]['bid_lim'] = bid_mount
                    best[sym]['bid_link'] = exchange.links['www']
            except Exception as exception: # noqa
                pass

        min_v = min(best[sym]['bid_lim'], best[sym]['ask_lim'])
        ask_with_fee = super().universe_fee_calculation(exchange=best[sym]['ask_exc'],
                                                        symbol=sym,
                                                        option='buy',
                                                        price=best[sym]['ask'])
        bid_with_fee = super().universe_fee_calculation(exchange=best[sym]['bid_exc'],
                                                        symbol=sym,
                                                        option='sell',
                                                        price=best[sym]['bid'])
        spread = round(bid_with_fee['fee_cost'] - ask_with_fee['fee_cost'], 5)
        best[sym]['СПРЕД'] = spread

        if spread > 0 and spread > self._best['spread'] and min_v > 0.1 \
                and best[sym]['ask'] > 0.01 \
                and best[sym]['bid'] > 0.01 \
                and spread > 0.1 \
                and ask_with_fee['fee'] > 0.0 \
                and bid_with_fee['fee'] > 0.0 \
                and spread * min_v > super().min_profit:
            self._best['symbol'] = sym
            self._best['ask']['id'] = str(best[sym]['ask_exc'])
            self._best['ask']['fee'] = ask_with_fee['cost']
            self._best['ask']['value'] = best[sym]['ask']  # buy
            self._best['ask']['link'] = best[sym]['ask_link']
            self._best['bid']['id'] = str(best[sym]['bid_exc'])
            self._best['bid']['value'] = best[sym]['bid']  # sell
            self._best['bid']['fee'] = bid_with_fee['cost']
            self._best['bid']['link'] = best[sym]['bid_link']
            self._best['spread'] = spread
            self._best['mount'] = min_v

    def get_best_offer(self):
        for exchange in self._exchanges_object:
            try:
                pairs = list(filter(lambda sym: sym.endswith('/USDT'), exchange.symbols))
                for pair in pairs:
                    if pair not in self._working_directory.keys():
                        self._working_directory[pair] = [exchange]
                    else:
                        self._working_directory[pair].append(exchange)
            except Exception as ex: # noqa
                pass

        for key, value in list(self._working_directory.items()):
            if len(value) < 2:
                del self._working_directory[key]

        start = bot.send_message(chat_id=self._chat_id, text=f'Обрабатываем пары..')
        for i, (symbol, exchanges) in enumerate(self._working_directory.items()):
            Thread(target=self._counter, args=(symbol, exchanges)).start()
            if i % 10 == 0:
                time.sleep(0.5)
                bot.edit_message_text(message_id=start.message_id,
                                      chat_id=self._chat_id,
                                      text=f'Обработано {i} криптопар')
            self._best['total'] = i
        time.sleep(3)
        bot.delete_message(message_id=start.message_id, chat_id=self._chat_id)
        return self._best
