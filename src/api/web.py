import os
import zipfile
import requests
import re
import queue
from multiprocessing import Process, Queue
from typing import Callable, List, Dict, Tuple
from enum import Enum

from . import utils, parsing
from .company import Company
from src import config


class DataGetStatus(Enum):
    STARTED = 1
    DOWNLOADING = 2
    EXTRACTING = 3
    PARSING = 4
    FINISHED = 5


class BackgroundParseProcess:
    @staticmethod
    def parse_background(in_q: Queue, out_q: Queue):
        file_path = in_q.get()
        while file_path is not None:
            data_table = parsing.get_data_frame_from_xls(file_path)
            out_q.put(data_table)
            file_path = in_q.get()

    def __init__(self, callback: Callable[[DataGetStatus, int, int], None]):
        self.callback = callback
        self.in_q = Queue()
        self.out_q = Queue()
        self.comp_q = Queue()
        self.process = Process(target=BackgroundParseProcess.parse_background, args=(self.in_q, self.out_q))
        self.count_added = 0
        self.count_parsed = 0

    def parse_company(self, company, xls_path):
        self.in_q.put(xls_path)
        self.comp_q.put(company)
        self.count_added += 1

    def check_parse_status(self):
        try:
            data_table = self.out_q.get_nowait()
            while True:
                company = self.comp_q.get()
                company.data_table = data_table
                self.count_parsed += 1
                if self.callback is not None:
                    self.callback(DataGetStatus.PARSING, self.count_parsed, self.count_added)
                data_table = self.out_q.get_nowait()
        except queue.Empty:
            pass

    def start_parse(self):
        self.process.start()
        if self.callback is not None:
            self.callback(DataGetStatus.STARTED, 0, 0)

    def finish_parse(self):
        self.in_q.put(None)
        self.process.join()
        if self.callback is not None:
            self.callback(DataGetStatus.FINISHED, self.count_parsed, self.count_added)


def get_relevant_data(callback: Callable[[DataGetStatus, float, float], None],
                      parse_callback: Callable[[DataGetStatus, int, int], None]) -> Dict[str, List[Company]]:
    relevant_page = get_relevant_page()
    companies = []
    file_path = os.path.join(utils.get_tmp_path(), config.RELEVANT_ZIP_NAME)
    parse_process = BackgroundParseProcess(parse_callback)
    parse_process.start_parse()

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
        company = Company(int(re.search(r'(?<=_)[0-9]*(?=(.xlsx?))', p).group(0)), '')
        companies.append(company)
        parse_process.parse_company(company, p)
        parse_process.check_parse_status()
        if callback is not None:
            callback(DataGetStatus.EXTRACTING, extracted_size, uncompress_size)

    if callback is not None:
        callback(DataGetStatus.FINISHED, 0, 0)

    zf.close()

    parse_process.finish_parse()

    return dict([(parsing.get_relevant_year(relevant_page), companies)])


def get_archive_data(callback: Callable[[DataGetStatus, int, int, str], None],
                     parse_callback: Callable[[DataGetStatus, int, int], None]) -> Dict[str, List[Company]]:
    return_data = {}
    years_links = parsing.get_archive_years_links(get_archives_page())
    parse_process = BackgroundParseProcess(parse_callback)
    parse_process.start_parse()
    for year, year_link in years_links.items():
        return_data[year] = []
        xls_links = parsing.get_archive_companies_xls_links(get_page(year_link))

        if callback is not None:
            callback(DataGetStatus.STARTED, 0, 0, year)

        files_count = 0

        folder_path = os.path.join(utils.get_tmp_path(), 'archive', str(year))
        os.makedirs(folder_path, exist_ok=True)

        for c_id, xls_link in xls_links.items():
            response = requests.get(xls_link, stream=True)
            file_name = "kstat_" + c_id + ".xls"
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "wb") as f:
                for data in response.iter_content(chunk_size=4096):
                    f.write(data)
            company = Company(c_id, '')
            return_data[year].append(company)
            parse_process.parse_company(company, file_path)
            parse_process.check_parse_status()
            files_count += 1
            if callback is not None:
                callback(DataGetStatus.DOWNLOADING, files_count, len(xls_links.keys()), str(year))

        if callback is not None:
            callback(DataGetStatus.FINISHED, 0, 0, str(year))

    parse_process.finish_parse()

    return return_data


def get_relevant_page() -> str:
    return get_page(config.RELEVANT_PAGE_URL)


def get_archives_page() -> str:
    return get_page(config.ARCHIVES_PAGE_URL)


def get_page(url: str) -> str:
    r = requests.get(url)
    return r.text if r.ok else None
