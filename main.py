import os

import progressbar as pb

import src.api.web as d
import src.api.parsing as p
import src.api.utils as u
import src.config as c
import src.api.runtime as runtime
from src.ui.gui.archives_app import ArchivesApp

runtime.Runtime.init(__file__)

archives_pb = None
archives_pb_widgets = [
    pb.Percentage(),
    ' ', pb.Bar('>'),
    ' ', pb.ETA(),
    ' ', pb.FormatLabel(
        'Загружается файл %(value)d/%(max_value)d...')
]

is_unpacking = False
actual_pb_unpacker = None
actual_pb_unpacker_widgets = [
    'Распаковываем архив: ',
    ' ', pb.AnimatedMarker(),
]

actual_pb = None
actual_pb_widgets = [
    ' Загружается архив: ',
    ' | ', pb.DataSize(unit='Б', prefixes=('', 'К', 'М', 'Г', 'Т', 'П', 'Э', 'З', 'И')),
    ' '
]


def archives_data_dl_callback(bytes, current_file, done, total):
    global archives_pb
    if archives_pb is None:
        archives_pb = pb.ProgressBar(redirect_stdout=True, widgets=archives_pb_widgets, max_value=total).start()
    archives_pb.update(done)


def actual_data_dl_callback(bytes, current_file, done, total, unpacking):
    global actual_pb, is_unpacking, actual_pb_unpacker
    if not unpacking:
        if actual_pb is None:
            actual_pb = pb.ProgressBar(widgets=actual_pb_widgets).start()
        actual_pb.update(bytes)
    else:
        if not is_unpacking:
            actual_pb.finish()
            is_unpacking = True
            print("\nАрхив скачался.")
            actual_pb_unpacker = pb.ProgressBar(widgets=actual_pb_widgets,
                                                max_value=total).start()
        else:
            actual_pb_unpacker.update(done)


print("-= Выберите действие =-")
print("1. Скачать актуальные данные")
print("2. Скачать архивные данные")
print("3. Тест PyQt5")
i = input()
if i.startswith('1'):
    u.clean_tmp()
    print("Скачиваются архивные данные")
    d.get_relevant_data(lambda x, y, z: print(x, y, z))
    actual_pb_unpacker.finish()
    actual_pb.finish()


elif i.startswith('2'):
    periods = p.parse_archives(d.get_page(c.ARCHIVES_PAGE_URL))
    print("Выберите период:")
    for i in range(len(periods)):
        print("%d. I квартал %s" % (i + 1, periods[i][0]))
    sel = int(input())
    period = periods[sel - 1] if 0 <= sel <= len(periods) else periods[0]
    print("Выбран I квартал %s" % period[0])
    print("URL: %s" % period[1])

    u.clean_tmp()
    print('Скачиваются архивные данные: ')
    d.dl_archive_files(p.parse_annual_page(d.get_page(period[1])),
                       u.get_tmp_path(), archives_data_dl_callback)
    archives_pb.finish()
else:
    ArchivesApp.run()

print("Готово!")
