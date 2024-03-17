import os
from typing import NoReturn


def create_folder_if_not_exists(folder_path: str) -> NoReturn:
    """
    Creates a folder at the specified 'folder_path' if it does not already exist.

    Parameters:
    folder_path (str): The path of the folder to be created.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
