import os
import re
import zipfile
import requests
from enum import Enum
from multiprocessing import Pool
from threading import Thread, Event
from typing import Callable, List

from src import config
from . import utils, parsing
from .company import Company
from .company_data import CompanyData


class DataGetStatus(Enum):
    STARTED = 1
    DOWNLOADING = 2
    EXTRACTING = 3
    PARSING = 4
    FINISHED = 5


class BackgroundParseProcess:
    @staticmethod
    def parse(xls_path: str):
        return parsing.get_data_frame_and_company_name_from_xls(xls_path)

    def __init__(self, callback: Callable[[DataGetStatus, int, int], None]):
        self.callback = callback
        self.batch = []
        self.batch_size = os.cpu_count()
        self.pool = Pool(processes=self.batch_size)
        self.count_added = 0
        self.count_parsed = 0
        self.imap_iterator = None
        self.fetch_thread = Thread(target=self._fetch_from_pool)
        self.finish = False
        self.fetch_event = Event()

    def _push_to_pool(self):
        if (len(self.batch) < self.batch_size and not self.finish) or self.imap_iterator is not None:
            return
        if len(self.batch) > 0:
            self.imap_iterator = self.pool.imap(BackgroundParseProcess.parse, [x[2] for x in self.batch])
        self.fetch_event.set()

    def _fetch_from_pool(self):
        while True:
            self.fetch_event.wait()
            self.fetch_event.clear()
            if self.imap_iterator is None:
                if self.finish:
                    break
                continue
            for d in self.imap_iterator:
                if d is None:
                    continue
                data_frame, company_name = d
                company, year, _ = self.batch.pop(0)
                company.data[year] = CompanyData(company, year, data_frame)
                company.name = company_name
                self.count_parsed += 1
                if self.callback is not None:
                    self.callback(DataGetStatus.PARSING, self.count_parsed, self.count_added)
            self.imap_iterator = None
            self._push_to_pool()

    def parse_company(self, company, year, xls_path):
        self.batch.append((company, year, xls_path))
        self.count_added += 1
        self._push_to_pool()

    def start_parse(self):
        if self.callback is not None:
            self.callback(DataGetStatus.STARTED, 0, 0)
        self.fetch_thread.start()

    def finish_parse(self):
        self.finish = True
        self._push_to_pool()
        self.fetch_thread.join()
        if self.callback is not None:
            self.callback(DataGetStatus.FINISHED, self.count_parsed, self.count_added)


def get_relevant_data(callback: Callable[[DataGetStatus, float, float], None],
                      parse_callback: Callable[[DataGetStatus, int, int], None]) -> List[Company]:
    relevant_page = get_relevant_page()
    year = parsing.get_relevant_year(relevant_page)
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

    parse_process = BackgroundParseProcess(parse_callback)
    parse_process.start_parse()

    for file in zf.infolist():
        extracted_size += file.file_size
        p = zf.extract(file, os.path.join(utils.get_tmp_path(), ''.join(config.RELEVANT_ZIP_NAME.split('.')[:-1])))
        company = Company(int(re.search(r'(?<=_)[0-9]*(?=(.xlsx?))', p).group(0)), '')
        companies.append(company)
        parse_process.parse_company(company, year, p)
        if callback is not None:
            callback(DataGetStatus.EXTRACTING, extracted_size, uncompress_size)

    if callback is not None:
        callback(DataGetStatus.FINISHED, 0, 0)

    zf.close()
    parse_process.finish_parse()

    return companies


def get_archive_data(callback: Callable[[DataGetStatus, int, int, str], None],
                     parse_callback: Callable[[DataGetStatus, int, int], None]) -> List[Company]:
    companies = {}
    years_links = parsing.get_archive_years_links(get_archives_page())
    parse_process = BackgroundParseProcess(parse_callback)
    parse_process.start_parse()
    for year, year_link in years_links.items():
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
            if c_id in companies:
                company = companies[c_id]
            else:
                company = Company(c_id, '')
                companies[c_id] = company
            parse_process.parse_company(company, year, file_path)
            files_count += 1
            if callback is not None:
                callback(DataGetStatus.DOWNLOADING, files_count, len(xls_links.keys()), str(year))

        if callback is not None:
            callback(DataGetStatus.FINISHED, 0, 0, str(year))

    parse_process.finish_parse()

    return list(companies.values())


def get_relevant_page() -> str:
    return get_page(config.RELEVANT_PAGE_URL)


def get_archives_page() -> str:
    return get_page(config.ARCHIVES_PAGE_URL)


def get_page(url: str) -> str:
    r = requests.get(url)
    return r.text if r.ok else None
