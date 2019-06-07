from typing import NoReturn

import progressbar as pb

from api import web as d, config as c


class RelevantConsoleApp:
    pass


actual_pb_unpacker_widgets = [
    'Распаковано ', pb.widgets.Percentage(),
    ' из ', pb.widgets.DataSize('max_value', unit='Б', prefixes=c.BYTES_FORMAT_PREFIXES),
    ' ', pb.widgets.Bar(marker='>', left='[', right=']'),
    ' ', pb.widgets.Timer(format='Прошло времени: %(elapsed)s'),
    ' ', pb.widgets.AdaptiveETA(format_not_started='Осталось:  --:--:--',
                                format_finished='Время: %(elapsed)8s',
                                format='Осталось:  %(eta)8s',
                                format_zero='Осталось:  00:00:00',
                                format_NA='Осталось:      Н/Д')
]
actual_pb_widgets = [
    'Архив загружается! Уже загружено: ',
    pb.widgets.DataSize(unit='Б', prefixes=('', 'К', 'М', 'Г', 'Т', 'П', 'Э', 'З', 'И')),
    ' | ', pb.widgets.Timer(format='Прошло времени: %(elapsed)s')
]


def actual_data_dl_callback(status: d.DataGetStatus, done: float, total: float):
    global bar, previous_status, actual_pb_unpacker_widgets
    if status == d.DataGetStatus.STARTED:
        bar = pb.ProgressBar(widgets=actual_pb_widgets).start()
    elif status == d.DataGetStatus.DOWNLOADING:
        previous_status = d.DataGetStatus.DOWNLOADING
        bar.update(done)
    elif status == d.DataGetStatus.EXTRACTING:
        if previous_status == d.DataGetStatus.DOWNLOADING:
            bar.finish()
            previous_status = d.DataGetStatus.EXTRACTING
            print("\nАрхив скачался.\n")
            bar = pb.DataTransferBar(widgets=actual_pb_unpacker_widgets,
                                     max_value=total).start()
        else:
            bar.update(done)
    elif status == status.FINISHED:
        bar.finish()

def run_archives_downloader() -> NoReturn:
    pass