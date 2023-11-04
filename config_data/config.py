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
    ("info", "информация о текущем пользователе"),
    ("arbitrage", "Инструменты для арбитража крипты"),
    ("developer", "Информация о разработчике")
)
DATE_FORMAT = "%d.%m.%Y"
TIME_FORMAT = "%H:%M:%S"
DATE_FORMAT_FULL = "%Y.%m.%d (%H:%M:%S)"
ADDRESS_db = 'database/userdata.sql'
