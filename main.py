import os

import progressbar as pb

import src.api.dl as d
import src.api.parsing as p
import src.api.utils as u

archives_pb = None
archives_pb_widgets = [
    pb.Percentage(),
    ' ', pb.Bar('>'),
    ' ', pb.ETA(),
    ' ', pb.FormatLabel(
        'Загружается файл %(value)d/%(max_value)d...')
]


def actual_data_dl_callback(bytes, file_name, counter, total):
    # print(str(bytes) + " downloaded. File " + str(counter)
    #      + "/" + str(total) + " - " + file_name)
    pass


def archives_data_dl_callback(bytes, current_file, done, total):
    global archives_pb
    if archives_pb is None:
        archives_pb = pb.ProgressBar(redirect_stdout=True, widgets=archives_pb_widgets, max_value=total).start()
    archives_pb.update(done)


print('Скачиваем архивные данные: ')
d.dl_archive_files(p.parse_annual_page(d.get_page('http://cbr.ru/finmarket/fcsm/publication/insurers/2017-12-31/')),
                   u.make_tmp_abs_path(os.path.dirname(__file__)), archives_data_dl_callback)

archives_pb.finish()
