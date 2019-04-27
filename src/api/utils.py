import os
import os.path as path
import shutil
import sqlite3

import src.config as c


def get_tmp_path():
    return path.join(c.DATA_DIR, c.TMP_DIR)


def get_data_abs_path(p):
    return path.join(p, c.DATA_DIR)


def get_tmp_abs_path(p):
    return path.join(p, get_tmp_path())


def get_db_abs_path(p):
    return path.join(p, c.DATA_DIR, c.DB_FILENAME)


def get_schema_abs_path(p):
    return path.join(p, c.DATA_DIR, c.DB_SCHEMA_FILENAME)


def create_db(p):
    open(get_db_abs_path(p), 'a').close()
    db = sqlite3.connect(get_db_abs_path(p))
    schema_file = open(get_schema_abs_path(p), 'r')
    sql = schema_file.read()
    schema_file.close()
    db.executescript(sql)
    db.close()


def create_missing(p):
    dirs = [get_tmp_abs_path(p)]
    if not path.exists(get_db_abs_path(p)):
        create_db(p)


def cleanup_tmp(p):
    tmp_dir = get_tmp_abs_path(p)
    for the_file in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)
