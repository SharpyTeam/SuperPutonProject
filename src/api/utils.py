import os
import shutil
import sqlite3
from os import path

from src import config


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


def create_db():
    open(get_db_path(), 'a').close()
    db = sqlite3.connect(get_db_path())
    schema_file = open(get_schema_path(), 'r')
    sql = schema_file.read()
    schema_file.close()
    db.executescript(sql)
    db.close()


def create_missing():
    if not path.exists(get_db_path()):
        create_db()
    os.makedirs(get_tmp_path(), exist_ok=True)


def clean_tmp():
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
