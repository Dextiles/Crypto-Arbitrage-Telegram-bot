from telebot.types import Message
from telebot import types
from loader import bot
from keyboards.reply import bidaskreplies as stack
from keyboards.inline import crypto_instruments_key as inline
from utils.misc.crypto_instruments import arbitrage


@bot.message_handler(commands=["arbitrage2"])
def start_arbitrage(message: Message):
    bot.send_message(message.chat.id, f'Добро пожаловать в раздел полного арбитража, '
                                      f'мы полностью проанализируем ваши биржи и найдем лучшие связки и предложения',
                     reply_markup=stack.start_reply())
    bot.register_next_step_handler(message, get_best)


def get_best(message: Message):
    if message.text == 'Начать' or message.text == 'Еще раз':
        data = arbitrage.BestOfferFull(message).get_best_offer()
        bot.send_message(message.chat.id, f'Обработано {data["total"]} криптопар на биржах:\n'
                                          f'{", ".join(data["excnages"])}\n\n'
                                          f'Выгодная свзка: {data["symbol"]}\n'
                                          f'Купить: {data["ask"]["id"]}, цена {data["ask"]["value"]} USDT\n'
                                          f'Продать: {data["bid"]["id"]}, цена {data["bid"]["value"]} USDT\n'
                                          f'Спред: {data["spread"]} USDT')
