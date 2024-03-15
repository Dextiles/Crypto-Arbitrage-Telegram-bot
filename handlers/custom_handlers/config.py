from telebot.types import Message, ReplyKeyboardRemove  # noqa
from loader import bot
from datetime import datetime
from config_data.configuration import DATE_FORMAT_FULL, DATE_FORMAT_IN
import json
from database import userdata_controller as bd_controller
from database import userdata_view as bd_view
from keyboards.reply import config_replies as reply
from states.userstates.bot_states import UserSettings
from database.default_values_config.default_getter import GetDefaultValues
from fastnumbers import isfloat
from utils.misc.crypto_instruments.get_actual_symbols import get_actual_symbols


@bot.message_handler(commands=["config"])
def bot_info(message: Message):
    """
    Handles the 'config' command message, retrieves user information, and sends a message with user details,
    working exchanges list, blacklisted currencies, default profit, and last request time. Updates the bot state
    and last request time in the database.

    Args:
        message (Message): The message object containing the command information.

    Returns:
        None
    """
    bd_controller.create(message)
    current_user = bd_controller.get(message)
    bad_list_exchanges = bd_view.ConfigView(message).show_currency_in_black_list()
    bot.send_message(message.chat.id,
                     f'{current_user.username}, дата регистрации в проекте: '
                     f'{datetime.strftime(current_user.reg_date, DATE_FORMAT_FULL)}\n\n'
                     f'{bd_view.ConfigView(message).show_working_exchanges_list()}\n'
                     f'{bad_list_exchanges}\n'
                     f'Ваш установленный профит по арбиртражу: {current_user.default_profit} USDT\n\n'
                     f'Дата последнего запроса на сервисе:\n'
                     f'{datetime.strftime(current_user.last_request, DATE_FORMAT_IN)}',
                     reply_markup=reply.get_start_config_reply())
    bot.set_state(message.chat.id, UserSettings.Start, message.chat.id)
    bd_controller.update_last_request_time(message)


@bot.message_handler(func=lambda message: message.text == 'Изменить настройки', state=UserSettings.Start)
def start_config(message: Message):
    """
    A function that handles the start of the configuration process for the user settings.

    Parameters:
    - message: Message object containing information from the user

    Returns:
    - None
    """
    bd_controller.update_last_request_time(message)
    bot.send_message(message.chat.id, 'Выберите, что вы хотите изменить', reply_markup=reply.get_options_to_config_button())
    bot.set_state(message.chat.id, UserSettings.Choose_what_to_change, message.chat.id)


@bot.message_handler(func=lambda message: message.text == 'Выход',
                     state=UserSettings.Choose_what_to_change)
def exit_config(message: Message):
    """
    A function to handle exiting configuration settings.

    Parameters:
    - message (Message): The message object triggering the function.

    Returns:
    - None
    """
    bd_controller.update_last_request_time(message)
    bot.send_message(message.chat.id, 'Вы вышли из настройки\n/help - для просмотра доступных команд',
                     reply_markup=ReplyKeyboardRemove())
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(func=lambda message: message.text == 'Криптовалюты', state=UserSettings.Choose_what_to_change)
def choose_what_to_change(message: Message):
    """
    A handler for choosing what to change in the user settings, based on the message text.
    Takes a message of type Message as input.
    """
    bd_controller.update_last_request_time(message)
    get_actual_symbols(message)
    bot.send_message(message.chat.id, f'Напишите код криптовалюты, '
                                      f'которую хотите добавить в черный список (исключить из черного списка)\n'
                                      f'{bd_view.ConfigView(message).show_currency_in_black_list()}',
                     reply_markup=reply.get_go_exit_or_clear_buttons())
    bot.set_state(message.chat.id, UserSettings.CryptoCurrency, message.chat.id)


@bot.message_handler(func=lambda message: message.text not in ['Выход', 'Очистить черный список'],
                     state=UserSettings.CryptoCurrency)
def cryptocurrency_configuration(message: Message):
    """
    A function to handle cryptocurrency configuration based on user input.
    Updates the last request time, processes user input to uppercase,
    manages the list of work symbols and bad list currency, and sends
    appropriate messages based on the input provided.
    """
    bd_controller.update_last_request_time(message)
    message.text = message.text.upper()
    work_symbols = json.loads(bd_controller.get_common().allowed_symbols)
    bad_list_currency = json.loads(bd_controller.get(message).bad_list_currency)
    if (message.text in work_symbols and
            message.text not in bad_list_currency and
            len(bad_list_currency) < int(GetDefaultValues().max_bad_list_size)):
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
    elif len(bad_list_currency) >= int(GetDefaultValues().max_bad_list_size):
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
    """
    Handles the 'Выход' message when in the UserSettings.CryptoCurrency state.

    Args:
    message (Message): The message object containing the user input.

    Returns:
    None
    """
    bd_controller.update_last_request_time(message)
    bot.send_message(message.chat.id, 'Вы вышли из настройки\n/help - для просмотра доступных команд',
                     reply_markup=ReplyKeyboardRemove())
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(func=lambda message: message.text == 'Очистить черный список', state=UserSettings.CryptoCurrency)
def delete_all_bad_list(message: Message):
    """
    Handles the message for deleting all items from the bad list in the CryptoCurrency state.

    Args:
        message (Message): The message object containing the user's input.

    Returns:
        None
    """
    bd_controller.update_last_request_time(message)
    bd_controller.update(message, bad_list_currency=json.dumps([]))
    bot.send_message(message.chat.id, f'Вы очистили черный список!\n'
                                      f'{bd_view.ConfigView(message).show_currency_in_black_list()}',
                     reply_markup=ReplyKeyboardRemove())
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(func=lambda message: message.text == 'Криптобиржи', state=UserSettings.Choose_what_to_change)
def set_exchanges(message: Message):
    """
    Handles messages with text 'Криптобиржи' while in the state UserSettings.Choose_what_to_change.
    Updates the last request time in the database, sends a message to the chat to select a cryptocurrency exchange, and sets the state to UserSettings.Exchange.

    Parameters:
    message (Message): The message object

    Returns:
    None
    """
    bd_controller.update_last_request_time(message)
    bot.send_message(message.chat.id, 'Выберите криптобиржу',
                     reply_markup=reply.get_exchanges_buttons())
    bot.set_state(message.chat.id, UserSettings.Exchange, message.chat.id)


