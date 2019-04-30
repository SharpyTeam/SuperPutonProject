import os
import zipfile
import requests
import re
from typing import Callable, List, Dict
from enum import Enum

from . import utils, parsing
from .company import Company
from src import config


class DataGetStatus(Enum):
    STARTED = 1
    DOWNLOADING = 2
    EXTRACTING = 3
    FINISHED = 4


def get_relevant_data(callback: Callable[[DataGetStatus, float, float], None]) -> Dict[str, List[Company]]:
    """

    :param callback: (status, progress, total)
    :return:
    """
    relevant_page = get_relevant_page()
    companies = []
    file_path = os.path.join(utils.get_tmp_path(), config.RELEVANT_ZIP_NAME)

    with open(file_path, "wb") as f:
        with requests.get(parsing.get_relevant_archive_link(relevant_page), stream=True) as r:
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
    return dict([(parsing.get_relevant_year(relevant_page), companies)])


def get_archive_data(callback: Callable[[DataGetStatus, float, float, str], None]) -> Dict[str, List[Company]]:
    return_data = {}
    years_links = parsing.get_archive_years_links(get_archives_page())
    for year, year_link in years_links.items():
        return_data[year] = []
        xls_links = parsing.get_archive_companies_xls_links(get_page(year_link))

        if callback is not None:
            callback(DataGetStatus.STARTED, 0, 0, year)

        files_count = 0

        folder_path = os.path.join(utils.get_tmp_path(), 'archive', str(year))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for c_id, xls_link in xls_links.items():
            response = requests.get(xls_link, stream=True)
            file_name = "kstat_" + c_id + ".xls"
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "wb") as f:
                for data in response.iter_content(chunk_size=4096):
                    f.write(data)
            return_data[year].append(Company(c_id, ''))
            # TODO parse xls and add it to company here
            files_count += 1
            if callback is not None:
                callback(DataGetStatus.DOWNLOADING, files_count, len(xls_links.keys()), str(year))

        if callback is not None:
            callback(DataGetStatus.FINISHED, 0, 0, str(year))

    print(data)
    return data


def get_relevant_page() -> str:
    return get_page(config.RELEVANT_PAGE_URL)


def get_archives_page() -> str:
    return get_page(config.ARCHIVES_PAGE_URL)


def get_page(url: str) -> str:
    r = requests.get(url)
    return r.text if r.ok else None
