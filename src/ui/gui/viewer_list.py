import sys
from threading import Thread
from typing import Optional

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem

from api.runtime import Runtime
from ui.gui.viewer_sum_settings import ViewerSumSettingsApp
from .design import viewer_list_design


class ViewerListApp(QtWidgets.QMainWindow, viewer_list_design.Ui_MainWindow):
    preload_finished = QtCore.pyqtSignal()

    def __init__(self, period: Optional[str] = None, company_id: Optional[int] = None):
        super().__init__()
        self.by_period = period is not None
        self.period = period
        self.company_id = company_id
        self.setupUi(self)
        self.company = None
        self.data = None
        self.preload_finished.connect(self._preload_ended)
        self.sum_settings_button.clicked.connect(self._run_sum_settings)
        self.preloading_thread = Thread(target=self._preload_all, daemon=True)
        self.data_table.setEnabled(False)
        self.show_stats_button.setEnabled(False)
        self.show_table_button.setEnabled(False)
        self.sum_settings_button.setEnabled(False)
        self.exit_button.clicked.connect(self._handle_exit_button_click)
        self.preloading_thread.start()

    def _run_sum_settings(self):
        ViewerSumSettingsApp.run()

    def _handle_save_button_click(self):
        self._close()

    def _handle_exit_button_click(self):
        self._close()

    def _preload_ended(self):
        self.sum_settings_button.setEnabled(True)
        if self.by_period:
            self.label.setText("Данные по всем компаниям за " + str(self.period) + " год")
            self.data = [(x.id, x.name) + x.get_period_data_summed(self.period)
                         for x in Runtime.company_manager.get_companies() if
                         x.get_period_data_summed(self.period) is not None]
        else:
            self.company = Runtime.company_manager.get_company(self.company_id)
            available_periods = Runtime.db_wrapper.get_all_periods()
            self.data = [(period,) + self.company.get_period_data_summed(period)
                         for period in available_periods if self.company.get_period_data_summed(period) is not None]
            self.label.setText("Данные по компании \n" + self.company.name + "\nза всё время")
        self.data_table.setColumnCount(len(self.data[0]) if len(self.data) > 0 else 1)
        self.data_table.setRowCount(len(self.data))
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                self.data_table.setItem(i, j, QTableWidgetItem(str(self.data[i][j])))
        self.setWindowTitle("Просмотр данных")
        self.data_table.resizeColumnsToContents()
        self.data_table.setEnabled(True)

    def _preload_callback(self):
        self.preload_finished.emit()

    def _preload_all(self):
        Runtime.company_manager.load_from_db(self._preload_callback)

    def _close(self):
        self.close()

    @staticmethod
    def run(period: Optional[str] = None, company_id: Optional[int] = None):
        # app = QtWidgets.QApplication(sys.argv)
        window = ViewerListApp(period=period, company_id=company_id)
        window.show()
        # sys.exit(app.exec())
