from telebot import TeleBot # noqa
from telebot.storage import StateMemoryStorage # noqa
from config_data import configuration


storage = StateMemoryStorage()
bot = TeleBot(token=configuration.BOT_TOKEN, state_storage=storage)
