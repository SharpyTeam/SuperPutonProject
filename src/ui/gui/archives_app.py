import sys
from threading import Thread
from typing import List

from PyQt5 import QtWidgets, QtCore
from .design import archives_design
from src.api import web, parsing, utils
from src.api import config


class ArchivesApp(QtWidgets.QMainWindow, archives_design.Ui_MainWindow):
    preload_finished = QtCore.pyqtSignal()
    download_started = QtCore.pyqtSignal()
    download_progress_changed = QtCore.pyqtSignal(int, int)
    parse_progress_changed = QtCore.pyqtSignal()
    download_finished = QtCore.pyqtSignal()
    download_interrupted = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.is_downloading = False
        self.dlProgressBar.setVisible(False)
        self.parseProgressBar.setVisible(False)
        self.dl_pb_label.setVisible(False)
        self.parsing_pb_label.setVisible(False)
        self.preload_finished.connect(self._r_ui_preload_finished)
        self.download_started.connect(self._r_ui_download_started)
        self.download_progress_changed.connect(self._r_ui_download_progress_changed)
        self.parse_progress_changed.connect(self._r_ui_parse_progress_changed)
        self.download_finished.connect(self._r_ui_download_finished)
        preloading_thread = Thread(target=self._preload_year_list)
        preloading_thread.start()
        self.downloader_thread: Thread = Thread(target=self._begin_download)
        self.interrupter_thread: Thread = Thread(target=self._interrupt_download)
        self.year_list: List = []
        self.beginDownloadButton.clicked.connect(self.on_dl_button_press)

    def _r_ui_preload_finished(self):
        self.listWidget.clear()
        self.listWidget.addItems(self.year_list)
        self.beginDownloadButton.setEnabled(True)
        self.parsing_pb_label.setText("Список доступных архивов:")
        self.status_label.setVisible(False)
        self.parsing_pb_label.setVisible(True)

    def _r_ui_download_started(self):
        self.dlProgressBar.setTextVisible(False)
        self.dl_pb_label.setVisible(True)
        self.dlProgressBar.setVisible(True)
        self.dlProgressBar.setMinimum(0)
        self.dlProgressBar.setMaximum(100)
        self.dlProgressBar.setValue(100)

    def _r_ui_download_progress_changed(self, files_done: int, files_total: int, ):
        if not self.dlProgressBar.isTextVisible():
            self.dlProgressBar.setTextVisible(True)
            self.dlProgressBar.setMaximum(files_total)
        if self.dlProgressBar.isTextVisible():
            self.dlProgressBar.setValue(files_done)

    def _r_ui_parse_progress_changed(self, parsed: int, total: int):
        if not self.parseProgressBar.isVisible():
            self.parseProgressBar.setVisible(True)
            self.parseProgressBar.setMinimum(0)
            self.parseProgressBar.setValue(parsed)
            self.parseProgressBar.setMaximum(total)
        self.parseProgressBar.setValue(parsed)

    def _r_ui_download_finished(self):
        self.parseProgressBar.setVisible(False)
        self.dlProgressBar.setVisible(False)
        self.dl_pb_label.setVisible(False)
        self.parsing_pb_label.setVisible(False)
        self.status_label.setText("Всё скачалось!")
        self.listWidget.setVisible(False)

    def _preload_year_list(self):
        self.year_list = [i + ", I квартал" for i in
                          parsing.get_available_archive_years(web.download_page(config.ARCHIVES_PAGE_URL))]
        self.preload_finished.emit()

    def _archives_data_dl_callback(self, status: web.DataGetStatus, files_done: int, files_total: int, year: str):
        print(status, files_done, files_total, year)
        if status == web.DataGetStatus.SKIPPING:
            pass
        # TODO: Show icons next to widget items
        elif status == web.DataGetStatus.STARTED:
            self.download_started.emit()
        elif status == web.DataGetStatus.DOWNLOADING:
            self.download_progress_changed.emit(files_done, files_total)
        else:
            pass
        # TODO: Show icons next to widget items

    def _parsing_callback(self, status: web.DataGetStatus, parsed: int, total: int):
        print("> P:", status, parsed, total)
        if status == web.DataGetStatus.PARSING:
            self.parse_progress_changed.emit(parsed, total)

    def _begin_download(self):
        utils.clean_tmp()
        web.download_archive_data(lambda x, y, z, w: self._archives_data_dl_callback(x, y, z, w),
                                  lambda x, y, z: self._parsing_callback(x, y, z))
        self.download_finished.emit()

    def _interrupt_download(self):
        sys.exit(0)

    def on_dl_button_press(self):
        if not self.is_downloading:
            self.is_downloading = True
            self.parsing_pb_label.setText("Обработка и сохранение данных:")
            self.beginDownloadButton.setEnabled(False)
            self.status_label.setVisible(True)
            self.downloader_thread.start()
            self.beginDownloadButton.setText("Остановить загрузку (аварийное завершение)")
        else:
            sys.exit(0)
        # print("85")

        # self.dlProgressBar.setVisible(True)
        # self.parseProgressBar.setVisible(True)
        # self.dl_pb_label.setVisible(True)

    def exit_app(self):
        self.close()

    @staticmethod
    def run():
        app = QtWidgets.QApplication(sys.argv)
        window = ArchivesApp()
        window.show()
        sys.exit(app.exec())
