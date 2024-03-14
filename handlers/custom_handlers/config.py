from telebot.types import Message, ReplyKeyboardRemove  # noqa
from loader import bot
from datetime import datetime
from config_data.configuration import DATE_FORMAT_FULL, DATE_FORMAT_IN
import json
from database import userdata_controller as bd_controller
from database import userdata_view as bd_view
from keyboards.reply import config_replies as reply
from states.userstates.bot_states import UserSettings
from utils.misc.crypto_instruments.get_actual_symbols import get_actual_symbols


@bot.message_handler(commands=["config"])
def bot_info(message: Message):
    current_user = bd_controller.get(message)
    bad_list_exchanges = bd_view.ConfigView(message).show_currency_in_black_list()
    exchanges = json.loads(current_user.work_exchanges)
    bot.send_message(message.chat.id,
                     f'{current_user.username}, дата регистрации в проекте: '
                     f'{datetime.strftime(current_user.reg_date, DATE_FORMAT_FULL)}\n\n'
                     f'Ваши рабочие криптобиржы (Всего {len(exchanges)} из 9): \n'
                     f'{", ".join(exchanges)}\n'
                     f'{bad_list_exchanges}\n'
                     f'Ваш установленный профит по арбиртражу: {current_user.default_profit}\n\n'
                     f'Дата последнего запроса на сервисе:\n'
                     f'{datetime.strftime(current_user.last_request, DATE_FORMAT_IN)}',
                     reply_markup=reply.get_start_config_reply())
    bot.set_state(message.chat.id, UserSettings.Start, message.chat.id)
    bd_controller.update_last_request_time(message)


@bot.message_handler(func=lambda message: message.text == 'Изменить настройки', state=UserSettings.Start)
def start_config(message: Message):
    bd_controller.update_last_request_time(message)
    bot.send_message(message.chat.id, 'Выберите, что вы хотите изменить', reply_markup=reply.get_options_to_config())
    bot.set_state(message.chat.id, UserSettings.Choose_what_to_change, message.chat.id)


@bot.message_handler(func=lambda message: message.text == 'Выход',
                     state=(UserSettings.Choose_what_to_change, UserSettings.Start))
def exit_config(message: Message):
    bd_controller.update_last_request_time(message)
    bot.send_message(message.chat.id, 'Вы вышли из настройки\n/help - для просмотра доступных команд',
                     reply_markup=ReplyKeyboardRemove())
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(func=lambda message: message.text == 'Криптовалюты', state=UserSettings.Choose_what_to_change)
def choose_what_to_change(message: Message):
    bd_controller.update_last_request_time(message)
    if bd_controller.is_time_out(message, 24) or len(json.loads(bd_controller.get(message).work_symbols)) == 0:
        invoke = bot.send_message(message.chat.id, f'Подождите, выполняется обновление списка криптовалют...\n'
                                                   f'Данная процедура выполняется раз в сутки, '
                                                   f'последнее обновление: '
                                                   f'{datetime.strftime(bd_controller.get(message).work_symbols_date_analysis, DATE_FORMAT_FULL)}',
                                  reply_markup=ReplyKeyboardRemove())
        symbols = get_actual_symbols(exchanges=json.loads(bd_controller.get(message).work_exchanges))
        bot.delete_message(invoke.chat.id, invoke.message_id)
    else:
        symbols = json.loads(bd_controller.get(message).work_symbols)
    bd_controller.update(message, work_symbols=json.dumps(list(symbols)))
    bot.send_message(message.chat.id, f'Напишите код криптовалюты, '
                                      f'которую хотите добавить в черный список (исключить из черного списка)\n'
                                      f'{bd_view.ConfigView(message).show_currency_in_black_list()}',
                     reply_markup=reply.go_exit_or_clear())
    bot.set_state(message.chat.id, UserSettings.CryptoCurrency, message.chat.id)


@bot.message_handler(func=lambda message: message.text not in ['Выход', 'Очистить черный список'],
                     state=UserSettings.CryptoCurrency)
def cryptocurrency_configuration(message: Message):
    bd_controller.update_last_request_time(message)
    message.text = message.text.upper()
    work_symbols = json.loads(bd_controller.get(message).work_symbols)
    bad_list_currency = json.loads(bd_controller.get(message).bad_list_currency)
    if message.text in work_symbols and message.text not in bad_list_currency and len(bad_list_currency) < 40:
        bad_list_currency.append(message.text)
        bd_controller.update(message, bad_list_currency=json.dumps(bad_list_currency))
        bot.send_message(message.chat.id,
                         f'Валюта {message.text} успешно исключена из арбитража! '
                         f'{bd_view.ConfigView(message).show_currency_in_black_list()}'
                         f'Продолжайте писать коды валют, либо нажмите "Выход"')
    elif message.text in bad_list_currency and message.text in work_symbols:
        bad_list_currency.remove(message.text)
        bd_controller.update(message, bad_list_currency=json.dumps(bad_list_currency))
        bot.send_message(message.chat.id,
                         f'Валюта {message.text} успешно включена в арбитраж!\n'
                         f'{bd_view.ConfigView(message).show_currency_in_black_list()}'
                         f'Продолжайте писать коды валют, либо нажмите "Выход"')
    elif message.text == 'USDT':
        bot.send_message(message.chat.id, f'Вы не можете удалить USDT из арбитража!\n'
                                          f'{bd_view.ConfigView(message).show_currency_in_black_list()}'
                                          f'Пожалуйста, напишите другую валюту, либо нажмите "Выход"')
    elif len(bad_list_currency) >= 40:
        bot.send_message(message.chat.id, f'Достигнут максимальный размер черного списка!\n'
                                          f'{bd_view.ConfigView(message).show_currency_in_black_list()}'
                                          f'Чтобы добавить валюту, сперва освободите место, '
                                          f'удалив другую валюту или очистив черный список соответствующей кнопкой!')
    else:
        bot.send_message(message.chat.id, f'Такой криптовалютой не торгуют на ваших криптобиржах!\n'
                                          f'{bd_view.ConfigView(message).show_currency_in_black_list()}'
                                          f'Пожалуйста, напишите другую валюту, либо нажмите "Выход"')


@bot.message_handler(func=lambda message: message.text == 'Выход', state=UserSettings.CryptoCurrency)
def exit_config(message: Message):
    bd_controller.update_last_request_time(message)
    bot.send_message(message.chat.id, 'Вы вышли из настройки\n/help - для просмотра доступных команд',
                     reply_markup=ReplyKeyboardRemove())
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(func=lambda message: message.text == 'Очистить черный список', state=UserSettings.CryptoCurrency)
def delete_all_bad_list(message: Message):
    bd_controller.update_last_request_time(message)
    bd_controller.update(message, bad_list_currency=json.dumps([]))
    bot.send_message(message.chat.id, f'Вы очистили черный список!\n'
                                      f'{bd_view.ConfigView(message).show_currency_in_black_list()}',
                     reply_markup=ReplyKeyboardRemove())
    bot.delete_state(message.from_user.id, message.chat.id)
