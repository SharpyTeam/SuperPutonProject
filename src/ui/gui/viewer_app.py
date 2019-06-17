import sys
from threading import Thread
from typing import List, Optional

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem

from api import db
from api.models.company import Company
from ui.gui.viewer_list import ViewerListApp
from .design import viewer_design


class ViewerApp(QtWidgets.QMainWindow, viewer_design.Ui_MainWindow):
    preload_finished = QtCore.pyqtSignal()
    data_option_selected = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        ViewerApp.wnd = self
        self.db_wrapper = db.DBWrapper()
        self.db_wrapper.start()
        self.preload_finished.connect(self._r_ui_preload_finished)
        self.data_option_selected.connect(self._r_ui_data_option_selected)
        self.companies_list: Optional[List[Company]] = None
        self.periods_list: Optional[List[str]] = None
        self.setupUi(self)
        self.exit_button.clicked.connect(lambda _: self._close())
        self.year_rb.toggled.connect(self._handle_year_rb_toggle)
        self.company_rb.toggled.connect(self._handle_company_rb_toggle)
        self.year_rb.setEnabled(False)
        self.company_rb.setEnabled(False)
        self.data_table.setEnabled(False)
        self.show_data_button.clicked.connect(self._run_viewer_list)
        self.preload_data_thread = Thread(target=self._preload_data, daemon=True)
        self.preload_data_thread.start()

    def _close(self):
        sys.exit(0)

    def _run_viewer_list(self):
        if self.year_rb.isChecked():
            ViewerListApp.run(period=str(self.data_table.selectedItems()[0].text()))
        else:
            ViewerListApp.run(company_id=int(self.data_table.selectedItems()[0].text()))

    def _r_ui_preload_finished(self):
        self.year_rb.setEnabled(True)
        self.company_rb.setEnabled(True)
        self.label.setVisible(False)
        self.data_table.setEnabled(True)
        self.show_data_button.setEnabled(True)

    def _r_ui_data_option_selected(self):
        self.data_table.clear()
        if self.year_rb.isChecked():
            self.data_table.setColumnCount(1)
            self.data_table.setHorizontalHeaderLabels(["Доступные периоды"])
            self.data_table.setRowCount(len(self.periods_list))
            for i in range(len(self.periods_list)):
                self.data_table.setItem(i, 0, QTableWidgetItem(self.periods_list[i]))
            if len(self.periods_list) == 0:
                self.data_table.setRowCount(1)
                self.data_table.setItem(0, 0, QTableWidgetItem("НЕТ ДОСТУПНЫХ ПЕРИОДОВ"))
        else:
            self.data_table.setColumnCount(2)
            self.data_table.setHorizontalHeaderLabels(["№ в реестре", "Название"])
            self.data_table.setRowCount(len(self.companies_list))
            for i in range(len(self.companies_list)):
                self.data_table.setItem(i, 0, QTableWidgetItem(str(self.companies_list[i].id)))
                self.data_table.setItem(i, 1, QTableWidgetItem(str(self.companies_list[i].name)))
            if len(self.companies_list) == 0:
                self.data_table.setColumnCount(1)
                self.data_table.setHorizontalHeaderLabels(["Список компаний"])
                self.data_table.setRowCount(1)
                self.data_table.setItem(0, 0, QTableWidgetItem("НЕТ ДАННЫХ О КОМПАНИЯХ"))

        self.data_table.resizeColumnsToContents()

    def _company_preload_callback(self, companies: List[Company]):
        self.companies_list = companies

    def _preload_data(self):
        self.periods_list = self.db_wrapper.get_all_periods()
        self.db_wrapper.get_all_companies_names_async(self._company_preload_callback)
        while self.companies_list is None or self.periods_list is None:
            pass
        self.preload_finished.emit()

    def _handle_year_rb_toggle(self):
        if self.year_rb.isChecked():
            self.company_rb.setChecked(False)

        self.data_option_selected.emit()

    def _handle_company_rb_toggle(self):
        if self.year_rb.isChecked():
            self.company_rb.setChecked(False)

        self.data_option_selected.emit()

    @staticmethod
    def run():
        app = QtWidgets.QApplication(sys.argv)
        window = ViewerApp()
        window.show()
        sys.exit(app.exec())
