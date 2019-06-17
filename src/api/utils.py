import os
import shutil
from datetime import datetime
from os import path
from typing import NoReturn

from python_utils import converters

from . import config


def get_working_directory() -> str:
    return os.getcwd()


def get_tmp_path() -> str:
    return path.join(get_working_directory(), config.DATA_DIR, config.TMP_DIR)


def get_exports_path() -> str:
    return path.join(get_working_directory(), config.DATA_DIR, config.EXPORTS_DIR)


def get_data_path() -> str:
    return path.join(get_working_directory(), config.DATA_DIR)


def get_db_path() -> str:
    return path.join(get_working_directory(), config.DATA_DIR, config.DB_FILENAME)


def get_schema_path() -> str:
    return path.join(get_working_directory(), config.DATA_DIR, config.DB_SCHEMA_FILENAME)


def create_missing() -> NoReturn:
    os.makedirs(get_tmp_path(), exist_ok=True)
    os.makedirs(get_exports_path(), exist_ok=True)


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


def get_parent_directory(directory: str, levels: int = 1) -> str:
    for _ in range(levels):
        directory = os.path.dirname(directory)
    return directory


def chdir(main_file_path: str) -> NoReturn:
    if os.path.isabs(main_file_path):
        os.chdir(get_parent_directory(os.path.normpath(main_file_path), levels=1))
    else:
        os.chdir(get_parent_directory(os.path.normpath(os.path.join(os.getcwd(), main_file_path))))


def format_bytes(bytes_count: int) -> str:
    if bytes_count is not None:
        scaled, power = converters.scale_1024(bytes_count, len(config.BYTES_FORMAT_PREFIXES))
    else:
        scaled = power = 0
    return "{scaled:1.5f} {prefix}Б".format(scaled=scaled, prefix=config.BYTES_FORMAT_PREFIXES[power])


def get_file_name_for_export(company_id: int, year: str) -> str:
    return "Данные_" + str(company_id) + "_" + year + "_" + datetime.now().strftime('%d.%m.%Y_%H-%M-%S') + ".xlsx"
