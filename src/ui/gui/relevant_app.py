import sys
from threading import Thread

from PyQt5 import QtWidgets

from .design import relevant_design
from src.api import config
from ...api import web, parsing, utils


class RelevantApp(QtWidgets.QMainWindow, relevant_design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.parseProgressBar.setVisible(False)
        self.dl_progress_label.setVisible(False)
        self.parsing_pb_label.setVisible(False)
        preloading_thread = Thread(target=self._preload_last_year)
        preloading_thread.start()
        self.downloader_thread: Thread = Thread(target=self._begin_download)
        self.interrupter_thread: Thread = Thread(target=self._interrupt_download)
        self.current_year = "-"
        self.extract_pb_label.setVisible(False)
        self.extract_pb.setVisible(False)
        self.beginDownloadButton.clicked.connect(self.on_dl_button_press)

    def _preload_last_year(self):
        self.current_year = parsing.get_relevant_year(web.download_page(config.RELEVANT_PAGE_URL))
        self.beginDownloadButton.setEnabled(True)
        self.parsing_pb_label.setText("Список доступных архивов:")
        self.status_label.setVisible(False)
        self.parsing_pb_label.setVisible(True)

    def _actual_data_dl_callback(self, status: web.DataGetStatus, done: float, total: float):
        if status == web.DataGetStatus.STARTED:
            self.status_label.setText("Скачивание данных...")
        elif status == web.DataGetStatus.DOWNLOADING:
            self.previous_status = web.DataGetStatus.DOWNLOADING
            self.dl_progress_label.setText("Загружено: " + utils.format_bytes(done))
        else:
            self.status_label.setText("Подождите...")
            self.dl_progress_label.setText("Данные скачались!")

    def _actual_data_extract_callback(self, status: web.DataGetStatus, done: float, total: float):
        if status == web.DataGetStatus.STARTED:
            self.status_label.setText("Распаковка...")
            self.dl_progress_label.setVisible(False)
            self.extract_pb_label.setVisible(True)
            self.extract_pb.setVisible(True)
        elif status == web.DataGetStatus.EXTRACTING:
            if self.previous_status == web.DataGetStatus.DOWNLOADING:
                self.status_label.setText("Распаковка и обработка...")
                self.previous_status = web.DataGetStatus.EXTRACTING
            self.dl_progress_label.setText(
                "Распаковано: " + utils.format_bytes(done) + " из " + utils.format_bytes(total))
        elif status == status.FINISHED:
            self.status_label.setText("Обработка...")
            # self.

    def _parsing_callback(self, status: web.DataGetStatus, parsed: int, total: int):
        print("> P:", status, parsed, total)
        if status == web.DataGetStatus.PARSING:
            if not self.parseProgressBar.isVisible():
                self.parseProgressBar.setVisible(True)
                self.parseProgressBar.setMinimum(0)
                self.parseProgressBar.setValue(parsed)
                self.parseProgressBar.setMaximum(total)
            self.parseProgressBar.setValue(parsed)

    def _begin_download(self):
        utils.clean_tmp()
        web.download_archive_data(lambda x, y, z, w: self._archives_data_dl_callback(x, y, z, w),
                                  lambda x, y, z: self._parsing_callback(x, y, z))
        self.parseProgressBar.setVisible(False)
        self.dlProgressBar.setVisible(False)
        self.dl_pb_label.setVisible(False)
        self.parsing_pb_label.setVisible(False)
        self.status_label.setText("Всё скачалось!")

    def _interrupt_download(self):
        pass

    def on_dl_button_press(self):
        self.parsing_pb_label.setText("Обработка и сохранение данных:")
        self.beginDownloadButton.setEnabled(False)
        self.status_label.setVisible(True)
        self.downloader_thread.start()
        print("85")

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
