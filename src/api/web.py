import os
import zipfile
import requests
import re
from typing import Callable, List
from enum import Enum

from . import utils, parsing
from .company import Company
from src import config


class DataGetStatus(Enum):
    STARTED = 1
    DOWNLOADING = 2
    EXTRACTING = 3
    FINISHED = 4


def get_relevant_data(callback: Callable[[DataGetStatus, float, float], None]) -> List[Company]:
    """

    :param callback: (status, progress, total)
    :return:
    """
    companies = []
    file_path = os.path.join(utils.get_tmp_path(), config.RELEVANT_ZIP_NAME)

    with open(file_path, "wb") as f:
        with requests.get(parsing.get_relevant_archive_link(get_relevant_page()), stream=True) as r:
            r.raise_for_status()
            data_length = 0
            if callback is not None:
                callback(DataGetStatus.STARTED, 0, 0)
            for data in r.iter_content(chunk_size=4096):
                data_length += len(data)
                f.write(data)
                if callback is not None:
                    callback(DataGetStatus.DOWNLOADING, data_length, float('inf'))
        f.flush()

    zf = zipfile.ZipFile(file_path, 'r')
    uncompress_size = sum((file.file_size for file in zf.infolist()))
    extracted_size = 0

    if callback is not None:
        callback(DataGetStatus.EXTRACTING, extracted_size, uncompress_size)

    for file in zf.infolist():
        extracted_size += file.file_size
        p = zf.extract(file, os.path.join(utils.get_tmp_path(), ''.join(config.RELEVANT_ZIP_NAME.split('.')[:-1])))
        companies.append(Company(int(re.search(r'(?<=_)[0-9]*(?=(.xlsx?))', p).group(0)), ''))
        # TODO parse xls and add it to company here
        if callback is not None:
            callback(DataGetStatus.EXTRACTING, extracted_size, uncompress_size)

    if callback is not None:
        callback(DataGetStatus.FINISHED, 0, 0)

    zf.close()
    print([x.index for x in companies])
    return companies


def dl_archive_files(entries, dir, callback):
    file_c = 1
    for c_id, url in entries:
        response = requests.get(url, stream=True)
        file_name = "kstat_" + c_id + ".xls"
        file_path = os.path.join(dir, file_name)
        with open(file_path, "wb") as f:
            dl = 0
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                if callback is not None:
                    callback(dl, file_name, file_c, len(entries))
        file_c += 1


def get_relevant_page() -> str:
    return get_page(config.RELEVANT_PAGE_URL)


def get_page(url: str) -> str:
    r = requests.get(url)
    return r.text if r.ok else None
