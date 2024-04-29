import time
import ccxt
from loader import bot
from telebot.types import Message, ReplyKeyboardRemove  # noqa
from typing import NoReturn
from telebot import types as btn  # noqa
from threading import Thread
import json
from database import userdata_controller as db_controller
from utils.misc.logger import Logger


class Exchanges:
    def __init__(self, message: Message) -> NoReturn:
        """
        Initializes the class instance with the given message.

        Parameters:
            message (Message): The message object containing the user information.

        Returns:
            NoReturn: This function does not return anything.
        """
        self._logger = Logger(message)
        self.__current_user = db_controller.get(message)
        self.__exchanges = json.loads(self.__current_user.work_exchanges)
        self.__min_profit = self.__current_user.default_profit
        self.__bad_list_values = json.loads(self.__current_user.bad_list_currency)
        self.__exchanges_obj = [getattr(ccxt, exchange)() for exchange in self.__exchanges]
        self.__load_markets_all(message)

    def __load_markets_all(self, message: Message) -> NoReturn:
        """
        Loads all markets for all exchanges.
        Args:
            message (Message): The message object containing the chat ID.
        Returns:
            NoReturn: This function does not return anything.
        """
        invoke = bot.send_message(message.chat.id, '\U0001F554 Подождите, идет загрузка бирж...\n'
                                                   'Пока можете перекусить.. \U0001F355',
                                  reply_markup=ReplyKeyboardRemove())
        thread_objects = list()
        for exchange in [exchange for exchange in self.__exchanges_obj if exchange.has['fetchMarkets']]:
            try:
                thread_obj = Thread(target=exchange.load_markets)
                thread_objects.append(thread_obj)
                thread_obj.start()
            except Exception as ex:
                self._logger.log_exception(error=ex, func_name='__load_markets_all', handler_name='/arbitrage')
        for thread_obj in thread_objects:
            try:
                thread_obj.join()
            except Exception as ex:
                self._logger.log_exception(error=ex, func_name='__load_markets_all', handler_name='/arbitrage')
        bot.delete_message(invoke.chat.id, invoke.message_id)

    def universe_fee_calculation(self, exchange, symbol: str, option: str, price: float) \
            -> dict[str, float]:
        """
        Calculates the fee for a given symbol and price using the specified exchange.

        Args:
            exchange (Exchange): The exchange object used to calculate the fee.
            symbol (str): The symbol for which the fee is being calculated.
            option (str): The option type, either 'buy' or 'sell'.
            price (float): The price at which the fee is being calculated.

        Returns:
            dict[str, float]: A dictionary containing the cost, fee, and fee cost.

        Raises:
            ValueError: If the option is neither 'buy' nor 'sell' and the symbol is not in the exchange's symbols.

        """
        try:
            if option not in ('byu', 'sell') and symbol not in exchange.symbols:
                raise ValueError(f'Exchange {exchange.id} does not support symbol {symbol}.')
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
            self._logger.log_exception(error=ex, func_name='universe_fee_calculation', handler_name='arbitrage')

    @property
    def min_profit(self) -> int:
        return self.__min_profit

    @property
    def exchanges_objects(self):
        return self.__exchanges_obj

    @property
    def exchanges(self) -> list:
        return self.__exchanges

    @property
    def bad_list_values(self) -> list:
        return self.__bad_list_values


class BestOffer(Exchanges):
    def __init__(self, message: Message) -> NoReturn:
        """
        Initializes the class instance with the given message.

        Args:
            message (Message): The message object containing information about the chat.

        Returns:
            None
        """
        self._logger = Logger(message)
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

    def _counter(self, sym: str, exchanges: list) -> NoReturn:
        """
        This function is a private method that calculates the best bid and ask prices for a given symbol and exchange.

        Parameters:
            sym (str): The symbol to calculate the best prices for.
            exchanges (list): A list of exchanges to fetch the order book from.

        Returns:
            None

        Raises:
            None
        """
        best = {sym: {'ask': 0, 'ask_exc': exchanges[0],
                      'bid': 0, 'bid_exc': exchanges[0],
                      'ask_lim': 0.0, 'ask_link': '',
                      'bid_lim': 0.0, 'bid_link': '',
                      'СПРЕД': 0.0}}
        for exchange in exchanges:
            try:
                orderbook = exchange.fetch_order_book(sym)
                bid, bid_mount = orderbook['bids'][0]
                ask, ask_mount = orderbook['asks'][0]
                best[sym]['mount'] = min(ask_mount, bid_mount)
                if best[sym]['ask'] == 0 or best[sym]['ask'] > ask:
                    best[sym]['ask'] = ask
                    best[sym]['ask_exc'] = exchange
                    best[sym]['ask_lim'] = ask_mount
                    best[sym]['ask_link'] = exchange.urls['www']
                if best[sym]['bid'] == 0 or best[sym]['bid'] < bid:
                    best[sym]['bid'] = bid
                    best[sym]['bid_exc'] = exchange
                    best[sym]['bid_lim'] = bid_mount
                    best[sym]['bid_link'] = exchange.urls['www']
            except Exception as exception:
                self._logger.log_exception(error=exception, func_name='_counter', handler_name='arbitrage')

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
                and spread > 0.5 \
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

    def get_best_offer(self) -> NoReturn:
        """
        Retrieves the best offer for each cryptocurrency pair traded on supported exchanges.

        This function iterates through each exchange object and filters the symbol
        list to only include pairs that end with '/USDT'.
        For each pair, it checks if it already exists in the working directory. If not, it adds
        the exchange to the pair's list of exchanges.
        If the pair already exists, it appends the exchange to the existing list.

        If any exception occurs during the process, it logs the exception using the logger.

        After iterating through all exchanges and pairs, the function removes any pairs that have less than 2 exchanges.

        It then initializes a list of thread objects and sends a message to the chat indicating that pairs are being
        processed.

        For each pair in the working directory, it checks if the pair's cryptocurrency is not in the bad list values and
        if the symbol's name is not in the bad list values.
        If both conditions are met, it creates a new thread and starts it to perform the counter calculation.
        Every 10 pairs, it sleeps for 0.1 seconds and updates the message with the number of processed
        cryptopairs.

        After all threads have completed, it deletes the initial message.
        """
        for exchange in self._exchanges_object:
            try:
                pairs = list(filter(lambda sym: sym.endswith('/USDT'), exchange.symbols))
                for pair in pairs:
                    if pair not in self._working_directory.keys():
                        self._working_directory[pair] = [exchange]
                    else:
                        self._working_directory[pair].append(exchange)
            except Exception as ex:
                self._logger.log_exception(error=ex, func_name='get_best_offer', handler_name='arbitrage')

        for key, value in list(self._working_directory.items()):
            if len(value) < 2:
                del self._working_directory[key]

        thread_objects = list()
        start = bot.send_message(chat_id=self._chat_id, text=f'\U0000231B Обрабатываем пары..')
        for i, (symbol, exchanges) in enumerate(self._working_directory.items()):
            if symbol.split('/USDT')[0] not in super().bad_list_values:  # + сюда условие - торгуемые криптовалюты
                thread = Thread(target=self._counter, args=(symbol, exchanges))  # запуск вычисления
                thread_objects.append(thread)
                thread.start()
                if i % 10 == 0:
                    time.sleep(0.1)
                    bot.edit_message_text(message_id=start.message_id,
                                          chat_id=self._chat_id,
                                          text=f'\U0000231B Обработано {i} криптопар')
            self._best['total'] = i
        for thread in thread_objects:
            thread.join()
        bot.delete_message(message_id=start.message_id, chat_id=self._chat_id)
        return self._best
