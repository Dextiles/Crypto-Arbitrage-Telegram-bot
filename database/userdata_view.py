from database import userdata_controller
from telebot.types import Message  # noqa
import json


class ConfigView:
    def __init__(self, message: Message):
        """
        Initialize the class with the provided message.

        Parameters:
            message (Message): The message object to initialize the class with.
        """
        self._current_user = userdata_controller.get(message)

    def show_currency_in_black_list(self) -> str:
        """
        Generate a string containing the cryptocurrencies in the user's black list.
        Returns:
            str: A string displaying the cryptocurrencies in the black list.
        """
        if len(json.loads(self._current_user.bad_list_currency)) == 0:
            bad_list_cur = 'У вас нет криптовалют в черном списке!\n'
        else:
            list_symbols = json.loads(self._current_user.bad_list_currency)
            bad_list_cur = (f'Криптовалюты в черном списке (Всего: {len(list_symbols)} из 40):\n'
                            f'{", ".join(*[list_symbols])}\n\n')
        return bad_list_cur

    def show_working_exchanges_list(self) -> str:
        """
        A function that shows the list of working exchanges for the current user.
        Returns a string containing the list of exchanges or a message if there are no exchanges.
        Returns:
            str: A string containing the list of exchanges
        """
        if len(json.loads(self._current_user.work_exchanges)) == 0:
            exchanges = 'У вас нет рабочих криптобирж!\n'
        else:
            exchanges = (
                f'Ваши рабочие криптобиржы (Всего: {len(json.loads(self._current_user.work_exchanges))} из 9):\n'
                f'{", ".join(json.loads(self._current_user.work_exchanges))}\n\n')
        return exchanges

