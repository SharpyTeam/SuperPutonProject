import sys
from threading import Thread

from PyQt5 import QtWidgets, QtCore

from api.config import RuntimeConfig
from api.runtime import Runtime
from .design import viewer_sum_settings_design


class ViewerFullTableApp(QtWidgets.QMainWindow, viewer_sum_settings_design.Ui_MainWindow):
    preload_finished = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        ViewerFullTableApp.wnd = self
        self.setupUi(self)
        self.preload_finished.connect(self._preload_finished)
        self.string_codes = None
        self.preloading_thread = Thread(target=self._preload_string_codes, daemon=True)
        self.listWidget.setEnabled(False)
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self._handle_save_button_click)
        self.exit_button.clicked.connect(self._handle_exit_button_click)
        self.preloading_thread.start()

    def _handle_save_button_click(self):
        RuntimeConfig.rows_indices_to_sum = [x.text() for x in self.listWidget.selectedItems()]
        self._close()

    def _handle_exit_button_click(self):
        self._close()

    def _preload_finished(self):
        self.listWidget.setEnabled(True)
        self.save_button.setEnabled(True)
        self.listWidget.addItems(self.string_codes)

    def _string_codes_fetch_callback(self, string_codes):
        self.string_codes = [x[0] for x in string_codes]

    def _preload_string_codes(self):
        Runtime.db_wrapper.commit_async(("SELECT DISTINCT string_code FROM reports", None),
                                        self._string_codes_fetch_callback)

    def _close(self):
        self.close()

    @staticmethod
    def run():
        app = QtWidgets.QApplication(sys.argv)
        window = ViewerFullTableApp()
        window.show()
        sys.exit(app.exec())
