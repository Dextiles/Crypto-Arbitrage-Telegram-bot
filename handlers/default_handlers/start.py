from telebot.types import Message
from loader import bot
from peewee import *
from database.Users import User


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    try:
        User.create(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
        bot.send_message(message.chat.id, "Добро пожаловать, вы у нас впервые!")
    except IntegrityError:
        bot.send_message(message.chat.id, f'Рад вас снова видеть, {message.from_user.full_name}!'),
