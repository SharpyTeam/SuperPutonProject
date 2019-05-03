import os

import progressbar as pb

import src.api.utils as u
import src.api.web as d
from src.ui.gui.archives_app import ArchivesApp

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

actual_pb_unpacker_widgets = [
    'Распаковано ', pb.widgets.Percentage(),
    ' из ', pb.widgets.DataSize('max_value', unit='Б', prefixes=('', 'К', 'М', 'Г', 'Т', 'П', 'Э', 'З', 'И')),
    ' ', pb.widgets.Bar(marker='>', left='[', right=']'),
    ' ', pb.widgets.Timer(format='Прошло времени: %(elapsed)s'),
    ' ', pb.widgets.AdaptiveETA(format_not_started='Осталось:  --:--:--',
                                format_finished='Время: %(elapsed)8s',
                                format='Осталось:  %(eta)8s',
                                format_zero='Осталось:  00:00:00',
                                format_NA='Осталось:      Н/Д')
]

previous_status = d.DataGetStatus.STARTED
actual_pb_widgets = [
    'Архив загружается! Уже загружено: ',
    pb.widgets.DataSize(unit='Б', prefixes=('', 'К', 'М', 'Г', 'Т', 'П', 'Э', 'З', 'И')),
    ' | ', pb.widgets.Timer(format='Прошло времени: %(elapsed)s')
]


def archives_data_dl_callback(status: d.DataGetStatus, files_done: int, files_total: int, year: str):
    global bar
    if status == d.DataGetStatus.STARTED:
        print("Скачиваются архивы за %s год:" % year)
    elif status == d.DataGetStatus.DOWNLOADING:
        if bar is None:
            bar = pb.ProgressBar(redirect_stdout=True, widgets=archives_pb_widgets, max_value=files_total).start()
        bar.update(files_done)
    else:
        bar.finish()
        bar = None
        print()


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


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("-= Выберите действие =-")
    print("1. Скачать актуальные данные")
    print("2. Скачать архивные данные")
    print("3. Актуальные данные (GUI)")
    print("4. Архивные данные (GUI)")
    print("5. Работа с БД (GUI)")
    i = input()
    if i.startswith('1'):
        u.clean_tmp()
        print("Скачиваются актуальные данные")
        d.get_relevant_data(lambda x, y, z: actual_data_dl_callback(x, y, z), lambda x, y, z: print("L1:", x, y, z))
    elif i.startswith('2'):
        u.clean_tmp()
        print('Скачиваются архивные данные: ')
        # TODO use second callback
        d.get_archive_data(lambda x, y, z, w: archives_data_dl_callback(x, y, z, w),
                           lambda x, y, z: print("L2:", x, y, z))
    elif i.startswith('3'):
        raise NotImplementedError("GUI для скачивания актуальных данных ещё не реализован")
    elif i.startswith('4'):
        ArchivesApp.run()
    else:
        raise NotImplementedError("GUI для просмотра/изменения/обработки данных в БД ещё не реализован")

    print("Готово!")


if __name__ == "__main__":
    main()
