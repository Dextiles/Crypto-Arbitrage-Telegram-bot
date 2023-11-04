from telebot.types import Message
from loader import bot
from database.Users import User


@bot.message_handler(commands=["info"])
def bot_info(message: Message):
    cur = User.get_or_none(User.user_id == message.from_user.id)

    bot.send_message(message.chat.id, f'Время регистрации в проекте: {cur.reg_date}')
