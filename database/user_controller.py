import userdata
from vedis import Vedis
from config_data import config
from states.userstates import arbitrage_states


def get_user(user_id: int) -> userdata.Users:
    """
    Retrieves a user from the database based on the provided user ID.

    Args:
        user_id (int): The ID of the user to retrieve.

    Returns:
        userdata.Users: The user object matching the provided user ID.
    """
    try:
        return userdata.Users.get_or_none(userdata.Users.user_id == user_id)
    except Exception as ex:
        with open('database/error.log', 'a') as log_file:
            log_file.write(str(ex))


def get_current_state(user_id: int):
    """
    Get the current state of a user based on their ID.

    Parameters:
        user_id (int): The ID of the user.

    Returns:
        str: The current state of the user.

    Raises:
        KeyError: If the user ID is not found in the database.
    """
    with Vedis(config.STATES_db) as db:
        try:
            return db[user_id].decode()
        except KeyError:
            return arbitrage_states.DefaultStart.INVOKE.value


def set_state(user_id, value):
    """
    Sets the state of a user in the database.

    Parameters:
        user_id (str): The ID of the user.
        value (str): The value to set for the user's state.

    Returns:
        bool: True if the state was successfully set, False otherwise.
    """
    with Vedis(config.STATES_db) as db:
        try:
            db[user_id] = value
            return True
        except Exception as ex:
            with open('database/error.log', 'a') as log_file:
                log_file.write(str(ex))
            return False
