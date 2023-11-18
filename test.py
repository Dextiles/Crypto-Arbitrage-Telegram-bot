import time

import ccxt
from datetime import datetime
import asyncio
from threading import Thread

atr = dict()


async def main():
    excanges_list = ['binance',
                     'bybit', 'okx', 'kucoin',
                     'kraken', 'bitstamp', 'bitfinex',
                     'upbit', 'gateio', 'gemini',
                     'coinbase', 'cryptocom']
    start = datetime.now()
    excanges = [getattr(ccxt, exchange)() for exchange in excanges_list]
    for i, exchange in enumerate(excanges):
        print(f'Компаную биржу {exchange.id}, {round(i / len(excanges) * 100)}%')
        try:
            exchange.load_markets()
            pairs = list(filter(lambda sym: sym.endswith('/USDT'), exchange.symbols))
            for pair in pairs:
                if pair not in atr.keys():
                    atr[pair] = [exchange]
                else:
                    atr[pair].append(exchange)
        except Exception as ex:
            print(ex)
    for key, value in list(atr.items()):
        if len(value) < 2:
            del atr[key]

    for i, (symbol, exchanges) in enumerate(atr.items()):
        Thread(target=counter, args=(i, symbol, exchanges)).start()
        if i % 10 == 0:
            time.sleep(1)

    end = datetime.now() - start
    time.sleep(3)

    print(f'Лучшее предложение: {max_spread}')
    print(f'Время обработки составило: {end}, обработано {len(atr.values())} криптопар')


max_spread = {'Связка': '', 'Купить': '', 'Продать': '', 'Спред': 0.0}


def counter(i_num, sym, exch):
    best = {sym: {'ask': 0, 'ask_exc': '', 'bid': 0, 'bid_exc': '', 'СПРЕД': 0}}
    print(f'Анализирую связку {sym}, {round(i_num / len(atr.keys()) * 100, 1)}%')
    for exchange in exch:
        try:
            orderbook = exchange.fetch_order_book(sym)
            bid = orderbook['bids'][0][0]
            ask = orderbook['asks'][0][0]
            if best[sym]['ask'] == 0 or best[sym]['ask'] > ask:
                best[sym]['ask'] = ask
                best[sym]['ask_exc'] = exchange.id
            if best[sym]['bid'] == 0 or best[sym]['bid'] < bid:
                best[sym]['bid'] = bid
                best[sym]['bid_exc'] = exchange.id
        except Exception as exception:
            print(exception)
    spread = round(best[sym]['bid'] - best[sym]['ask'], 5)
    best[sym]['СПРЕД'] = spread

    if spread > 0 and spread > max_spread['Спред']:
        max_spread['Связка'] = sym
        max_spread['Купить'] = best[sym]['ask_exc']
        max_spread['Продать'] = best[sym]['bid_exc']
        max_spread['Спред'] = best[sym]['СПРЕД']


asyncio.run(main())
