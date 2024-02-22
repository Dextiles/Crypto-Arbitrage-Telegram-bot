from telebot.types import Message # noqa
from loader import bot
from peewee import *
from database.userdata import Users
from telebot import types # noqa


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    """
    Handles the start command for the bot. Creates a new user, or sends a welcome
    back message if the user already exists.
    Parameters:
    - message: Message - the message object triggering the command
    """
    invoke_text = 'Это сервис по арбитражу криптовалют!'
    try:
        Users.create(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
        bot.send_message(message.chat.id, f"Добро пожаловать, вы у нас впервые!\n"
                                          f"{invoke_text}",
                         reply_markup=types.ReplyKeyboardRemove())
    except IntegrityError:
        bot.send_message(message.chat.id, f'Рад вас снова видеть, {message.from_user.full_name}\n'
                                          f'{invoke_text}!',
                         reply_markup=types.ReplyKeyboardRemove())
    finally:
        pass
