import os
from dotenv import load_dotenv, find_dotenv


if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
DEFAULT_COMMANDS = (
    ("start", "Начать работу"),
    ("help", "Документация по использованию"),
    ("info", "Информация о текущем пользователе"),
    ("arbitrage", "Инструмент для арбитража критовалют"),
    ("developer", "Информация о разработчике")
)
DATE_FORMAT = "%d.%m.%Y"
TIME_FORMAT = "%H:%M:%S"
DATE_FORMAT_FULL = "%d.%m.%Y, %H:%M:%S"
ADDRESS_db = 'database/userdata.sql'
STATES_db = 'database/userstates.vdb'
ROUND_VALUE = 5
