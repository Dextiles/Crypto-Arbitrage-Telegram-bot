from telebot.types import Message
from loader import bot
from peewee import *
from database.userdata import Users
from telebot import types


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    invoke_text = ('Это сервис криптоаналитики. Мы представляем следующие инструменты:\n'
                   '1. Арбитраж криптовалют (ищет наиболее выгодные предложения по '
                   'заданным рентабельным валютным связкам на установленных криптобиржах)\n'
                   'В РАЗРАБОТКЕ:\n'
                   '2. Сквозная аналитика (отслеживание изменений в реальном времени)\n'
                   '3. Прогнозирование (использование компьютерных алгоритмов и'
                   ' стратегий для прогнозирования роста или падения криптовалют, уведомление в реальном времени)\n'
                   '4. Просмотр OHLCV в виде графика тиков\n'
                   '5. Просмотр информации о конкретной криптовалюте')
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
