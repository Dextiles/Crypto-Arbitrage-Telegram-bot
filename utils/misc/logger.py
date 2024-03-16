from datetime import datetime
from config_data.configuration import DATE, TIME, Y
from telebot.types import Message  # noqa
from database import userdata_controller as bd_controller
from utils.misc.path_worker import create_folder_if_not_exists


class Logger:
    def __init__(self, message: Message):
        self.__current_user = bd_controller.get(message)

    def log_exception(self, error: Exception, func_name: str, handler_name: str):
        path = f'logs/errors_logs/{datetime.now().strftime(Y)}'
        create_folder_if_not_exists(path)
        with open(f'{path}/{datetime.now().strftime(DATE)}.log', 'a', encoding='utf-8') as file:
            file.write(f'{datetime.now().strftime(TIME)}--'
                       f'{self.__current_user.username}--'
                       f'id{self.__current_user.user_id}--'
                       f'/{handler_name}--'
                       f'{error}--'
                       f'{func_name}\n')

    def log_activity(self, handler_name: str):
        path = f'logs/activity_logs/{datetime.now().strftime(Y)}'
        create_folder_if_not_exists(path)
        with open(f'{path}/{datetime.now().strftime(DATE)}.log', 'a', encoding='utf-8') as file:
            file.write(f'{datetime.now().strftime(TIME)}--'
                       f'{self.__current_user.username}--'
                       f'id{self.__current_user.user_id}--'
                       f'/{handler_name}\n')
