from telebot.types import Message  # noqa
from telebot import types  # noqa
from loader import bot
from keyboards.reply import arbitrage_replies as stack
from keyboards.inline import crypto_instruments_btns as inline  # noqa
from utils.misc.crypto_instruments import arbitrage
from config_data.configuration import ROUND_VALUE
from datetime import datetime
from config_data.configuration import DATE_FORMAT_FULL
import states.userstates.bot_states as Arbitrage  # noqa
from states.userstates import bot_states as states
from database import userdata_controller as bd_controller
from utils.misc.logger import Logger
from typing import NoReturn


@bot.message_handler(commands=["arbitrage"])
def start_arbitrage(message: Message) -> NoReturn:
    """
    A function to handle the 'arbitrage' command message.
    Takes a Message object as a parameter.
    Sends a welcome message about cryptocurrency arbitrage to the chat and
    sets the user's state to the start of the arbitrage process.
    """
    bd_controller.create(message)
    Logger(message).log_activity('arbitrage')
    bd_controller.update_last_request_time(message)
    bot.send_message(message.chat.id, f'\U0001F310 Добро пожаловать в арбитраж криптовалют!\n'
                                      f'Бот полностью проанализируем ваши биржи и найдем лучшие связки и предложения\n\n'
                                      f'Ключ к успеху: Правильно настроенный бот: Правильно настроенный бот - '
                                      f'богатство в доме\n\n'
                                      f'Перед началом работы, рекомендуем установить настройки - /config. \n\n',
                     reply_markup=stack.create_start_reply(), parse_mode='Markdown')
    bot.set_state(message.from_user.id, states.Arbitrage.Start, message.chat.id)


@bot.message_handler(func=lambda message: message.text.startswith('Начать'), state=states.Arbitrage.Start)
def get_best(message: Message) -> NoReturn:
    """
    Message handler for starting the process. Retrieves and sends the best offer for arbitrage trading,
    including various details such as datetime, total number of crypto pairs on selected exchanges, best symbol,
    buy and sell details, net spread, available currency for operation, and total profit.
    Removes the reply keyboard and deletes the state after execution.
    """
    bd_controller.update_last_request_time(message)
    arbitrage_data = arbitrage.BestOffer(message).get_best_offer()
    bot.send_message(message.chat.id,
                     f'Запрос актуален на \U0001F554 '
                     f'{datetime.strftime(datetime.now(), DATE_FORMAT_FULL)}\n\n'
                     f'\U0001F4CC Обработано {arbitrage_data["total"]} криптопар на избранных биржах '
                     f'(/config - просмотр ваших настроек)\n\n'
                     f'\U00002757 Выгодная связка: {arbitrage_data["symbol"]} \U00002757\n'
                     f'\U00002795 Купить: {arbitrage_data["ask"]["id"]}, цена '
                     f'{round(arbitrage_data["ask"]["value"], ROUND_VALUE)} USDT\n'
                     f'(Комиссия в {round(arbitrage_data["ask"]["fee"], ROUND_VALUE)})\n'
                     f'\U00002796 Продать: {arbitrage_data["bid"]["id"]}, цена '
                     f'{round(arbitrage_data["bid"]["value"], ROUND_VALUE)} USDT\n'
                     f'(Комиссия в {round(arbitrage_data["bid"]["fee"], ROUND_VALUE)})\n\n'
                     f'Чистый спред:\n\U0001F4B2 {arbitrage_data["spread"]} USDT\n\n'
                     f'Валюта доступная для операции: '
                     f'{round(arbitrage_data["mount"], ROUND_VALUE)}\n'
                     f'Полный профит с {round(arbitrage_data["ask"]["value"] * arbitrage_data["mount"], 5)} '
                     f'USDT:\n'
                     f'\U0001F4B5 {round(arbitrage_data["mount"] * arbitrage_data["spread"], ROUND_VALUE)} USDT ',
                     reply_markup=inline.get_exchanges_links(bid_link=arbitrage_data["bid"]["link"],
                                                             ask_link=arbitrage_data["ask"]["link"],
                                                             ask_id=arbitrage_data["ask"]["id"],
                                                             bid_id=arbitrage_data["bid"]["id"],
                                                             message=message))
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(func=lambda message: message.text.startswith('Выход'), state=states.Arbitrage.Start)
def exit_arbitrage(message: Message) -> NoReturn:
    """
    A handler for exiting the arbitrage process when the user sends the message 'Выход'.

    Args:
    message (Message): The message object containing the user's input.

    Returns:
    None
    """
    bd_controller.update_last_request_time(message)
    bot.send_message(message.chat.id, 'Хорошего дня!\n'
                                      '/help - документация', reply_markup=types.ReplyKeyboardRemove())
    bot.delete_state(message.from_user.id, message.chat.id)

