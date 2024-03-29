from typing import List


# URL
MAIN_URL = "http://cbr.ru"
RELEVANT_PAGE_URL = "http://cbr.ru/finmarket/account/account_repor_insure/information_ssd/report_individual_ssd" \
                    "/report_individual_ins/"
ARCHIVES_PAGE_URL = "http://cbr.ru/finmarket/account/account_repor_insure/archive/"

# Селекторы
RELEVANT_DATA_URL_SELECTOR = "p.file:nth-child(4) > a:nth-child(1)"
RELEVANT_YEAR_SELECTOR = "#UniDbQuery_ToYear > option:nth-child(1)"
ARCHIVES_PAGES_URLS_SELECTOR = "div.switcher:nth-child(3) > div.switcher-line_with-year > div:nth-child(2) > " \
                               "span:nth-child(1) > a:nth-child(1) "
ARCHIVES_YEARS_SELECTOR = "div.switcher:nth-child(3) > div.switcher-line_with-year > div:nth-child(1) > " \
                          "span:nth-child(1) > a:nth-child(1) "
ARCHIVES_COMPANIES_ROWS_SELECTOR = ".data > tbody:nth-child(1) > tr"

# Название файлов и папок
DATA_DIR = "data"
TMP_DIR = "tmp"
EXPORTS_DIR = "exports"
DB_FILENAME = "data.db"
DB_SCHEMA_FILENAME = "schema.sql"
RELEVANT_ZIP_NAME = "relevant.zip"

# Прочее
DB_LOCK_TIMEOUT = 10.0
BYTES_FORMAT_PREFIXES = ('', 'К', 'М', 'Г', 'Т', 'П', 'Э', 'З', 'И')


class RuntimeConfig:
    rows_indices_to_sum: List[int] = [100, 180]
