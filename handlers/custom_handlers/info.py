from telebot.types import Message
from loader import bot
from database.userdata import Users
from datetime import datetime
from config_data.config import DATE_FORMAT_FULL
import json


@bot.message_handler(commands=["info"])
def bot_info(message: Message):
    current_user = Users.get_or_none(Users.user_id == message.from_user.id)
    if current_user.bad_list_currency is None:
        bad_list_exchanges = 'У вас нет криптовалют в черном списке!'
    else:
        bad_list_exchanges = (f'Криптовалюты в черном списке:\n'
                              f'{", ".join(json.loads(current_user.bad_list_currency))}')

    bot.send_message(message.chat.id, f'{current_user.username}, дата регистрации в проекте: '
                                      f'{datetime.strftime(current_user.reg_date, DATE_FORMAT_FULL)}\n\n'
                                      f'Ваши рабочие криптобиржы: \n'
                                      f'{", ".join(json.loads(current_user.work_exchanges))}\n\n'
                                      f'{bad_list_exchanges}')
