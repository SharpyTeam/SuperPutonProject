# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Documents\Projects\HSE\SuperPutonProject\ui_src\viewer_list.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1096, 828)
        MainWindow.setWindowTitle("Загрузка...")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout.addWidget(self.line_3)
        self.data_table = QtWidgets.QTableWidget(self.centralwidget)
        self.data_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.data_table.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.data_table.setObjectName("data_table")
        self.data_table.setColumnCount(0)
        self.data_table.setRowCount(0)
        self.verticalLayout.addWidget(self.data_table)
        self.std_label = QtWidgets.QLabel(self.centralwidget)
        self.std_label.setObjectName("std_label")
        self.verticalLayout.addWidget(self.std_label)
        self.warning_label_2 = QtWidgets.QLabel(self.centralwidget)
        self.warning_label_2.setText("Невозможно показать диаграмму. Выберите элементы, находящиеся в одном и том же столбце.")
        self.warning_label_2.setObjectName("warning_label_2")
        self.verticalLayout.addWidget(self.warning_label_2)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.verticalLayout.addWidget(self.line_4)
        self.show_table_button = QtWidgets.QPushButton(self.centralwidget)
        self.show_table_button.setObjectName("show_table_button")
        self.verticalLayout.addWidget(self.show_table_button)
        self.show_stats_button = QtWidgets.QPushButton(self.centralwidget)
        self.show_stats_button.setObjectName("show_stats_button")
        self.verticalLayout.addWidget(self.show_stats_button)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.sum_settings_button = QtWidgets.QPushButton(self.centralwidget)
        self.sum_settings_button.setObjectName("sum_settings_button")
        self.verticalLayout.addWidget(self.sum_settings_button)
        self.exit_button = QtWidgets.QPushButton(self.centralwidget)
        self.exit_button.setObjectName("exit_button")
        self.verticalLayout.addWidget(self.exit_button)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1096, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("MainWindow", "Подождите, загрузка..."))
        self.std_label.setText(_translate("MainWindow", "Здесь будет показано среднее квадратическое отклонение. Выберите столбец."))
        self.show_table_button.setText(_translate("MainWindow", "Показать полную таблицу"))
        self.show_stats_button.setText(_translate("MainWindow", "Показать диаграмму для выбранного столбца (выберите столбец...)"))
        self.sum_settings_button.setText(_translate("MainWindow", "Настройки суммирования строк"))
        self.exit_button.setText(_translate("MainWindow", "Назад"))


