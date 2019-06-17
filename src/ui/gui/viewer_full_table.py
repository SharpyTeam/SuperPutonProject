import os
import subprocess
import sys
import warnings

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem

# Some magic to suppress deprecation warnings
# IDK why it's writing it into console instead of throwing simple warning
with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull

        from StyleFrame import StyleFrame, Styler
        from StyleFrame import utils as sf_utils

        sys.stderr = old_stderr

# Magic ends here

from pandas import DataFrame

from api import parsing, utils
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
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self._handle_export_button_click)
        self.exit_button.clicked.connect(self._handle_exit_button_click)
        self._init_table()

    def _handle_exit_button_click(self):
        self._close()

    def _handle_export_button_click(self):
        utils.create_missing()
        path = QtWidgets.QFileDialog.getSaveFileName(self, "Сохранить", os.path.join(utils.get_exports_path(),
                                                                                     utils.get_file_name_for_export(
                                                                                         self.company_id, self.period)),
                                                     "Файл Excel (*.xlsx)")
        self.export_button.setEnabled(False)
        if not path:
            return
        elif os.path.exists(path[0]):
            os.remove(path[0])
        headers = parsing.table_columns
        with StyleFrame.ExcelWriter(path[0]) as writer:
            export_data = [[float(cell) for cell in row[1:]] for row in self.data]
            export_string_codes = [int(row[0]) for row in self.data]
            df = DataFrame(data=export_data, columns=headers, index=export_string_codes)
            df.index.name = "Код строки"
            sf = StyleFrame(df)
            sf.apply_headers_style(Styler(bold=True, font_size=14))
            sf.to_excel(writer, sheet_name='Полная таблица',
                        index=True, best_fit=headers)
            writer.save()

        self.export_button.setEnabled(True)
        result = QtWidgets.QMessageBox.question(self, "Успех!",
                                                "Данные успешно экспортированы!\nОткрыть файл?",
                                                buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            command = 'start' if Runtime.is_windows else 'xdg-open'
            subprocess.Popen([command, os.path.normpath(path[0])], shell=True)

    def _init_table(self):
        self.label.setText("Данные компании\n " + str(self.company.name) + " \nза " + str(self.period) + " год")
        self.data = [[i for i in map(str, list([x] + y))] for x, y in self.company.get_period_data(self.period)]
        self.data_table.setColumnCount(len(self.data[0]) if len(self.data) > 0 else 1)
        self.data_table.setRowCount(len(self.data))
        self.data_table.setHorizontalHeaderLabels(["Код строки"] + parsing.table_columns)
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                self.data_table.setItem(i, j, QTableWidgetItem(str(self.data[i][j])))
        self.data_table.resizeColumnsToContents()
        self.export_button.setEnabled(True)
        self.setWindowTitle("Просмотр полной таблицы")

    def _close(self):
        self.close()

    @staticmethod
    def run(period: str, company_id: int):
        window = ViewerFullTableApp(period, company_id)
        window.show()
