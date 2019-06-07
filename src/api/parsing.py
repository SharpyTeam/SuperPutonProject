import re
from typing import Dict, Optional, Tuple, List

import math
import pandas as p
import xlrd
from bs4 import BeautifulSoup as Bs

from . import config


def get_archive_years_links(archives_page: str) -> Dict[str, str]:
    doc = Bs(archives_page, 'lxml')
    a_list = doc.select(config.ARCHIVES_PAGES_URLS_SELECTOR)
    year_list = [re.search('[0-9]+', str(e.string)).group(0) for e in doc.select(config.ARCHIVES_YEARS_SELECTOR)]
    return dict(zip(year_list, list(map(lambda a: config.MAIN_URL + a['href'], a_list))))


def get_available_archive_years(archives_page: str) -> List[str]:
    doc = Bs(archives_page, 'lxml')
    year_list = [re.search('[0-9]+', str(e.string)).group(0) for e in doc.select(config.ARCHIVES_YEARS_SELECTOR)]
    return year_list


def get_archive_companies_xls_links(archive_year_page: str) -> Dict[str, str]:
    doc = Bs(archive_year_page, 'lxml')
    companies_rows = doc.select(config.ARCHIVES_COMPANIES_ROWS_SELECTOR)
    d = {}
    for row in companies_rows:
        td = row.find_all('td')
        if len(td) < 7:
            continue
        a = td[6].find('a')
        if a is None:
            continue
        d[str(td[5].string)] = config.MAIN_URL + a['href']
    return d


def get_relevant_archive_link(relevant_page: str) -> str:
    doc = Bs(relevant_page, 'lxml')
    a = doc.select_one(config.RELEVANT_DATA_URL_SELECTOR)
    return config.MAIN_URL + a['href']


def get_relevant_year(relevant_page: str) -> str:
    doc = Bs(relevant_page, 'lxml')
    year_e = doc.select_one(config.RELEVANT_YEAR_SELECTOR)
    return re.search('[0-9]+', year_e['value']).group(0)


table_columns = [
    'Страховые премии по договорам страхования',  # 0
    'Страховая сумма по заключенным договорам страхования',  # 1
    'Заключенных договоров страхования',  # 2
    'Договоров страхования на конец отчетного периода',  # 3
    'Заявленных страховых случаев',  # 4
    'Урегулированных страховых случаев',  # 5
    'Страховых случаев с отказом в выплате',  # 6
    'Всего выплат по договорам страхования',  # 7
    'Страховые выплаты',  # 8
    'Прочие выплаты'  # 9
]

table_columns_mappings = {
    # Unified column index to xls column index
    '2014': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    '2016': [3, 6, 5, 14, 7, 8, 9, 10, 11, 13],
    '2018': [2, 4, 3, 12, 5, 6, 7, 8, 9, 11]
}


def get_data_frame_and_company_name_from_xls(path: str) -> Optional[Tuple[p.DataFrame, str]]:
    try:
        # 2016 or 2018 format
        frame = p.read_excel(path, header=None, sheet_name='Раздел 1')
    except (IndexError, ValueError, OverflowError, xlrd.XLRDError):
        try:
            # 2014 format
            f = p.read_excel(path, header=None, sheet_name=['1C-1', 'Титульный лист'])
            frame = f['1C-1']
            frame_title = f['Титульный лист']
        except (IndexError, ValueError, OverflowError, xlrd.XLRDError):
            # unknown data
            return None

    if 'Наименование показателя' in frame.iloc[22, 0]:
        # 2018 format
        actual_columns_mapping = table_columns_mappings['2018']
        first_row_index = (28, 1)
        company_name = frame.iloc[13, 3]
    elif 'Наименование показателя' in frame.iloc[14, 0]:
        # 2016-2017 format
        actual_columns_mapping = table_columns_mappings['2016']
        first_row_index = (19, 2)
        company_name = frame.iloc[7, 2]
    elif 'Наименование показателя' in str(frame.iloc[2, 0]):
        # 2014-2015 format
        actual_columns_mapping = table_columns_mappings['2014']
        first_row_index = (6, 1)
        company_name = frame_title.iloc[13, 1]
    else:
        return None  # unknown data

    rows_list = []
    indices_list = []

    for row in range(first_row_index[0], frame.shape[0]):
        # Ignore fractional and empty row indices
        try:
            row_index = int(frame.iloc[row, first_row_index[1]])
        except ValueError:
            continue

        final_row = []

        for column in range(len(table_columns)):
            try:
                num = float(frame.iloc[row, actual_columns_mapping[column]])
                if not math.isfinite(num):
                    num = 0.0
            except ValueError:
                num = 0.0
            final_row.append(num)

        # Unfilled cells will contain 0.0's

        rows_list.append(final_row)
        indices_list.append(row_index)

    final_table = p.DataFrame(rows_list, index=indices_list)

    return final_table, company_name
