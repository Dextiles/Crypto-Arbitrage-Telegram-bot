from telebot.types import Message  # noqa
from loader import bot
from database import userdata_controller as bd_controller
from datetime import datetime


@bot.message_handler(state=None)
def bot_echo(message: Message):
    """
    A function that echoes the message without any state or filter.
    Takes a Message object as input.
    """
    bd_controller.create(message)
    bot.reply_to(
        message, "Эхо без состояния или фильтра.\n" f"Сообщение: {message.text}"
    )
    bd_controller.update_last_request_time(message)