@bot.message_handler(func=lambda message: message.text in GetDefaultValues().exchanges,
                     state=UserSettings.Exchange)
def set_exchanges(message: Message):
    """
    A handler function for setting exchanges in the user settings.
    It updates the last request time, modifies the user's list of exchanges based on the message text,
    and sends a message to the user with the updated list of working exchanges.
    Parameters:
    - message: Message object containing the user's input.
    Return Type: None
    """
    bd_controller.update_last_request_time(message)
    user_exchanges = json.loads(bd_controller.get(message).work_exchanges)
    if message.text in user_exchanges:
        user_exchanges.remove(message.text)
        bd_controller.update(message, work_exchanges=json.dumps(user_exchanges))
        bot.send_message(message.chat.id, f'Криптобиржа {message.text} исключена из арбитража!\n'
                                          f'{bd_view.ConfigView(message).show_working_exchanges_list()}',
                         reply_markup=reply.get_exchanges_buttons())
    else:
        user_exchanges.append(message.text)
        bd_controller.update(message, work_exchanges=json.dumps(user_exchanges))
        bot.send_message(message.chat.id, f'Криптобиржа {message.text} успешно включена в арбитраж!\n'
                                          f'{bd_view.ConfigView(message).show_working_exchanges_list()}',
                         reply_markup=reply.get_exchanges_buttons())


@bot.message_handler(func=lambda message: message.text == 'Выход', state=UserSettings.Exchange)
def exit_config(message: Message):
    """
    Handles the 'Выход' message in the UserSettings.Exchange state.

    Args:
        message (Message): The message object

    Returns:
        None
    """
    bd_controller.update_last_request_time(message)
    bot.send_message(message.chat.id, 'Вы вышли из настройки\n/help - для просмотра доступных команд',
                     reply_markup=ReplyKeyboardRemove())
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(func=lambda message: message.text == 'Профит', state=UserSettings.Choose_what_to_change)
def choose_profit(message: Message):
    """
    Handles the message with text 'Профит' when the user is in the state of choosing what to change.
    Updates the last request time in the database controller.
    Sends a message to the chat to set the profit, considering that a higher profit reduces the chance of finding a suitable pair.
    Removes the reply keyboard and sets the user state to Profit.
    """
    bd_controller.update_last_request_time(message)
    bot.send_message(message.chat.id, 'Установите профит (учтите, чем больше профит вы установите, '
                                      'тем меньше шанс найти подходящую пару)',
                     reply_markup=ReplyKeyboardRemove())
    bot.set_state(message.chat.id, UserSettings.Profit, message.chat.id)


@bot.message_handler(func=lambda message: isfloat(message.text) or message.text.isdigit(), state=UserSettings.Profit)
def set_profit(message: Message):
    """
    A message handler that sets the profit in the UserSettings for a given message.

    Parameters:
    message (Message): The message object containing the profit information.

    Returns:
    None
    """
    bd_controller.update_last_request_time(message)
    bd_controller.update(message, default_profit=float(message.text))
    bot.send_message(message.chat.id, f'Вы установили профит в {message.text} USDT!\n',
                     reply_markup=ReplyKeyboardRemove())
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(func=lambda message: not isfloat(message.text) or not message.text.isdigit(), state=UserSettings.Profit)
def error_profit(message: Message):
    """
    A message handler for handling non-digit messages in the Profit state.
    It updates the last request time, then sends a message to the chat with a warning about incorrect input, and provides
    a button for exiting the state.
    """
    bd_controller.update_last_request_time(message)
    bot.send_message(message.chat.id, 'Некорректный ввод, нужно ввести число!', reply_markup=reply.go_exit_button())


@bot.message_handler(func=lambda message: message.text == 'Выход', state=UserSettings.Profit)
def exit_config(message: Message):
    """
    A decorator that handles messages with the text 'Выход' while in the 'Profit' state of the UserSettings.
    It updates the last request time in the database, sends a message to the chat indicating the user exited the settings,
    removes the reply keyboard, and deletes the state of the user.
    """
    bd_controller.update_last_request_time(message)
    bot.send_message(message.chat.id, 'Вы вышли из настройки\n/help - для просмотра доступных команд',
                     reply_markup=ReplyKeyboardRemove())
    bot.delete_state(message.from_user.id, message.chat.id)
