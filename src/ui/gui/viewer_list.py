from threading import Thread
from typing import Optional

import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem

from api import parsing
from api.runtime import Runtime
from ui.gui.viewer_full_table import ViewerFullTableApp
from ui.gui.viewer_sum_settings import ViewerSumSettingsApp
from .design import viewer_list_design


class ViewerListApp(QtWidgets.QMainWindow, viewer_list_design.Ui_MainWindow):
    preload_finished = QtCore.pyqtSignal()

    def __init__(self, period: Optional[str] = None, company_id: Optional[int] = None):
        super().__init__()
        ViewerListApp.wnd = self
        self.by_period = period is not None
        self.period = period
        self.company_id = company_id
        self.setupUi(self)
        self.company = None
        self.data = None
        self.preload_finished.connect(self._preload_ended)
        self.sum_settings_button.clicked.connect(self._run_sum_settings)
        self.show_stats_button.clicked.connect(self._run_diagram_view)
        self.show_table_button.clicked.connect(self._run_full_table_view)
        self.preloading_thread = Thread(target=self._preload_all, daemon=True)
        self.data_table.setEnabled(False)
        self.show_stats_button.setEnabled(False)
        self.show_table_button.setEnabled(False)
        self.sum_settings_button.setEnabled(False)
        self.exit_button.clicked.connect(self._handle_exit_button_click)
        self.selected_column = 0
        self.selected_rows = []
        self.data_table.itemSelectionChanged.connect(self._handle_selection_changed)
        self.preloading_thread.start()
        self.warning_label_2.setVisible(False)

    def _warning_message(self):
        self.show_stats_button.setEnabled(False)
        self.show_stats_button.setText("Показать диаграмму для выбранного столбца (выберите столбец...)")
        self.std_label.setText("Здесь будет показано среднее квадратическое отклонение. Выберите столбец.")

    def _handle_selection_changed(self):
        if len(self.data_table.selectedItems()) == 0:
            self._warning_message()
            self.show_table_button.setText("Показать полную таблицу (выберите строку!)")
            self.show_table_button.setEnabled(False)
            return

        if len(set([i.column() for i in self.data_table.selectedItems()])) > 1:
            self.warning_label_2.setVisible(True)
            self.show_stats_button.setDisabled(True)
            return
        else:
            self.show_stats_button.setDisabled(False)
            self.warning_label_2.setVisible(False)

        if len(set([i.row() for i in self.data_table.selectedItems()])) > 1:
            self.show_table_button.setEnabled(False)
            self.show_table_button.setText("Показать полную таблицу (выберите одну строку!)")
        else:
            self.show_table_button.setEnabled(True)
            self.show_table_button.setText("Показать полную таблицу")

        self.selected_column = self.data_table.selectedItems()[0].column()
        self.selected_rows = [i.row() for i in self.data_table.selectedItems()]
        self.selected_column -= 2 if self.by_period else 1
        if self.selected_column < 0:
            self._warning_message()
            return
        self.show_stats_button.setEnabled(True)
        self.show_stats_button.setText("Показать диаграмму для выбранных ячеек")
        if self.by_period:
            std = Runtime.company_manager.get_companies_standard_deviation_for_period(self.selected_column, self.period)
        else:
            std = Runtime.company_manager.get_company_standard_deviation_for_periods(self.selected_column,
                                                                                     self.company_id)

        self.std_label.setText("Среднеквадратичное отклонение по всему столбцу: " + str(std))

    def _run_diagram_view(self):
        fig, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(aspect="equal"))

        if self.by_period:
            companies_ids = []
            for i in self.data_table.selectedItems():
                companies_ids.append(int(self.data[i.row()][0]))
            data = Runtime.company_manager.get_companies_diagram_data_for_period(self.selected_column, self.period,
                                                                                 companies_ids)
            labels = [l.name for l in Runtime.company_manager.get_companies(tuple(companies_ids))]

        else:
            periods = []
            for i in self.data_table.selectedItems():
                periods.append(str(self.data[i.row()][0]))
            data = Runtime.company_manager.get_company_diagram_data_for_periods(self.selected_column,
                                                                                self.company_id, periods)
            labels = periods
        ax.pie(data, labels=labels)
        ax.axis('equal')
        ax.set_title("Диаграмма по выделенным данным")
        plt.show()

    def _run_sum_settings(self):
        ViewerSumSettingsApp.run(self)

    def _run_full_table_view(self):
        if self.by_period:
            company_id = (int(self.data[self.data_table.selectedItems()[0].row()][0]))
            year = self.period
        else:
            company_id = self.company_id
            year = (str(self.data[self.data_table.selectedItems()[0].row()][0]))
        ViewerFullTableApp.run(year, company_id)

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
        self.data_table.setHorizontalHeaderLabels(
            (["№ компании", "Название компании"] if self.by_period else ["Год"]) + parsing.table_columns)
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
        window = ViewerListApp(period=period, company_id=company_id)
        window.show()
