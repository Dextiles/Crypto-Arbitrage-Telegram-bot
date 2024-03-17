from telebot.types import Message  # noqa
from loader import bot
from database import userdata_controller as bd_controller
from telebot import types  # noqa
from config_data.configuration import DATE_FORMAT_IN
from datetime import datetime
from utils.misc.logger import Logger


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    """
    Handles the start command for the bot. Creates a new user, or sends a welcome
    back message if the user already exists.
    Parameters:
    - message: Message - the message object triggering the command
    """
    invoke_text = ('Это сервис по арбитражу криптовалют!'
                   '/help - просмотр списка команд и их описания')
    if bd_controller.create(message):
        bot.send_message(message.chat.id, invoke_text)
    else:
        current_user = bd_controller.get(message)
        bot.send_message(message.chat.id,
                         f'Рад вас снова видеть, {current_user.first_name}!\n'
                         f'Ваш последний запрос был {datetime.strftime(current_user.last_request, DATE_FORMAT_IN)}\n'
                         f'С этого момента многое изменилось!\n\n'
                         f'Забыли команды: /help для просмотра списка команд и их описания')
        bd_controller.update_last_request_time(message)
    Logger(message).log_activity('start')
