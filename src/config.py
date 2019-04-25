# URL
MAIN_URL = "http://cbr.ru"
RELEVANT_DATA_URL = "http://cbr.ru/finmarket/account/account_repor_insure/information_ssd/report_individual_ssd" \
                    "/report_individual_ins/"
ARCHIVE_URL = "http://cbr.ru/finmarket/account/account_repor_insure/archive/"


# Селекторы
RELEVANT_DATA_URL_SELECTOR = "p.file:nth-child(4) > a:nth-child(1)"
RELEVANT_YEAR_SELECTOR = "#UniDbQuery_ToYear > option:nth-child(1)"
ARCHIVES_URLS_SELECTOR = "div.switcher:nth-child(3) > div.switcher-line_with-year > div:nth-child(1) > " \
                         "span:nth-child(1) > a:nth-child(1) "
ARCHIVES_IDS_SELECTOR = ".data > tbody:nth-child(1) > tr > td:nth-child(6)"
ARCHIVES_XLS_URLS_SELECTOR = ".data > tbody:nth-child(1) > tr > td:nth-child(10) > a:nth-child(1)"

# Название файлов и папок
DATA_DIR = "data"
TMP_DIR = "tmp"
DB_FILENAME = "data.db"
RELEVANT_ZIP_NAME = "relevant.zip"
