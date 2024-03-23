from telebot.types import Message  # noqa
from database import userdata_model
from peewee import *
from datetime import datetime, timedelta
from database.default_values_config.default_getter import GetDefaultValues
import json


def create(message: Message) -> bool:
    """
    Create a user in the database using the information from the message object.

    Args:
        message (Message): The message object containing user information.

    Returns:
        bool: True if the user is successfully created, False if there is an IntegrityError.
    """
    try:
        userdata_model.Users.create(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name)

        userdata_model.WorkDirectory.create(
            work_symbols_date_analysis=None,
        )

    except IntegrityError:
        return False
    else:
        return True


def get(message: Message) -> userdata_model.Users:
    """
    Retrieves user data based on the provided message object.

    Args:
        message (Message): The message object containing user information.

    Returns:
        userdata_model.Users: The user data retrieved based on the provided message.
    """
    try:
        return userdata_model.Users.get_or_none(user_id=message.from_user.id)
    except Exception:
        if create(message):
            return userdata_model.Users.get_or_none(user_id=message.from_user.id)


def get_common() -> userdata_model.WorkDirectory:
    """
    This function returns the common WorkDirectory object.
    """
    return userdata_model.WorkDirectory.get_or_none()


def update_common(**kwargs) -> bool:
    """
    A function that updates a common entity using the provided keyword arguments and returns a boolean indicating success.
    """
    try:
        userdata_model.WorkDirectory.update(**kwargs).execute()
    except Exception:
        return False
    else:
        return True


def update(message: Message, **kwargs) -> bool:
    """
    Update the user object in the database using the message object.

    Args:
        message (Message): The message object containing user information.
        **kwargs: Additional keyword arguments to pass to the update method.

    Returns:
        None
    """
    try:
        userdata_model.Users.update(**kwargs).where(userdata_model.Users.user_id == message.from_user.id).execute()
    except IntegrityError:
        return False
    else:
        return True


def delete(message: Message) -> bool:
    """
    Delete the user object from the database using the message object.

    Args:
        message (Message): The message object containing user information.

    Returns:
        bool: True if the user is successfully deleted, False if there is an IntegrityError.
    """
    try:
        userdata_model.Users.delete().where(userdata_model.Users.user_id == message.from_user.id).execute()
    except Exception:
        return False
    else:
        return True


def update_last_request_time(message: Message) -> bool:
    """
    Update the last request time for the user in the database using the message object.

    Args:
        message (Message): The message object containing user information.

    Returns:
        bool: True if the last request time is successfully updated, False if there is an IntegrityError.
    """
    try:
        update(message, last_request=datetime.now())
    except Exception:
        return False
    else:
        return True


def is_time_out(hours: int) -> bool:
    """
    A function to check if the time for a message is out based on a specified number of hours.

    Args:
        hours (int): The number of hours to compare the message time against.

    Returns:
        bool: True if the message time is older than the specified hours, False otherwise.
    """
    if get_common().work_symbols_date_analysis is None:
        return True
    else:
        return datetime.now() - get_common().work_symbols_date_analysis > timedelta(hours=hours)


def set_default(message: Message) -> bool:
    """
    A function that sets default values in a message.

    Parameters:
    - message (Message): The message to update with default values.

    Returns:
    - bool: True if the default values were set successfully, False otherwise.
    """
    try:
        update(message,
               default_profit=GetDefaultValues().profit,
               bad_list_currency=json.dumps([]),
               work_exchanges=json.dumps(GetDefaultValues().exchanges))
    except Exception:
        return False
    else:
        return True
