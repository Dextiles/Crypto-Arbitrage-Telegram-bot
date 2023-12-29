from telebot.types import Message  # noqa
from telebot import types  # noqa
from loader import bot
from keyboards.reply import bidaskreplies as stack
from keyboards.inline import crypto_instruments_key as inline
from utils.misc.crypto_instruments import arbitrage
from config_data.config import ROUND_VALUE
from datetime import datetime
from config_data.config import DATE_FORMAT_FULL
from database import userstates_worker
from states.userstates.arbitrage_states import CryptoArbitrageFull


@bot.message_handler(commands=["arbitrage2"])
def start_arbitrage(message: Message):
    bot.send_message(message.chat.id, f'Добро пожаловать в раздел полного арбитража, '
                                      f'мы полностью проанализируем ваши биржи и найдем лучшие связки и предложения',
                     reply_markup=stack.start_reply())
    userstates_worker.set_state(message.chat.id, CryptoArbitrageFull.START_ARBITRAGE.value)


@bot.message_handler(func=lambda message: userstates_worker.get_current_state(message.chat.id) == CryptoArbitrageFull.START_ARBITRAGE.value)
def get_best(message: Message):
    if message.text == 'Начать':
        data = arbitrage.BestOfferFull(message).get_best_offer()
        bot.send_message(message.chat.id, f'Запрос актуален на '
                                          f'{datetime.strftime(datetime.now(), DATE_FORMAT_FULL)}\n\n'
                                          f'Обработано {data["total"]} криптопар на избранных биржах\n'
                                          f'(/info - просмотр ваших настроек)\n\n'
                                          f'Выгодная свзка: {data["symbol"]}\n'
                                          f'Купить: {data["ask"]["id"]}, цена '
                                          f'{round(data["ask"]["value"], ROUND_VALUE)} USDT\n'
                                          f'(Комиссия в {round(data["ask"]["fee"], ROUND_VALUE)})\n'
                                          f'Продать: {data["bid"]["id"]}, цена '
                                          f'{round(data["bid"]["value"], ROUND_VALUE)} USDT\n'
                                          f'(Комиссия в {round(data["bid"]["fee"], ROUND_VALUE)})\n\n'
                                          f'Чистый спред:\n=> {data["spread"]} USDT <=\n\n'
                                          f'Валюта доступная для операции: '
                                          f'{round(data["mount"], ROUND_VALUE)}\n'
                                          f'Полный профит с {round(data["ask"]["value"] * data["mount"], 5)} USDT:\n'
                                          f'=> {round(data["mount"] * data["spread"], ROUND_VALUE)} USDT <=\n')
    elif message.text == 'Выход':
        bot.send_message(message.chat.id, f'Спасибо за использование сервиса!',
                         reply_markup=types.ReplyKeyboardRemove())
        return
    return
