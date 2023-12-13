from telebot import TeleBot # noqa
from telebot.storage import StateMemoryStorage # noqa
from config_data import config

storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
