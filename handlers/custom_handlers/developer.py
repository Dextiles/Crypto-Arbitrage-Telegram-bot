from telebot.types import Message # noqa
from keyboards.inline import about_developer_btns
from loader import bot
from database import userdata_controller as bd_controller


@bot.message_handler(commands=["developer"])
def about_me(message: Message):
    """
    Handles the 'developer' command to provide information about the service developer.
    Takes a Message object as a parameter.
    Returns None.
    """
    bd_controller.create(message)
    bot.send_message(message.chat.id, '\U0001F464 Разработчик сервиса: Иван Пермяков\n'
                                      'Основной директ, сотрудничество: @Dextiles\n\n',
                     reply_markup=about_developer_btns.get_about_developer_markup())
    bd_controller.update_last_request_time(message)
