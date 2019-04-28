import os
import os.path as path
import shutil
import sqlite3

import src.config as c
from src.api.runtime import Runtime


def get_tmp_path():
    return path.join(c.DATA_DIR, c.TMP_DIR)


def get_data_abs_path():
    return path.join(Runtime.get_app_path(), c.DATA_DIR)


def get_tmp_abs_path():
    return path.join(Runtime.get_app_path(), get_tmp_path())


def get_db_abs_path():
    return path.join(Runtime.get_app_path(), c.DATA_DIR, c.DB_FILENAME)


def get_schema_abs_path():
    return path.join(Runtime.get_app_path(), c.DATA_DIR, c.DB_SCHEMA_FILENAME)


def create_db():
    open(get_db_abs_path(), 'a').close()
    db = sqlite3.connect(get_db_abs_path())
    schema_file = open(get_schema_abs_path(), 'r')
    sql = schema_file.read()
    schema_file.close()
    db.executescript(sql)
    db.close()


def create_missing():
    dirs = [get_tmp_abs_path()]
    if not path.exists(get_db_abs_path()):
        create_db()


def cleanup_tmp():
    tmp_dir = get_tmp_abs_path()
    for the_file in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)
