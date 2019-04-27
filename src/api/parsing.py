from bs4 import BeautifulSoup as Bs

from src import config


def parse_archives(archives_page):
    doc = Bs(archives_page, 'lxml')
    a_list = doc.select(config.ARCHIVES_PAGES_URLS_SELECTOR)
    year_list = [str(e.string) for e in doc.select(config.ARCHIVES_YEARS_SELECTOR)]
    return list(zip(year_list, list(map(lambda a: config.MAIN_URL + a['href'], a_list))))


def parse_relevant_page(relevant_page):
    doc = Bs(relevant_page, 'lxml')
    a = doc.select_one(config.RELEVANT_DATA_URL_SELECTOR)
    return config.MAIN_URL + a['href']


def parse_relevant_year(relevant_page):
    doc = Bs(relevant_page, 'lxml')
    year_e = doc.select_one(config.RELEVANT_YEAR_SELECTOR)
    return year_e['value']


def parse_annual_page(annual_page):
    doc = Bs(annual_page, 'lxml')
    ids_list = doc.select(config.ARCHIVES_IDS_SELECTOR)
    a_list = doc.select(config.ARCHIVES_XLS_URLS_SELECTOR)
    ids_mapped = [str(x.string) for x in ids_list]
    a_mapped = list(map(lambda a: config.MAIN_URL + a['href'], a_list))
    return list(zip(ids_mapped, a_mapped))
