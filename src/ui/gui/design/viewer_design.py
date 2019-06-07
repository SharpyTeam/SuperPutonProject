# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Documents\Projects\HSE\SuperPutonProject\ui_src\viewer.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setText("Подождите, загружаются данные из базы данных...")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.company_rb = QtWidgets.QRadioButton(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.company_rb.setFont(font)
        self.company_rb.setObjectName("company_rb")
        self.verticalLayout.addWidget(self.company_rb)
        self.year_rb = QtWidgets.QRadioButton(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.year_rb.setFont(font)
        self.year_rb.setObjectName("year_rb")
        self.verticalLayout.addWidget(self.year_rb)
        self.data_table = QtWidgets.QTableWidget(self.centralwidget)
        self.data_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.data_table.setProperty("showDropIndicator", False)
        self.data_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.data_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.data_table.setObjectName("data_table")
        self.data_table.setColumnCount(0)
        self.data_table.setRowCount(0)
        self.verticalLayout.addWidget(self.data_table)
        self.show_data_button = QtWidgets.QPushButton(self.centralwidget)
        self.show_data_button.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.show_data_button.sizePolicy().hasHeightForWidth())
        self.show_data_button.setSizePolicy(sizePolicy)
        self.show_data_button.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.show_data_button.setFont(font)
        self.show_data_button.setObjectName("show_data_button")
        self.verticalLayout.addWidget(self.show_data_button)
        self.exit_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.exit_button.sizePolicy().hasHeightForWidth())
        self.exit_button.setSizePolicy(sizePolicy)
        self.exit_button.setObjectName("exit_button")
        self.verticalLayout.addWidget(self.exit_button)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Просмотр данных"))
        self.company_rb.setText(_translate("MainWindow", "Выбрать компанию"))
        self.year_rb.setText(_translate("MainWindow", "Выбрать год"))
        self.show_data_button.setText(_translate("MainWindow", "Показать данные"))
        self.exit_button.setText(_translate("MainWindow", "Выход"))


