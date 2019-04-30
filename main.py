import os

import progressbar as pb

import src.api.web as d
import src.api.parsing as p
import src.api.utils as u
import src.config as c

# TODO move all to main function
os.chdir(os.path.dirname(os.path.abspath(__file__)))

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
if input().startswith('1'):
    u.clean_tmp()
    print("Скачиваются актуальные данные")
    d.get_relevant_data(lambda x, y, z: print(x, y, z))
    actual_pb_unpacker.finish()
    actual_pb.finish()


else:
    u.clean_tmp()
    print('Скачиваются архивные данные: ')
    d.get_archive_data(lambda x, y, z, w: print(x, y, z, w))
    archives_pb.finish()

print("Готово!")
