from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem

from api import web, parsing
from api.runtime import Runtime
from .design import viewer_full_table_design


class ViewerFullTableApp(QtWidgets.QMainWindow, viewer_full_table_design.Ui_MainWindow):
    preload_finished = QtCore.pyqtSignal()

    def __init__(self, period: str, company_id: int):
        super().__init__()
        ViewerFullTableApp.wnd = self
        self.period = period
        self.company_id = company_id
        self.company = Runtime.company_manager.get_company(self.company_id)
        self.setupUi(self)
        self.exit_button.clicked.connect(self._handle_exit_button_click)
        self._init_table()

    def _handle_exit_button_click(self):
        self._close()

    def _init_table(self):
        self.label.setText("Данные компании\n " + str(self.company.name) + " \nза " + str(self.period) + " год")
        self.data = [[i for i in map(str, list([x] + y))] for x, y in self.company.get_period_data(self.period)]
        print()
        self.data_table.setColumnCount(len(self.data[0]) if len(self.data) > 0 else 1)
        self.data_table.setRowCount(len(self.data))
        self.data_table.setHorizontalHeaderLabels(["Код строки"] + parsing.table_columns)
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                self.data_table.setItem(i, j, QTableWidgetItem(str(self.data[i][j])))
        self.data_table.resizeColumnsToContents()

    def _close(self):
        self.close()

    @staticmethod
    def run(period: str, company_id: int):
        window = ViewerFullTableApp(period, company_id)
        window.show()
