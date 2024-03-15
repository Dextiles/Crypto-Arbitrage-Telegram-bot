import json


def get_data() -> dict:
    """
    Reads and loads data from a JSON file containing default values.
    No parameters.
    Returns the data loaded from the JSON file.
    """
    with open('database/default_values_config/dafault_values.json', 'r', encoding='utf-8') as file:
        return json.load(file)


class GetDefaultValues:
    """
    Initializes the object with default data obtained from the get_data function.
    """
    def __init__(self):
        """
        Initializes the object by setting the default data attribute using the get_data function.
        """
        self.__default_data = get_data()

    @property
    def exchanges(self):
        return self.__default_data['exchanges']

    @property
    def profit(self):
        return self.__default_data['profit']

    @property
    def max_bad_list_size(self):
        return self.__default_data['max_bad_list_size']

