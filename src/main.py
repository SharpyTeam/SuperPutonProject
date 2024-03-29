import os
import sys


os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.runtime import Runtime


import api.utils as u
import api.web as web

from ui.console.archives_console import archives_data_dl_callback
from ui.console.relevant_console import actual_data_dl_callback

from ui.gui.archives_app import ArchivesApp
from ui.gui.relevant_app import RelevantApp
from ui.gui.viewer_app import ViewerApp

bar = None

previous_status = web.DataGetStatus.STARTED

actual_dl_status = None
actual_parse_status = None


def parsing_callback(status: web.DataGetStatus):
    global actual_parse_status
    actual_parse_status = web.DataGetStatus
    if status == web.DataGetStatus.FINISHED:
        print("Всё обработано.")


def main():
    u.create_missing()

    if sys.version_info < (3, 7, 3):
        print("-----------------")
        print("Проект написан на Python 3.7.3 и может работать некорректно на более старых версиях Python.")
        print("Ваша версия Python: " + ".".join(list(map(str, sys.version_info))[:3]))
        print("-----------------\n")

    Runtime.is_windows = sys.platform == 'win32'
    print("-= Выберите действие =-")
    print("1. Скачать актуальные данные")
    print("2. Скачать архивные данные")
    print("3. Скачать актуальные данные (GUI)")
    print("4. Скачать архивные данные (GUI)")
    print("5. Работа с БД (GUI)")
    i = input()
    if i.startswith('1'):
        u.clean_tmp()
        print("Скачиваются актуальные данные")
        web.download_relevant_data(lambda x, y, z: actual_data_dl_callback(x, y, z),
                                   lambda x, y, z: None,
                                   lambda x, y, z: parsing_callback(x))
    elif i.startswith('2'):
        u.clean_tmp()
        print('Скачиваются архивные данные: ')
        web.download_archive_data(lambda x, y, z, w: archives_data_dl_callback(x, y, z, w),
                                  lambda x, y, z: parsing_callback(x))
    elif i.startswith('3'):
        RelevantApp.run()
    elif i.startswith('4'):
        ArchivesApp.run()
    else:
        ViewerApp.run()

    print("Готово!")


if __name__ == "__main__":
    main()
