from datetime import datetime
from config_data.configuration import DATE, TIME, Y
from telebot.types import Message  # noqa
from database import userdata_controller as bd_controller
from utils.misc.path_worker import create_folder_if_not_exists
from typing import NoReturn


class Logger:
    def __init__(self, message: Message) -> NoReturn:
        """
        Initialize the class with the provided Message object.

        Parameters:
            message (Message): The Message object to initialize the class with.

        Returns:
            None
        """
        self.__current_user = bd_controller.get(message)

    def log_exception(self, error: Exception, func_name: str, handler_name: str) -> NoReturn:
        """
        Logs an exception to the error log file.

        Parameters:
            error (Exception): The exception to be logged.
            func_name (str): The name of the function where the exception occurred.
            handler_name (str): The name of the handler for the exception.

        Returns:
            None
        """
        path = f'logs/errors_logs/{datetime.now().strftime(Y)}'
        create_folder_if_not_exists(path)
        with open(f'{path}/{datetime.now().strftime(DATE)}.log', 'a', encoding='utf-8') as file:
            file.write(f'{datetime.now().strftime(TIME)}--'
                       f'{self.__current_user.username}--'
                       f'id{self.__current_user.user_id}--'
                       f'/{handler_name}--'
                       f'{error}--'
                       f'{func_name}\n')

    def log_activity(self, handler_name: str) -> NoReturn:
        """
        Logs activity to a specific file in the 'logs/activity_logs' directory with the current timestamp, user information, and the provided handler name.

        Parameters:
            handler_name (str): The name of the handler triggering the activity log.

        Returns:
            None
        """
        path = f'logs/activity_logs/{datetime.now().strftime(Y)}'
        create_folder_if_not_exists(path)
        with open(f'{path}/{datetime.now().strftime(DATE)}.log', 'a', encoding='utf-8') as file:
            file.write(f'{datetime.now().strftime(TIME)}--'
                       f'{self.__current_user.username}--'
                       f'id{self.__current_user.user_id}--'
                       f'/{handler_name}\n')
