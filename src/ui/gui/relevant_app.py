import sys
from threading import Thread
from typing import List

from PyQt5 import QtWidgets, QtCore
from .design import relevant_design
from api import web, parsing, utils
from api import config


class RelevantApp(QtWidgets.QMainWindow, relevant_design.Ui_MainWindow):
    preload_finished = QtCore.pyqtSignal()
    download_started = QtCore.pyqtSignal()
    download_progress_changed = QtCore.pyqtSignal(int, int)
    extract_started = QtCore.pyqtSignal()
    extract_progress_changed = QtCore.pyqtSignal(int, int)
    parse_progress_changed = QtCore.pyqtSignal(int, int)
    download_finished = QtCore.pyqtSignal()
    download_interrupted = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.is_downloading = False
        self.parseProgressBar.setVisible(False)
        self.extract_pb.setVisible(False)
        self.extract_pb_label.setVisible(False)
        self.parsing_pb_label.setVisible(False)
        self.dl_progress_label.setVisible(False)
        self.preload_finished.connect(self._r_ui_preload_finished)
        self.download_started.connect(self._r_ui_download_started)
        self.extract_started.connect(self._r_ui_extract_started)
        self.download_progress_changed.connect(self._r_ui_download_progress_changed)
        self.extract_progress_changed.connect(self._r_ui_extract_progress_changed)
        self.parse_progress_changed.connect(self._r_ui_parse_progress_changed)
        self.download_finished.connect(self._r_ui_download_finished)
        preloading_thread = Thread(target=self._preload_year_list, daemon=True)
        preloading_thread.start()
        self.downloader_thread: Thread = Thread(target=self._begin_download, daemon=True)
        self.interrupter_thread: Thread = Thread(target=self._interrupt_download, daemon=True)
        self.year = None
        self.beginDownloadButton.clicked.connect(self.on_dl_button_press)

    def _r_ui_preload_finished(self):
        self.beginDownloadButton.setEnabled(True)
        self.status_label.setVisible(False)
        self.year_label.setText("Актуальные данные: " + self.year + " год")

    def _r_ui_download_started(self):
        self.dl_progress_label.setVisible(True)
        self.dl_progress_label.setText("Начинается загрузка...")
        self.beginDownloadButton.setEnabled(True)

    def _r_ui_download_progress_changed(self, done: int, total: int):
        self.status_label.setText("Скачивание данных...")
        self.dl_progress_label.setText("Загружено: " + utils.format_bytes(done))

    def _r_ui_extract_started(self):
        self.status_label.setText("Распаковка и обработка...")
        self.status_label.setVisible(True)
        self.parseProgressBar.setVisible(True)
        self.parseProgressBar.setMaximum(100)
        self.parseProgressBar.setTextVisible(False)
        self.parseProgressBar.setValue(100)
        self.extract_pb.setVisible(True)
        self.extract_pb_label.setVisible(True)
        self.parsing_pb_label.setVisible(True)

    def _r_ui_extract_progress_changed(self, done: int, total: int):
        self.extract_pb.setValue(done)
        if self.extract_pb.maximum() != total:
            self.extract_pb.setMaximum(total)

    def _r_ui_parse_progress_changed(self, parsed: int, total: int):
        if not self.parseProgressBar.isTextVisible():
            self.parseProgressBar.setTextVisible(True)
            self.parseProgressBar.setMaximum(total)
        if self.parseProgressBar.isTextVisible():
            self.parseProgressBar.setMaximum(total)
            self.parseProgressBar.setValue(parsed)

    def _r_ui_download_finished(self):
        self.parseProgressBar.setVisible(False)
        self.extract_pb.setVisible(False)
        self.extract_pb_label.setVisible(False)
        self.parsing_pb_label.setVisible(False)
        self.status_label.setText("Всё скачалось!")
        self.dl_progress_label.setText("Данные за " + self.year + " год успешно скачаны и обработаны.")
        self.beginDownloadButton.setText("Закрыть программу")
        self.beginDownloadButton.setEnabled(True)

    def _preload_year_list(self):
        self.year = parsing.get_relevant_year(web.download_page(config.RELEVANT_PAGE_URL))
        self.preload_finished.emit()

    def _relevant_data_dl_callback(self, status: web.DataGetStatus, done: int, total: int):
        if status == web.DataGetStatus.SKIPPING:
            self.download_finished.emit()
        # TODO: Show icons next to widget items
        elif status == web.DataGetStatus.STARTED:
            self.download_started.emit()
        elif status == web.DataGetStatus.DOWNLOADING:
            self.download_progress_changed.emit(done, total)
        else:
            pass
        # TODO: Show icons next to widget items

    def _extracting_callback(self, status: web.DataGetStatus, done: int, total: int):
        if status == web.DataGetStatus.STARTED:
            self.extract_started.emit()
        elif status == web.DataGetStatus.EXTRACTING:
            self.extract_progress_changed.emit(done, total)

    def _parsing_callback(self, status: web.DataGetStatus, parsed: int, total: int):
        if status == web.DataGetStatus.PARSING:
            self.parse_progress_changed.emit(parsed, total)

    def _begin_download(self):
        utils.clean_tmp()
        web.download_relevant_data(lambda x, y, z: self._relevant_data_dl_callback(x, y, z),
                                   lambda x, y, z: self._extracting_callback(x, y, z),
                                   lambda x, y, z: self._parsing_callback(x, y, z))
        utils.clean_tmp()
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
        window = RelevantApp()
        window.show()
        sys.exit(app.exec())
