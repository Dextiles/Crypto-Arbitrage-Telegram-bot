from telebot.types import Message  # noqa
from loader import bot
from database import userdata_controller as bd_controller
from utils.misc.logger import Logger


@bot.message_handler(state=None)
def bot_echo(message: Message):
    """
    A function that echoes the message without any state or filter.
    Takes a Message object as input.
    """
    Logger(message).log_activity("echo")
    bd_controller.create(message)
    bot.reply_to(
        message, "Команда не распознана. Пожалуйста, введите /help для получения списка команд.",
    )
    bd_controller.update_last_request_time(message)
