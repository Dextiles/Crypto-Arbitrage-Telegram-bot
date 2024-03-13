from telebot.types import Message # noqa
from keyboards.inline import about_developer
from loader import bot


@bot.message_handler(commands=["developer"])
def about_me(message: Message):
    """
    Handles the 'developer' command to provide information about the service developer.
    Takes a Message object as a parameter.
    Returns None.
    """
    bot.send_message(message.chat.id, '\U0001F464 Разработчик сервиса: Иван Пермяков\n'
                                      'Fullstack-разработчик, Веб-дизайнер\n(сайты под ключ, '
                                      'телеграм боты, windows и web приложения)\n'
                                      'Пишу на C#/C++/Python/SQL\n\n'
                                      'Основной директ, сотрудничество: @Dextiles\n\n',
                     reply_markup=about_developer.get_about_developer_markup())
