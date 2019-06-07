import progressbar as pb

from api import web as d

bar = None

archives_pb_widgets = [
    'Файлов загружено: ', pb.widgets.FormatLabel("%(value)s/%(max_value)s"), ' (', pb.widgets.Percentage(), ')'
                                                                                                            ' ',
    pb.widgets.Bar(marker='>', left='[', right=']'),
    ' ', pb.widgets.Timer(format='Прошло времени: %(elapsed)s'),
    ' ', pb.widgets.AdaptiveETA(format_not_started='Осталось:  --:--:--',
                                format_finished='Время: %(elapsed)8s',
                                format='Осталось:  %(eta)8s',
                                format_zero='Осталось:  00:00:00',
                                format_NA='Осталось:      Н/Д')
]


def archives_data_dl_callback(status: d.DataGetStatus, files_done: int, files_total: int, year: str):
    global bar
    if status == d.DataGetStatus.SKIPPING:
        print("Архив за %s год уже скачан, переходим к следующему году." % year)
    elif status == d.DataGetStatus.STARTED:
        print("Скачиваются архивы за %s год:" % year)
    elif status == d.DataGetStatus.DOWNLOADING:
        if bar is None:
            bar = pb.ProgressBar(redirect_stdout=True, widgets=archives_pb_widgets, max_value=files_total).start()
        bar.update(files_done)
    else:
        bar.finish()
        bar = None
        print()
