import re
from bs4 import BeautifulSoup as Bs
from typing import Dict

from src import config


def get_archive_years_links(archives_page: str) -> Dict[str, str]:
    doc = Bs(archives_page, 'lxml')
    a_list = doc.select(config.ARCHIVES_PAGES_URLS_SELECTOR)
    year_list = [re.search('[0-9]+', str(e.string)).group(0) for e in doc.select(config.ARCHIVES_YEARS_SELECTOR)]
    return dict(zip(year_list, list(map(lambda a: config.MAIN_URL + a['href'], a_list))))


def get_archive_companies_xls_links(archive_year_page: str) -> Dict[str, str]:
    doc = Bs(archive_year_page, 'lxml')
    ids_list = doc.select(config.ARCHIVES_IDS_SELECTOR)
    a_list = doc.select(config.ARCHIVES_XLS_URLS_SELECTOR)
    ids_mapped = [str(x.string) for x in ids_list]
    a_mapped = list(map(lambda a: config.MAIN_URL + a['href'], a_list))
    return dict(zip(ids_mapped, a_mapped))


def get_relevant_archive_link(relevant_page: str) -> str:
    doc = Bs(relevant_page, 'lxml')
    a = doc.select_one(config.RELEVANT_DATA_URL_SELECTOR)
    return config.MAIN_URL + a['href']


def get_relevant_year(relevant_page: str) -> str:
    doc = Bs(relevant_page, 'lxml')
    year_e = doc.select_one(config.RELEVANT_YEAR_SELECTOR)
    return re.search('[0-9]+', year_e['value']).group(0)
