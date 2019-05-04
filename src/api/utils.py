import os
import shutil
from os import path
from typing import NoReturn

from src import config
from . import db


def get_working_directory() -> str:
    return os.getcwd()


def get_tmp_path() -> str:
    return path.join(get_working_directory(), config.DATA_DIR, config.TMP_DIR)


def get_data_path() -> str:
    return path.join(get_working_directory(), config.DATA_DIR)


def get_db_path() -> str:
    return path.join(get_working_directory(), config.DATA_DIR, config.DB_FILENAME)


def get_schema_path() -> str:
    return path.join(get_working_directory(), config.DATA_DIR, config.DB_SCHEMA_FILENAME)


def create_missing() -> NoReturn:
    if not path.exists(get_db_path()):
        db.create_db()
    os.makedirs(get_tmp_path(), exist_ok=True)


def clean_tmp() -> NoReturn:
    create_missing()
    tmp_dir = get_tmp_path()
    for the_file in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)
