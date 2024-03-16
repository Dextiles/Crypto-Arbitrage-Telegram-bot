from telebot.types import Message # noqa
from config_data.configuration import DEFAULT_COMMANDS
from loader import bot
from database import userdata_controller as bd_controller
from utils.misc.logger import Logger


@bot.message_handler(commands=["help"])
def bot_help(message: Message):
    """
    Handles the 'help' command by sending a list of available commands and their descriptions as a reply to the user's message.

    Parameters:
    - message: Message object representing the message sent by the user.

    Returns:
    - None
    """
    Logger(message).log_activity("help")
    bd_controller.create(message)
    text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, "\n".join(text))
    bd_controller.update_last_request_time(message)
